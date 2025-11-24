import os
import subprocess
import time
import sys

def kill_port_8000():
    """Kill all processes using port 8000"""
    print("=" * 60)
    print("Stopping old backend processes...")
    print("=" * 60)

    try:
        # Get PIDs using port 8000
        result = subprocess.run(
            'netstat -ano | findstr :8000 | findstr LISTENING',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            lines = result.stdout.strip().split('\n')
            pids = set()
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    pids.add(pid)

            for pid in pids:
                print(f"Killing process {pid}...")
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)

        print("Waiting for port to be released...")
        time.sleep(3)
    except Exception as e:
        print(f"Error killing processes: {e}")

def start_backend():
    """Start the backend"""
    print("\n" + "=" * 60)
    print("Starting new backend...")
    print("=" * 60 + "\n")

    # Start backend
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    kill_port_8000()
    start_backend()
