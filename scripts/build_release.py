"""Build a version-matched source ZIP, EXE, Windows ZIP and SHA-256 manifest.

Run from Windows using the build venv. No Git operations or network publishing.
Existing releases are never overwritten. Change __version__ for a new release.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from auto_elden_ring import __version__


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    subprocess.run([str(a) for a in args],cwd=ROOT,check=True)


def main():
    if sys.platform!="win32":
        raise SystemExit("The EXE must be built on Windows x64.")
    release = ROOT/"releases"/__version__
    if release.exists():
        raise SystemExit(f"Release already exists: {release}. Increment the version instead of overwriting it.")
    run(sys.executable,"-m","unittest","discover","-s","tests","-v")
    work = ROOT/".build"/__version__
    work.mkdir(parents=True,exist_ok=True)
    name = f"Auto-Elden-Ring-{__version__}-win-x64"
    version = tuple(int(n) for n in __version__.split("."))+(0,)
    version_file = work/"windows-version.txt"
    version_file.write_text("VSVersionInfo(ffi=FixedFileInfo(filevers="+repr(version)+", prodvers="+repr(version)+
        ", mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0,0)), kids=[StringFileInfo([StringTable('040904B0', ["
        "StringStruct('CompanyName','Auto Elden Ring'),StringStruct('FileDescription','Offline rune and weapon upgrade calculator'),"
        f"StringStruct('FileVersion','{__version__}'),StringStruct('ProductName','Auto Elden Ring'),StringStruct('ProductVersion','{__version__}')"
        "])]),VarFileInfo([VarStruct('Translation',[1033,1200])])])",encoding="utf-8")
    run(sys.executable,"-m","PyInstaller","--noconfirm","--clean","--onefile","--windowed",
        "--collect-all","customtkinter",
        "--name",name,"--add-data",f"{ROOT/'elden_ring_costs.json'}{os.pathsep}.",
        "--icon",ROOT/"assets"/"app.ico","--add-data",f"{ROOT/'assets'}{os.pathsep}assets",
        "--version-file",version_file,"--distpath",work/"dist","--workpath",work/"work","--specpath",work,ROOT/"main.py")
    exe = work/"dist"/(name+".exe")
    report = work/"exe-self-test.json"
    run(exe,"--self-test","--report",report)
    ui_report=work/"exe-ui-check.json"
    run(exe,"--ui-smoke","--report",ui_report)
    sys.path.insert(0,str(ROOT/"tests"))
    from test_save_reader import fixture
    save_fixture=work/"ER0000.sl2"
    save_fixture.write_bytes(fixture())
    save_report=work/"exe-save-check.json"
    run(exe,"--save-check",save_fixture,"--report",save_report)
    save_result=json.loads(save_report.read_text(encoding="utf-8"))
    if save_result["status"]!="PASS" or save_result["app_version"]!=__version__ or save_result["ordinary_stones_total"]!=22:
        raise SystemExit("Packaged save-reader fixture check failed.")
    result = json.loads(report.read_text(encoding="utf-8"))
    if result["status"]!="PASS" or result["app_version"]!=__version__:
        raise SystemExit("Packaged executable self-check failed.")
    ui_result=json.loads(ui_report.read_text(encoding="utf-8"))
    if ui_result["status"]!="PASS" or ui_result["app_version"]!=__version__:
        raise SystemExit("Packaged GUI smoke check failed.")
    # Publish artifacts into the local release directory only after all checks.
    release.mkdir(parents=True)
    shutil.copy2(exe,release/exe.name)
    shutil.copy2(report,release/"VERIFICATION_EXE.json")
    shutil.copy2(ui_report,release/"VERIFICATION_UI.json")
    shutil.copy2(save_report,release/"VERIFICATION_SAVE.json")
    source_files = [p for p in ROOT.iterdir() if p.is_file() and p.suffix in (".py",".json",".md",".txt",".ps1",".bat")]
    source_files.append(ROOT/".gitignore")
    for directory in ("auto_elden_ring","tests","scripts","docs","assets",".github"):
        source_files.extend(p for p in (ROOT/directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    source_files = sorted(set(source_files))
    snapshot = {str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in source_files}
    source_zip = release/f"auto-elden-ring-{__version__}-source.zip"
    with zipfile.ZipFile(source_zip,"w",zipfile.ZIP_DEFLATED) as archive:
        for p in source_files:
            archive.write(p,f"auto-elden-ring-{__version__}/"+str(p.relative_to(ROOT)).replace("\\","/"))
    portable_zip = release/f"auto-elden-ring-{__version__}-windows-x64.zip"
    with zipfile.ZipFile(portable_zip,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.write(exe,exe.name)
        for p in (ROOT/"README.md",ROOT/"CHANGELOG.md"):
            archive.write(p,p.name)
        for p in sorted((ROOT/"docs").rglob("*")):
            if p.is_file():
                archive.write(p,str(p.relative_to(ROOT)).replace("\\","/"))
        archive.write(ROOT/"assets/fonts/OFL.txt","licenses/OpenDyslexic-OFL.txt")
        for p in (ROOT/"assets/licenses").glob("*.txt"):
            archive.write(p,"licenses/"+p.name)
        archive.write(report,"VERIFICATION_EXE.json")
        archive.write(ui_report,"VERIFICATION_UI.json")
        archive.write(save_report,"VERIFICATION_SAVE.json")
    manifest = {"version":__version__,"python":sys.version,"platform":"Windows x64", "game_data_sha256":sha(ROOT/"elden_ring_costs.json"),
                "build_dependencies":(ROOT/"requirements-build.txt").read_text(encoding="utf-8"),
                "source_files_sha256":snapshot,"artifacts_sha256":{p.name:sha(p) for p in (release/exe.name,source_zip,portable_zip)},
                "verification":result,"gui_verification":ui_result,"save_verification":save_result}
    (release/"RELEASE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    (release/"SHA256SUMS.txt").write_text("".join(f"{sha(p)}  {p.name}\n" for p in sorted(release.iterdir()) if p.is_file()),encoding="utf-8")
    print(f"Release ready: {release}")


if __name__=="__main__":
    main()
