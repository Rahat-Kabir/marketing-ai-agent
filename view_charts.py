#!/usr/bin/env python3
"""
Legacy chart viewer - redirects to new unified chart viewer system
"""

import os
import sys

def main():
    print("🔄 This script has been upgraded!")
    print("=" * 40)
    print("The chart viewing system has been enhanced with new features:")
    print("  • Unified chart management")
    print("  • Multiple export formats (HTML, PNG, SVG)")
    print("  • Terminal previews")
    print("  • Automatic browser opening")
    print("  • Chart gallery and search")
    print("")
    print("🚀 Please use the new chart viewer:")
    print("   python chart_viewer.py")
    print("")
    print("📚 For specific charts, try:")
    print("   python chart_viewer.py --list")
    print("   python chart_viewer.py --view <chart_name>")
    print("   python chart_viewer.py --preview <chart_name>")
    print("")
    
    # Try to run the new viewer
    try:
        if len(sys.argv) > 1:
            # User provided arguments, try to launch new viewer with view command
            chart_name = sys.argv[1]
            print(f"🔄 Redirecting to view chart: {chart_name}")
            os.system(f"python chart_viewer.py --view {chart_name}")
        else:
            # Interactive mode
            print("🎯 Launching interactive chart viewer...")
            os.system("python chart_viewer.py")
    except Exception as e:
        print(f"❌ Error launching new viewer: {e}")
        print("💡 Please run: python chart_viewer.py")

if __name__ == "__main__":
    main()