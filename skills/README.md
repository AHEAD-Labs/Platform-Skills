# Skills

Each skill is **one folder**: `skills/<id>/`, with a `SKILL.md` at its root. That is the only rule for where a skill goes.

- `<id>` uses lowercase letters, digits and hyphens, and equals `name` in the frontmatter of `SKILL.md`.
- Keep everything the skill needs inside its folder (reference files, data, templates).
- Platform is a frontmatter field (`ahead-platform`), not a folder. Do not sort skills into platform subfolders.
- To update a skill, edit its folder and bump `version`. Git history is the version history.
- Do not commit ZIP files. A ZIP is an export format, not the format stored here. To start from a Glean export, unzip it into the skill's folder.
- Only the file types on the allowed list, under the size limits, are accepted. The check that fails tells you which file and why.
- No credentials, tokens, API keys or client data. This repository is public.

Required and recommended frontmatter fields are listed in [standards/README.md](../standards/README.md). How to open a pull request, and who reviews it, is in [CONTRIBUTING.md](../CONTRIBUTING.md).
