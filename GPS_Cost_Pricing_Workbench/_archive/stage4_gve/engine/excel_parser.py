"""
Parse the GPS Pricing Workbench Excel file.

Expected sheet: "Pricing with sales costs"
  Col 0: ePack Part #
  Col 1: Tier
  Col 2: Base warranty
  Col 3: Upgrade description
  Col 4: Type (Onsite / Depot)
  Col 5+: alternating geo columns — each geo block has:
           row 0 (header row 1): geo label spanning 5 cols
           row 1 (header row 2): subheaders  Cost | C-Price | GP% | ESS profit | L-Price
           Then data rows with the 5 values per geo.

We find geo blocks by scanning the top header rows for non-empty region labels.
"""

import re
from openpyxl import load_workbook


def _clean(val):
    if val is None:
        return None
    if isinstance(val, str):
        return val.strip()
    return val


def _to_float(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.replace("$", "").replace(",", "").strip()
        try:
            return float(val)
        except ValueError:
            return None
    return None


def _extract_upgrade_years(upgrade_desc):
    """Extract target year count from upgrade description string.
    E.g. '3Y Onsite NBD' → 3, '5Y Courier/Carry in' → 5, '1Y Onsite NBD' → 1
    Returns None if not found.
    """
    if not upgrade_desc:
        return None
    m = re.search(r"(\d+)Y", str(upgrade_desc), re.IGNORECASE)
    return int(m.group(1)) if m else None


def _find_pricing_sheet(wb):
    """Return the worksheet that contains pricing data."""
    candidates = [s for s in wb.sheetnames if "pricing" in s.lower()]
    if candidates:
        return wb[candidates[0]]
    # fallback: try first sheet
    return wb.worksheets[0]


def _find_cost_sheet(wb):
    """Return the worksheet that contains standard / upsell costs."""
    for name in wb.sheetnames:
        if "upsell" in name.lower() or "standard cost" in name.lower():
            return wb[name]
    return None


def parse_excel(filepath):
    """
    Parse the pricing Excel file.

    Returns:
        {
            "tiers_found": [...],        # ordered list of unique tiers found
            "regions": [...],            # list of region column names
            "rows": [
                {
                    "part_number": str,
                    "tier": str,
                    "base_warranty": str,
                    "upgrade_description": str,
                    "delivery_type": str,
                    "upgrade_years": int|None,
                    "prices": {
                        "<region>": {
                            "sales_cost": float|None,
                            "channel_price": float|None,
                            "list_price": float|None,
                        }
                    }
                }
            ],
            "errors": [...]
        }
    """
    wb = load_workbook(filepath, data_only=True)
    ws = _find_pricing_sheet(wb)

    errors = []

    # --- Detect header rows ---
    # Scan first 5 rows to find:
    #   row A: geo labels (may span merged cells)
    #   row B: column subheaders (Cost, C-Price, GP%, ESS profit, L-Price)
    # The first 5 columns are fixed: Part#, Tier, Base, Upgrade, Type

    FIXED_COLS = 5  # columns 0-4 are fixed metadata

    # Read up to 6 header rows into a flat list-of-lists
    header_rows = []
    for row in ws.iter_rows(min_row=1, max_row=6, values_only=True):
        header_rows.append(list(row))

    # For merged cells, openpyxl data_only returns None for merged slaves.
    # We need to un-merge by reading the actual merge info.
    # Re-open with data_only=False to get merge ranges, then reopen with data_only=True for values.
    wb_meta = load_workbook(filepath, data_only=False)
    ws_meta = None
    for name in wb_meta.sheetnames:
        if "pricing" in name.lower():
            ws_meta = wb_meta[name]
            break
    if ws_meta is None:
        ws_meta = wb_meta.worksheets[0]

    # Build a filled-in version of the top rows respecting merge spans
    def fill_merged(ws_m, max_row=6, max_col=60):
        """Return a 2D list (row, col) with merged cells filled in."""
        grid = [[None] * max_col for _ in range(max_row)]
        for row in ws_m.iter_rows(min_row=1, max_row=max_row, max_col=max_col, values_only=True):
            pass  # dummy to force load
        for r in range(max_row):
            for c in range(max_col):
                cell = ws_m.cell(row=r + 1, column=c + 1)
                grid[r][c] = _clean(cell.value)
        # Propagate merge spans (skip merges that fall outside our grid window)
        for merge in ws_m.merged_cells.ranges:
            r0 = merge.min_row - 1
            c0 = merge.min_col - 1
            if r0 >= max_row or c0 >= max_col:
                continue
            val = grid[r0][c0]
            for r in range(r0, min(merge.max_row, max_row)):
                for c in range(c0, min(merge.max_col, max_col)):
                    grid[r][c] = val
        return grid

    MAX_COL = 80
    grid = fill_merged(ws_meta, max_row=6, max_col=MAX_COL)

    # Find the subheader row: the row that contains 'Cost' or 'C-Price' in geo columns
    subheader_row_idx = None
    for ri, row in enumerate(grid):
        hits = sum(
            1 for c in range(FIXED_COLS, len(row))
            if row[c] and str(row[c]).strip().lower() in ("cost", "c-price", "l-price")
        )
        if hits >= 2:
            subheader_row_idx = ri
            break

    if subheader_row_idx is None:
        errors.append("Could not find column subheaders (Cost / C-Price / L-Price) in the first 6 rows.")
        return {"tiers_found": [], "regions": [], "rows": [], "errors": errors}

    # The geo label row is just above the subheader row
    geo_row_idx = subheader_row_idx - 1

    # Build mapping: column index → region name
    # The geo row has region names spread across blocks; subheader row tells us which sub-col is Cost/C-Price/L-Price
    col_to_region = {}
    col_role = {}  # col_index → 'sales_cost' | 'channel_price' | 'list_price' | None

    current_region = None
    for ci in range(FIXED_COLS, MAX_COL):
        geo_val = grid[geo_row_idx][ci] if geo_row_idx >= 0 else None
        sub_val = grid[subheader_row_idx][ci]

        if geo_val:
            current_region = str(geo_val).strip().upper()

        if current_region and sub_val:
            sub_lower = str(sub_val).strip().lower()
            if sub_lower == "cost":
                col_to_region[ci] = current_region
                col_role[ci] = "sales_cost"
            elif sub_lower == "c-price":
                col_to_region[ci] = current_region
                col_role[ci] = "channel_price"
            elif sub_lower == "l-price":
                col_to_region[ci] = current_region
                col_role[ci] = "list_price"

    regions = list(dict.fromkeys(col_to_region.values()))  # unique, ordered

    if not regions:
        errors.append("No region columns detected. Check that the sheet has geo headers above Cost/C-Price/L-Price.")
        return {"tiers_found": [], "regions": [], "rows": [], "errors": errors}

    # --- Parse data rows ---
    data_start_row = subheader_row_idx + 2  # 1-indexed for openpyxl (+1), plus skip subheader itself (+1)

    tiers_seen = []
    rows_out = []

    for row in ws.iter_rows(min_row=data_start_row, values_only=True):
        part_number = _clean(row[0]) if len(row) > 0 else None
        tier = _clean(row[1]) if len(row) > 1 else None
        base_warranty = _clean(row[2]) if len(row) > 2 else None
        upgrade_desc = _clean(row[3]) if len(row) > 3 else None
        delivery_type = _clean(row[4]) if len(row) > 4 else None

        # Skip empty or header-like rows
        if not part_number or not tier:
            continue
        if str(part_number).lower() in ("epack part #", "part #", "part number"):
            continue

        if tier not in tiers_seen:
            tiers_seen.append(tier)

        upgrade_years = _extract_upgrade_years(upgrade_desc)

        prices = {}
        for ci, region in col_to_region.items():
            if ci >= len(row):
                continue
            role = col_role.get(ci)
            if not role:
                continue
            if region not in prices:
                prices[region] = {"sales_cost": None, "channel_price": None, "list_price": None}
            prices[region][role] = _to_float(row[ci])

        rows_out.append({
            "part_number": part_number,
            "tier": tier,
            "base_warranty": base_warranty or "",
            "upgrade_description": upgrade_desc or "",
            "delivery_type": delivery_type or "",
            "upgrade_years": upgrade_years,
            "prices": prices,
        })

    return {
        "tiers_found": tiers_seen,
        "regions": regions,
        "rows": rows_out,
        "errors": errors,
    }
