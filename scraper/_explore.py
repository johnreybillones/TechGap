"""Introspect the JobStreet GraphQL API to find the correct query names."""

import asyncio
import json
import sys
from pathlib import Path
import httpx

FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures"


async def main():
    graphql_url = "https://ph.jobstreet.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://ph.jobstreet.com",
        "Referer": "https://ph.jobstreet.com/",
    }

    # Step 1: Try GraphQL introspection
    print("=" * 55)
    print("STEP 1: GraphQL Introspection")
    print("=" * 55)

    introspection = {
        "query": "{ __schema { queryType { fields { name description args { name type { name kind } } } } } }"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(graphql_url, json=introspection, headers=headers)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            if "errors" in data:
                print(f"Introspection blocked: {data['errors'][0].get('message', '')[:120]}")
            else:
                fields = data.get("data", {}).get("__schema", {}).get("queryType", {}).get("fields", [])
                print(f"Found {len(fields)} query fields:")
                for f in fields:
                    args_str = ", ".join([a["name"] for a in f.get("args", [])])
                    print(f"  {f['name']}({args_str})")

                with open(FIXTURES_DIR / "graphql_schema.json", "w", encoding="utf-8") as fh:
                    json.dump(data, fh, indent=2)
                print("Saved schema to graphql_schema.json")
                return
        else:
            print(f"Response: {resp.text[:300]}")

    # Step 2: Try common SEEK query names
    print("\n" + "=" * 55)
    print("STEP 2: Probing common query names")
    print("=" * 55)

    probe_queries = [
        "jobSearch",
        "search",
        "jobListing",
        "jobs",
        "jobDetails",
        "searchResults",
        "getJobSearch",
        "getJobs",
        "jobSearchV2",
        "jobCardSearch",
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for qname in probe_queries:
            query = {
                "query": f"{{ {qname} {{ __typename }} }}"
            }
            try:
                resp = await client.post(graphql_url, json=query, headers=headers)
                data = resp.json()
                err = data.get("errors", [{}])[0].get("message", "")
                if "Cannot query field" in err:
                    # Expected - field doesn't exist
                    pass
                else:
                    print(f"  ⭐ '{qname}': {err[:120]}")
            except Exception as e:
                print(f"  '{qname}': Error - {e}")


if __name__ == "__main__":
    asyncio.run(main())
