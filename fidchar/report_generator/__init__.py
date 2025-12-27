"""Report Generator - A general-purpose report rendering library.

Provides data models and renderers for creating reports in HTML format
from structured data.

Usage:
    From within fidchar:
        from report_generator import ReportTable, HTMLSectionRenderer

    Standalone demo:
        python -m report_generator.main
"""

from fidchar.report_generator.models import ReportTable, ReportCard, CardSection
from fidchar.report_generator.renderers import (
    HTMLSectionRenderer,
    HTMLCardRenderer
)

__all__ = [
    'ReportTable',
    'ReportCard',
    'CardSection',
    'HTMLSectionRenderer',
    'HTMLCardRenderer',
]

__version__ = '0.1.0'
