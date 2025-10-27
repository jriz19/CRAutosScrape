#!/usr/bin/env python3
"""
Reseller Dashboard Launcher
Launch the business-focused dashboard for car resellers
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the reseller dashboard"""
    dashboard_path = Path(__file__).parent / "reseller_dashboard.py"
    
    print("Launching Car Reseller Business Intelligence Dashboard...")
    print("=" * 60)
    print("Business-focused dashboard for car dealers and resellers")
    print("Features: Profit calculator, market opportunities, pricing insights")
    print("Dashboard will open at: http://localhost:8502")
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    
    try:
        # Launch Streamlit on different port to avoid conflicts
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8502",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nReseller dashboard stopped by user")
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()