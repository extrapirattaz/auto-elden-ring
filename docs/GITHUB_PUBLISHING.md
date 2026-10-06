# GitHub publishing checklist

## Repository form

Create **one repository** on your own account, or reuse the one you created:

- Repository name: **auto-elden-ring**
- Display/product name: **Auto Elden Ring**
- Visibility: **Public**
- Description (paste exactly):

> All-in-one Elden Ring rune and weapon upgrade calculator, build planner, save viewer and farming companion for Windows.

Start with an empty repository: the prepared source already has README.md and
.gitignore. The choice of a project-wide licence remains yours; third-party
notices are included under assets/licenses and assets/fonts. Suggested topics:
elden-ring, rune-calculator, weapon-upgrades, python, windows, build-planner.
Use the Code tab for source and Releases for downloads. A GitHub Project board
and GitHub Packages are optional and unnecessary for distributing this app.

## Put the current source in Code

Extract auto-elden-ring-6.1.0-source.zip. Copy the **contents** of its
auto-elden-ring-6.1.0 folder to the repository root, so README.md, main.py,
auto_elden_ring/, assets/, tests/, scripts/ and docs/ are immediately visible.
Do not put the source ZIP itself in Code. Use GitHub Desktop to clone your empty
repository, copy these files into the clone, commit as `Import Auto Elden Ring
6.1.0`, then push. The source contains thousands of small offline icons, so this
avoids the browser's 100-file upload batches. The web alternative is Code →
Add file → Upload files for each batch.

Do not copy the development workspace wholesale. In particular, .venv/, .build/,
archive/, releases/, user profiles, actual .sl2/.co2 files, personal music and
custom screenshots stay outside Code. All required runtime assets are already
inside the verified source ZIP.

## Preserve source history for every public version

For a new empty repository, the optional prepared history bundle imports exact
snapshots with one commit/tag per public version and main at 6.1.0. Its author is
explicitly an archive-import identity, not a claim about original authorship.
See the included publishing/HISTORY_INSTRUCTIONS.md for the local clone and push
commands. Nothing is uploaded by preparing this bundle.

If importing manually instead, import each source ZIP in this order:
1.0.1, 2.0.0, 2.0.1, 2.0.2, 3.0.0, 4.0.0, 4.0.1, 5.0.0, 6.0.0, 6.0.1, 6.1.0.
For each snapshot replace the preceding source files completely, keep .git,
commit `Import Auto Elden Ring VERSION`, and create tag `vVERSION` on that commit.
GitHub Desktop supports History → right-click commit → Create Tag.
Disable GitHub Actions while importing historical snapshots: their original
workflows may publish automatically on v* tags. The current workflow is manual
and only builds/downloads artifacts; it does not publish releases.

If you upload only the current Code now, publish the current release first and
add historical releases after importing their source commits/tags. Do not label
the 6.1.0 commit as v2.0.0: GitHub's automatic source archive would then be wrong.

## Create Releases

Open the repository's Releases page and create a draft for each version. Select
its existing matching vVERSION tag. Enter the title from the table below and
paste the entire matching docs/releases/VERSION.md file into release notes.
Attach the individual files listed below from releases/VERSION, then publish.
The source ZIP is platform-independent Python; the Windows ZIP/EXE are x64.
The attached source ZIP is the exact build snapshot; GitHub also creates source
downloads automatically from the tag's source commit.

Historical releases: leave **Set as the latest release** off. Current 6.1.0:
turn it on. Leave **Set as a pre-release** off for this release plan; use drafts
until all attachments are present. Historical versions retain their historical
behavior and bugs; their existing evidence is audited, not claimed as newly run.

| Version | Tag | Release title | Status | Notes to paste |
| --- | --- | --- | --- | --- |
| 1.0.1 | v1.0.1 | Auto Elden Ring 1.0.1 | Historical release | [Notes](releases/1.0.1.md) |
| 2.0.0 | v2.0.0 | Auto Elden Ring 2.0.0 | Historical release | [Notes](releases/2.0.0.md) |
| 2.0.1 | v2.0.1 | Auto Elden Ring 2.0.1 | Historical release | [Notes](releases/2.0.1.md) |
| 2.0.2 | v2.0.2 | Auto Elden Ring 2.0.2 | Historical release | [Notes](releases/2.0.2.md) |
| 3.0.0 | v3.0.0 | Auto Elden Ring 3.0.0 | Historical release | [Notes](releases/3.0.0.md) |
| 4.0.0 | v4.0.0 | Auto Elden Ring 4.0.0 | Historical release | [Notes](releases/4.0.0.md) |
| 4.0.1 | v4.0.1 | Auto Elden Ring 4.0.1 | Historical release | [Notes](releases/4.0.1.md) |
| 5.0.0 | v5.0.0 | Auto Elden Ring 5.0.0 | Historical release | [Notes](releases/5.0.0.md) |
| 6.0.0 | v6.0.0 | Auto Elden Ring 6.0.0 | Historical release | [Notes](releases/6.0.0.md) |
| 6.0.1 | v6.0.1 | Auto Elden Ring 6.0.1 | Historical release | [Notes](releases/6.0.1.md) |
| 6.1.0 | v6.1.0 | Auto Elden Ring 6.1.0 | Latest release | [Notes](releases/6.1.0.md) |

Do not upload the original 1.0.0. Its personal example-path comment has been
removed in the rebuilt 1.0.1 edition; the original is retained only in the ignored
local archive. All other historical source/binary pairs are preserved as built.

## Exact attachments per version

Each list refers to files **inside** the corresponding local release folder.
Upload the files rather than dragging the release folder itself.

### 1.0.1 — releases/1.0.1

- Auto-Elden-Ring-1.0.1-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_EXE.json
- auto-elden-ring-1.0.1-source.zip
- auto-elden-ring-1.0.1-windows-x64.zip

### 2.0.0 — releases/2.0.0

- Auto-Elden-Ring-2.0.0-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_EXE.json
- VERIFICATION_LOCAL.json
- VERIFICATION_UI.json
- auto-elden-ring-2.0.0-source.zip
- auto-elden-ring-2.0.0-windows-x64.zip

### 2.0.1 — releases/2.0.1

- Auto-Elden-Ring-2.0.1-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- TEST_RESULTS.txt
- VERIFICATION_EXE.json
- VERIFICATION_LOCAL.json
- VERIFICATION_UI.json
- auto-elden-ring-2.0.1-source.zip
- auto-elden-ring-2.0.1-windows-x64.zip

### 2.0.2 — releases/2.0.2

- Auto-Elden-Ring-2.0.2-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- TEST_RESULTS.txt
- VERIFICATION_EXE.json
- VERIFICATION_LOCAL.json
- VERIFICATION_UI.json
- auto-elden-ring-2.0.2-source.zip
- auto-elden-ring-2.0.2-windows-x64.zip

### 3.0.0 — releases/3.0.0

- Auto-Elden-Ring-3.0.0-win-x64.exe
- PERFORMANCE.json
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_ARTIFACTS.json
- VERIFICATION_EXE.json
- VERIFICATION_SOURCE.json
- VERIFICATION_SOURCE_UI.json
- VERIFICATION_TESTS.json
- VERIFICATION_UI.json
- auto-elden-ring-3.0.0-source.zip
- auto-elden-ring-3.0.0-windows-x64.zip

### 4.0.0 — releases/4.0.0

- Auto-Elden-Ring-4.0.0-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_EXE.json
- VERIFICATION_NATIVE.json
- VERIFICATION_SAVE.json
- VERIFICATION_UI.json
- auto-elden-ring-4.0.0-source.zip
- auto-elden-ring-4.0.0-windows-x64.zip

### 4.0.1 — releases/4.0.1

- Auto-Elden-Ring-4.0.1-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_EXE.json
- VERIFICATION_NATIVE.json
- VERIFICATION_SAVE.json
- VERIFICATION_UI.json
- auto-elden-ring-4.0.1-source.zip
- auto-elden-ring-4.0.1-windows-x64.zip

### 5.0.0 — releases/5.0.0

- Auto-Elden-Ring-5.0.0-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_AUDIO.json
- VERIFICATION_EXE.json
- VERIFICATION_NATIVE.json
- VERIFICATION_SAVE.json
- VERIFICATION_UI.json
- auto-elden-ring-5.0.0-source.zip
- auto-elden-ring-5.0.0-windows-x64.zip

### 6.0.0 — releases/6.0.0

- Auto-Elden-Ring-6.0.0-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_AUDIO.json
- VERIFICATION_EXE.json
- VERIFICATION_NATIVE.json
- VERIFICATION_SAVE.json
- VERIFICATION_UI.json
- auto-elden-ring-6.0.0-source.zip
- auto-elden-ring-6.0.0-windows-x64.zip

### 6.0.1 — releases/6.0.1

- Auto-Elden-Ring-6.0.1-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_AUDIO.json
- VERIFICATION_EXE.json
- VERIFICATION_NATIVE.json
- VERIFICATION_SAVE.json
- VERIFICATION_UI.json
- auto-elden-ring-6.0.1-source.zip
- auto-elden-ring-6.0.1-windows-x64.zip

### 6.1.0 — releases/6.1.0

- Auto-Elden-Ring-6.1.0-win-x64.exe
- RELEASE_MANIFEST.json
- SHA256SUMS.txt
- VERIFICATION_AUDIO.json
- VERIFICATION_EXE.json
- VERIFICATION_NATIVE.json
- VERIFICATION_RESCAN.json
- VERIFICATION_SAVE.json
- VERIFICATION_UI.json
- auto-elden-ring-6.1.0-source.zip
- auto-elden-ring-6.1.0-windows-x64.zip

## Verified GitHub references

- [Create a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
- [Upload source files and browser limits](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [Create release drafts and attach binaries](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Create tags on source commits with GitHub Desktop](https://docs.github.com/en/desktop/managing-commits/managing-tags-in-github-desktop)

These instructions prepare manual publication. No repository, release, commit or
push has been created on your GitHub account by this work.
