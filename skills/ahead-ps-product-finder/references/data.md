# Data snapshot

Source: Salesforce report "AHEAD Services Product Estimates Report" (all Active, Orderable Professional Services estimate products). Export date is in `data/snapshot.json`.

## Refresh
1. Run the report in Salesforce and export it as CSV (Details Only, Comma Delimited).
2. `python3 scripts/refresh_data.py "<export>.csv"` rewrites `data/estimate_products.csv` and `data/snapshot.json` and prints the products added and removed. Check that list looks sensible.
3. Required report columns: `Estimate Product Name`, `Product: Item Code / Manufacturer SKU`, `Product: Item Description`, `Active`, `Product: Item State`, `Level 1 Service`. Used when present: Service OEM, Pillar, L1/L2/L3, Category, Sub-category, Service Brief Link, Item Name.
4. Rows with `Active` not 1 or Item State not `Orderable` are dropped by the script.

## Known data quirks
- Level is read from the P: name (`SL1-Level1`, `SL2-Configurable`, `SL3-Custom`). The `CHS` variants carry SL2 in the name.
- The export writes an en dash in some names as `?` (14 names). Flag `name-has-?`.
- 10 rows share a SKU with another product. Flag `shared-sku`.
- 54 rows have no description. Flag `no-description`; treat as tentative.
- No template column or template active flag: `T_Name` is derived. Adding `Estimate: Template` and its active flag to the report would remove the derivation.
- Cost, margin and currency columns are intentionally not kept.
