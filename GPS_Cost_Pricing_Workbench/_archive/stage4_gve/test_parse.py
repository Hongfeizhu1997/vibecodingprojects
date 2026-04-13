import sys, json
sys.path.insert(0, ".")
from engine.excel_parser import parse_excel

result = parse_excel("EMEA ThinkNB Costing and pricing ZS 20250702.xlsx")
print("Errors:", result["errors"])
print("Tiers found:", result["tiers_found"])
print("Regions found:", result["regions"])
print("Row count:", len(result["rows"]))
if result["rows"]:
    r = result["rows"][0]
    print("\nSample row:")
    print("  Part#:", r["part_number"])
    print("  Tier:", r["tier"])
    print("  Base:", r["base_warranty"])
    print("  Upgrade:", r["upgrade_description"])
    print("  Delivery:", r["delivery_type"])
    print("  Years:", r["upgrade_years"])
    print("  Regions with prices:", list(r["prices"].keys())[:5])
    first_region = list(r["prices"].keys())[0] if r["prices"] else None
    if first_region:
        print("  Sample prices:", r["prices"][first_region])
