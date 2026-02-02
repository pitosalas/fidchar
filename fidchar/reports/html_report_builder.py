#!/usr/bin/env python3
"""HTML comprehensive report builder module.

Handles the creation of comprehensive HTML reports with all sections.
Uses Bootstrap CSS and report_generator renderers for cleaner code.
"""

import pandas as pd
from datetime import datetime
from fidchar.reports import base_report_builder as brb
from fidchar.reports import html_templates as templates
from fidchar.core import analysis as an
from fidchar.report_generator.models import ReportTable, ReportCard, CardSection
from fidchar.report_generator.renderers import HTMLSectionRenderer, HTMLCardRenderer
import shutil
import os

from fidchar.reports.html_section_generators import HTMLSectionGeneratorsMixin
from fidchar.reports.section_handlers import (
    generate_table_sections,
    generate_definitions_section,
    _extract_section_options
)


class HTMLReportBuilder(HTMLSectionGeneratorsMixin, brb.BaseReportBuilder):
    """HTML report builder with inherited state."""

    def __init__(self, df, config, report_data):
        super().__init__(df, config, report_data)
        self.table_renderer = HTMLSectionRenderer()
        self.card_renderer = HTMLCardRenderer()

    def generate_html_header_section(self, options=None):
        """Generate the custom header and executive summary sections for fidchar report.
         """
        options = options or {}
        show_one_time = options.get('show_one_time', True)
        show_stopped = options.get('show_stopped', True)

        # If all subsections are disabled, suppress the entire section
        if not show_one_time and not show_stopped:
            return ""

        # Calculate statistics from instance data
        total_donations = len(self.df)
        years_covered = f"{self.df['Year'].min()} - {self.df['Year'].max()}"

        # Build cards HTML based on options (using precomputed instance variables)
        cards_html = ""
        if show_one_time:
            cards_html += f"""
            <div class="col-md-3">
                <div class="card border-start border-4 border-primary">
                    <div class="card-body">
                        <h6 class="card-title">One-Time Donations</h6>
                        <p class="card-text"><strong>{self.one_time_count} organizations</strong></p>
                        <p class="card-text">Total: ${self.one_time_total:,.2f}</p>
                    </div>
                </div>
            </div>"""

        if show_stopped:
            cards_html += f"""
            <div class="col-md-3">
                <div class="card border-start border-4 border-warning">
                    <div class="card-body">
                        <h6 class="card-title">Stopped Recurring</h6>
                        <p class="card-text"><strong>{self.stopped_count} organizations</strong></p>
                        <p class="card-text">Total: ${self.stopped_total:,.2f}</p>
                    </div>
                </div>
            </div>"""

        # Only show row if we have cards to display
        cards_section = f"""
        <div class="row mb-5">
{cards_html}
        </div>""" if cards_html else ""

        return f"""    <div class="report-section section-header">
        <header class="text-center mb-5 pb-3 border-bottom">
            <h1 class="display-4">Charitable Donation Analysis Report</h1>
            <p class="text-muted">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="alert alert-light border">
                <strong>Total Donations:</strong> {total_donations:,} donations |
                <strong>Total Amount:</strong> ${self.total_amount:,.2f} |
                <strong>Years Covered:</strong> {years_covered}
            </div>
        </header>
{cards_section}
    </div>"""

    def _build_html_document(self, custom_header, custom_footer):
        """Build a complete HTML document with Bootstrap CSS.

        Uses instance configuration for document title, CSS files, and container class.

        Args:
            custom_header: HTML content for header section
            custom_footer: HTML content for footer section

        Returns:
            Complete HTML document string
        """
        # Document configuration (constant for this report type)
        doc_title = "Charitable Donation Analysis Report"
        container_class = "container"
        css_files = ["colors.css", "styles.css"]

        # Build CSS links for external files
        css_links = ""
        for css_file in css_files:
            css_links += f'  <link rel="stylesheet" href="{css_file}">\n'

        header_block = custom_header if custom_header else ""
        footer_block = custom_footer if custom_footer else ""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
{css_links}</head>
<body class="small">
<div class="{container_class}">
{header_block}
{footer_block}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    def _render_two_column_table(self, df_data, title=None):
        """Render DataFrame data as two-column layout for print.

        Args:
            df_data: List of dictionaries to convert to DataFrame
            title: Optional title to display above the columns

        Returns:
            HTML string with two-column table layout
        """
        mid_point = (len(df_data) + 1) // 2
        df_left = pd.DataFrame(df_data[:mid_point])
        df_right = pd.DataFrame(df_data[mid_point:])

        table_left = ReportTable.from_dataframe(df_left, title=None)
        table_right = ReportTable.from_dataframe(df_right, title=None)

        left_html = self.table_renderer.render(table_left)
        right_html = self.table_renderer.render(table_right)

        columns_html = f"""
        <div class="row">
            <div class="col-md-6">{left_html}</div>
            <div class="col-md-6">{right_html}</div>
        </div>
        """

        if title:
            return f"""
        <h2 class="mb-3">{title}</h2>
{columns_html}"""
        else:
            return columns_html

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, charities):
        """Generate complete HTML report using render_html_document base"""
        # Store data as instance variables for access by section handlers
        self.category_totals = category_totals
        self.yearly_amounts = yearly_amounts
        self.yearly_counts = yearly_counts
        self.one_time = one_time
        self.stopped_recurring = stopped_recurring
        self.charities = charities

        # Calculate summary statistics (precomputed to avoid duplication)
        self.total_amount = category_totals.sum()
        self.one_time_total = one_time["Total_Amount"].sum()
        self.one_time_count = len(one_time)
        self.stopped_total = stopped_recurring["Total_Amount"].sum()
        self.stopped_count = len(stopped_recurring)

        # Precompute recurring configuration (used in multiple template calls)
        pattern_config = self.config.get('recurring_charity', {}).get('pattern_based', {})
        self.recurring_min_years = pattern_config.get('min_years', 6)
        self.recurring_min_amount = pattern_config.get('min_amount', 1000)

        # Get exec section options from config
        exec_options = {}
        exec_enabled = False
        sections = self.config.get("sections", [])
        for section in sections:
            section_name = section if isinstance(section, str) else section.get("name")
            if section_name == "exec":
                exec_enabled = True
                if isinstance(section, dict):
                    section_opts = _extract_section_options(section)
                    # Check include flag: defaults to True if not specified
                    include = section_opts.get("include", True)
                    if include == False:
                        exec_enabled = False
                        break
                    exec_options = section_opts
                break

        # Generate custom header only if exec section is enabled
        custom_header = ""
        if exec_enabled:
            custom_header = self.generate_html_header_section(exec_options)

        # Generate sections HTML (excluding definitions which will be added at the end)
        sections_html = generate_table_sections(
            self.config,
            builder=self,
            exclude_definitions=True  # We'll add this manually at the end
        )

        # Check if detailed section should be included
        detailed_enabled = False
        detailed_max_shown = None
        for section in sections:
            section_name = section if isinstance(section, str) else section.get("name")
            if section_name == "detailed":
                detailed_enabled = True
                if isinstance(section, dict):
                    section_opts = _extract_section_options(section)
                    # Check include flag: defaults to True if not specified
                    include = section_opts.get("include", True)
                    if include == False:
                        detailed_enabled = False
                    # Get max_shown option
                    detailed_max_shown = section_opts.get("max_shown")
                break

        # Generate charity cards section only if enabled
        charity_cards_html = ""
        if detailed_enabled:
            # Determine how many charities to show
            charities_to_show = charities.head(detailed_max_shown) if detailed_max_shown else charities
            num_shown = len(charities_to_show)
            total_charities = len(charities)

            # Update title based on whether we're limiting or showing all
            if detailed_max_shown and num_shown < total_charities:
                title_text = f"Detailed Analysis ({num_shown} of {total_charities} charities)"
            else:
                title_text = f"Detailed Analysis ({num_shown} charities)"

            charity_cards_html = f"""
    <div class="report-section section-detailed">
        <h2 class="section-title">{title_text}</h2>
        <p>Complete donation history and trend analysis for each charity:</p>
"""
            for i, (tax_id, _) in enumerate(charities_to_show.iterrows(), 1):
                charity_cards_html += self.generate_charity_card_bootstrap(i, tax_id)
            charity_cards_html += "\n    </div>"

        # Check if definitions section should be included
        definitions_enabled = False
        for section in sections:
            section_name = section if isinstance(section, str) else section.get("name")
            if section_name == "definitions":
                definitions_enabled = True
                if isinstance(section, dict):
                    section_opts = _extract_section_options(section)
                    # Check include flag: defaults to True if not specified
                    include = section_opts.get("include", True)
                    if include == False:
                        definitions_enabled = False
                break

        # Generate definitions section (at the very end) only if enabled
        definitions_html = ""
        if definitions_enabled:
            definitions_html = generate_definitions_section()

        # Combine body content: sections + charity cards + definitions
        body_content = f"{sections_html}\n{charity_cards_html}\n{definitions_html}"

        # Generate footer
        custom_footer = """
    <footer class="mt-5 pt-3 border-top text-center text-muted">
        <small>Generated by fidchar donation analysis tool</small>
    </footer>"""

        # External CSS files - all styles consolidated into styles.css
        # colors.css: Color definitions (minimal, mostly empty)
        # styles.css: All screen and print styles (includes @media print section)

        # Build complete HTML document
        html_content = self._build_html_document(
            custom_header=custom_header + body_content,
            custom_footer=custom_footer
        )

        # Get output directory from config
        output_dir = self.config.get("output_dir", "output")

        # Copy CSS files to output directory
        for css_file in ["colors.css", "styles.css"]:
            css_source = os.path.join(os.path.dirname(__file__), css_file)
            css_dest = os.path.join(output_dir, css_file)
            shutil.copy(css_source, css_dest)

        html_file_path = os.path.join(output_dir, "donation_analysis.html")
        with open(html_file_path, "w") as f:
            f.write(html_content)


# Helper functions for section generation

