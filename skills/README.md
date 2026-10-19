# Skills

Platform Skills live here, one directory (or package) per Skill.

| Directory | Contents |
| --- | --- |
| `claude/` | Skills published to Claude (stage two) |
| `glean/` | Skills published to Glean |
| `shared/` | Content common to both platforms, including the baseline Glean exports below |

Use a Skill's own name (for example `ahead-skill-package-builder`) as its identifier, and keep everything the Skill needs inside its package or directory. Place a Skill under `shared/` when one source serves both platforms, and under a platform directory when it differs by platform.

## Baseline Glean exports

The six organization-wide Skill export ZIPs from Glean are staged on the pilot pull request; their hashes are listed for the baseline in that PR. They are source artifacts: **do not extract, rewrite, repackage, rename, or modify them.** They must remain byte-for-byte unchanged.

| Package | Status |
| --- | --- |
| `ahead-daily-digest.zip` | Baseline export, not yet approved as Platform Skill |
| `ahead-meeting-prep-and-notes.zip` | Baseline export, not yet approved as Platform Skill |
| `ahead-skill-package-builder.zip` | Baseline export, not yet approved as Platform Skill |
| `ahead-weekly-recap.zip` | Baseline export, not yet approved as Platform Skill |
| `outlook-event-creation.zip` | Baseline export, not yet approved as Platform Skill |
| `story-writing-for-presentations.zip` | Baseline export, not yet approved as Platform Skill |

**OPEN:** whether ZIP stays the canonical Git representation or is materialized into an expanded directory is pending validation with Glean. See [Package philosophy](../README.md#package-philosophy) and the [Validation matrix](../README.md#validation-matrix).

New or changed Skills are audited in Skills Auditor first (full audit for new, delta/regression audit for updates). The expected first set is listed under [Initial Landing Set](../README.md#initial-landing-set).
