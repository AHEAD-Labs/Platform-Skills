# ahead-deliverable-hub

Builds AHEAD deliverable hubs: branded, self-contained HTML websites that hold an engagement's deliverables. Start from the Phase 1 discovery template, the Phase 2 target design template, or build a custom hub from an SOW. Also fills, checks and hands over an existing hub.

## Status

| Item | Value |
|---|---|
| Version | 1.3.5 |
| Publication status | Approved for enterprise-wide distribution (2026-10-28). |
| Owner | ethan.cunningham@ahead.com |
| Team | AI HIVE |
| Platform | Claude and Glean. |
| Sensitivity | Internal. The skill contains no client content; the hubs it produces are client-facing. |

Approved for enterprise-wide distribution: Michal Lubas approved AHEAD distribution (via Teams, 2026-10-27) and the AHEAD eTech team (Enterprise GPT team), via Grace, approved after a review call (2026-10-28).

## Why a hub

A deliverable hub puts an engagement's whole package in one file instead of a folder of separate documents. For the client that means one place to open, read and share, with the conclusion first and the detail one click away. For the team it means one current version everyone builds in, so there is no "which file is latest" and nothing emailed around. Because the skill builds every hub, they all carry the same look and pass the same checks. Teams use it to hand a phase over, present straight from one file, trace each claim to its evidence, and give the next phase a running start. The hub is self-contained and opens offline in any modern browser, with no access requests.

## Install

1. Zip the `ahead-deliverable-hub` folder (the folder itself at the top level of the zip).
2. In Claude, go to Customize > Skills and upload the zip.
3. To update, upload the new zip. Hubs built earlier keep working.

## Use

Ask Claude for a deliverable hub, a discovery hub, a target design package, or a hub built from an SOW. Claude asks which way in you want if you have not said, builds with `scripts/build.py`, runs `scripts/check.py`, and fills slots with `scripts/fill_slot.py`. Do not edit the HTML or the styles by hand.

## What is in the package

| Path | Purpose |
|---|---|
| `SKILL.md` | Instructions Claude follows |
| `SPEC.md` | Specification, acceptance criteria and open items |
| `references/` | Phase patterns, config schema, writing rules, collaboration steps, changelog |
| `assets/` | Presets (`discovery`, `target-design`, `blank`), styles, script, fonts, AHEAD logo |
| `scripts/` | `build.py`, `fill_slot.py`, `check.py`, `guide.py`, `selftest.py`, `hublib.py` |
| `evals/` | `evals.json` (cases and recorded results) and `run_script_evals.py` |

Python 3 standard library only. No network calls.

## Testing

```bash
python3 scripts/selftest.py              # builds every template and checks the guards
python3 evals/run_script_evals.py        # runs the script-checkable evaluation assertions
```

`evals/evals.json` holds each case with binary assertions and a result per assertion. Script-checkable assertions have recorded results from `run_script_evals.py`. The model-behavior cases (way-in question, SOW conflict, non-trigger, cross-client refusal, fixed-look explanation) are `not_run` until a person runs the prompt in a clean Claude session with the skill installed and records dated evidence.

## Known limits

- The visual check of the tabs at about 1280 px and 1440 px has not been recorded.
- The scripts have not been run against real engagement data.
- `check.py --final` finds remaining placeholders, spelling, style and names. It does not detect invented content. A principal reviews the Overview before client handover.
- Plain content (`--text`, `--md`, `--html-file`, `--image`) does not replace a table, register, heatmap, gantt or headline numbers. Use `--rows`, `--block` or `--values`, add `--append`, or use `--force` to replace on purpose.
