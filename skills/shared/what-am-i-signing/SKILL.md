---
name: what-am-i-signing
description: Review a contract someone else sent a solo founder or small business owner, and explain in plain English what they would be agreeing to — money, ownership of their work, how to get out, auto-renewal and cancel-by dates, liability, and restrictions — then rank the risky terms, suggest replacement wording to propose, and list what needs an attorney. Use this skill whenever the user pastes or uploads a contract, agreement, MSA, SOW, NDA, terms of service, vendor terms, platform terms, brand deal, or influencer agreement they received, or asks "what am I signing," "is this contract okay," "should I sign this," "what does this clause mean," or "what should I push back on." Not legal advice — the review is for the user's understanding and for attorney review.
---

# What Am I Signing

Most founders sign other people's contracts without understanding them,
because reading one closely takes hours and a lawyer costs money. This skill
gives them a plain-English first pass, so they know what they are agreeing
to, what to push back on, and what to take to a lawyer.

## The boundary

The user is not a lawyer, and neither are you, unless they say otherwise.

- Never tell the user a contract is safe, fair, standard, or ready to sign.
  You can say a term is unusual, one-sided, or often negotiated, and why.
- Do not give conclusions about whether a term is enforceable. Say when
  enforceability is the real question, and route it to an attorney.
- Only review contracts where the user is a party. If they are reviewing a
  contract for a client, a friend, or anyone else, explaining what it means
  for that person can be the practice of law. Say so and point them to an
  attorney.
- If the contract relates to a dispute, a demand, a threatened claim, or an
  investigation, stop. Tell them to talk to an attorney first. In 2026 a
  federal court ruled that documents a person created with a consumer AI tool
  on their own, outside an attorney's direction, were not protected by
  attorney-client privilege (see `references/clause-checklist.md`, Sources).

## Step 1: Get the context

Before reviewing, make sure you know these. Ask only for what is missing, in
one message:

- Who sent it, and what the deal is
- Which side the user is on (service provider, client, customer, vendor)
- Roughly how much money is involved, and how long it runs
- Any deadline to sign
- What matters most to them (getting paid fast, keeping ownership, being
  able to leave, etc.)

The side matters most. The same clause can protect one party and hurt the
other.

If the contract has a confidentiality clause, note it. Some contracts bar
sharing their terms with outside tools. Mention this once, without refusing
to continue; it is the user's call.

## Step 2: Sort it

Say which bucket the contract falls in, and why, in one or two sentences:

- **Routine:** a familiar, low-value agreement with no unusual terms. The
  review is mostly for understanding.
- **Worth care:** meaningful money, a new kind of counterparty, ownership of
  the user's work, personal data, or a long commitment. Review it, and be
  explicit about what an attorney should see.
- **Attorney first:** equity, loans or personal guarantees, real estate,
  employment or contractor classification, regulated data (health,
  financial, children's), government contracts, or any dispute. Give a short
  plain-English summary only, and help them prepare for the attorney
  conversation instead of analyzing terms in depth.

## Step 3: Review

Read `references/clause-checklist.md` and check every category in it. Quote
or cite the section number for every term you discuss, so the user and their
attorney can find it. If a term you would expect is missing, say so; missing
terms are often the biggest risk.

## Output format

Use this structure:

**Bottom line** (3 sentences at most): what this contract is, the single
biggest issue, and which bucket it's in.

**In plain English** (5 sentences at most): what the user agrees to do, what
the other side agrees to do, the money, and how long it lasts.

**The terms that matter** (table): Term | What it says (section) | What it
means for you. Cover money, ownership, exit, renewal, liability, restrictions,
and disputes. Skip rows that don't apply.

**Red flags, ranked** (High / Medium / Low): one sentence each on why it
matters in practice.

**What to push back on**: for each item, the replacement wording the user
could propose, marked as a proposal for their attorney to confirm. Keep asks
realistic; a founder who pushes back on everything often gets nothing.

**What's missing**: terms the user would expect that aren't there.

**Don't sign without an attorney**: the specific items, plus the questions to
ask about each.

**Dates to put on your calendar**: signing deadline, payment dates, renewal
and cancel-by dates, notice periods.

**Where I assumed**: every assumption, and what changes if it's wrong.

Close by suggesting the user take the red flags and attorney questions to a
lawyer, and offer to turn them into a one-page brief (the
attorney-prep-packet skill does this, if installed).
