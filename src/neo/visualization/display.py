"""
Chart display manager for terminal and browser display.
"""

import os
import json
import webbrowser
from typing import Dict, Any, Optional, List
import pandas as pd


class ChartDisplayManager:
    """
    Manages different ways to display charts - terminal ASCII, browser, etc.
    """
    
    def __init__(self):
        self.terminal_width = 80
        
    def display_chart_summary(self, chart_result: Dict[str, Any]) -> str:
        """
        Create a terminal-friendly summary of the chart.
        
        Args:
            chart_result: Result from VisualizationEngine.generate_chart
            
        Returns:
            Formatted summary string
        """
        if not chart_result['success']:
            return self._format_error_summary(chart_result)
            
        summary = []
        summary.append("📊 Chart Generated Successfully!")
        summary.append("=" * 40)
        
        # Chart info
        if chart_result.get('chart_data'):
            data = chart_result['chart_data']
            summary.append(f"Title: {data.get('title', 'Untitled Chart')}")
            summary.append(f"Type: {data.get('chart_type', 'Unknown').replace('_', ' ').title()}")
            summary.append(f"Data Points: {data.get('data_points', 0)}")
            
        # Available files
        summary.append("\nGenerated Files:")
        for format_type, filepath in chart_result['files'].items():
            relative_path = os.path.relpath(filepath)
            summary.append(f"  {format_type.upper()}: {relative_path}")
            
        # Instructions
        summary.append("\nTo view your chart:")
        if 'html' in chart_result['files']:
            summary.append("  • Browser: Chart should open automatically")
            summary.append(f"  • Manual: Open {os.path.relpath(chart_result['files']['html'])}")
            
        if 'png' in chart_result['files']:
            summary.append(f"  • Image: {os.path.relpath(chart_result['files']['png'])}")
            
        return "\n".join(summary)
        
    def _format_error_summary(self, chart_result: Dict[str, Any]) -> str:
        """Format error summary for failed chart generation."""
        summary = []
        summary.append("❌ Chart Generation Failed")
        summary.append("=" * 40)
        
        for error in chart_result.get('errors', []):
            summary.append(f"Error: {error}")
            
        summary.append("\nTroubleshooting Tips:")
        summary.append("  • Check your SQL query syntax")
        summary.append("  • Verify plotly code creates a 'fig' variable")
        summary.append("  • Ensure data is not empty")
        
        return "\n".join(summary)
        
    def create_ascii_chart(self, data: pd.DataFrame, chart_type: str = "bar") -> str:
        """
        Create a simple ASCII representation of data.
        
        Args:
            data: DataFrame with data to visualize
            chart_type: Type of chart ('bar', 'line', 'table')
            
        Returns:
            ASCII art representation
        """
        if data.empty:
            return "📈 No data to display"
            
        if chart_type == "table":
            return self._create_ascii_table(data)
        elif chart_type == "bar":
            return self._create_ascii_bar_chart(data)
        else:
            return self._create_ascii_table(data)
            
    def _create_ascii_table(self, data: pd.DataFrame, max_rows: int = 10) -> str:
        """Create an ASCII table representation."""
        if len(data) > max_rows:
            display_data = data.head(max_rows)
            truncated = True
        else:
            display_data = data
            truncated = False
            
        # Convert to string and create table
        table_lines = []
        table_lines.append("📋 Data Preview:")
        table_lines.append("-" * 40)
        
        # Simple table formatting
        for i, row in display_data.iterrows():
            line_parts = []
            for col, value in row.items():
                # Truncate long values
                str_val = str(value)
                if len(str_val) > 15:
                    str_val = str_val[:12] + "..."
                line_parts.append(f"{col}: {str_val}")
            table_lines.append(" | ".join(line_parts))
            
        if truncated:
            table_lines.append(f"... and {len(data) - max_rows} more rows")
            
        return "\n".join(table_lines)
        
    def _create_ascii_bar_chart(self, data: pd.DataFrame) -> str:
        """Create a simple ASCII bar chart."""
        if len(data.columns) < 2:
            return self._create_ascii_table(data)
            
        # Assume first column is labels, second is values
        labels_col = data.columns[0]
        values_col = data.columns[1]
        
        # Get top 10 items for display
        chart_data = data.nlargest(10, values_col)
        
        if chart_data.empty:
            return "📊 No data to chart"
            
        chart_lines = []
        chart_lines.append(f"📊 {values_col} by {labels_col} (Top 10)")
        chart_lines.append("-" * 50)
        
        # Calculate scaling
        max_value = chart_data[values_col].max()
        max_bar_length = 30
        
        for _, row in chart_data.iterrows():
            label = str(row[labels_col])[:15]  # Truncate long labels
            value = row[values_col]
            
            # Calculate bar length
            if max_value > 0:
                bar_length = int((value / max_value) * max_bar_length)
            else:
                bar_length = 0
                
            # Create bar
            bar = "█" * bar_length
            
            # Format value
            if isinstance(value, float):
                value_str = f"{value:.1f}"
            else:
                value_str = str(value)
                
            chart_lines.append(f"{label:15} │{bar:<30} {value_str}")
            
        return "\n".join(chart_lines)
        
    def open_chart_in_browser(self, filepath: str) -> bool:
        """
        Open a chart file in the default browser.
        
        Args:
            filepath: Path to the HTML file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return False
                
            abs_path = os.path.abspath(filepath)
            webbrowser.open(f"file://{abs_path}")
            return True
        except Exception as e:
            print(f"Error opening browser: {e}")
            return False
            
    def show_chart_gallery(self, charts: List[Dict[str, Any]]) -> str:
        """
        Display a gallery of available charts.
        
        Args:
            charts: List of chart info from VisualizationEngine.list_recent_charts
            
        Returns:
            Formatted gallery string
        """
        if not charts:
            return "[CHARTS] No charts found. Generate your first chart!"
            
        gallery_lines = []
        gallery_lines.append("[CHARTS] Recent Charts Gallery")
        gallery_lines.append("=" * 50)
        
        for i, chart in enumerate(charts, 1):
            name_parts = chart['name'].split('_')
            clean_name = ' '.join(name_parts[:-2]) if len(name_parts) > 2 else chart['name']
            
            modified_str = chart['modified'].strftime("%Y-%m-%d %H:%M")
            size_kb = chart['size'] // 1024
            
            gallery_lines.append(f"{i:2d}. {clean_name}")
            gallery_lines.append(f"    Date: {modified_str} | Size: {size_kb}KB")
            
            formats = ', '.join(chart['available_formats'])
            gallery_lines.append(f"    Formats: {formats}")
            gallery_lines.append("")
            
        gallery_lines.append("TIP: To view a chart, note its number and use the chart viewer.")
        
        return "\n".join(gallery_lines)
        
    def display_chart_quick_preview(self, json_path: str) -> str:
        """
        Show a quick preview of chart data from JSON file.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            Quick preview string
        """
        try:
            if not os.path.exists(json_path):
                return "📊 Chart file not found"
                
            with open(json_path, 'r') as f:
                chart_data = json.load(f)
                
            # Extract basic info
            layout = chart_data.get('layout', {})
            title = layout.get('title', {})
            if isinstance(title, dict):
                title_text = title.get('text', 'Untitled Chart')
            else:
                title_text = str(title) if title else 'Untitled Chart'
                
            data_traces = chart_data.get('data', [])
            
            preview_lines = []
            preview_lines.append(f"📊 {title_text}")
            preview_lines.append("-" * min(len(title_text) + 4, 40))
            
            if data_traces:
                trace = data_traces[0]
                trace_type = trace.get('type', 'unknown')
                
                # Get data info
                x_data = trace.get('x', [])
                y_data = trace.get('y', [])
                
                preview_lines.append(f"Chart Type: {trace_type.title()}")
                
                if x_data:
                    preview_lines.append(f"Data Points: {len(x_data)}")
                    if len(x_data) <= 5:
                        preview_lines.append(f"X Values: {', '.join(map(str, x_data))}")
                    else:
                        preview_lines.append(f"X Range: {x_data[0]} to {x_data[-1]}")
                        
                if y_data and isinstance(y_data, list):
                    if len(y_data) <= 5:
                        preview_lines.append(f"Y Values: {', '.join(map(str, y_data))}")
                    else:
                        min_y = min(y_data) if y_data else 0
                        max_y = max(y_data) if y_data else 0
                        preview_lines.append(f"Y Range: {min_y} to {max_y}")
                        
            return "\n".join(preview_lines)
            
        except Exception as e:
            return f"📊 Error reading chart: {e}"