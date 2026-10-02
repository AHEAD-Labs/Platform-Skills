# Contributing

This is an internal team workflow. Skills are reviewed in Skills Marketplace before they reach this repository; this guide covers changes to the approved source.

1. **Create a branch** from `main`, for example `update/<skill-name>`.
2. **Add or update the skill** under [`skills/`](skills/README.md).
3. **Open a pull request** into `main`. Use the pull request template and describe what changed and why (for example, which UAT feedback it addresses).
4. **Another teammate reviews the exact change.** The author does not approve their own pull request.
5. **Merge only after approval.**
6. **The merged state is the approved version.**
7. **Publish separately.** Publishing to Claude and Glean is a manual step done after merge, not part of the pull request.

Do not commit credentials, tokens, API keys, or client data.
