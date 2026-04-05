"""Quick script to see the raw output from the Apify actor — saves to file."""
import sys, os, json
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv(".env")

from apify_client import ApifyClient

token = os.getenv("APIFY_API_TOKEN")
client = ApifyClient(token)

print("Running actor...")
run = client.actor("shahidirfan/jobstreet-scraper").call(run_input={
    "keyword": "web developer",
    "country": "ph",
    "results_wanted": 2,
    "posted_date": "anytime"
})

print(f"Status: {run['status']}")
dataset_id = run["defaultDatasetId"]
items = list(client.dataset(dataset_id).iterate_items())
print(f"Got {len(items)} items.")

if items:
    keys = list(items[0].keys())
    print(f"\nKeys in first item ({len(keys)} total):")
    for k in keys:
        v = items[0][k]
        print(f"  {k!r:30s}: {repr(v)[:100]}")
    
    # Save full item to JSON
    with open("scraper/debug_sample.json", "w") as f:
        json.dump(items[0], f, indent=2, default=str)
    print("\nFull first item saved to: scraper/debug_sample.json")
