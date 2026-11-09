## What changed

<!-- Which skill(s), and what changed. -->

## Why

<!-- For example, the UAT feedback this addresses, or a link to the Skills Auditor review. -->

## Type

- [ ] New Skill (full audit)
- [ ] Update to an approved Platform Skill (delta/regression audit)
- [ ] Tooling / docs / governance (no Skill content)

## Checklist

- [ ] Skill PRs: the ZIP passes `tools/skillpkg.py validate`; the Skills Auditor result (full or delta, per `plan`) is linked from the internal repo, or marked pending
- [ ] No credentials, tokens, API keys, or client data are included
- [ ] A teammate other than the author has reviewed this exact change
- [ ] Content is appropriate for a public repository (check the Skill's `sensitivity`); audit findings stay internal
- [ ] I understand that publishing to Claude/Glean is separate from merging
