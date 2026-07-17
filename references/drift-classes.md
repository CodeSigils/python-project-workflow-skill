# Drift Classes and Remediation

This document describes the two distinct drift classes that affect skill repositories,
their causes, detection strategies, and remediation procedures. Understanding the
difference is critical because they require fundamentally different fixes.

---

## Two Drift Classes

| Class | Name | What Drifts | Root Cause | Detection | Fix |
|-------|------|-------------|------------|-----------|-----|
| **A** | **Payload drift** | Mirrored payload references differ from their canonical root sources, an undeclared payload entry appears, or a canonical/runtime entry is a symlink instead of a regular file | Human edited a canonical reference but forgot to run sync, edited a mirrored reference directly, left an orphan, or introduced a link across the shipping boundary | Payload sync check (`sync-payload.sh --ci`) fails | Run `bash scripts/sync-payload.sh` to synchronize declared mirrors and remove payload-side links/orphans; replace canonical source links manually |
| **B** | **Mirror staleness** | Installed copy predates a restructuring | Agent loads a static copy that does not auto-update | `diff -rq <repo>/skills/<name>/ <installed>/skills/<name>/` shows mismatch | Re-install from source or use a client-supported live source directory |

---

## Class A: Payload Drift

### Mechanism

```
Canonical references           Runtime payload
references/                    skills/python-project-workflow/
├── a.md ─────────────────────▶├── SKILL.md  (authored in place)
└── b.md ─────────────────────▶└── references/
                                  ├── a.md  (mirrored)
                                  └── b.md  (mirrored)
```

The payload directory (`skills/python-project-workflow/`) has mixed ownership.
Its `SKILL.md` is authored in place. Root `references/*.md` files are canonical
sources mirrored into the payload by `scripts/sync-payload.sh`. The script reads
`scripts/payload-manifest.json` for mirrored membership and treats `SKILL.md` as
an explicitly allowed authored-in-place file. No scripts currently ship.

### Common Causes

1. Edited a canonical root reference but didn't run the sync script
2. Edited a mirrored reference under `skills/python-project-workflow/references/` directly
3. Added a new source type without updating the manifest or sync policy
4. Renamed/deleted a source file but the old copy remains in payload
5. CI payload sync check was disabled or bypassed
6. Replaced a canonical source or payload entry with a symlink

### Detection

- **CI gate**: `bash scripts/sync-payload.sh --ci` exits 1 on any drift
- **Local check**: Run the same command locally before committing
- **Manifest validation**: the script requires regular canonical source files and flags payload symlinks and orphans

### Remediation

```bash
# Regenerate payload from source (normal mode)
bash scripts/sync-payload.sh

# Verify clean
bash scripts/sync-payload.sh --ci  # should print "Payload in sync" and exit 0
```

### Prevention

- The `--ci` mode in CI makes drift a blocking failure
- Path-restricted CI triggers run the gate for payload, canonical reference, maintenance-script, workflow, and key repository-documentation changes
- The manifest declares mirrored members; the sync script also records the authored-in-place `SKILL.md` exception

---

## Class B: Mirror Staleness

### Mechanism

```
Repo (canonical)                    Agent runtime (installed copy)
├── skills/                         ├── skills/
│   └── python-project-workflow/        └── python-project-workflow/
│       ├── SKILL.md (v2)                 ├── SKILL.md (v1)  ← STALE
│       └── references/                   └── references/
│           ├── a.md                      │   ├── a.md
│           ├── b.md (NEW)                │   └── (missing b.md)
│           └── c.md (REMOVED)            │       (c.md still present)
```

An installed copy in an agent's configured skill directory is a **static
snapshot** taken at install time. It has no connection to the repository after
installation.

### Common Causes

1. Skill was installed through a client installer or manual copy, then the repo evolved
2. Repository was restructured (files added/removed/renamed in `skills/<name>/`)
3. Reference files were added to the payload but the installed copy wasn't refreshed
4. Using a pinned/versioned install that doesn't track main branch

### Detection

```bash
# Compare repo payload vs installed copy
diff -rq /path/to/repo/skills/python-project-workflow/ /path/to/installed-skills/python-project-workflow/
```

Any output indicates mirror staleness. Treat this as a **blocking review finding** —
the agent is loading a different version of the skill than what the repo contains.

### Remediation

**Option 1: Re-install from the original source** (for end users)

Use the current install mechanism documented by the active client. Confirm the
source repository and inspect the refreshed payload before enabling it.

**Option 2: Re-copy from repo** (for maintainers)
```bash
cp -r /path/to/repo/skills/python-project-workflow/ /path/to/installed-skills/
```

**Option 3: Use a client-supported live source directory for development**

When the client supports external skill directories or directory links, point it
at `/path/to/python-project-workflow/skills` instead of maintaining a copy.

This eliminates the copy entirely — the agent loads directly from the repo.
Every commit is immediately reflected. **This is the single most effective
prevention for mirror staleness.**

---

## Comparison Summary

| Aspect | Class A: Payload Drift | Class B: Mirror Staleness |
|--------|------------------------|---------------------------|
| **What diverges** | Source ↔ Payload (both in repo) | Repo payload ↔ Agent installed copy |
| **Who observes** | CI / maintainer running sync | Agent at runtime / reviewer comparing |
| **Fix location** | Run sync script in repo | Re-install or use `external_dirs` |
| **Prevention** | CI gate on relevant main-branch and pull-request changes | Live source directory (dev) or re-install (prod) |
| **Risk if ignored** | Distributed payload contains stale references | Agent behaves differently than repo source |

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it's wrong | Correct approach |
|--------------|----------------|------------------|
| Editing mirrored files under `skills/python-project-workflow/references/` | Changes are overwritten by the next sync | Edit the corresponding root `references/` source, then run sync |
| Looking for a root `SKILL.md` | No such canonical file exists in this repository | Edit `skills/python-project-workflow/SKILL.md` in place |
| Adding files to payload without manifest entry | Creates orphans that CI will flag | Add to `scripts/payload-manifest.json` first |
| Committing a mirrored reference change without its root source | Creates reference drift | Keep canonical and mirrored reference content identical through the sync command |
| Installing skill once and never updating | Mirror staleness guaranteed | Use a live source directory for development; schedule re-installs for production |
| Linking individual files instead of the skill directory | Fragile; breaks on restructure | Link or configure the complete `skills/` directory when the client supports it |
| Committing symlinks inside the canonical or runtime payload trees | Can escape the shipping boundary or become broken after copying only the payload | Keep every shipped and canonical reference entry as a regular file; use client-level directory configuration only outside the payload |

---

## Verification Checklist

Before marking a skill repo change as complete:

- [ ] Edited `skills/python-project-workflow/SKILL.md` in place or changed canonical root `references/` as appropriate
- [ ] `bash scripts/sync-payload.sh` runs cleanly
- [ ] `bash scripts/sync-payload.sh --ci` exits 0
- [ ] If developing locally: using a client-supported live source directory (no mirror to go stale)
- [ ] If testing installed copy: verified `diff -rq` shows no differences
- [ ] Repository CI passes, including the payload drift gate
- [ ] Installed-copy staleness was checked separately when an installed copy is in scope
