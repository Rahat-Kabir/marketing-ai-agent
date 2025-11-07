#!/usr/bin/env python3
"""
Unified Chart Viewer for CRM AI Agent
Enhanced chart viewing with multiple display options and chart management.
"""

import os
import sys
import argparse
import webbrowser
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from neo.visualization import VisualizationEngine, ChartDisplayManager, ChartUtils
except ImportError:
    print("❌ Error: Visualization modules not found. Please ensure the project is properly set up.")
    sys.exit(1)


class ChartViewer:
    """Unified chart viewer with multiple display modes."""
    
    def __init__(self):
        self.viz_engine = VisualizationEngine()
        self.display_manager = ChartDisplayManager()
        
    def list_charts(self, limit: int = 20) -> None:
        """List available charts."""
        charts = self.viz_engine.list_recent_charts(limit)
        gallery = self.display_manager.show_chart_gallery(charts)
        print(gallery)
        
    def view_chart(self, chart_name: str, format_type: str = "html") -> None:
        """View a specific chart."""
        charts = self.viz_engine.list_recent_charts()
        
        # Find matching chart
        matching_charts = [c for c in charts if chart_name.lower() in c['name'].lower()]
        
        if not matching_charts:
            print(f"ERROR: No charts found matching '{chart_name}'")
            print("\nAvailable charts:")
            self.list_charts(10)
            return
            
        chart = matching_charts[0]
        
        if format_type == "html":
            if 'html' in chart['available_formats']:
                print(f"Opening {chart['name']} in browser...")
                success = self.display_manager.open_chart_in_browser(chart['html_path'])
                if not success:
                    print(f"ERROR: Failed to open browser. Try opening manually: {chart['html_path']}")
            else:
                print(f"ERROR: HTML format not available for {chart['name']}")
                
        elif format_type == "preview":
            if 'json' in chart['available_formats']:
                preview = self.display_manager.display_chart_quick_preview(chart['json_path'])
                print(preview)
            else:
                print(f"ERROR: Preview not available for {chart['name']}")
                
        elif format_type == "info":
            self._show_chart_info(chart)
            
    def _show_chart_info(self, chart: dict) -> None:
        """Show detailed information about a chart."""
        print(f"Chart Information: {chart['name']}")
        print("=" * 50)
        print(f"Modified: {chart['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Size: {chart['size'] // 1024}KB")
        print(f"Available Formats: {', '.join(chart['available_formats'])}")
        print(f"HTML Path: {os.path.relpath(chart['html_path'])}")
        
        if 'json' in chart['available_formats']:
            print(f"JSON Path: {os.path.relpath(chart['json_path'])}")
            
        if 'png' in chart['available_formats']:
            print(f"PNG Path: {os.path.relpath(chart['png_path'])}")
            
    def cleanup_charts(self, days: int = 7) -> None:
        """Clean up old charts."""
        print(f"Cleaning up charts older than {days} days...")
        deleted_count = self.viz_engine.cleanup_old_charts(days)
        print(f"Deleted {deleted_count} old chart files")
        
    def interactive_mode(self) -> None:
        """Interactive chart browsing mode."""
        print("Interactive Chart Viewer")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("  1. List recent charts")
            print("  2. View chart by name")
            print("  3. Chart gallery")
            print("  4. Cleanup old charts")
            print("  5. Exit")
            
            try:
                choice = input("\nEnter choice (1-5): ").strip()
                
                if choice == "1":
                    self.list_charts()
                    
                elif choice == "2":
                    chart_name = input("Enter chart name (partial match): ").strip()
                    if chart_name:
                        print("\nView options:")
                        print("  html - Open in browser")
                        print("  preview - Show quick preview")
                        print("  info - Show chart information")
                        format_type = input("Format (html/preview/info) [html]: ").strip() or "html"
                        self.view_chart(chart_name, format_type)
                        
                elif choice == "3":
                    self.list_charts(15)
                    
                elif choice == "4":
                    try:
                        days = int(input("Delete charts older than how many days? [7]: ") or "7")
                        self.cleanup_charts(days)
                    except ValueError:
                        print("ERROR: Invalid number of days")
                        
                elif choice == "5":
                    print("Goodbye!")
                    break
                    
                else:
                    print("ERROR: Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"ERROR: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Chart Viewer for CRM AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chart_viewer.py                          # Interactive mode
  python chart_viewer.py --list                   # List all charts
  python chart_viewer.py --view customer_chart    # View specific chart
  python chart_viewer.py --preview sales_data     # Quick preview
  python chart_viewer.py --cleanup --days 3       # Cleanup old charts
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available charts')
    parser.add_argument('--view', '-v', metavar='NAME',
                       help='View chart by name (opens in browser)')
    parser.add_argument('--preview', '-p', metavar='NAME',
                       help='Show quick preview of chart')
    parser.add_argument('--info', '-i', metavar='NAME',
                       help='Show detailed chart information')
    parser.add_argument('--cleanup', '-c', action='store_true',
                       help='Clean up old charts')
    parser.add_argument('--days', '-d', type=int, default=7,
                       help='Days to keep when cleaning up (default: 7)')
    parser.add_argument('--limit', type=int, default=20,
                       help='Limit number of charts to show (default: 20)')
    
    args = parser.parse_args()
    
    viewer = ChartViewer()
    
    try:
        if args.list:
            viewer.list_charts(args.limit)
        elif args.view:
            viewer.view_chart(args.view, "html")
        elif args.preview:
            viewer.view_chart(args.preview, "preview")
        elif args.info:
            viewer.view_chart(args.info, "info")
        elif args.cleanup:
            viewer.cleanup_charts(args.days)
        else:
            # Interactive mode
            viewer.interactive_mode()
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()