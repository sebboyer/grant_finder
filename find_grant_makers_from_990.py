import os, re, csv
from bs4 import BeautifulSoup

INPUT_DIR = "/Users/sebboyer/Documents/Zeffy/grant_finder/irs_data"
OUTPUT_CSV = "/Users/sebboyer/Documents/Zeffy/grant_finder/grant_givers_extracted.csv"

def get_text(node):
    return node.text.strip() if node and node.text else None

def extract_org_metadata(soup):
    ein_tag = soup.find("EIN") or soup.find(lambda t: t.name and t.name.lower().endswith("ein"))
    name_tag = soup.find("BusinessNameLine1Txt") or soup.find(lambda t: t.name and ("Name" in t.name and "Business" in t.name))
    period_tag = soup.find("TaxPeriodEndDt") or soup.find(lambda t: t.name and t.name.lower().endswith("taxperiodenddt"))
    return (
        get_text(name_tag),
        get_text(ein_tag),
        get_text(period_tag),
    )

def extract_contributors_schedule_b(soup):
    rows = []
    for grp in soup.find_all(re.compile(r"ContributorInformationGrp$")):
        bn = grp.find(re.compile(r"Contributor(Name)?Business"))
        business_name = get_text(bn.find(re.compile(r"BusinessNameLine1Txt$"))) if bn else None
        person_name = get_text(grp.find(re.compile(r"ContributorPersonNm$")))
        donor_name = business_name or person_name

        cash_amt = grp.find(re.compile(r"ContributorCashAmt$"))
        noncash_amt = grp.find(re.compile(r"ContributorNonCashAmt$"))
        total_amt = grp.find(re.compile(r"Contributor(Total)?(Amt|Amount)$"))
        amt = get_text(total_amt) or get_text(cash_amt) or get_text(noncash_amt)

        if donor_name:
            rows.append({"donor_name": donor_name, "amount": amt})
    return rows

def extract_contributors_generic(soup):
    rows = []
    name_like_tags = soup.find_all(lambda t: t.name and (
        ("Contributor" in t.name and ("Name" in t.name or "PersonNm" in t.name or "BusinessName" in t.name)) or
        ("Donor" in t.name and "Name" in t.name)
    ))
    for tag in name_like_tags:
        inner_line1 = tag.find(re.compile(r"BusinessNameLine1Txt$"))
        donor_name = get_text(inner_line1) or get_text(tag)
        if not donor_name:
            continue
        amt_node = None
        for cand in tag.find_all_next(limit=6):
            if cand.name and re.search(r"(Contributor|Donor).*(Amt|Amount)$", cand.name):
                amt_node = cand; break
            if cand.name and re.search(r"(CashAmt|NonCashAmt|Amount|Amt)$", cand.name):
                amt_node = cand; break
        rows.append({"donor_name": donor_name, "amount": get_text(amt_node)})
    return rows

def extract_grant_givers_from_file(xml_path):
    with open(xml_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "xml")
    org_name, ein, period_end = extract_org_metadata(soup)
    donors = extract_contributors_schedule_b(soup)
    if not donors:
        donors = extract_contributors_generic(soup)
    seen, unique = set(), []
    for d in donors:
        key = (d.get("donor_name"), d.get("amount"))
        if d.get("donor_name") and key not in seen:
            unique.append(d); seen.add(key)
    return {"organization_name": org_name, "ein": ein, "tax_period_end": period_end, "donors": unique}

def batch_extract(input_dir, out_csv):
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith("_public.xml")]
    files.sort()
    rows = []
    for path in files:
        info = extract_grant_givers_from_file(path)
        base = os.path.basename(path)
        if info["donors"]:
            for d in info["donors"]:
                rows.append({
                    "file": base,
                    "ein": info["ein"] or "",
                    "organization_name": info["organization_name"] or "",
                    "tax_period_end": info["tax_period_end"] or "",
                    "grant_giver_name": d.get("donor_name") or "",
                    "amount_reported": d.get("amount") or "",
                })
        else:
            rows.append({
                "file": base,
                "ein": info["ein"] or "",
                "organization_name": info["organization_name"] or "",
                "tax_period_end": info["tax_period_end"] or "",
                "grant_giver_name": "",
                "amount_reported": "",
            })
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "file","ein","organization_name","tax_period_end","grant_giver_name","amount_reported"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows from {len(files)} files to {out_csv}")

if __name__ == "__main__":
    batch_extract(INPUT_DIR, OUTPUT_CSV)