# Drift Classes (Runtime Summary)

Use this reference when you encounter mismatches between canonical files, the
shipped payload, or an installed skill copy. Load it for routing and symptom
recognition; the maintainer procedure lives in repository docs.

## Class A: Payload Drift

- **Symptom:** Root canonical references and
  `skills/python-project-workflow/references/` differ, an undeclared payload
  entry appears, or a canonical/runtime entry becomes a symlink.
- **Risk:** The skill ships stale, missing, or boundary-unsafe content.
- **Runtime action:** Edit canonical source first (`SKILL.md` in place;
  `references/` in root), then run the project's sync/drift command if
  available (`bash scripts/sync-payload.sh` / `--ci`). Do not treat mirrored
  payload refs as canonical.
- **Escalate:** If canonical ownership or manifest policy is unclear, report it
  as a maintainer decision rather than patching mirrors ad hoc.

## Class B: Installed-Copy Staleness

- **Symptom:** An installed skill copy differs from the repository payload.
- **Risk:** The agent runs behavior different from reviewed source.
- **Runtime action:** Compare repo payload to the installed copy, then reinstall
  or point the client at a supported live source directory. Do not claim the
  repo and installed copy are equivalent without checking.
- **Escalate:** Record the compared paths and the reinstall/source-directory
  action taken or needed.

Detailed maintainer procedure: `docs/drift-classes.md` in the source repository.
