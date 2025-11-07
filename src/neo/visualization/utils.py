"""
Utility functions for the visualization system.
"""

import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import Engine, text


class ChartUtils:
    """
    Utility functions for chart operations and data analysis.
    """
    
    @staticmethod
    def validate_sql_query(query: str) -> Tuple[bool, str]:
        """
        Validate SQL query for safety and correctness.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        query_lower = query.lower().strip()
        
        # Check for dangerous operations
        dangerous_keywords = [
            'drop', 'delete', 'truncate', 'alter', 'create', 'insert', 
            'update', 'grant', 'revoke', 'exec', 'execute'
        ]
        
        for keyword in dangerous_keywords:
            if f' {keyword} ' in f' {query_lower} ':
                return False, f"Query contains potentially dangerous keyword: {keyword}"
                
        # Must contain SELECT
        if not query_lower.startswith('select'):
            return False, "Query must start with SELECT"
            
        # Basic syntax checks
        if query.count('(') != query.count(')'):
            return False, "Mismatched parentheses in query"
            
        return True, ""
        
    @staticmethod
    def validate_plotly_code(plotly_code: str) -> Tuple[bool, str]:
        """
        Validate plotly code for safety and correctness.
        
        Args:
            plotly_code: Python plotly code
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for dangerous operations
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess', 'exec(', 'eval(',
            'open(', '__import__', 'globals()', 'locals()', 'file(', 'input(',
            'raw_input('
        ]
        
        code_lower = plotly_code.lower()
        
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return False, f"Code contains potentially dangerous pattern: {pattern}"
                
        # Must create a figure
        if 'fig' not in plotly_code:
            return False, "Code must create a variable named 'fig'"
            
        # Should use plotly
        if not any(lib in plotly_code for lib in ['px.', 'go.', 'plotly']):
            return False, "Code should use plotly (px. or go.)"
            
        return True, ""
        
    @staticmethod
    def suggest_chart_type(data: pd.DataFrame) -> str:
        """
        Suggest appropriate chart type based on data characteristics.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Suggested chart type
        """
        if data.empty:
            return "table"
            
        num_cols = len(data.select_dtypes(include=['number']).columns)
        cat_cols = len(data.select_dtypes(include=['object', 'category']).columns)
        date_cols = len(data.select_dtypes(include=['datetime']).columns)
        
        # Time series data
        if date_cols > 0 and num_cols > 0:
            return "line"
            
        # Single categorical + single numerical
        if cat_cols == 1 and num_cols == 1:
            unique_categories = data.iloc[:, 0].nunique()
            if unique_categories <= 10:
                return "bar"
            else:
                return "histogram"
                
        # Multiple numerical columns
        if num_cols >= 2:
            return "scatter"
            
        # Single categorical column (for proportions)
        if cat_cols == 1:
            return "pie"
            
        # Default
        return "table"
        
    @staticmethod
    def generate_chart_suggestions(data: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Generate multiple chart suggestions for given data.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            List of chart suggestions with code templates
        """
        suggestions = []
        
        if data.empty:
            return suggestions
            
        columns = data.columns.tolist()
        
        # Bar chart suggestion
        if len(columns) >= 2:
            cat_col = None
            num_col = None
            
            for col in columns:
                if data[col].dtype in ['object', 'category'] and cat_col is None:
                    cat_col = col
                elif pd.api.types.is_numeric_dtype(data[col]) and num_col is None:
                    num_col = col
                    
            if cat_col and num_col:
                suggestions.append({
                    'type': 'bar',
                    'description': f'Bar chart of {num_col} by {cat_col}',
                    'code': f"fig = px.bar(df, x='{cat_col}', y='{num_col}', title='{num_col} by {cat_col}')"
                })
                
        # Line chart suggestion (if datetime column exists)
        date_cols = data.select_dtypes(include=['datetime']).columns
        num_cols = data.select_dtypes(include=['number']).columns
        
        if len(date_cols) > 0 and len(num_cols) > 0:
            date_col = date_cols[0]
            num_col = num_cols[0]
            suggestions.append({
                'type': 'line',
                'description': f'Time series of {num_col} over {date_col}',
                'code': f"fig = px.line(df, x='{date_col}', y='{num_col}', title='{num_col} Over Time')"
            })
            
        # Pie chart suggestion
        if len(columns) >= 1:
            cat_col = None
            for col in columns:
                if data[col].dtype in ['object', 'category']:
                    cat_col = col
                    break
                    
            if cat_col:
                suggestions.append({
                    'type': 'pie',
                    'description': f'Distribution of {cat_col}',
                    'code': f"fig = px.pie(df, names='{cat_col}', title='Distribution of {cat_col}')"
                })
                
        # Scatter plot suggestion
        num_cols = data.select_dtypes(include=['number']).columns
        if len(num_cols) >= 2:
            x_col = num_cols[0]
            y_col = num_cols[1]
            suggestions.append({
                'type': 'scatter',
                'description': f'Scatter plot of {y_col} vs {x_col}',
                'code': f"fig = px.scatter(df, x='{x_col}', y='{y_col}', title='{y_col} vs {x_col}')"
            })
            
        return suggestions
        
    @staticmethod
    def preview_data(engine: Engine, sql_query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Preview data from SQL query without running full visualization.
        
        Args:
            engine: Database engine
            sql_query: SQL query
            limit: Number of rows to preview
            
        Returns:
            Dictionary with preview data and metadata
        """
        try:
            # Add LIMIT to query if not present
            query_lower = sql_query.lower()
            if 'limit' not in query_lower:
                preview_query = f"{sql_query.rstrip(';')} LIMIT {limit}"
            else:
                preview_query = sql_query
                
            # Execute query
            df = pd.read_sql(text(preview_query), engine)
            
            return {
                'success': True,
                'data': df,
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'column_types': df.dtypes.to_dict(),
                'sample_data': df.head(3).to_dict('records'),
                'suggestions': ChartUtils.generate_chart_suggestions(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'suggestions': []
            }
            
    @staticmethod
    def cleanup_chart_name(name: str) -> str:
        """
        Clean up chart name for use as filename.
        
        Args:
            name: Original chart name
            
        Returns:
            Cleaned filename-safe name
        """
        # Remove or replace problematic characters
        clean_name = "".join(c for c in name if c.isalnum() or c in " _-")
        clean_name = clean_name.replace(" ", "_")
        clean_name = clean_name.strip("_-")
        
        # Ensure not empty
        if not clean_name:
            clean_name = "chart"
            
        # Limit length
        if len(clean_name) > 50:
            clean_name = clean_name[:50]
            
        return clean_name.lower()
        
    @staticmethod
    def get_chart_metadata(chart_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract metadata from generated chart files.
        
        Args:
            chart_files: Dictionary of format -> filepath
            
        Returns:
            Chart metadata
        """
        metadata = {
            'files': chart_files,
            'total_size': 0,
            'formats': list(chart_files.keys())
        }
        
        # Calculate total size
        for filepath in chart_files.values():
            if os.path.exists(filepath):
                metadata['total_size'] += os.path.getsize(filepath)
                
        # Extract info from JSON if available
        if 'json' in chart_files and os.path.exists(chart_files['json']):
            try:
                with open(chart_files['json'], 'r') as f:
                    chart_data = json.load(f)
                    
                layout = chart_data.get('layout', {})
                title = layout.get('title', {})
                
                if isinstance(title, dict):
                    metadata['title'] = title.get('text', 'Untitled')
                else:
                    metadata['title'] = str(title) if title else 'Untitled'
                    
                # Extract chart type
                data_traces = chart_data.get('data', [])
                if data_traces:
                    metadata['chart_type'] = data_traces[0].get('type', 'unknown')
                    metadata['data_points'] = len(data_traces[0].get('x', []))
                    
            except Exception:
                pass
                
        return metadata