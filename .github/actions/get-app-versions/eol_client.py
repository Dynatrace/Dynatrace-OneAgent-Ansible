#!/usr/bin/env python3
import argparse
import requests
import sys
import json
import re


class ParseException(Exception):
    pass


class Date:
    def __init__(self, date: str):
        pattern = r"(\d{4})-(\d{2})-(\d{2})"
        match = re.search(pattern, date)
        if match:
            year, month, day = match.groups()
            self.year = int(year)
            self.month = int(month)
            self.day = int(day)
        else:
            raise ParseException("Date is not properly formatted")

    def __gt__(self, other):
        if self.year < other.year:
            return False
        if self.year == other.year and self.month < other.month:
            return False
        if self.month == other.month and self.day <= other.day:
            return False
        return True


def is_supported(val: dict) -> bool:
    return not val.get("isEol", True)


def print_formatted(val):
    print(json.dumps(val))


def get_versions(app: str) -> dict:
    api_url = f"https://endoflife.date/api/v1/products/{app}"
    response = requests.get(api_url)
    value = None
    if response.status_code == requests.codes.ok:
        value = response.json()
    else:
        print(f"ERROR: {response.status_code}: {response.reason}", file=sys.stderr)
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple end of life api client")
    parser.add_argument("app", help="Application name")
    parser.add_argument("--get_latest", help="Get latest version", action="store_true")
    args = parser.parse_args()
    releases = get_versions(args.app)["result"]["releases"]
    if not releases:
        sys.exit(1)
    supported_versions = [release.get("name") for release in releases if is_supported(release)]
    if args.get_latest:
        latest_release = max(releases, key=lambda v: Date(v.get("releaseDate")))
        print(latest_release.get("name"))
    else:
        print_formatted(supported_versions)
