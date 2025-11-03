import os, re, csv
from bs4 import BeautifulSoup

INPUT_DIR = "/Users/sebboyer/Documents/Zeffy/grant_finder/irs_data"   # change this
OUTPUT_CSV = "/Users/sebboyer/Documents/Zeffy/grant_finder/pf_forms_extracted.csv"

def txt(node):
    return node.text.strip() if node and node.text else None

def detect_return_type(soup):
    rt = soup.find("ReturnTypeCd")
    if rt and txt(rt):
        return txt(rt)
    # PF schema markers (for older/variant schemas)
    if soup.find(re.compile(r"(IRS)?990PF")) or soup.find(re.compile(r"Form990PF")) or soup.find(re.compile(r"Form990PFPart")):
        return "990PF"
    any_rt = soup.find(lambda t: t.name and t.name.lower().endswith("returntypecd"))
    return txt(any_rt)

def is_pf_return(soup):
    rt = detect_return_type(soup)
    if rt and "990PF" in rt.upper():
        return True
    # Fallback: PF parts present
    if soup.find(re.compile(r"(IRS)?990PF")) or soup.find(re.compile(r"Form990PF")) or soup.find(re.compile(r"Form990PFPart")):
        return True
    return False

def extract_org_fields(soup):
    ein = txt(soup.find("EIN")) or txt(soup.find(lambda t: t.name and t.name.lower().endswith("ein")))
    # Prefer the standard header location
    header_name = soup.find("BusinessNameLine1Txt")
    if header_name:
        name = txt(header_name)
    else:
        # Try alternate business name tags that pop up across years
        bn = soup.find(re.compile(r"BusinessName$|BusinessNameLine1|BusinessName1"))
        name = txt(bn)
    tax_period_end = txt(soup.find("TaxPeriodEndDt")) or txt(soup.find(lambda t: t.name and t.name.lower().endswith("taxperiodenddt")))
    return_type = detect_return_type(soup) or ""
    return name, ein, tax_period_end, return_type

def extract_pf_names_from_folder(input_dir, out_csv):
    candidates = []
    for f in os.listdir(input_dir):
        if f.lower().endswith(".xml") or f.lower().endswith("_public.xml"):
            candidates.append(os.path.join(input_dir, f))
    candidates.sort()

    rows = []
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                soup = BeautifulSoup(fh.read(), "xml")
            if is_pf_return(soup):
                name, ein, tpe, rtype = extract_org_fields(soup)
                rows.append({
                    "file": os.path.basename(path),
                    "ein": ein or "",
                    "organization_name": name or "",
                    "tax_period_end": tpe or "",
                    "return_type": rtype or "990PF"
                })
        except Exception as e:
            rows.append({
                "file": os.path.basename(path),
                "ein": "",
                "organization_name": "",
                "tax_period_end": "",
                "return_type": f"ERROR: {e}"
            })

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file","ein","organization_name","tax_period_end","return_type"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} PF rows from {len(candidates)} XML files to {out_csv}")

if __name__ == "__main__":
    extract_pf_names_from_folder(INPUT_DIR, OUTPUT_CSV)