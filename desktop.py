import os
import sys
import subprocess
import time


def get_resource_path(filename):
    # Running inside .app
    if hasattr(sys, '_MEIPASS'):
        base = os.path.join(sys._MEIPASS)
        return os.path.join(base, filename)

    # Running locally (development mode)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def get_app_resources():
    # Running inside .app bundle
    if hasattr(sys, "_MEIPASS"):
        exe_path = os.path.dirname(sys.executable)
        resources = os.path.abspath(os.path.join(exe_path, "..", "Resources"))
        return resources

    # Running locally → use project root
    return os.path.dirname(os.path.abspath(__file__))


print("=== LAUNCHING STREAMLIT ===")

resources = get_app_resources()
dashboard_script = os.path.join(resources, "dashboard_app.py")

print("RESOURCES:", resources)
print("SCRIPT:", dashboard_script)

if not os.path.exists(dashboard_script):
    print("ERROR: dashboard_app.py NOT FOUND!")
    print("Looked in:", dashboard_script)
    sys.exit(1)

cmd = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    dashboard_script
]

print("CMD:", " ".join(cmd))
print("------------------------------------")

subprocess.Popen(cmd)
time.sleep(2)
sys.exit(0)
