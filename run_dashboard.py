import subprocess
import webbrowser
import time

# start streamlit
process = subprocess.Popen(
    ["streamlit", "run", "dashboard_app.py"]
)

# wait for server to start
time.sleep(3)

# open browser
webbrowser.open("http://localhost:8501")

process.wait()
