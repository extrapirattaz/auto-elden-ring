# Optional complete source history

The prepared auto-elden-ring-history.bundle contains one exact source commit and
tag for each of the eleven public versions: 1.0.1, 2.0.0, 2.0.1, 2.0.2, 3.0.0,
4.0.0, 4.0.1, 5.0.0, 6.0.0, 6.0.1 and 6.1.0. Main contains 6.1.0. Each tracked Git blob
is checked against the corresponding archive bytes. No EXEs, profiles or saves
are committed. Git commit authors identify the archive import, not original
authorship; import timestamps describe when this history was assembled.

This is the fastest way to publish all source versions correctly to a **new,
empty repository**. No remote publication has been performed. If you already
pushed an initial README or other commits, use the manual source-import method
in GITHUB_PUBLISHING.md rather than overwriting that remote history.

1. Create your public auto-elden-ring repository with no initial files.
2. Before pushing historical tags, disable Actions in that repository's settings
   (Actions → General → Actions permissions → Disable actions → Save).
   Original historical workflows may otherwise run when their tags are pushed.
3. Open PowerShell in the directory containing the supplied bundle. Choose a
   new local destination folder and run these commands yourself:

```powershell
git clone .\auto-elden-ring-history.bundle .\auto-elden-ring-upload
Set-Location .\auto-elden-ring-upload
git remote set-url origin https://github.com/YOUR_ACCOUNT/auto-elden-ring.git
git push -u origin main
git push origin --tags
```

Replace YOUR_ACCOUNT with your own GitHub account name. Authentication is handled
by Git/GitHub. These commands are instructions for your manual publication; the
local preparation tool never runs them. Existing Windows Git credentials are not
read into the source, reports or bundle.

4. Create Releases on the matching tags, following GITHUB_PUBLISHING.md. Upload
   the matching EXE, both ZIPs, manifest, hashes and verification reports for
   each version. Only 6.1.0 should be marked latest.
5. Keep Actions disabled unless you deliberately want the optional build jobs.
   The current 6.1.0 workflow is manual and does not create GitHub Releases.

To regenerate a bundle locally after preparing all release folders:

```powershell
python scripts/prepare_github_history.py --destination .build/github-history-repository --bundle publishing/auto-elden-ring-history.bundle --report publishing/HISTORY_VERIFICATION.json
```

Both output paths must be new. The helper has no remote or push operation and
refuses to overwrite an existing repository/bundle. GitHub Desktop can open the
cloned local repository if you prefer its UI for later commits.

[GitHub's Actions permissions documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
and [tagging with GitHub Desktop](https://docs.github.com/en/desktop/managing-commits/managing-tags-in-github-desktop)
describe the corresponding controls.
