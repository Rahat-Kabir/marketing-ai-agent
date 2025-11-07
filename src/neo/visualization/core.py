"""
Core visualization engine for CRM AI Agent.
"""

import os
import json
import io
import webbrowser
import pandas as pd
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional, Tuple
from sqlalchemy import text, Engine
import plotly.io as pio


class VisualizationEngine:
    """
    Unified visualization engine that handles chart generation, file management,
    and display across multiple formats.
    """
    
    def __init__(self, output_dir: str = "output/charts"):
        """
        Initialize the visualization engine.
        
        Args:
            output_dir: Directory for chart outputs
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
        
        # Configure plotly for better performance
        pio.renderers.default = "browser"
        
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _generate_filename(self, name: str) -> str:
        """
        Generate a standardized filename with timestamp.
        
        Args:
            name: Base name for the chart
            
        Returns:
            Standardized filename without extension
        """
        # Clean the name
        clean_name = "".join(c for c in name if c.isalnum() or c in "_-").strip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{clean_name}_{timestamp}"
        
    def generate_chart(
        self,
        name: str,
        sql_query: str,
        plotly_code: str,
        engine: Engine,
        auto_open: bool = True,
        export_formats: list = None
    ) -> Dict[str, Any]:
        """
        Generate a chart with multiple output formats.
        
        Args:
            name: Chart name
            sql_query: SQL query to get data
            plotly_code: Plotly code to generate chart
            engine: Database engine
            auto_open: Whether to automatically open chart in browser
            export_formats: List of formats to export ['html', 'json', 'png', 'svg']
            
        Returns:
            Dictionary with file paths and status
        """
        if export_formats is None:
            export_formats = ['html', 'json']
            
        result = {
            'success': False,
            'files': {},
            'errors': [],
            'chart_data': None
        }
        
        try:
            # Generate standardized filename
            base_filename = self._generate_filename(name)
            
            # Execute the visualization code
            fig = self._execute_visualization_code(sql_query, plotly_code, engine)
            
            if fig is None:
                result['errors'].append("Failed to generate figure")
                return result
                
            # Export to requested formats
            if 'json' in export_formats:
                json_path = self._export_json(fig, base_filename)
                result['files']['json'] = json_path
                
            if 'html' in export_formats:
                html_path = self._export_html(fig, base_filename)
                result['files']['html'] = html_path
                
            if 'png' in export_formats:
                png_path = self._export_png(fig, base_filename)
                if png_path:
                    result['files']['png'] = png_path
                    
            if 'svg' in export_formats:
                svg_path = self._export_svg(fig, base_filename)
                if svg_path:
                    result['files']['svg'] = svg_path
            
            # Auto-open in browser if requested and HTML was created
            if auto_open and 'html' in result['files']:
                self._open_in_browser(result['files']['html'])
                
            result['success'] = True
            result['chart_data'] = {
                'title': getattr(fig.layout, 'title', {}).get('text', name),
                'chart_type': self._detect_chart_type(fig),
                'data_points': len(fig.data[0].x) if fig.data and hasattr(fig.data[0], 'x') else 0
            }
            
        except Exception as e:
            result['errors'].append(f"Chart generation failed: {str(e)}")
            
        return result
        
    def _execute_visualization_code(
        self, 
        sql_query: str, 
        plotly_code: str, 
        engine: Engine
    ) -> Optional[Any]:
        """
        Execute the SQL query and plotly code to generate the figure.
        
        Returns:
            Plotly figure object or None if failed
        """
        # Capture output for debugging
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Prepare the complete code
        pre_code = f'''
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from sqlalchemy import text

# Execute SQL query
df = pd.read_sql(text("""{sql_query}"""), engine)

# Generated plotly code
'''
        
        # Complete code
        code = pre_code + plotly_code
        
        # Execution environment
        exec_globals = {'engine': engine}
        exec_locals = {}
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, exec_globals, exec_locals)
                
            # Extract the figure
            if 'fig' in exec_locals:
                return exec_locals['fig']
            elif 'fig' in exec_globals:
                return exec_globals['fig']
            else:
                print(f"Warning: No 'fig' variable found in visualization code")
                return None
                
        except Exception as e:
            print(f"Error executing visualization code: {e}")
            stderr_output = stderr_capture.getvalue()
            if stderr_output:
                print(f"STDERR: {stderr_output}")
            return None
            
    def _export_json(self, fig: Any, base_filename: str) -> str:
        """Export figure to JSON format."""
        json_path = os.path.join(self.output_dir, f"{base_filename}.json")
        fig_json = pio.to_json(fig)
        with open(json_path, 'w') as f:
            f.write(fig_json)
        return json_path
        
    def _export_html(self, fig: Any, base_filename: str) -> str:
        """Export figure to HTML format."""
        html_path = os.path.join(self.output_dir, f"{base_filename}.html")
        fig.write_html(html_path, include_plotlyjs='cdn')
        return html_path
        
    def _export_png(self, fig: Any, base_filename: str) -> Optional[str]:
        """Export figure to PNG format using kaleido."""
        try:
            import kaleido
            png_path = os.path.join(self.output_dir, f"{base_filename}.png")
            fig.write_image(png_path, width=1200, height=800, scale=2)
            return png_path
        except ImportError:
            print("Warning: kaleido not installed, PNG export unavailable")
            return None
        except Exception as e:
            print(f"Warning: PNG export failed: {e}")
            return None
            
    def _export_svg(self, fig: Any, base_filename: str) -> Optional[str]:
        """Export figure to SVG format using kaleido."""
        try:
            import kaleido
            svg_path = os.path.join(self.output_dir, f"{base_filename}.svg")
            fig.write_image(svg_path, format='svg', width=1200, height=800)
            return svg_path
        except ImportError:
            print("Warning: kaleido not installed, SVG export unavailable")
            return None
        except Exception as e:
            print(f"Warning: SVG export failed: {e}")
            return None
            
    def _open_in_browser(self, html_path: str) -> None:
        """Open HTML file in the default web browser."""
        try:
            abs_path = os.path.abspath(html_path)
            webbrowser.open(f"file://{abs_path}")
        except Exception as e:
            print(f"Warning: Could not open browser: {e}")
            
    def _detect_chart_type(self, fig: Any) -> str:
        """Detect the type of chart from the figure."""
        if not fig.data:
            return "unknown"
            
        trace_type = fig.data[0].type
        if trace_type == 'bar':
            return 'bar_chart'
        elif trace_type == 'scatter':
            if fig.data[0].mode == 'lines':
                return 'line_chart'
            else:
                return 'scatter_plot'
        elif trace_type == 'pie':
            return 'pie_chart'
        elif trace_type == 'histogram':
            return 'histogram'
        else:
            return trace_type or 'unknown'
            
    def list_recent_charts(self, limit: int = 10) -> list:
        """
        List recent charts in the output directory.
        
        Args:
            limit: Maximum number of charts to return
            
        Returns:
            List of chart info dictionaries
        """
        charts = []
        
        if not os.path.exists(self.output_dir):
            return charts
            
        # Get all HTML files (our primary format)
        html_files = [f for f in os.listdir(self.output_dir) if f.endswith('.html')]
        
        # Sort by modification time (newest first)
        html_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(self.output_dir, x)),
            reverse=True
        )
        
        for filename in html_files[:limit]:
            filepath = os.path.join(self.output_dir, filename)
            base_name = filename[:-5]  # Remove .html extension
            
            chart_info = {
                'name': base_name,
                'html_path': filepath,
                'json_path': os.path.join(self.output_dir, f"{base_name}.json"),
                'png_path': os.path.join(self.output_dir, f"{base_name}.png"),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)),
                'size': os.path.getsize(filepath)
            }
            
            # Check which formats exist
            chart_info['available_formats'] = ['html']
            if os.path.exists(chart_info['json_path']):
                chart_info['available_formats'].append('json')
            if os.path.exists(chart_info['png_path']):
                chart_info['available_formats'].append('png')
                
            charts.append(chart_info)
            
        return charts
        
    def cleanup_old_charts(self, keep_days: int = 7) -> int:
        """
        Clean up old chart files.
        
        Args:
            keep_days: Number of days to keep charts
            
        Returns:
            Number of files deleted
        """
        if not os.path.exists(self.output_dir):
            return 0
            
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"Warning: Could not delete {filepath}: {e}")
                    
        return deleted_count