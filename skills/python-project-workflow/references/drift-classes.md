# Drift Classes and Remediation

This document describes the two distinct drift classes that affect skill repositories,
their causes, detection strategies, and remediation procedures. Understanding the
difference is critical because they require fundamentally different fixes.

---

## Two Drift Classes

| Class | Name | What Drifts | Root Cause | Detection | Fix |
|-------|------|-------------|------------|-----------|-----|
| **A** | **Payload drift** | Derived copy (payload) out of sync with canonical source | Human edited source but forgot to run sync script; CI gate missing or bypassed | Payload sync check (`sync-payload.sh --ci`) fails | Run `bash scripts/sync-payload.sh` to regenerate payload from manifest |
| **B** | **Mirror staleness** | Installed copy predates a restructuring | Agent loads a static copy that does not auto-update | `diff -rq <repo>/skills/<name>/ <installed>/skills/<name>/` shows mismatch | Re-install from source or use a client-supported live source directory |

---

## Class A: Payload Drift

### Mechanism

```
Source of truth (repo)          Payload (shipped to hub)
├── SKILL.md                    ├── SKILL.md
├── references/                 ├── references/
│   ├── a.md                    │   ├── a.md
│   └── b.md                    │   └── b.md
└── scripts/                    └── scripts/
    └── check.py                    └── check.py
```

The payload directory (`skills/python-project-workflow/`) is a **derived artifact**.
It is generated from the canonical source by `scripts/sync-payload.sh` reading
`scripts/payload-manifest.json`.

### Common Causes

1. Edited `SKILL.md` or a reference file but didn't run the sync script
2. Added a new reference file but didn't update the manifest (when using explicit array)
3. Renamed/deleted a source file but the old copy remains in payload
4. CI payload sync check was disabled or bypassed

### Detection

- **CI gate**: `bash scripts/sync-payload.sh --ci` exits 1 on any drift
- **Local check**: Run the same command locally before committing
- **Manifest validation**: Script also verifies every manifest entry exists at source

### Remediation

```bash
# Regenerate payload from source (normal mode)
bash scripts/sync-payload.sh

# Verify clean
bash scripts/sync-payload.sh --ci  # should print "Payload in sync" and exit 0
```

### Prevention

- The `--ci` mode in CI makes drift a blocking failure
- Path-restricted CI triggers mean only changes to shipping-surface files run the gate
- Payload manifest (`scripts/payload-manifest.json`) is the single source of truth for what ships

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
| **Prevention** | CI gate on every push | Live source directory (dev) or re-install (prod) |
| **Risk if ignored** | Hub publishes stale skill | Agent behaves differently than repo source |

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it's wrong | Correct approach |
|--------------|----------------|------------------|
| Editing files directly in `skills/python-project-workflow/` | Bypasses manifest; changes lost on next sync | Edit source (root `SKILL.md`, root `references/`, `scripts/`), then run sync |
| Adding files to payload without manifest entry | Creates orphans that CI will flag | Add to `scripts/payload-manifest.json` first |
| Committing payload changes without source changes | Drift by definition | Source is truth; payload is derived |
| Installing skill once and never updating | Mirror staleness guaranteed | Use a live source directory for development; schedule re-installs for production |
| Linking individual files instead of the skill directory | Fragile; breaks on restructure | Link or configure the complete `skills/` directory when the client supports it |

---

## Verification Checklist

Before marking a skill repo change as complete:

- [ ] Source files edited (root `SKILL.md`, `references/`, `scripts/`)
- [ ] `bash scripts/sync-payload.sh` runs cleanly
- [ ] `bash scripts/sync-payload.sh --ci` exits 0
- [ ] If developing locally: using a client-supported live source directory (no mirror to go stale)
- [ ] If testing installed copy: verified `diff -rq` shows no differences
- [ ] CI passes (includes both drift gates)
