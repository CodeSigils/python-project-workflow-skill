# Release checklist

Use this checklist for tagged releases. Replace `X.Y.Z` with the intended
semantic version and do not publish until the branch is green.

1. Confirm the worktree and branch are the intended release source.
2. Review `docs/portability-contract.md`. Runtime claims must match recorded
   evidence; untested clients remain `candidate`.
3. Update `CITATION.cff` to `X.Y.Z` and review user-facing documentation.
4. Run every command in the README's **Verify** section. Run live behavioral
   evaluation only for clients available to the maintainer, and retain redacted
   summaries outside the repository until the results are recorded.
5. Commit the release preparation, then create an annotated tag:

   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   ```

6. Push the branch and tag, watch the GitHub Actions run, and create the GitHub
   release only after all required jobs pass.
7. Verify the published archive contains `skills/python-project-workflow/` and
   that the release notes distinguish structural portability from runtime
   verification.

Windows runtime verification is currently out of scope. Do not infer Windows
support from Linux or macOS results.
