"""
Unified visualization module for CRM AI Agent.

This module provides a comprehensive visualization system with:
- Multiple output formats (HTML, JSON, PNG, SVG)
- Terminal display capabilities
- Auto-browser opening
- Standardized file management
"""

from .core import VisualizationEngine
from .display import ChartDisplayManager
from .utils import ChartUtils

__all__ = ['VisualizationEngine', 'ChartDisplayManager', 'ChartUtils']