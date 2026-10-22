# DAX patterns and confirmed schema facts — Solutions Engineering model

Model: **Solutions Engineering Semantic Model** (`44ea7eec-f6f5-4406-90c1-f30473b82b35`,
AI Models Production). Pull this file before writing non-trivial DAX against it. For
cross-model query construction rules (DAX shapes, row-limit behavior), see
`dax-patterns-general.md`.

## Confirmed facts — as of 2026-10-09

Facts marked *(owner)* come from the model owner; the rest were verified live.

### Reading this model's structure

- Useful column names for deal-level detail: `DIM_OPPORTUNITY[OPPORTUNITY_NAME]`, `[STAGENAME]`, `[PROBABILITY]`, `[HAS_SSE]`, `[SOLUTION_LEAD]`; `FCT_OPPTYLINE_SPLIT[LOSS_REASON]`; `DIM_OPPORTUNITY_TEAM[TEAM_MEMBER_ROLE]`. Applying the SSE role filter via `TREATAS` or a plain column filter both work.

### Fiscal calendar and dates

- *(owner)* AHEAD's fiscal year equals the calendar year (January–December). Quarters are calendar quarters.
- *(owner)* All booked figures are dated by **opportunity close date**.
- *(owner)* "This year" may include future-dated closes. Include them, but state in the scope line that the figure is by opportunity close date for the full year, including any future-dated closes.
- `DIM_DATE` has `IS_CURRENT_MONTH`, `IS_CURRENT_QUARTER`, `IS_PREVIOUS_QUARTER`, `IS_NEXT_QUARTER`, `IS_CURRENT_YEAR`, but **no previous-month flag**. For "last month," filter `DIM_DATE[YEAR]` (numeric) and `DIM_DATE[MONTH_NUMBER]`; `MONTH_NUMBER` is a **zero-padded string** (`"09"`, not `9`).

### What "booked" means here

- *(owner)* Booked numbers are `REVENUE_ACV` and `GROSS_MARGIN_AMOUNT_ACV` on `FCT_OPPTYLINE_SPLIT` where `DIM_OPPORTUNITY[PROBABILITY] = 100`.
- The main booked measures are **`Booked Revenue`** and **`Booked Margin`** (not Core's `Booked Revenue ACV` / `Booked Margin Commissionable`). Both also apply `IS_BOOKING = TRUE` on top of `PROBABILITY = 100`.
- **`IS_BOOKING` is not the same thing as booked.** As in Core, `IS_BOOKING = TRUE` only marks a line as eligible for standard sales reporting. It says nothing about deal stage. Use `Booked Margin` / `Booked Revenue`, which apply the probability filter; never use `IS_BOOKING` alone as a booking filter.
- **Margin is not comparable to Core's.** This model's margin is *gross margin amount ACV*; Core's `Booked Margin Commissionable` is *commissionable margin ACV*. 2026 YTD showed ~$914.7M here vs ~$903.7M in Core. Label which margin is in use whenever both models appear in one answer, and don't present the difference as an error.
- `Total Margin` sums `GROSS_MARGIN_AMOUNT_ACV` with only `IS_BOOKING = TRUE` (no probability filter), so it includes open pipeline. Don't use it for booked figures.

### Plan vs. actuals (CSE and SSE)

- *(owner)* Plan is **margin**, and actuals are **margin**. Compare plan to `Booked Margin` (gross margin amount ACV, `PROBABILITY = 100`), never to `Booked Revenue`. A revenue-vs-plan comparison overstates attainment roughly 6x (observed in a fresh-session test).
- *(owner)* CSE plan comes from `FCT_CSE_PLAN_2026` (measure `CSE Plan`); SSE plan comes from `FCT_SSE_PLAN_2026` (measure `SSE Plan`).
- Plan grain: CSE plan is by `GEO` (and product/services, date); SSE plan is by `REGION`, `SUBPILLAR`, `CATEGORY`, `SALES_COVERAGE`. **There is no per-person plan** for either role. Say so when asked about an individual's attainment.
- 2026 full-year plan totals (as of 2026-10-09): CSE ≈ $828.5M, SSE ≈ $983.4M.
- *(owner)* Plan exists only at **quarter level and higher**. It cannot be prorated, so never compare plan to a month, week, or partial period, and never prorate it for a partial quarter. For a quarter in progress, compare quarter-to-date actuals to the full-quarter plan and state that it is quarter-to-date against the full quarter's plan, not a pace measure.
- Plan only covers 2026, with one set of rows for each of the four quarters. Quarterly plan totals (as of 2026-10-09), CSE / SSE: Q1 $164.2M / $196.7M, Q2 $206.5M / $245.8M, Q3 $206.3M / $245.8M, Q4 $251.5M / $295.1M. The plan responds to `DIM_DATE` filters at quarter or year level. Filter actuals to the same period as the plan you compare against.
- **CSE attainment** = `Booked Margin (Account Team)` with `DIM_USER[PATH_LEVEL3] = "Paul Erck"` ÷ `CSE Plan`, for the same quarter or year. **SSE attainment** = `Booked Margin` filtered to the "Solutioning Team Member" role ÷ `SSE Plan`.

### Who is a CSE and who is an SSE

- *(owner)* SSEs are people tagged with the team-member role **"Solutioning Team Member"** in `DIM_OPPORTUNITY_TEAM[TEAM_MEMBER_ROLE]`. Despite the model's own description text, don't read "SSE" as "Specialist Sales Engineer."
- *(owner)* **CSEs are defined by the account team, not by an opportunity-team role.** A CSE's bookings are the booked revenue/margin on the customers whose **account team** (`FCT_ACCOUNT_TEAM_SPLIT`) rolls up to **Paul Erck's organization** (`DIM_USER[PATH_LEVEL3] = "Paul Erck"`). Use the `(Account Team)` measures — `Booked Margin (Account Team)` and `Booked Revenue (Account Team)` — with that filter:
  `CALCULATE([Booked Margin (Account Team)], DIM_USER[PATH_LEVEL3] = "Paul Erck")`
  These measures take their customer list from the account team and ignore the opportunity team, so they cover **all** booked deals on those customers, not only deals where a CSE is on the opportunity. Current-quarter check (2026-10-09): Booked Margin (Account Team) ≈ $18.3M, Booked Revenue (Account Team) ≈ $133.5M against a CSE Plan of ≈ $251.5M.
- **Do not use the opportunity-team role "Client Solutions Engineer" to measure CSE bookings.** It gives a different, smaller number (≈ $15.8M vs ≈ $18.3M for the same quarter) and is not how AHEAD defines CSE credit.
- **To get SSE-credited bookings, filter the role:**
  `CALCULATE([Booked Margin], DIM_OPPORTUNITY_TEAM[TEAM_MEMBER_ROLE] = "Solutioning Team Member")`
  2026 YTD check (2026-10-09): total Booked Margin ≈ $914.7M; SSE-role ≈ $686.0M.
- **These are not additive.** SSE bookings (opportunity-team role) and CSE bookings (account-team customers) are measured on different bases and overlap each other and the total. Never add them together, and never sum role rows across roles.
- **Other "SSE" fields use a different definition and give a different number:** `Booked Margin w/ SSE` (and `Open/Closed ... w/ SSE`) test `DIM_OPPORTUNITY[HAS_SSE] = TRUE` **or** a non-blank `SOLUTION_LEAD` (2026 YTD ≈ $705.8M, vs ≈ $686.0M for the role filter). `Solution Lead Margin` keys on the opportunity's solution lead. `DIM_SSE_TEAM` / `RPT_SSE_BRIDGE` carry SSE team rosters (Intelligent Operations, AI & Cloud, Mid-Market, etc.) and can overlap across teams. For "what did SSEs book," use the **role filter** and say which definition you used; mention the flag-based measure only if the user asks about "deals with an SSE involved."

### Win/loss

- *(owner)* Closed-won opportunities must **not** include closed-lost deals. `Distinct Count of Closed Opps` is the **closed-won** count: distinct opportunities at `PROBABILITY = 100` with `IS_BOOKING = TRUE`. (2026 YTD as of 2026-10-09: 25,105 won.)
- `Lost Opps` counts distinct opportunities with `STAGENAME = "Closed Lost"` and `LOSS_REASON <> "Duplicate"` (2026 YTD: 15,134). Duplicate-reason losses are excluded, so confirm the loss-reason treatment before comparing lost counts across cuts.
- Two ratios exist, and they answer different questions. `Closed Opps Ratio` = won ÷ (won + lost) is the **win rate** (2026 YTD ≈ 62.4%). `Close Ratio` = won ÷ `Total Opportunities` (every `IS_BOOKING` opportunity, including open pipeline) ≈ 47.8% and is **not** a win rate. For "win rate," use `Closed Opps Ratio` and say so.

- There is **no measure for lost-deal revenue or margin** — only the `Lost Opps` count and `Closed Lost Margin`. A lost-deal revenue figure has to be hand-summed over `FCT_OPPTYLINE_SPLIT[REVENUE_ACV]` for `STAGENAME = "Closed Lost"`; label it as an unvalidated size indicator, not a booked amount.

### DAX gotchas

- `TOPN` output is not sorted. Add an explicit `ORDER BY` when listing top deals.

- Grouping by a boolean column (e.g. `DIM_OPPORTUNITY[HAS_SSE]`) and filtering it inside `SUMMARIZECOLUMNS` fails with "a single value cannot be determined." Move the filter into `TREATAS` / `CALCULATETABLE` instead.
- Filtering month with an un-padded string (`"9"`) returns "value not found." Use `"09"`.
