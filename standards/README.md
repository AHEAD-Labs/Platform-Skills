# Standards

This repository has one layout rule and a small set of frontmatter fields. The layout rule is in [skills/README.md](../skills/README.md); the fields are below.

Guidance on how to write a good skill is not copied here, so there is only one version to keep current. Ask a maintainer where the current guidance lives.

## Frontmatter

Every skill's `SKILL.md` starts with YAML frontmatter.

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | **Yes** | The skill's id. Equals the folder name `skills/<id>/`. |
| `description` | **Yes** | What the skill does and when to use it. |
| `version` | Recommended | Bump it on every update. |
| `owner` | Recommended | Who is responsible for the skill: a team name or GitHub handle. For an assisted submission, the contributor. |
| `team` | Recommended | The owning team. |
| `ahead-platform` | Recommended | The platform or platforms the skill is for, for example Claude, Glean or both. |
| `audience` | Recommended | Who the skill is for. |
| `publication-status` | Recommended | Where the skill stands, in plain words. |
| `glean-link` | Recommended | Pointer to the skill in Glean, if it has been published there. Maintained by hand. |
| `claude-link` | Recommended | Pointer to the skill in Claude, if it has been published there. Maintained by hand. |

A missing recommended field produces a warning, not a failure.

Add a note to this folder only when this repository needs a rule of its own.
