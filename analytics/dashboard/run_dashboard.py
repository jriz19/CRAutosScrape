#!/usr/bin/env python3
"""
Dashboard Runner Script
Launch the Streamlit dashboard for vehicle market analysis
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit dashboard"""
    dashboard_path = Path(__file__).parent / "streamlit_app.py"
    
    print("Launching Costa Rica Vehicle Market Intelligence Dashboard...")
    print("=" * 60)
    print("Dashboard will open in your default web browser")
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()