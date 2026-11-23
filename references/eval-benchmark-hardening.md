# Eval and Benchmark Hardening (Runtime Summary)

Use this reference only when the repository contains eval, benchmark, fixture,
or quality-gate runners and the task touches them. It is a thin runtime
checklist; maintainer detail lives in repository docs.

## Checklist

- **Record effective behavior:** machine-readable artifacts should capture
  configured backend/model and effective backend/model/fallback reason when
  fallbacks, retries, skips, or generated assertions are possible.
- **Keep assertions behavior-specific:** prefer diagnostic assertion groups that
  allow wording variation but require intended behavior; avoid generic phrases
  that almost any answer satisfies.
- **Use TDD for runner/eval changes:** add/tighten failing test, confirm intended
  failure, change minimally, rerun focused test, then rerun project-native full
  gates.
- **Validate schema changes:** when output schema changes, update validators and
  negative-path tests so malformed assertion groups produce actionable errors.
- **Sync payload boundaries:** if runtime payload changed, synchronize mirrors
  only through project-approved commands.

Detailed maintainer guidance: `docs/eval-benchmark-hardening.md` in the source
repository.
