#!/usr/bin/env python3
"""
Extract grant information from IRS 990PF XML files.

This script reads the pf_forms_extracted.csv file and extracts detailed
grant information from each XML file, creating a comprehensive summary
of all grants given by private foundations.
"""

import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# IRS XML namespace
IRS_NAMESPACE = {'irs': 'http://www.irs.gov/efile'}


def parse_xml_file(xml_path: Path) -> Optional[ET.Element]:
    """Parse an XML file and return the root element."""
    try:
        tree = ET.parse(xml_path)
        return tree.getroot()
    except Exception as e:
        logger.error(f"Error parsing {xml_path.name}: {e}")
        return None


def get_text(element: Optional[ET.Element], path: str, namespaces: dict) -> str:
    """Safely extract text from an XML element."""
    if element is None:
        return ""
    
    found = element.find(path, namespaces)
    if found is not None and found.text:
        return found.text.strip()
    return ""


def extract_filer_info(root: ET.Element) -> Dict[str, str]:
    """Extract basic filer information from the return."""
    filer_info = {}
    
    # Extract EIN
    filer_info['ein'] = get_text(root, './/irs:Filer/irs:EIN', IRS_NAMESPACE)
    
    # Extract organization name (try both possible tags)
    name = get_text(root, './/irs:Filer/irs:BusinessName/irs:BusinessNameLine1Txt', IRS_NAMESPACE)
    if not name:
        name = get_text(root, './/irs:Filer/irs:Name/irs:BusinessNameLine1Txt', IRS_NAMESPACE)
    filer_info['organization_name'] = name
    
    # Extract tax period end
    filer_info['tax_period_end'] = get_text(root, './/irs:TaxPeriodEndDt', IRS_NAMESPACE)
    
    return filer_info


def extract_grants_from_xml(xml_path: Path) -> List[Dict[str, str]]:
    """Extract all grant information from a single XML file."""
    root = parse_xml_file(xml_path)
    if root is None:
        return []
    
    # Get filer information
    filer_info = extract_filer_info(root)
    
    # Find all grant entries
    grants = []
    grant_elements = root.findall('.//irs:GrantOrContributionPdDurYrGrp', IRS_NAMESPACE)
    
    for grant_elem in grant_elements:
        grant = {
            'source_file': xml_path.name,
            'filer_ein': filer_info['ein'],
            'filer_organization_name': filer_info['organization_name'],
            'tax_period_end': filer_info['tax_period_end']
        }
        
        # Extract recipient business name
        recipient_name = get_text(grant_elem, 'irs:RecipientBusinessName/irs:BusinessNameLine1Txt', IRS_NAMESPACE)
        if not recipient_name:
            # Try person name if business name not found
            recipient_name = get_text(grant_elem, 'irs:RecipientPersonNm', IRS_NAMESPACE)
        
        # Sometimes there's a second line for the business name
        recipient_name2 = get_text(grant_elem, 'irs:RecipientBusinessName/irs:BusinessNameLine2Txt', IRS_NAMESPACE)
        if recipient_name2:
            recipient_name = f"{recipient_name} {recipient_name2}"
        
        grant['recipient_name'] = recipient_name
        
        # Extract US address (most common)
        grant['recipient_address_line1'] = get_text(grant_elem, 'irs:RecipientUSAddress/irs:AddressLine1Txt', IRS_NAMESPACE)
        grant['recipient_address_line2'] = get_text(grant_elem, 'irs:RecipientUSAddress/irs:AddressLine2Txt', IRS_NAMESPACE)
        grant['recipient_city'] = get_text(grant_elem, 'irs:RecipientUSAddress/irs:CityNm', IRS_NAMESPACE)
        grant['recipient_state'] = get_text(grant_elem, 'irs:RecipientUSAddress/irs:StateAbbreviationCd', IRS_NAMESPACE)
        grant['recipient_zip'] = get_text(grant_elem, 'irs:RecipientUSAddress/irs:ZIPCd', IRS_NAMESPACE)
        
        # If no US address, try foreign address
        if not grant['recipient_city']:
            grant['recipient_city'] = get_text(grant_elem, 'irs:RecipientForeignAddress/irs:CityNm', IRS_NAMESPACE)
            grant['recipient_state'] = get_text(grant_elem, 'irs:RecipientForeignAddress/irs:ProvinceOrStateNm', IRS_NAMESPACE)
            grant['recipient_country'] = get_text(grant_elem, 'irs:RecipientForeignAddress/irs:CountryCd', IRS_NAMESPACE)
        else:
            grant['recipient_country'] = 'US'
        
        # Extract other grant details
        grant['recipient_relationship'] = get_text(grant_elem, 'irs:RecipientRelationshipTxt', IRS_NAMESPACE)
        grant['recipient_foundation_status'] = get_text(grant_elem, 'irs:RecipientFoundationStatusTxt', IRS_NAMESPACE)
        grant['grant_purpose'] = get_text(grant_elem, 'irs:GrantOrContributionPurposeTxt', IRS_NAMESPACE)
        
        # Extract grant amount
        amount = get_text(grant_elem, 'irs:Amt', IRS_NAMESPACE)
        grant['grant_amount'] = amount if amount else "0"
        
        # Only add if we have at least a recipient name and amount
        if grant['recipient_name'] or grant['grant_amount'] != "0":
            grants.append(grant)
    
    return grants


def process_all_files(csv_file: Path, xml_dir: Path, output_file: Path):
    """Process all XML files listed in the CSV and extract grant information."""
    
    logger.info(f"Reading foundation list from {csv_file}")
    
    all_grants = []
    total_files = 0
    files_with_grants = 0
    errors = 0
    
    # Read the CSV file
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_files += 1
            xml_filename = row['file']
            xml_path = xml_dir / xml_filename
            
            if not xml_path.exists():
                logger.warning(f"File not found: {xml_filename}")
                errors += 1
                continue
            
            # Extract grants from this file
            grants = extract_grants_from_xml(xml_path)
            
            if grants:
                files_with_grants += 1
                all_grants.extend(grants)
                logger.info(f"Processed {xml_filename}: Found {len(grants)} grants")
            
            # Log progress every 100 files
            if total_files % 100 == 0:
                logger.info(f"Progress: {total_files} files processed, {len(all_grants)} grants found")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing complete!")
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Files with grants: {files_with_grants}")
    logger.info(f"Total grants found: {len(all_grants)}")
    logger.info(f"Errors: {errors}")
    logger.info(f"{'='*60}\n")
    
    # Write results to CSV
    if all_grants:
        logger.info(f"Writing results to {output_file}")
        
        # Define column order
        fieldnames = [
            'source_file',
            'filer_ein',
            'filer_organization_name',
            'tax_period_end',
            'recipient_name',
            'recipient_address_line1',
            'recipient_address_line2',
            'recipient_city',
            'recipient_state',
            'recipient_zip',
            'recipient_country',
            'recipient_relationship',
            'recipient_foundation_status',
            'grant_purpose',
            'grant_amount'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_grants)
        
        logger.info(f"Successfully wrote {len(all_grants)} grants to {output_file}")
        
        # Generate summary statistics
        generate_summary_stats(all_grants)
    else:
        logger.warning("No grants found in any files!")


def generate_summary_stats(grants: List[Dict[str, str]]):
    """Generate and log summary statistics about the grants."""
    
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY STATISTICS")
    logger.info(f"{'='*60}")
    
    # Total grant amount
    total_amount = sum(float(g['grant_amount']) for g in grants if g['grant_amount'])
    logger.info(f"Total grant amount: ${total_amount:,.2f}")
    
    # Average grant amount
    avg_amount = total_amount / len(grants) if grants else 0
    logger.info(f"Average grant amount: ${avg_amount:,.2f}")
    
    # Count unique filers (grantors)
    unique_filers = len(set(g['filer_ein'] for g in grants if g['filer_ein']))
    logger.info(f"Unique grantors (foundations): {unique_filers}")
    
    # Count unique recipients
    unique_recipients = len(set(g['recipient_name'] for g in grants if g['recipient_name']))
    logger.info(f"Unique recipients: {unique_recipients}")
    
    # Top 10 largest grants
    logger.info(f"\nTop 10 Largest Grants:")
    sorted_grants = sorted(grants, key=lambda x: float(x['grant_amount']) if x['grant_amount'] else 0, reverse=True)
    for i, grant in enumerate(sorted_grants[:10], 1):
        logger.info(f"{i}. ${float(grant['grant_amount']):,.2f} to {grant['recipient_name']} from {grant['filer_organization_name']}")
    
    logger.info(f"{'='*60}\n")


def main():
    """Main execution function."""
    # Define paths
    script_dir = Path(__file__).parent
    csv_file = script_dir / "pf_forms_extracted.csv"
    xml_dir = script_dir / "irs_data"
    output_file = script_dir / "grants_information_summary.csv"
    
    # Verify input files exist
    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_file}")
        return
    
    if not xml_dir.exists():
        logger.error(f"XML directory not found: {xml_dir}")
        return
    
    logger.info("Starting grant information extraction...")
    logger.info(f"Source CSV: {csv_file}")
    logger.info(f"XML directory: {xml_dir}")
    logger.info(f"Output file: {output_file}")
    logger.info("")
    
    # Process all files
    process_all_files(csv_file, xml_dir, output_file)
    
    logger.info("Done!")


if __name__ == "__main__":
    main()

