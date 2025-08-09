#!/usr/bin/env python3
import csv
import json
import sys
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

API_BASE = "https://dataportal.arc.gov.au/NCGP/API/grants"

@dataclass
class Investigator:
    title: Optional[str]
    first_name: Optional[str]
    family_name: Optional[str]
    role_name: Optional[str]
    role_code: Optional[str]
    is_fellowship: Optional[bool]
    orcid: Optional[str]

    @property
    def full_name(self) -> str:
        parts = [p for p in [self.title, self.first_name, self.family_name] if p]
        return " ".join(parts)

@dataclass
class GrantRecord:
    code: str
    scheme_name: str
    funding_commencement_year: Optional[int]
    grant_status: Optional[str]
    funding_at_announcement: Optional[float]
    funding_current: Optional[float]
    administering_organisation: Optional[str]
    administering_organisation_announcement: Optional[str]
    summary: Optional[str]
    field_of_research: Any
    socio_economic_objective: Any
    national_interest_test_statement: Optional[str]
    investigators_current: List[Investigator]
    investigators_announcement: List[Investigator]

    def chief_investigators(self) -> List[Investigator]:
        source = self.investigators_current or self.investigators_announcement or []
        return [inv for inv in source if (inv.role_code or "").upper() == "CI" or (inv.role_name or "").lower() == "chief investigator"]


def make_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "arc-dp-crawler/1.0"})
    return session


def fetch_page(session: requests.Session, page_number: int, page_size: int = 1000) -> Dict[str, Any]:
    params = {"page[number]": page_number, "page[size]": page_size}
    resp = session.get(API_BASE, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_detail(session: requests.Session, grant_id: str) -> Dict[str, Any]:
    url = f"{API_BASE}/{grant_id}"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_investigators(raw_list: Any) -> List[Investigator]:
    if not isinstance(raw_list, list):
        return []
    out: List[Investigator] = []
    for item in raw_list:
        out.append(
            Investigator(
                title=item.get("title"),
                first_name=item.get("firstName"),
                family_name=item.get("familyName"),
                role_name=item.get("roleName"),
                role_code=item.get("roleCode"),
                is_fellowship=item.get("isFellowship"),
                orcid=(item.get("orcidIdentifier") or None),
            )
        )
    return out


def parse_grant(attributes: Dict[str, Any]) -> GrantRecord:
    return GrantRecord(
        code=attributes.get("code"),
        scheme_name=attributes.get("scheme-name"),
        funding_commencement_year=attributes.get("funding-commencement-year"),
        grant_status=attributes.get("grant-status"),
        funding_at_announcement=attributes.get("funding-at-announcement"),
        funding_current=attributes.get("funding-current"),
        administering_organisation=attributes.get("administering-organisation") or attributes.get("current-admin-organisation"),
        administering_organisation_announcement=attributes.get("announcement-administering-organisation") or attributes.get("announcement-admin-organisation"),
        summary=attributes.get("grant-summary"),
        field_of_research=attributes.get("field-of-research") or attributes.get("primary-field-of-research"),
        socio_economic_objective=attributes.get("socio-economic-objective"),
        national_interest_test_statement=attributes.get("national-interest-test-statement"),
        investigators_current=parse_investigators(attributes.get("investigators-current")),
        investigators_announcement=parse_investigators(attributes.get("investigators-at-announcement")),
    )


def is_discovery_project(attributes: Dict[str, Any]) -> bool:
    return (attributes.get("scheme-name") or "").strip().lower() == "discovery projects"


def is_funded(attributes: Dict[str, Any]) -> bool:
    # Consider funded if any funding amount is present and > 0
    funding_keys = (
        # detail endpoint keys
        "funding-at-announcement",
        "funding-current",
        # list endpoint keys
        "announced-funding-amount",
        "current-funding-amount",
    )
    for key in funding_keys:
        try:
            val = attributes.get(key)
            if isinstance(val, (int, float)) and float(val) > 0:
                return True
        except Exception:
            continue
    return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Crawl ARC Discovery Projects and extract Chief Investigators")
    parser.add_argument("--out-csv", default="/Users/a1227750/arc_discovery_projects.csv", help="Output CSV path")
    parser.add_argument("--out-json", default="/Users/a1227750/arc_discovery_projects.json", help="Output JSON path")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit number of pages to scan (for testing)")
    parser.add_argument("--page-size", type=int, default=1000, help="Page size for list endpoint")
    parser.add_argument("--sleep", type=float, default=0.1, help="Sleep seconds between detail requests to be polite")
    parser.add_argument("--year-from", type=int, default=None, help="Only include grants with funding-commencement-year >= this year")
    parser.add_argument("--year-to", type=int, default=None, help="Only include grants with funding-commencement-year <= this year")

    args = parser.parse_args()

    session = make_session()

    print("Discovering Discovery Projects IDs...", file=sys.stderr)
    page = 1
    total_pages_seen = None
    dp_ids: List[str] = []

    while True:
        if args.max_pages and page > args.max_pages:
            break
        data = fetch_page(session, page, args.page_size)
        meta = data.get("meta", {})
        if total_pages_seen is None:
            total_pages_seen = meta.get("total-pages")
        items = data.get("data", [])
        if not items:
            break
        for item in items:
            attributes = item.get("attributes", {})
            if not is_discovery_project(attributes):
                continue
            if args.year_from and (attributes.get("funding-commencement-year") or 0) < args.year_from:
                continue
            if args.year_to and (attributes.get("funding-commencement-year") or 0) > args.year_to:
                continue
            if not is_funded(attributes):
                # Detail endpoint has same amounts; skip unfunded
                continue
            dp_ids.append(item.get("id"))
        page += 1
        if total_pages_seen and page > total_pages_seen:
            break

    print(f"Found {len(dp_ids)} Discovery Projects (funded) to fetch details", file=sys.stderr)

    results: List[GrantRecord] = []
    for idx, gid in enumerate(dp_ids, start=1):
        try:
            detail = fetch_detail(session, gid)
            attributes = (detail.get("data") or {}).get("attributes") or {}
            grant = parse_grant(attributes)
            results.append(grant)
            if args.sleep:
                time.sleep(args.sleep)
            if idx % 50 == 0:
                print(f"Fetched {idx}/{len(dp_ids)}", file=sys.stderr)
        except Exception as e:
            print(f"Error fetching {gid}: {e}", file=sys.stderr)
            continue

    # Write JSON
    json_serializable = [
        {
            **{k: v for k, v in asdict(rec).items() if not k.startswith("investigators_")},
            "investigators_current": [asdict(inv) for inv in rec.investigators_current],
            "investigators_at_announcement": [asdict(inv) for inv in rec.investigators_announcement],
            "chief_investigators": [asdict(inv) for inv in rec.chief_investigators()],
        }
        for rec in results
    ]
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(json_serializable, f, ensure_ascii=False, indent=2)
    
    # Write CSV
    fieldnames = [
        "code",
        "funding_commencement_year",
        "grant_status",
        "funding_at_announcement",
        "funding_current",
        "administering_organisation",
        # Field of Research columns
        "for_primary_codes",
        "for_primary_names",
        "for_all_codes",
        "for_all_names",
        # Chief Investigators
        "chief_investigators",
        "chief_investigators_orcids",
    ]
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in results:
            # Flatten Field of Research
            for_list = rec.field_of_research
            primary_codes: List[str] = []
            primary_names: List[str] = []
            all_codes: List[str] = []
            all_names: List[str] = []
            if isinstance(for_list, list):
                for item in for_list:
                    code = item.get("code")
                    name = item.get("name")
                    if code:
                        all_codes.append(str(code))
                    if name:
                        all_names.append(str(name))
                    if item.get("isPrimary"):
                        if code:
                            primary_codes.append(str(code))
                        if name:
                            primary_names.append(str(name))
            elif isinstance(for_list, str):
                # Older schema may provide a single string
                all_names = [for_list]
                primary_names = [for_list]
            
            cis = rec.chief_investigators()
            ci_names = "; ".join([ci.full_name for ci in cis])
            ci_orcids = "; ".join([ci.orcid.strip() for ci in cis if ci.orcid])
            writer.writerow({
                "code": rec.code,
                "funding_commencement_year": rec.funding_commencement_year,
                "grant_status": rec.grant_status,
                "funding_at_announcement": rec.funding_at_announcement,
                "funding_current": rec.funding_current,
                "administering_organisation": rec.administering_organisation,
                "for_primary_codes": "; ".join(primary_codes),
                "for_primary_names": "; ".join(primary_names),
                "for_all_codes": "; ".join(all_codes),
                "for_all_names": "; ".join(all_names),
                "chief_investigators": ci_names,
                "chief_investigators_orcids": ci_orcids,
            })

    print(f"Wrote {len(results)} records to {args.out_csv} and {args.out_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
