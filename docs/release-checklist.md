# Release checklist

A release is a tag. The tag is the trigger, and `workflows/release.yml` enacts
it. Replace `X.Y.Z` with the intended semantic version and do not publish until
the branch is green.

## When to release

Release when one of these is true, and not otherwise:

- **A published contract changed** — the skill's inputs, outputs, profile
  schema, dimension catalog, or required agent capabilities. Bump the minor
  version, or the major version when a consumer's existing profile or recorded
  transcript stops validating.
- **A defect would mislead an agent acting on the skill's guidance.** Bump the
  patch version.
- **The recorded portability evidence changed** — a client became verified, or
  a candidate regressed. Bump the patch version.

Do not release for changes confined to this repository's own maintainer
tooling: CI, the scripts under `scripts/` and `.github/scripts/`, or
documentation outside the shipped payload. Those change no agent's behaviour,
so a tag would claim otherwise. Such maintenance accumulates until the next
contract change carries it.

There is no calendar and nobody is scheduled. A release exists when a
maintainer judges one of the conditions above is true and says so. If nobody
judges that, no release happens, and that is a valid state rather than a
failure — `check-version-consistency.py` reports the local version against the
latest tag on every run, so the gap is visible without being an error.

## Procedure

1. Confirm the worktree and branch are the intended release source.
2. Review `docs/portability-contract.md`. Runtime claims must match recorded
   evidence; untested clients remain `candidate`.
3. Update `CITATION.cff` to `X.Y.Z`. This may land before the tag: when the
   local version is ahead of the latest tag the check reports
   `RELEASE PENDING` and passes, precisely so this step and the tag can be
   separate commits. Only a local version *behind* the tag is an error.
4. Run every command in the README's **Verify** section. Run live behavioral
   evaluation only for clients available to the maintainer, and retain redacted
   summaries outside the repository until the results are recorded.
5. Commit the release preparation, then create an annotated tag:

   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   ```

6. Push the branch and the tag together:

   ```bash
   git push origin main vX.Y.Z
   ```

   The tag push starts `workflows/release.yml`, which creates the GitHub
   release with generated notes. **Do not create the release by hand.** A
   manual release and a workflow release are indistinguishable to whoever reads
   the repository next, so the history stops recording which path produced a
   release — which is how `v0.1.0` and `v0.2.0` came to exist without the
   workflow that claims to create them ever having run.
7. Watch the `release` job. If it fails, the tag is already public: delete the
   tag, fix the cause, and re-tag. Do not fall back to creating the release by
   hand, because that is the state this procedure exists to prevent.
8. Confirm the published archive contains `skills/python-project-workflow/`
   and that the release notes distinguish structural portability from runtime
   verification. The scheduled `release-integrity` job checks that the latest
   tag has a published release; it is a backstop, not a substitute for looking.

Windows runtime verification is currently out of scope. Do not infer Windows
support from Linux or macOS results.
