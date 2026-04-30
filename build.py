import os
import platform
import shutil
import subprocess

APP_NAME = "dashboard"
ENTRY_FILE = "desktop.py"

FOLDERS = ["src", "data", "models", "config"]
FILES = ["dashboard_app.py", "db.sqlite3"]

def clean():
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists(f"{APP_NAME}.spec"):
        os.remove(f"{APP_NAME}.spec")

def build():
    system = platform.system().lower()

    if system != "darwin":
        print("Run this on macOS for .app build.")
        return

    # macOS build
    subprocess.run([
        "pyinstaller",
        "--windowed",
        "--name", APP_NAME,
        "--noconfirm",
        ENTRY_FILE
    ])

    # place resources into .app
    res_path = f"dist/{APP_NAME}.app/Contents/Resources/"
    os.makedirs(res_path, exist_ok=True)

    for f in FILES:
        shutil.copy(f, res_path)

    for folder in FOLDERS:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(res_path, folder), dirs_exist_ok=True)

    print("\n=== macOS Build Done ===")

if __name__ == "__main__":
    clean()
    build()
