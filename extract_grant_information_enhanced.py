#!/usr/bin/env python3
"""
Enhanced grant information extraction from IRS 990/990PF XML files.

This version extracts comprehensive foundation-level and grant-level data
including all recommended fields from the analysis.
"""

import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging
from collections import defaultdict

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


def get_text_from_paths(element: Optional[ET.Element], paths: List[str], namespaces: dict) -> str:
    """Try multiple paths and return the first non-empty result."""
    for path in paths:
        result = get_text(element, path, namespaces)
        if result:
            return result
    return ""


def extract_foundation_info(root: ET.Element, xml_filename: str) -> Dict[str, str]:
    """Extract comprehensive foundation information from the return."""
    foundation = {
        'source_file': xml_filename,
    }
    
    # Basic Info
    foundation['filer_ein'] = get_text(root, './/irs:Filer/irs:EIN', IRS_NAMESPACE)
    
    # Organization name (try multiple possible locations)
    name = get_text_from_paths(root, [
        './/irs:Filer/irs:BusinessName/irs:BusinessNameLine1Txt',
        './/irs:Filer/irs:Name/irs:BusinessNameLine1Txt',
        './/irs:ReturnHeader/irs:Filer/irs:BusinessName/irs:BusinessNameLine1Txt'
    ], IRS_NAMESPACE)
    foundation['filer_organization_name'] = name
    
    # Tax period
    foundation['tax_period_begin'] = get_text(root, './/irs:TaxPeriodBeginDt', IRS_NAMESPACE)
    foundation['tax_period_end'] = get_text(root, './/irs:TaxPeriodEndDt', IRS_NAMESPACE)
    
    # Formation year
    foundation['formation_year'] = get_text_from_paths(root, [
        './/irs:FormationYr',
        './/irs:IRS990/irs:FormationYr',
        './/irs:IRS990EZ/irs:FormationYr'
    ], IRS_NAMESPACE)
    
    # Contact Information
    # Try multiple locations for address (Filer, BooksInCareOf, USAddress)
    foundation['foundation_address_line1'] = get_text_from_paths(root, [
        './/irs:Filer/irs:USAddress/irs:AddressLine1Txt',
        './/irs:BooksInCareOfDetail/irs:USAddress/irs:AddressLine1Txt',
        './/irs:IRS990/irs:USAddress/irs:AddressLine1Txt',
        './/irs:IRS990EZ/irs:USAddress/irs:AddressLine1Txt'
    ], IRS_NAMESPACE)
    
    foundation['foundation_address_line2'] = get_text_from_paths(root, [
        './/irs:Filer/irs:USAddress/irs:AddressLine2Txt',
        './/irs:BooksInCareOfDetail/irs:USAddress/irs:AddressLine2Txt',
        './/irs:IRS990/irs:USAddress/irs:AddressLine2Txt'
    ], IRS_NAMESPACE)
    
    foundation['foundation_city'] = get_text_from_paths(root, [
        './/irs:Filer/irs:USAddress/irs:CityNm',
        './/irs:BooksInCareOfDetail/irs:USAddress/irs:CityNm',
        './/irs:IRS990/irs:USAddress/irs:CityNm',
        './/irs:IRS990EZ/irs:USAddress/irs:CityNm'
    ], IRS_NAMESPACE)
    
    foundation['foundation_state'] = get_text_from_paths(root, [
        './/irs:Filer/irs:USAddress/irs:StateAbbreviationCd',
        './/irs:BooksInCareOfDetail/irs:USAddress/irs:StateAbbreviationCd',
        './/irs:IRS990/irs:USAddress/irs:StateAbbreviationCd',
        './/irs:IRS990EZ/irs:USAddress/irs:StateAbbreviationCd'
    ], IRS_NAMESPACE)
    
    foundation['foundation_zip'] = get_text_from_paths(root, [
        './/irs:Filer/irs:USAddress/irs:ZIPCd',
        './/irs:BooksInCareOfDetail/irs:USAddress/irs:ZIPCd',
        './/irs:IRS990/irs:USAddress/irs:ZIPCd',
        './/irs:IRS990EZ/irs:USAddress/irs:ZIPCd'
    ], IRS_NAMESPACE)
    
    foundation['foundation_phone'] = get_text_from_paths(root, [
        './/irs:BooksInCareOfDetail/irs:PhoneNum',
        './/irs:PreparerPersonGrp/irs:PhoneNum',
        './/irs:IRS990/irs:BooksInCareOfDetail/irs:PhoneNum',
        './/irs:IRS990EZ/irs:BooksInCareOfDetail/irs:PhoneNum'
    ], IRS_NAMESPACE)
    
    foundation['foundation_website'] = get_text_from_paths(root, [
        './/irs:IRS990/irs:WebsiteAddressTxt',
        './/irs:IRS990EZ/irs:WebsiteAddressTxt',
        './/irs:IRS990PF/irs:WebsiteAddressTxt'
    ], IRS_NAMESPACE)
    
    # Legal domicile
    foundation['legal_domicile_state'] = get_text_from_paths(root, [
        './/irs:IRS990/irs:LegalDomicileStateCd',
        './/irs:IRS990EZ/irs:LegalDomicileStateCd'
    ], IRS_NAMESPACE)
    
    # Financial Data
    foundation['total_assets_boy'] = get_text_from_paths(root, [
        './/irs:TotalAssetsBOYAmt',
        './/irs:IRS990/irs:NetAssetsOrFundBalancesBOYAmt',
        './/irs:IRS990EZ/irs:NetAssetsOrFundBalancesBOYAmt'
    ], IRS_NAMESPACE)
    
    foundation['total_assets_eoy'] = get_text_from_paths(root, [
        './/irs:TotalAssetsEOYAmt',
        './/irs:IRS990/irs:NetAssetsOrFundBalancesEOYAmt',
        './/irs:IRS990EZ/irs:NetAssetsOrFundBalancesEOYAmt',
        './/irs:Form990TotalAssetsGrp/irs:EOYAmt'
    ], IRS_NAMESPACE)
    
    foundation['total_liabilities_eoy'] = get_text_from_paths(root, [
        './/irs:TotalLiabilitiesEOYAmt',
        './/irs:IRS990/irs:TotalLiabilitiesEOYAmt',
        './/irs:IRS990EZ/irs:TotalLiabilitiesEOYAmt'
    ], IRS_NAMESPACE)
    
    foundation['net_assets_eoy'] = get_text_from_paths(root, [
        './/irs:NetAssetsOrFundBalancesEOYAmt',
        './/irs:IRS990/irs:NetAssetsOrFundBalancesEOYAmt',
        './/irs:IRS990EZ/irs:NetAssetsOrFundBalancesEOYAmt'
    ], IRS_NAMESPACE)
    
    foundation['fair_market_value_eoy'] = get_text_from_paths(root, [
        './/irs:FMVAssetsEOYAmt',
        './/irs:IRS990PF/irs:FMVAssetsEOYAmt'
    ], IRS_NAMESPACE)
    
    foundation['total_revenue'] = get_text_from_paths(root, [
        './/irs:CYTotalRevenueAmt',
        './/irs:TotalRevenueAmt',
        './/irs:IRS990/irs:CYTotalRevenueAmt',
        './/irs:IRS990EZ/irs:TotalRevenueAmt'
    ], IRS_NAMESPACE)
    
    foundation['total_expenses'] = get_text_from_paths(root, [
        './/irs:CYTotalExpensesAmt',
        './/irs:TotalExpensesAmt',
        './/irs:IRS990/irs:CYTotalExpensesAmt',
        './/irs:IRS990EZ/irs:TotalExpensesAmt'
    ], IRS_NAMESPACE)
    
    # Investment Income (990PF specific)
    foundation['investment_income'] = get_text_from_paths(root, [
        './/irs:GrossInvestmentIncome509Amt',
        './/irs:DividendsAndInterestFromSecAmt',
        './/irs:IRS990/irs:CYInvestmentIncomeAmt',
        './/irs:IRS990EZ/irs:InvestmentIncomeAmt'
    ], IRS_NAMESPACE)
    
    # Distribution Info (990PF specific)
    foundation['distributable_amount'] = get_text_from_paths(root, [
        './/irs:DistributableAmountAmt',
        './/irs:IRS990PF/irs:DistributableAmountAmt'
    ], IRS_NAMESPACE)
    
    foundation['total_distributions'] = get_text_from_paths(root, [
        './/irs:TotalDistributionAmt',
        './/irs:QualifyingDistributionsAmt',
        './/irs:IRS990PF/irs:TotalDistributionAmt'
    ], IRS_NAMESPACE)
    
    foundation['undistributed_income'] = get_text_from_paths(root, [
        './/irs:UndistributedIncomeAmt',
        './/irs:IRS990PF/irs:UndistributedIncomeAmt'
    ], IRS_NAMESPACE)
    
    # Foundation Type
    foundation['is_private_operating_foundation'] = get_text_from_paths(root, [
        './/irs:PrivateOperatingFoundationInd',
        './/irs:IRS990PF/irs:PrivateOperatingFoundationInd'
    ], IRS_NAMESPACE)
    
    foundation['is_501c3'] = get_text_from_paths(root, [
        './/irs:Organization501c3Ind',
        './/irs:IRS990/irs:Organization501c3Ind',
        './/irs:IRS990EZ/irs:Organization501c3Ind'
    ], IRS_NAMESPACE)
    
    # Mission/Purpose
    foundation['mission_description'] = get_text_from_paths(root, [
        './/irs:PrimaryExemptPurposeTxt',
        './/irs:MissionDesc',
        './/irs:ActivityOrMissionDesc',
        './/irs:IRS990/irs:MissionDesc',
        './/irs:IRS990EZ/irs:PrimaryExemptPurposeTxt'
    ], IRS_NAMESPACE)
    
    # Limit mission to 500 chars
    if len(foundation['mission_description']) > 500:
        foundation['mission_description'] = foundation['mission_description'][:497] + '...'
    
    return foundation


def extract_grants_from_xml(xml_path: Path) -> tuple[Dict[str, str], List[Dict[str, str]]]:
    """Extract foundation info and all grant information from a single XML file."""
    root = parse_xml_file(xml_path)
    if root is None:
        return {}, []
    
    # Get foundation information
    foundation_info = extract_foundation_info(root, xml_path.name)
    
    # Find all grant entries (try multiple possible paths)
    grants = []
    
    # Try 990PF grant format
    grant_elements = root.findall('.//irs:GrantOrContributionPdDurYrGrp', IRS_NAMESPACE)
    
    # Also try RecipientTable format (Schedule I)
    if not grant_elements:
        grant_elements = root.findall('.//irs:RecipientTable', IRS_NAMESPACE)
    
    for grant_elem in grant_elements:
        grant = {
            'source_file': xml_path.name,
            'filer_ein': foundation_info['filer_ein'],
            'filer_organization_name': foundation_info['filer_organization_name'],
            'tax_period_end': foundation_info['tax_period_end']
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
        
        # Try USAddress without "Recipient" prefix (for RecipientTable format)
        if not grant['recipient_city']:
            grant['recipient_city'] = get_text(grant_elem, 'irs:USAddress/irs:CityNm', IRS_NAMESPACE)
            grant['recipient_state'] = get_text(grant_elem, 'irs:USAddress/irs:StateAbbreviationCd', IRS_NAMESPACE)
            grant['recipient_zip'] = get_text(grant_elem, 'irs:USAddress/irs:ZIPCd', IRS_NAMESPACE)
            grant['recipient_address_line1'] = get_text(grant_elem, 'irs:USAddress/irs:AddressLine1Txt', IRS_NAMESPACE)
        
        # If no US address, try foreign address
        if not grant['recipient_city']:
            grant['recipient_city'] = get_text(grant_elem, 'irs:RecipientForeignAddress/irs:CityNm', IRS_NAMESPACE)
            grant['recipient_state'] = get_text(grant_elem, 'irs:RecipientForeignAddress/irs:ProvinceOrStateNm', IRS_NAMESPACE)
            grant['recipient_country'] = get_text(grant_elem, 'irs:RecipientForeignAddress/irs:CountryCd', IRS_NAMESPACE)
        else:
            grant['recipient_country'] = 'US'
        
        # NEW: Recipient EIN
        grant['recipient_ein'] = get_text_from_paths(grant_elem, [
            'irs:RecipientEIN',
            'irs:EINOfRecipient',
            'irs:RecipientUSAddress/irs:EIN'
        ], IRS_NAMESPACE)
        
        # Existing fields
        grant['recipient_relationship'] = get_text(grant_elem, 'irs:RecipientRelationshipTxt', IRS_NAMESPACE)
        grant['recipient_foundation_status'] = get_text(grant_elem, 'irs:RecipientFoundationStatusTxt', IRS_NAMESPACE)
        
        # NEW: IRS Section/Classification
        grant['recipient_irc_section'] = get_text(grant_elem, 'irs:IRCSectionDesc', IRS_NAMESPACE)
        
        # Grant purpose
        grant['grant_purpose'] = get_text_from_paths(grant_elem, [
            'irs:GrantOrContributionPurposeTxt',
            'irs:PurposeOfGrantTxt'
        ], IRS_NAMESPACE)
        
        # Limit purpose to 500 chars
        if len(grant['grant_purpose']) > 500:
            grant['grant_purpose'] = grant['grant_purpose'][:497] + '...'
        
        # Extract grant amounts
        # Try cash amount first, then general amount
        cash_amount = get_text_from_paths(grant_elem, [
            'irs:CashGrantAmt',
            'irs:Amt'
        ], IRS_NAMESPACE)
        
        non_cash_amount = get_text(grant_elem, 'irs:NonCashAssistanceAmt', IRS_NAMESPACE)
        non_cash_desc = get_text(grant_elem, 'irs:NonCashAssistanceDesc', IRS_NAMESPACE)
        
        # NEW: Cash vs non-cash split
        grant['cash_grant_amount'] = cash_amount if cash_amount else "0"
        grant['non_cash_grant_amount'] = non_cash_amount if non_cash_amount else "0"
        grant['non_cash_description'] = non_cash_desc
        
        # Total grant amount (cash + non-cash)
        total = 0
        if cash_amount:
            try:
                total += float(cash_amount)
            except ValueError:
                pass
        if non_cash_amount:
            try:
                total += float(non_cash_amount)
            except ValueError:
                pass
        
        grant['grant_amount'] = str(int(total)) if total > 0 else cash_amount if cash_amount else "0"
        
        # NEW: Valuation method (for non-cash grants)
        grant['valuation_method'] = get_text(grant_elem, 'irs:ValuationMethodUsedDesc', IRS_NAMESPACE)
        
        # Only add if we have at least a recipient name or amount
        if grant['recipient_name'] or grant['grant_amount'] != "0":
            grants.append(grant)
    
    return foundation_info, grants


def process_all_files(csv_file: Path, xml_dir: Path, output_grants_file: Path, output_foundations_file: Path):
    """Process all XML files and extract grant and foundation information."""
    
    logger.info(f"Reading foundation list from {csv_file}")
    
    all_grants = []
    all_foundations = {}  # Use dict to avoid duplicates by EIN
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
            
            # Extract foundation info and grants from this file
            foundation_info, grants = extract_grants_from_xml(xml_path)
            
            # Store foundation info (using EIN+file as key to handle multiple years)
            if foundation_info.get('filer_ein'):
                key = f"{foundation_info['filer_ein']}_{foundation_info['source_file']}"
                all_foundations[key] = foundation_info
            
            if grants:
                files_with_grants += 1
                all_grants.extend(grants)
                logger.info(f"Processed {xml_filename}: Found {len(grants)} grants")
            elif foundation_info.get('filer_ein'):
                logger.info(f"Processed {xml_filename}: Foundation data only (no grants)")
            
            # Log progress every 100 files
            if total_files % 100 == 0:
                logger.info(f"Progress: {total_files} files processed, {len(all_grants)} grants found")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing complete!")
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Files with grants: {files_with_grants}")
    logger.info(f"Total grants found: {len(all_grants)}")
    logger.info(f"Total foundations: {len(all_foundations)}")
    logger.info(f"Errors: {errors}")
    logger.info(f"{'='*60}\n")
    
    # Write grants to CSV
    if all_grants:
        logger.info(f"Writing grants to {output_grants_file}")
        
        grant_fieldnames = [
            'source_file', 'filer_ein', 'filer_organization_name', 'tax_period_end',
            'recipient_name', 'recipient_ein', 'recipient_address_line1', 'recipient_address_line2',
            'recipient_city', 'recipient_state', 'recipient_zip', 'recipient_country',
            'recipient_relationship', 'recipient_foundation_status', 'recipient_irc_section',
            'grant_purpose', 'grant_amount', 'cash_grant_amount', 'non_cash_grant_amount',
            'non_cash_description', 'valuation_method'
        ]
        
        with open(output_grants_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=grant_fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_grants)
        
        logger.info(f"Successfully wrote {len(all_grants)} grants to {output_grants_file}")
    
    # Write foundations to CSV
    if all_foundations:
        logger.info(f"Writing foundations to {output_foundations_file}")
        
        foundation_fieldnames = [
            'source_file', 'filer_ein', 'filer_organization_name', 
            'tax_period_begin', 'tax_period_end', 'formation_year',
            'foundation_address_line1', 'foundation_address_line2', 
            'foundation_city', 'foundation_state', 'foundation_zip',
            'foundation_phone', 'foundation_website', 'legal_domicile_state',
            'total_assets_boy', 'total_assets_eoy', 'total_liabilities_eoy', 
            'net_assets_eoy', 'fair_market_value_eoy',
            'total_revenue', 'total_expenses', 'investment_income',
            'distributable_amount', 'total_distributions', 'undistributed_income',
            'is_private_operating_foundation', 'is_501c3', 'mission_description'
        ]
        
        with open(output_foundations_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=foundation_fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_foundations.values())
        
        logger.info(f"Successfully wrote {len(all_foundations)} foundations to {output_foundations_file}")
    
    # Generate summary statistics
    if all_grants:
        generate_summary_stats(all_grants, all_foundations)


def generate_summary_stats(grants: List[Dict[str, str]], foundations: Dict[str, Dict[str, str]]):
    """Generate and log summary statistics."""
    
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY STATISTICS")
    logger.info(f"{'='*60}")
    
    # Grant statistics
    total_amount = sum(float(g['grant_amount']) for g in grants if g['grant_amount'])
    logger.info(f"Total grant amount: ${total_amount:,.2f}")
    
    avg_amount = total_amount / len(grants) if grants else 0
    logger.info(f"Average grant amount: ${avg_amount:,.2f}")
    
    unique_filers = len(set(g['filer_ein'] for g in grants if g['filer_ein']))
    logger.info(f"Unique grantors (foundations): {unique_filers}")
    
    unique_recipients = len(set(g['recipient_name'] for g in grants if g['recipient_name']))
    logger.info(f"Unique recipients: {unique_recipients}")
    
    # Foundation statistics
    foundations_with_website = sum(1 for f in foundations.values() if f.get('foundation_website'))
    logger.info(f"\nFoundations with website: {foundations_with_website}/{len(foundations)}")
    
    foundations_with_phone = sum(1 for f in foundations.values() if f.get('foundation_phone'))
    logger.info(f"Foundations with phone: {foundations_with_phone}/{len(foundations)}")
    
    foundations_with_assets = sum(1 for f in foundations.values() if f.get('total_assets_eoy'))
    logger.info(f"Foundations with asset data: {foundations_with_assets}/{len(foundations)}")
    
    # Grant enhancements
    grants_with_ein = sum(1 for g in grants if g.get('recipient_ein'))
    logger.info(f"\nGrants with recipient EIN: {grants_with_ein}/{len(grants)}")
    
    grants_with_relationship = sum(1 for g in grants if g.get('recipient_relationship'))
    logger.info(f"Grants with relationship data: {grants_with_relationship}/{len(grants)}")
    
    non_cash_grants = sum(1 for g in grants if g.get('non_cash_grant_amount') and float(g['non_cash_grant_amount']) > 0)
    logger.info(f"Non-cash grants: {non_cash_grants}/{len(grants)}")
    
    logger.info(f"{'='*60}\n")


def main():
    """Main execution function."""
    script_dir = Path(__file__).parent
    csv_file = script_dir / "pf_forms_extracted.csv"
    xml_dir = script_dir / "irs_data"
    output_grants_file = script_dir / "grants_information_summary.csv"
    output_foundations_file = script_dir / "foundations_information_summary.csv"
    
    # Verify input files exist
    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_file}")
        return
    
    if not xml_dir.exists():
        logger.error(f"XML directory not found: {xml_dir}")
        return
    
    logger.info("Starting ENHANCED grant and foundation information extraction...")
    logger.info(f"Source CSV: {csv_file}")
    logger.info(f"XML directory: {xml_dir}")
    logger.info(f"Output grants file: {output_grants_file}")
    logger.info(f"Output foundations file: {output_foundations_file}")
    logger.info("")
    
    # Process all files
    process_all_files(csv_file, xml_dir, output_grants_file, output_foundations_file)
    
    logger.info("Done!")


if __name__ == "__main__":
    main()

