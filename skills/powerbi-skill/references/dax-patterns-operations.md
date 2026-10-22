# DAX patterns and confirmed schema facts — Operations model

Model: **Operations Semantic Model** (`4757420e-ea5a-45e0-870c-b1e07e784c9d`,
AI Models Production). Pull this file before writing non-trivial DAX against it. For
cross-model query construction rules (DAX shapes, row-limit behavior), see
`dax-patterns-general.md`.

## Confirmed facts — as of 2026-10-09

Facts marked *(owner)* come from the model owner; the rest were verified live. Figures
are point-in-time and will drift.

### Reading this model's structure

- There is **no procurement table** (procurement shows up only as `FCT_SHIPMENT[PROCUREMENT_REP]` and PO fields) and **no deal-registration measure**.
- Column-name traps: `DIM_DATE[YEAR]` is numeric; `DIM_DATE[QUARTER]` is the text `"Q3"`; `DIM_DATE[MONTH_NUMBER]` is a **zero-padded string** (`"09"`); there is no `DIM_DATE[MONTH]`. There is no previous-month flag (`IS_CURRENT_MONTH`, `IS_CURRENT_QUARTER`, `IS_PREVIOUS_QUARTER`, `IS_NEXT_QUARTER`, `IS_CURRENT_YEAR`, `IS_TTM` do exist). For "last month," filter `YEAR` and `MONTH_NUMBER`; for "last quarter," `DIM_DATE[IS_PREVIOUS_QUARTER] = TRUE()` works on this model (verified: on 2026-10-12 it returns the same 23,277 quotes as `YEAR = 2026` and `QUARTER = "Q3"`). The flags describe the quote/booking date the measure switches to, so check which date the measure uses.
- Boolean-looking flags can be text: `FCT_DEAL_REGISTRATION[IS_EXPIRING_SOON]` is the string `"true"`/`"false"`, so comparing it to `TRUE()` errors.

### Date relationships — each fact uses a different date

Measures in `aaMeasures` switch dates with `USERELATIONSHIP`; a raw `DIM_DATE` filter on an un-switched column uses the **active** one:

| Fact | Active date (what a plain DIM_DATE filter hits) | Dates the measures switch to |
|---|---|---|
| `FCT_OPPTYLINE_SPLIT` | `DATE_CLOSE` (opportunity close) | — |
| `FCT_QUOTELINE` | `DATE_OPPORTUNITY_CLOSE` | `DATE_QUOTE_CREATED` (all `... by Quote Created Date` measures) |
| `FCT_SHIPMENT` | `DATE_ORDER` (order date) | `DATE_OPPORTUNITY_CLOSE` (Order Booked Revenue/Margin, international), `DATE_ACTUAL_SHIP`, `DATE_ACTUAL_DELIVERED`, `DATE_EST_SHIP` |
| `FCT_DEAL_REGISTRATION` | `DATE_DEAL_REG_CREATED` | `DATE_DEAL_REG_EXPIRED` is inactive |

Always read the measure's description for its date basis before comparing two measures. "Relative to Today" measures ignore `DIM_DATE` entirely.

### Booked (bookings) — Operations vs Core

- `Booked Revenue ACV` = `FCT_OPPTYLINE_SPLIT[REVENUE_ACV]` at `PROBABILITY = 100` with `IS_BOOKING = TRUE`, by close date. **It ties exactly to Core's `Booked Revenue ACV`** (2026 YTD $5,668,480,766 in both as of 2026-10-09).
- Operations' `Booked Margin ACV` is **gross margin ACV** (2026 YTD ≈ $915.8M). Core's booked margin is **commissionable** margin (≈ $905.1M). They differ by design; label which one an answer uses. Percent version: `Booked Margin ACV %`; prior year: `Booked Margin ACV SPLY` (needs a DIM_DATE filter).
- **Route plain booked-sales questions to Core.** Use Operations for booked sales only when the question compares booked to orders/shipments, or is about quotes, orders, fulfillment, international ship-to, or deal registrations.
- Filtering by territory credits each split recipient (split-adjusted). Region/geo: `DIM_TERRITORY[REGION]` / `[GEO]` joined via `TERRITORY_ID` — the path for every fact in this model.
- `DIM_OPPORTUNITY_TEAM` is many-to-many on `OPPORTUNITY_ID` (~5 rows per opportunity): a booking or deal registration appears once per matching team member. Filter one person or role; never sum across members; prefer distinct counts. `DIM_OPPORTUNITY_TEAM` → `DIM_USER` is inactive: use `USERELATIONSHIP(DIM_OPPORTUNITY_TEAM[USER_SFID], DIM_USER[USER_SFID])`.

### Orders and shipments (FCT_SHIPMENT)

- Grain is **parcel**: one row per order line × shipment set × parcel. Order-line amounts and quantities repeat on every parcel row, so **never SUM `REVENUE_ACV`, `MARGIN_ACV`, `PO_AMOUNT` etc. directly** — use `Order Booked Revenue` / `Order Booked Margin`, which count each order line once (`SUMX(VALUES(ORDERLINE_ID), MIN(...))`).
- Shipment, parcel, tracking and ship-date fields exist **only for Phoenix/Unity orders** (`DATA_SOURCE = "phoenix"`, from April 2024). Legacy `CDI` / `Ahead` rows carry order data only (no `PO_SHIPMENT_STATUS`). Always say when a shipped/delivered/on-time figure is Phoenix-only.
- `Order Booked Revenue` / `Order Booked Margin` are dated by **opportunity close date** and count **every order line**, once per line — 2026 YTD margin ≈ $861.2M, revenue ≈ $5.27B (as of 2026-10-09). *(owner, restated 2026-10-12)* **These are the shipping/shipped-dollar figures.** When someone asks for "shipping margin and revenue" or "how much has shipped" in dollars, report `Order Booked Margin` and `Order Booked Revenue` as they are, with no shipment-status split, no "fully shipped" filter, and no shipment-rate calculation. Example (owner-confirmed): opportunity `AHD2026678735` → Order Booked Revenue $79,999,630, Order Booked Margin $16,980,634. `Margin Difference` / `Revenue Difference` = Booked − Order Booked, a **net** gap. Q3 2026: booked margin ≈ $284.3M, order booked ≈ $271.3M, gap ≈ $13.0M.
- *(owner, 2026-10-12)* **Keep a one-line caveat** with shipped-dollar answers: these are order-line dollars and do not show how much has physically shipped.
- **Do not derive a shipped-dollar figure from `PO_SHIPMENT_STATUS`** (for example Fully Shipped only) unless the user explicitly asks for a status breakdown. Status is still the right field for line **counts** (`Open Order Lines Not Shipped`, `Order Lines Shipped`, `Past Due Order Lines`, tracking) — see below. If a user asks for a status breakdown of dollars, give it as an added view, labeled as a status cut, next to the Order Booked figures.
- Lookup keys: `DIM_OPPORTUNITY[OPPORTUNITY_NUMBER]` is the `AHD2026…` identifier (`DEAL_NUMBER` is `DEAL2026…`); a PO is `FCT_SHIPMENT[PO_NAME]` (for example `PO00084713`); order lines are `ORDERLINE_ID` / `ORDERLINE_NUMBER`. Filter an opportunity's order measures with `DIM_OPPORTUNITY[OPPORTUNITY_NUMBER]`; leave `DIM_DATE` unfiltered for an all-time figure.
- **`PO_SHIPMENT_STATUS`** (current status, purchase-order level) values: `Fully Shipped`, `Partially Shipped`, `Not Shipped Yet`, `On Hold`, `Shipment Not Needed`, and blank. Blank occurs on every legacy row and on a few Phoenix rows. It drives line counts, not the Order Booked dollar figures.
- Measure definitions (owner-provided 2026-10-12; they match the live model): `Order Booked Margin = CALCULATE(SUMX(VALUES(FCT_SHIPMENT[ORDERLINE_ID]), CALCULATE(MIN(FCT_SHIPMENT[MARGIN_ACV]))), USERELATIONSHIP(DIM_DATE[DATE], FCT_SHIPMENT[DATE_OPPORTUNITY_CLOSE]))`; `Order Booked Revenue` is the same with `MIN(FCT_SHIPMENT[REVENUE_ACV])`.
- **`Open Order Lines Not Shipped`** = status `Not Shipped Yet` or `Partially Shipped` (62,705 as of 2026-10-09: 53,468 + 9,237). **`Past Due Order Lines`** counts `EST_SHIP_PASTDUE = 1` (30,682). *(owner)* Report them as-is, separately. **They are not nested:** only 494 of the 30,682 past-due lines are in an open status, so never say "X% of open lines are past due" from these two numbers. If someone wants open AND past due, intersect explicitly: `CALCULATE([Past Due Order Lines], FCT_SHIPMENT[PO_SHIPMENT_STATUS] IN {"Not Shipped Yet","Partially Shipped"})` (494) and label it as a derived intersection.
- Both status measures are dated by order date and describe *current* status: **leave DIM_DATE unfiltered for current backlog**. This overrides the general "no period means current calendar year" default.
- **"Orders missing tracking"** *(owner)*: line status `Not Shipped Yet`, `Partially Shipped` or `On Hold`, no tracking number, order age 2+ days — this is `Order Lines Over 48h Without Tracking` restricted to those statuses (57,129 as of 2026-10-09). **Do not use the unfiltered measure:** it returns 573,144 (72% of Phoenix lines) because it includes `Shipment Not Needed` (340,044 — these never need tracking). Report separately: `Fully Shipped` with no tracking (167,992 — a data-quality gap, may include freight/pickups) and blank/unknown status (7,979 on Phoenix). Never mix those into the main count.
  `CALCULATE([Order Lines Over 48h Without Tracking], FCT_SHIPMENT[PO_SHIPMENT_STATUS] IN {"Not Shipped Yet","Partially Shipped","On Hold"})`
- **On-time and cycle time** (Phoenix only, dated by actual ship/delivery date): `On-Time Ship %` = shipped on or before the **original** estimated ship date (`DATE_ORIGINAL_ESTIMATED_SHIP`), lines with both dates only; `On-Time Delivery %` similarly vs `DATE_ESTIMATED_DELIVERY`; `Avg Days Order to Ship`. September 2026: 83.4% on-time, 31.1 average days. Results come back as formatted strings ("83.4%"). Quote the on-time definition when answering.
- Counting measures: `Order Lines` and `Purchase Orders` (by order date, include unshipped lines), `Order Lines Shipped`, `Parcels Shipped`, `Parcels Delivered`, `Distinct Shipments` (by close date), `Order Lines Scheduled to Ship` (dated by `DATE_EST_SHIP`; filter a future window). Today-relative: `OrderCount AS of Today for Ahead destination` (shipped today), `OrderCount for 30 days Prior`, `OrderCount for Next 2 weeks`, `OrderCount for Next 30 days`.

### International *(owner: route to Operations; default = non-US ship-to)*

- "International" means the **shipping (ship-to) country is outside the United States**, from `FCT_SHIPMENT[SHIPPING_COUNTRY]` / `[SHIPPING_CONTINENT]` on order lines (Phoenix-covered). Measures: `Customers Shipping Internationally`, `% of Customers Shipping Internationally`, `Distinct Opp Count - Customers Shipping Internationally`, `Distinct Count of Shipping Countries` (excludes the US despite the name), `Distinct Count of Continents` (includes North America), and the share measures `Shipping Revenue %` / `% of Margin - Order` (group by `SHIPPING_CONTINENT` or `SHIPPING_COUNTRY`).
- 2026 YTD order revenue by ship-to (as of 2026-10-09): United States ≈ $5.076B (96.24%); non-US ≈ 3.8%. By continent: North America 96.56% (includes Canada ≈ 0.25%), Europe 2.45%, Asia 0.87%, Oceania 0.10%, South America 0.01%, Africa 0.01%. Largest non-US countries: UK 1.04%, Switzerland 0.52%, Germany 0.41%, Netherlands 0.29%. Say whether "international" is non-US or non-North America.
- **Billing-country reading is secondary**: `Distinct Opp Count - International Customers` and `Distinct Count of International Countries/Continents` use `FCT_SHIPMENT[BILLING_COUNTRY]`; `International Customers` uses `DIM_CUSTOMER[IS_INTERNATIONAL_CUSTOMER]`; `Revenue % - Customer` / `% of Margin - Opportunity` use `DIM_CUSTOMER[BILLING_CONTINENT]` on bookings. Offer billing as the alternative reading, and note a blank-continent bucket exists on customers.

### Quotes (FCT_QUOTELINE) *(owner)*

- Quote measures are dated by **quote created date** (inactive relationship), not opportunity close. Exceptions: `Total Quotes on Booked Oppty` (close date).
- Quote basis: use primary quotes (`IS_PRIMARY_QUOTE = TRUE`) for dollars; counts exclude quotes with no opportunity. `Total Quote by Quote Created Date`, `Total Oppty by Quote Created Date`, `Avg Quote per Oppty`, `Avg Quoteline per Quote`.
- **Win rate** *(owner)*: a cohort rate by quote-created period, won ÷ (won + lost), counting only **decided** (closed) quotes. `Booked Quotes (% of Closed)` is the quote win rate (2026 YTD 74.7%; 2025 69.7%); `Booked Oppty (% of Closed)` is the same idea per distinct opportunity (74.9%). Use the quote version by default and the opportunity version when the user says "opportunity win rate." Companion shares: `Lost Quotes (% of Closed)`, `Lost Oppty (% of Closed)`, `Pipeline Quotes (% of Total Quotes)`, `Pipeline Oppty (% of Total Oppty)`, `Closed Oppty (% of Total Oppty)`.
- **Recent months are immature**: open quotes are not in the denominator, so the latest months read high (September 2026 86.4%, October to date ~92%). Always say recent periods are not yet fully decided, show the open share (`Pipeline Quotes (% of Total Quotes)`) alongside, and flag partial months.
- Dollar measures by quote date: `All Revenue $` / `All Margin $ by Quote Created Date` (any stage), `Booked Revenue $` / `Booked Margin $ by Quote Created Date` (won), `Unweighted Pipeline Margin by Quote Created Date`. These are quote value, not bookings — for bookings by close date use `Booked Revenue ACV` / `Booked Margin ACV`.
- Quotes per rep: `Avg Quote per Rep per Month` divides by `Count of Active employee` over everyone in the current `DIM_USER` filter. **Filter `DIM_USER` to the quoting team** (department/title/`PATH_LEVEL`), or the denominator is all active employees. `Count of Active employee` counts people employed for the *whole* date window (hired before the first date, not terminated before the last). `DIM_USER` filters `FCT_QUOTELINE` on the quote creator.

### Deal registrations (FCT_DEAL_REGISTRATION)

- No measures exist; answers are hand-aggregated row counts (`COUNTROWS` of the table, or distinct `DEAL_REGISTRATION_ID`). Say the figure is a count of registrations, not dollars. `DIM_USER` filters this table on `COS_REP_SFID`, which is **unpopulated** — use `FCT_SHIPMENT[COS_REP]` or `DIM_OPPORTUNITY_TEAM` for COS questions.
- `DEAL_REG_STATUS` values (row counts as of 2026-10-09): Approved 33,488; Expired 14,962; No Deal Registration 11,454; Canceled 6,540; Pending with the OEM 5,769; Declined 3,004; Submitted 2,932; Needs to be submitted to OEM 2,865; **Pending 825**; blank 2,235.
- **"Pending deal registrations" = status `Pending` only** *(owner)* (825). Mention "Pending with the OEM," "Submitted" and "Needs to be submitted to OEM" as separate statuses if the user wants a broader reading; don't fold them in silently.
- **"Expiring soon" = status `Approved` with an expiration date (`DATE_DEAL_REG_EXPIRED`) in the next 30 days** *(owner)* (1,189 as of 2026-10-09). Remove the DIM_DATE filter (the active date is the created date). Do **not** use `IS_EXPIRING_SOON`: it is `"true"` on Approved, Expired and already-past rows and its threshold is undocumented. Approved rows also carry junk far-future dates (max 2206), so always bound the window both ways.
  `CALCULATE(COUNTROWS(FCT_DEAL_REGISTRATION), FCT_DEAL_REGISTRATION[DEAL_REG_STATUS] = "Approved", FCT_DEAL_REGISTRATION[DATE_DEAL_REG_EXPIRED] >= TODAY(), FCT_DEAL_REGISTRATION[DATE_DEAL_REG_EXPIRED] <= TODAY() + 30, REMOVEFILTERS(DIM_DATE))`
- Status and expiry fields are a current snapshot, not dated to a period.

### Region, geo and territory *(owner)*

- Every fact filters `DIM_TERRITORY` on `TERRITORY_ID`: use it for region/geo/territory cuts of bookings, quotes, orders and deal registrations. Bookings and order measures are split-adjusted by each seller's territory.
- **"By region" = `DIM_TERRITORY[REGION]`** (broad: East, Central, West, Mid-Market, House Account; a few minor values such as MSE, EMEA, Foundry Custom, plus blank). **"By geo" = `[GEO]`** (sub-regional: NorCal, PA, Ohio, New York 1/2, Georgia, Carolinas, and similar). **"By territory" = `[TERRITORY]`**, whose values are **seller names** (for example one East territory alone holds about 17% of all past-due lines). Also available: `MD`, `GEO_MD`, `EVP`, `REGION_EVP`, `TEAM_LEAD`. Say which level was used; offer the other.
- Show the **blank region and House Account buckets labeled**, never dropped (House Account Q3 2026 booked revenue is slightly negative). Region figures should sum to the unfiltered total — use that as a consistency check.
- Q3 2026 booked vs. ordered by region (as of 2026-10-12): Central $970.3M / $829.3M; East $453.8M / $436.3M; West $269.1M / $242.2M; Mid-Market $25.6M / $25.3M; blank $1.27M both; House Account −$0.53M both. Margin (gross): Central $156.5M / $150.3M, East $85.1M / $81.9M, West $37.5M / $34.1M, Mid-Market $5.1M / $5.0M. The regional order margin sums to the company figure ($271.3M). Central's revenue gap is much larger than its margin gap (low-margin lines) — flag it.
- Past-due order lines by region (as of 2026-10-12): East 15,827; Central 10,938; West 3,549; Mid-Market 511; House Account 15 (total 30,840). Same non-nesting rule as before.
- H1 2026 quote win rate by geo is a cohort by quote-created date: overall 72.4% on 45,855 quotes, with ~13% still open; small House Account geos and the blank geo have tiny counts — label them rather than ranking them against real territories.
- `TOPN` output is **not sorted**: add `ORDER BY` for any top-N list.
- `DIM_TERRITORY[REGION]` is not the customer's location. Customer location is `DIM_CUSTOMER[BILLING_*]`; order ship-to is `FCT_SHIPMENT[SHIPPING_*]`.

### People, headcount and quotes per rep *(owner)*

- **Quoting team = `DIM_USER[DEPARTMENT] = "666 - Operations"`.** In 2026 that department created 60,278 of 71,394 quotes (84%) from 164 people: Client Ops Specialist (69 creators), Sr Client Ops Specialist (23), Renewal Specialist (30), Client Operations Manager (12), plus managers/directors and maintenance-renewal specialists. Other creators: 705 Services Operations (2,471 quotes, 21 people), 676 Solutions Engineering (2,283 quotes spread over 180 people), many small departments, and **5,584 quotes with no department** on the user record. Report the share not in department 666 as outside the team; never fold it in silently.
- **Quotes per rep per month** = `Avg Quote per Rep per Month` **filtered to that department**, over **complete months only** (do not use a window that includes future or partial months — the measure divides by the number of months in the date filter, so a full-year filter dilutes it: department 666 for all of 2026 reads 24.3 vs. 31.1 for January–September). The **unfiltered** measure divides every quote by every active employee in the company and reads about 2.0 — never report that as quotes per rep.
  `CALCULATE([Avg Quote per Rep per Month], DIM_USER[DEPARTMENT] = "666 - Operations", DIM_DATE[YEAR] = 2026, DIM_DATE[MONTH_NUMBER] IN {"01","02","03","04","05","06","07","08","09"})` → 31.1 per rep per month (as of 2026-10-12).
  Q3 2026: 27.7 (19,510 quotes, 235 reps).
- **Headcount** = `Count of Active employee` as-is: people employed for the **whole** date window (hired on or before the first date, not terminated before the last). Department 666: 235 for Q3 2026, 208 for January–September. This differs from "active today" (no termination date, about 254 for Q3) and from a monthly-average headcount (~220–248 per month); state which basis is used (owner: whole-window, complete months) and note that people who joined or left mid-window are excluded.
- A top-N of quote creators must exclude the blank-creator row (2,059 quotes in Q3 2026 have no creator user) or it will displace a real person; say the blank bucket exists. Always `ORDER BY`.
- The quote creator's name is `DIM_USER[DISPLAY_NAME]` (title: `[TITLE]`); a creator top-N groups `DISPLAY_NAME`, `TITLE`, with `Total Quote by Quote Created Date`. Q3 2026 leaders (verified 2026-10-12): Jesse Johnson 467, Tess Wittmann 431, Jordan Price 375, Carey Borrelli 361, Megan Frank 354; all in department 666; 19,510 of the quarter's 23,277 quotes are in the team.
- Quote-creator names are people: they follow the user's RLS; keep individual names to what the question asks for.

### Products and customers

- **Customer roll-up** *(owner)*: rank customers and answer named-customer snapshots on **`DIM_CUSTOMER[ULTIMATE_PARENT_NAME]`** (27,552 distinct accounts roll up to 25,887 ultimate parents; one blank). The 2026 top booked-revenue customers are unchanged by the roll-up (Morgan Stanley $222.9M, Bank of New York $200.2M, Balyasny $169.9M, SMBC $162.5M, CHSPSC $121.9M). Show the account names under a parent only if asked. `DIM_CUSTOMER[CUSTOMER]` is the individual account. **Exception *(owner)*: international customer rankings and breakdowns use `DIM_CUSTOMER[CUSTOMER]` (the individual account), not the ultimate parent** — see the international bullet below.
- **Named customers** ("Amex"): abbreviations are rarely stored — search `DIM_CUSTOMER[CUSTOMER]` and `[ULTIMATE_PARENT_NAME]` with `SEARCH` (case-insensitive) on the long form. If more than one parent matches, give figures for each close match. Customers with no measure rows drop out of a `SUMMARIZECOLUMNS` that includes measures, so a missing row means "no data," not "no such customer."
- Customer snapshot shape (status measures, no date filter): `CALCULATE([Open Order Lines Not Shipped], DIM_CUSTOMER[ULTIMATE_PARENT_NAME] = "<name>")`; pending deal registrations for a customer: `CALCULATE(COUNTROWS(FCT_DEAL_REGISTRATION), FCT_DEAL_REGISTRATION[DEAL_REG_STATUS] = "Pending", DIM_CUSTOMER[ULTIMATE_PARENT_NAME] = "<name>", REMOVEFILTERS(DIM_DATE))` — blank means zero. Spot check (2026-10-12): Morgan Stanley open 8,251, missing tracking 7,777; American Express Travel Related Services open 103, past due 19, pending deal registrations 0.
- **"Ships the most internationally"** has no stored metric: rank by non-US ship-to **order revenue** (`Order Booked Revenue` with `FCT_SHIPMENT[SHIPPING_COUNTRY]` not blank and not "United States"), label it order booked revenue on all order lines, and say lines with a blank ship-to country are excluded. *(owner)* **Rank and group by the individual account, `DIM_CUSTOMER[CUSTOMER]`, not the ultimate parent.** 2026 YTD top ten by account (as of 2026-10-12, ordered revenue): Morgan Stanley $20.7M, CSL Behring $17.8M, Zurich Insurance Company Ltd $15.6M, Solera Holdings Inc $11.1M, Nielsen Consumer LLC (NielsenIQ) $11.0M, Tradeweb $9.8M, Rockstar Games Inc $8.5M, Five9 Inc. $7.1M, TikTok Inc. $6.5M, FEV Europe GmbH $5.8M. A parent roll-up gives a different order (Tradeweb would be third at $17.5M because its revenue is split across accounts); mention the parent view only if the user asks. Countries showing about $0 are net-zero lines.
- `DIM_PRODUCT_STAMPED` (`*_STAMPED`) preserves classification at booking time (use for historical reporting); `DIM_PRODUCT_CURRENT` (`*_CURRENT`) reflects today's taxonomy and can differ. Stamped joins on `PRODUCT_GROUP_ID`, current on `PRODUCT_ID`.
- `DIM_CUSTOMER` carries `BILLING_COUNTRY`, `BILLING_CONTINENT`, `IS_INTERNATIONAL_CUSTOMER`, `IS_FOUNDRY_CUSTOMER`; internal customers are excluded from `FCT_SHIPMENT`.

### DAX gotchas

- `TREATAS({2026}, DIM_DATE[YEAR])` inside `SUMMARIZECOLUMNS` works for year filtering with a column grouping; the order measures activate their own `USERELATIONSHIP`, so a `DIM_DATE` filter is evaluated on the date that measure switches to.
- `SAMEPERIODLASTYEAR` measures (`... SPLY`, `Order Booked Margin YoY %`) require a `DIM_DATE` filter and return blank without one.
- Grouping or filtering on a text `"true"/"false"` column with `TRUE()` errors; compare to the string.
