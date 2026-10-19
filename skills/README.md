# Skills

Skill **source packages** live here, as one ZIP per Skill: `skills/<dir>/<skill-id>.zip`. Expanded Skill folders are never committed here. The Glean-readable folder is generated into `projections/glean/<skill-id>/` for approved Skills only.

| Directory | Contents |
| --- | --- |
| `claude/` | Claude-specific source ZIPs (stage two; empty) |
| `glean/` | Glean-specific source ZIPs (empty so far) |
| `shared/` | Content common to both platforms, including the baseline Glean exports below |

Use the Skill's own name (for example `ahead-skill-package-builder`) as its identifier: lowercase letters, digits and hyphens, matching `name:` in `SKILL.md`. Keep everything the Skill needs inside its ZIP. Use `shared/` when one source serves both platforms, and a platform directory when it differs. The CI gate rejects anything else (loose `SKILL.md`, ZIPs elsewhere, symlinks).

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

**Implemented, not yet confirmed in Glean:** the ZIP stays canonical and is materialized into `projections/glean/<skill-id>/` by `tools/skillpkg.py project`. See [Package philosophy](../README.md#package-philosophy) and the [Validation matrix](../README.md#validation-matrix).

New or changed Skills are submitted by pull request and audited by Skills Auditor on that PR (full audit for new, delta/regression audit for updates); see [CONTRIBUTING](../CONTRIBUTING.md). The expected first set is listed under [Initial Landing Set](../README.md#initial-landing-set).
