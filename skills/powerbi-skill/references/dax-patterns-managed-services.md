# DAX patterns and confirmed schema facts — Managed Services model

Model: **Managed Services Semantic Model** (`9c273318-68de-4b79-be27-cc57127b1463`,
AI Models Production). Pull this file before writing non-trivial DAX against it. For
cross-model query construction rules (DAX shapes, row-limit behavior), see
`dax-patterns-general.md`.

## Confirmed facts — as of 2026-10-12

Facts marked *(owner)* come from the model owner; the rest were verified live.

### Reading this model's structure

- Several measures return text-formatted values (for example `"$10,899,736"`, `"60.60%"`, `"81% to Plan"`). Don't sum them client-side; compute totals in DAX.
- `DIM_DATE` has `IS_CURRENT_MONTH`, `IS_CURRENT_QUARTER`, `IS_PREVIOUS_QUARTER`, `IS_NEXT_QUARTER`, `IS_CURRENT_YEAR`, `IS_LAST_TWELVE_MONTHS`, but **no previous-month flag**. For "last month," filter `DIM_DATE[YEAR]` (numeric) and `DIM_DATE[MONTH_NUMBER]`, a **zero-padded string** (`"09"`, not `9`).
- "Last month" is the last **completed** calendar month, computed from today's date (in January, December of the prior year). The check values in this file are as-of 2026-10-12 tie-outs, not answers; re-query for the current period.
- Putting `KEEPFILTERS(DIM_PRACTICE[L1] = ...)` inside `SUMMARIZECOLUMNS` fails; wrap in `CALCULATETABLE` or use `CALCULATE`. The connector then appends a style notice about `CALCULATETABLE` around `SUMMARIZECOLUMNS`; it doesn't affect the result.
- Top-N output isn't sorted; add an explicit `ORDER BY`.

### Which measures are already Managed Services-scoped

- **Practice-scoped (`DIM_PRACTICE[L1] = "Managed (L1)"` is built in):** `Booked Revenue`/`Booked Margin` and their prior-period/YTD variants, all `Weighted Pipeline ...` measures, all plan measures, `Delivered Revenue`/`Delivered Margin` and variants, `Projected Delivered ...`, `Subscription MRR - Monthly Anniversary`, and `Headcount`. Opportunity-line measures also apply `IS_BOOKING = TRUE`; don't add either filter again.
- **Not practice-scoped, add the filter yourself when the question is about the practice:** every measure that says "covers all product families" (`Total MRR (First Month)`, `Total MRR (First Month) by Opportunity Close`, `Subscription MRR - Subscription Start`, `Subscription Revenue ACV/TCV`, `Subscription MRM`, `Total Contracts`, `Total Subscriptions by Contract End Date`, `Total List Price`). Use `CALCULATE([measure], KEEPFILTERS(DIM_PRACTICE[L1] = "Managed (L1)"))`.
- **Deliberately not practice-scoped (data is Managed Services only by source):** `Subscription MRR`, `Contract MRC`, `Contract Margin` (from `FCT_SUBSCRIPTION_MS`, including subscriptions with no stamped practice), ServiceNow hours and utilization measures, `Backlog`. Say so in the scope line.

### Plan vs. actuals — *(owner)* same-period basis

- Plan is **monthly** (unlike Solutions Engineering, where it exists only at quarter level and above) and comes from `FCT_PLAN_BY_PRACTICE` (`PLAN_TYPE` = Booked or Delivered, `FAMILY` = Managed Services).
- *(owner)* **"vs plan" means same-period plan:** actuals through the last completed month against plan through the same months. Show the full-year plan as context.
- **Don't use the model's `... Plan YTD` or `... Plan %` measures as-is for a partial year.** With a current-year filter, `Booked Margin Plan YTD` returns the full-year $32,449,263, and `Delivered Revenue Plan %` divides year-to-date actuals by the full-year plan ("81% to Plan"). Sum the monthly plan measure over the completed months instead: `CALCULATE([Delivered Revenue Plan], DIM_DATE[YEAR] = 2026, DIM_DATE[MONTH_NUMBER] <= "09")`.
- Booked margin plan is margin and compares to `Booked Margin`, not `Booked Revenue`. Delivered plan compares to `Delivered Revenue`/`Delivered Margin`.
- 2026 checks (as of 2026-10-12): booked margin $21,676,392 vs full-year plan $32,449,263; delivered revenue Jan–Sep $95,155,579 vs same-period plan $85,929,572 (≈ 111%), full-year plan $117,572,928.
- "This year" includes future-dated closes and months; say so in the scope line. Don't prorate an in-progress month: lead with the completed-month comparison and give the in-progress month's actuals separately, against its full-month plan, labeled as not comparable.

### Booked, pipeline, and delivered

- Booked = won opportunity lines (`DIM_OPPORTUNITY[IS_WON] = TRUE`, `IS_BOOKING = TRUE`) dated by close date, gross margin ACV (not Core's commissionable margin; label the basis).
- *(owner)* Delivered revenue is `Delivered Revenue` = sum of `FCT_DELIVERED_FINANCIALS[REVENUE]` for `DIM_PRACTICE[L1] = "Managed (L1)"` (Adaptive actuals by month). Use that measure as-is.
- `Book to Bill` divides booked by delivered over the same filter; with a full-year filter the booked side includes future-dated closes with no delivery yet. For a clean figure use completed months only (2026 Jan–Sep ≈ 0.94x; the full-year-filtered measure shows 0.95x).

### MRR and subscriptions

- *(owner)* **Current MRR** = `Subscription MRR` filtered to the current month (October 2026 = $10,899,736). `Subscription MRR - Monthly Anniversary` is the practice-scoped alternative and gives a different value for the same month ($10.74M); mention it only if asked. Future months already carry contracted MRR, so say "current month" explicitly.
- *(owner)* **New MRR** = `Total MRR (First Month)` dated by **subscription start**, with the Managed Services practice filter added (September 2026 = $270,560). Offer `Total MRR (First Month) by Opportunity Close` (≈ $357.5K for September) as the close-date reading.
- `Revenue ACV` / `Revenue TCV` repeat on every month of a subscription; filter to one month or use the `Subscription Revenue ACV/TCV` measures.

### Utilization, hours, and headcount

- *(owner)* A bare "utilization" question uses **`Effective UTIL`** (average weekly effective utilization per employee, 40-hour week, goal 70%) for the last completed month. September 2026 = 60.6%; the PTO-excluded variant is 62.55% and is an alternative only.
- Hours and utilization come from ServiceNow time worked for whoever logs time; they are **not** practice-scoped, and that population can differ from headcount.
- *(owner)* **Current headcount** = `Headcount` pinned to today's date (622 on 2026-10-12; the measure uses the last date in the filter, and with no date filter it also returned 622).
- The time-worked table contains weeks dated later in 2026; confirm the date range before quoting hours for a partial period.

### Customer profitability — *(owner)*

- Rank and describe customers by **`Operation Margin $`** (Subscription MRR minus COGS and labor cost of hours), with `Operation Margin %` alongside, as on the Customer Profitability report. Use **all contract statuses** and say so in the scope line; offer an Activated-only cut on request.
- 2026: total Operation Margin $ $74,838,487; labor $58,252,610, of which **$20,156,714 has no customer** (blank customer). Report that bucket separately; never rank it as a customer. List customers with labor cost but no MRR separately, and note negative-MRR rows (credits/adjustments) rather than ranking them.
- Future-month MRR is included in a full-year figure while labor covers only elapsed months, so full-year margin looks better than it is; state the period.
- **Presentation of a "least profitable" list:** three separate lists, never one merged table. (1) The ranking: the 10 lowest `Operation Margin $` among customers with `Subscription MRR` greater than zero. (2) Customers with labor cost but no MRR, largest labor first (top 10), under their own heading. (3) Negative-MRR rows (credits/adjustments) and the blank-customer labor bucket, noted but not ranked.
- Recipe: group by `DIM_CUSTOMER[CUSTOMER]`, filter `DIM_DATE[YEAR]`, and rank by **dollars** (`Operation Margin $`), not percent; tiny accounts produce huge negative percentages (for example -1,383%). Show `Subscription MRR`, `Cost of Hours`, and `Operation Margin $` per customer. Operation Margin $ also deducts delivery COGS, not labor alone, so say "after labor and delivery costs" in the scope line.
- Customers with labor but no MRR (for example State of Tennessee: TennCare, Verra Mobility, Wawa.com) may reflect MRR booked under a different or parent customer name rather than true zero revenue; flag that when listing them.

### Backlog — *(owner)*

- The model's `Backlog` = ACV of **Draft** contracts (not yet active), ignores date filters: $378,004,241 on 2026-10-12. `Backlog Opportunities` = won opportunities with a primary Managed Services quote and no subscription (1,918 with no date filter). Unlike `Backlog`, it **responds to date filters** (827 under a 2026 year filter); leave the date filter off for the current count.
- The Contract Out Years report's Backlog page shows a different view, **`Backlog Delta`** = `Subscription MRR - Monthly Anniversary` minus `Invoice Amount` (contracted MRR not yet invoiced), plus the Backlog Opportunities list, filtered to the Managed Services family.
- `Invoice Amount` (invoice lines on Annually-billed contracts divided by 12) and `Backlog Delta` are in the production model as of 2026-10-12 (108 measures).
  September 2026 check: MRR $11,053,517, invoiced $8,910,632, delta $2,142,885; October $10,097,227. Future months have no invoices, so the delta equals the full MRR there, and **with no period filter it sums every month (≈ $705M) — always state or filter a period**.
- **Which to lead with *(owner, 2026-10-12)*:** `Backlog Delta` is the figure the published Contract Out Years report's Backlog page shows (that page, filtered to the Managed Services family, uses `Backlog Delta` and the Backlog Opportunities list; the Draft-contract `Backlog` measure appears in neither report). A bare "backlog" or "contract backlog" question therefore **leads with `Backlog Delta`**, for the **current calendar month** when no period is given, with the period stated in the scope line and other periods (remainder of the year, a named month) offered. Give `Backlog Opportunities` (date filter off) alongside it, and give Draft-contract ACV (`Backlog`, $378.0M on 2026-10-12) as a secondary figure labeled "ACV of contracts not yet active." Current-month `Backlog Delta` can look high because the month's invoicing is incomplete (October 2026 = $10,097,227 on 2026-10-12); say so.
- Managed Services `Backlog` (Draft-contract ACV) is not the Services model's frozen September 2025 `PS Backlog`; don't mix them.
