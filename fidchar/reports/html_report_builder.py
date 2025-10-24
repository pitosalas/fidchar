#!/usr/bin/env python3
"""HTML comprehensive report builder module - BOOTSTRAP VERSION.

Handles the creation of comprehensive HTML reports with all sections.
Uses Bootstrap CSS and report_generator renderers for cleaner code.
"""

import pandas as pd
from datetime import datetime
from typing import List
import reports.base_report_builder as brb
from report_generator.models import ReportTable, ReportCard, CardSection
from report_generator.renderers import HTMLSectionRenderer, HTMLCardRenderer
import shutil
import os


def _build_html_document(tables: List[ReportTable], doc_title, custom_header, custom_footer, custom_styles, container_class, css_files=None):
    """Build a complete HTML document with Bootstrap CSS.

    Private helper function for building HTML reports with custom header/footer/styles.
    """
    hr = HTMLSectionRenderer()
    sections = "\n".join(hr.render(t) for t in tables)

    styles_block = f"<style>\n{custom_styles}\n</style>" if custom_styles else ""

    # Build CSS links for multiple external files
    css_links = ""
    if css_files:
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
{css_links}  {styles_block}
</head>
<body>
<div class="{container_class}">
{header_block}
{sections}
{footer_block}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def generate_html_header_section(total_donations, total_amount, years_covered,
                                one_time_total, stopped_total, top_charities_count):
    """Generate the custom header and executive summary sections for fidchar report"""
    return f"""        <header class="text-center mb-5 pb-3 border-bottom">
            <h1 class="display-4">Charitable Donation Analysis Report</h1>
            <p class="text-muted">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="alert alert-light border">
                <strong>Total Donations:</strong> {total_donations:,} donations |
                <strong>Total Amount:</strong> ${total_amount:,.2f} |
                <strong>Years Covered:</strong> {years_covered}
            </div>
        </header>

        <div class="row mb-5">
            <div class="col-md-4">
                <div class="card border-start border-4 border-primary">
                    <div class="card-body">
                        <h5 class="card-title">One-Time Donations</h5>
                        <p class="card-text"><strong>78 organizations</strong></p>
                        <p class="card-text">Total: ${one_time_total:,.2f}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card border-start border-4 border-warning">
                    <div class="card-body">
                        <h5 class="card-title">Stopped Recurring</h5>
                        <p class="card-text"><strong>5 organizations</strong></p>
                        <p class="card-text">Total: ${stopped_total:,.2f}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card border-start border-4 border-success">
                    <div class="card-body">
                        <h5 class="card-title">Top {top_charities_count} Charities</h5>
                        <p class="card-text"><strong>Major recipients</strong></p>
                        <p class="card-text">Detailed analysis below</p>
                    </div>
                </div>
            </div>
        </div>"""


class HTMLReportBuilder(brb.BaseReportBuilder):
    """HTML report builder with inherited state - BOOTSTRAP VERSION"""

    def __init__(self, df, config, charity_details, graph_info, charity_evaluations, recurring_ein_set=None):
        super().__init__(df, config, charity_details, graph_info, charity_evaluations, recurring_ein_set)
        self.table_renderer = HTMLSectionRenderer()
        self.card_renderer = HTMLCardRenderer()

    def generate_top_charities_bootstrap(self, top_charities):
        """Generate top charities table using Bootstrap renderer"""
        # Build DataFrame with formatted org names that include badges
        df_data = []
        for ein, row in top_charities.iterrows():
            # Get formatted org name with badges
            charity_info = self.format_charity_info(ein, row['Organization'], row['Amount_Numeric'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total Amount': f"${row['Amount_Numeric']:,.0f}"
            })

        df_for_table = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df_for_table,
            title=f"Top {len(top_charities)} Charities by Total Donations"
        )
        return self.table_renderer.render(table)

    def generate_category_table_bootstrap(self, category_totals, total_amount):
        """Generate category totals table using Bootstrap renderer"""
        df = category_totals.reset_index()
        df.columns = ['Charitable Sector', 'Total Amount']
        df['Percentage'] = (df['Total Amount'] / total_amount * 100).apply(lambda x: f"{x:.1f}%")
        df['Total Amount'] = df['Total Amount'].apply(lambda x: f"${x:,.0f}")

        table = ReportTable.from_dataframe(
            df,
            title="Donations by Charitable Sector"
        )
        return self.table_renderer.render(table)

    def generate_yearly_table_bootstrap(self, yearly_amounts, yearly_counts):
        """Generate yearly analysis table using Bootstrap renderer"""
        df = pd.DataFrame({
            'Year': sorted(yearly_amounts.index),
            'Total Amount': [f"${yearly_amounts[year]:,.0f}" for year in sorted(yearly_amounts.index)],
            'Number of Donations': [yearly_counts[year] for year in sorted(yearly_amounts.index)]
        })

        table = ReportTable.from_dataframe(
            df,
            title="Yearly Analysis"
        )
        return self.table_renderer.render(table)

    def generate_one_time_table_bootstrap(self, one_time, max_shown=20):
        """Generate one-time donations table using Bootstrap renderer"""
        # Build DataFrame with formatted org names that include badges
        df_data = []
        for ein, row in one_time.head(max_shown).iterrows():
            # Get formatted org name with badges
            charity_info = self.format_charity_info(ein, row['Organization_Name'], row['Total_Amount'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Amount': f"${row['Total_Amount']:,.2f}",
                'Date': row['First_Date'].strftime("%m/%d/%Y")
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=f"One-Time Donations ({len(one_time)} organizations)"
        )
        return self.table_renderer.render(table)

    def generate_stopped_table_bootstrap(self, stopped_recurring, max_shown=15):
        """Generate stopped recurring table using Bootstrap renderer"""
        # Build DataFrame with formatted org names that include badges
        df_data = []
        for ein, row in stopped_recurring.head(max_shown).iterrows():
            # Get formatted org name with badges
            charity_info = self.format_charity_info(ein, row['Organization_Name'], row['Total_Amount'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total Amount': f"${row['Total_Amount']:,.2f}",
                'Donations': row['Donation_Count'],
                'First Date': row['First_Date'].strftime("%m/%d/%Y"),
                'Last Date': row['Last_Date'].strftime("%m/%d/%Y")
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=f"Stopped Recurring Donations ({len(stopped_recurring)} organizations)"
        )
        return self.table_renderer.render(table)

    def generate_recurring_summary_section_html(self, data):
        """Generate recurring charities summary as HTML using HTMLSectionRenderer"""
        if data is None:
            return """
    <div class="report-section">
        <h2 class="section-title">Recurring Charities Summary</h2>
        <p>No recurring charities identified.</p>
    </div>"""

        # Build DataFrame from rows
        df_data = []
        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'

            # Get formatted org name with badges
            charity_info = self.format_charity_info(row['ein'], row['organization'], row['total_donated'])

            df_data.append({
                'EIN': row['ein'],
                'Organization': charity_info['html_org'],
                'Total Donated': f"${row['total_donated']:,.2f}",
                'Last Donation': last_date_str
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=None  # Title will be in section header
        )
        table_html = self.table_renderer.render(table)

        return f"""
    <div class="report-section">
        <h2 class="section-title">Recurring Charities (≥5 years, ≥$1,000/year)</h2>
        <p>{data['count']} charities meeting recurring threshold - at least 5 years with $1,000+ donations:</p>
        {table_html}
        <p style="font-weight: bold; margin-top: 20px;">
            Total donated to recurring charities: ${data['total']:,.2f}
        </p>
    </div>"""

    def generate_remaining_charities_section_html(self, data):
        """Generate remaining charities section as HTML"""
        if data is None or data['count'] == 0:
            return ""

        # Build DataFrame from rows
        df_data = []
        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'

            # Get formatted org name with badges
            charity_info = self.format_charity_info(row['ein'], row['organization'], row['total_donated'])

            df_data.append({
                'Organization': charity_info['html_org'],
                'Total Donated': f"${row['total_donated']:,.2f}",
                'Donations': row['donation_count'],
                'Years': row['unique_years']
            })

        df = pd.DataFrame(df_data)

        table = ReportTable.from_dataframe(
            df,
            title=None  # Title will be in section header
        )
        table_html = self.table_renderer.render(table)

        return f"""
    <div class="report-section">
        <h2 class="section-title">Remaining Charities ({data['count']} organizations)</h2>
        <p>Multi-year, multi-donation charities that don't meet the recurring threshold (5 years with $1,000+ each year). These represent sustained giving relationships at lower amounts or fewer qualifying years.</p>
        {table_html}
        <p style="font-weight: bold; margin-top: 20px;">
            Total donated to remaining charities: ${data['total']:,.2f}
        </p>
    </div>"""

    def generate_charity_card_bootstrap(self, i, tax_id):
        """Generate charity detail as Bootstrap card"""
        org_donations = self.charity_details[tax_id]
        has_graph = self.graph_info.get(tax_id) is not None
        evaluation = self.charity_evaluations.get(tax_id)

        # Get description from charapi evaluation
        description = getattr(evaluation, 'summary', None) if evaluation else None
        if not description:
            description = "No description available"

        org_name = org_donations["Organization"].iloc[0] if not org_donations.empty else "Unknown"
        sector = org_donations["Charitable Sector"].iloc[0] if not org_donations.empty else "Unknown"
        total_donated = org_donations["Amount_Numeric"].sum()
        donation_count = len(org_donations)

        # Get formatted org name with badges
        charity_info = self.format_charity_info(tax_id, org_name, total_donated)
        org_name_with_badges = charity_info['html_org']

        sections = [
            CardSection(
                section_type="key_value",
                content={
                    "Tax ID": tax_id,
                    "Sector": sector,
                    "Total Donated": f"${total_donated:,.2f}",
                    "Number of Donations": str(donation_count)
                }
            )
        ]

        if evaluation:
            sections.append(CardSection(
                section_type="list",
                title="Charity Evaluation:",
                content=[
                    f"⭐ Outstanding: {evaluation.outstanding_count} metrics",
                    f"✓ Acceptable: {evaluation.acceptable_count} metrics",
                    f"⚠ Unacceptable: {evaluation.unacceptable_count} metrics"
                ]
            ))

            if evaluation.alignment_score is not None and evaluation.alignment_score > 0:
                # Get preference metrics breakdown
                alignment_score = evaluation.alignment_score
                from charapi.data.charity_evaluation_result import MetricCategory
                preference_metrics = [m for m in evaluation.metrics if m.category == MetricCategory.PREFERENCE]

                breakdown_items = [f"<strong>Overall Score: {alignment_score}/100</strong>"]
                for metric in preference_metrics:
                    status_icon = "⭐" if metric.status.value == "outstanding" else "✓" if metric.status.value == "acceptable" else "⚠"
                    breakdown_items.append(f"{status_icon} {metric.name}: {metric.display_value}")

                sections.append(CardSection(
                    section_type="list",
                    title="Alignment with Your Goals:",
                    content=breakdown_items
                ))

            if evaluation.summary:
                sections.append(CardSection(
                    section_type="text",
                    content=evaluation.summary
                ))

        graph_filename = f"images/charity_{i:02d}_{tax_id.replace('-', '')}.png" if has_graph else None

        card = ReportCard(
            title=f"{org_name_with_badges}",
            badge=None,  # Badges are now in the title
            sections=sections,
            image_url=graph_filename,
            image_position="right"  # Right position - will need custom rendering
        )

        return self.card_renderer.render(card)

    def generate_report(self, category_totals, yearly_amounts, yearly_counts, one_time,
                       stopped_recurring, top_charities):
        """Generate complete HTML report using render_html_document base"""
        total_amount = category_totals.sum()
        total_donations = len(self.df)
        years_covered = f"{self.df['Year'].min()} - {self.df['Year'].max()}"
        one_time_total = one_time["Total_Amount"].sum()
        stopped_total = stopped_recurring["Total_Amount"].sum()
        top_charities_count = len(top_charities)

        # Generate custom header
        custom_header = generate_html_header_section(
            total_donations, total_amount, years_covered,
            one_time_total, stopped_total, top_charities_count
        )

        # Generate HTML tables using Bootstrap renderers
        categories_html = self.generate_category_table_bootstrap(category_totals, total_amount)
        yearly_html = self.generate_yearly_table_bootstrap(yearly_amounts, yearly_counts)
        top_charities_html = self.generate_top_charities_bootstrap(top_charities)

        # Generate sections HTML (excluding definitions which will be added at the end)
        sections_html = generate_table_sections(
            categories_html,
            yearly_html,
            top_charities_html,
            one_time,
            stopped_recurring,
            self.config,
            self.charity_evaluations,
            self,
            top_charities_count,
            exclude_definitions=True,  # We'll add this manually at the end
            top_charities=top_charities
        )

        # Generate charity cards section
        charity_cards_html = f"""
    <div class="report-section">
        <h2 class="section-title">Detailed Analysis of Top {top_charities_count} Charities</h2>
        <p>Complete donation history and trend analysis for each of the top {top_charities_count} charities:</p>
"""
        for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
            charity_cards_html += self.generate_charity_card_bootstrap(i, tax_id)
        charity_cards_html += "\n    </div>"

        # Generate definitions section (at the very end)
        definitions_html = generate_definitions_section()

        # Combine body content: sections + charity cards + definitions
        body_content = f"{sections_html}\n{charity_cards_html}\n{definitions_html}"

        # Generate footer
        custom_footer = """
    <footer class="mt-5 pt-3 border-top text-center text-muted">
        <small>Generated by fidchar donation analysis tool</small>
    </footer>"""

        # External CSS files - both screen and print styles are now in separate files
        # Screen styles: reports/styles.css
        # Print styles: reports/print.css

        # Build complete HTML document
        html_content = _build_html_document(
            [],  # Empty tables list - we're using custom_header/footer for all content
            doc_title="Charitable Donation Analysis Report",
            custom_header=custom_header + body_content,
            custom_footer=custom_footer,
            custom_styles=None,  # No embedded styles - using external CSS files
            container_class="container my-5",
            css_files=["colors.css", "styles.css", "print.css"]  # Reference external CSS files
        )

        # Copy CSS files to output directory
        for css_file in ["colors.css", "styles.css", "print.css"]:
            css_source = os.path.join(os.path.dirname(__file__), css_file)
            css_dest = f"../output/{css_file}"
            shutil.copy(css_source, css_dest)

        with open("../output/donation_analysis.html", "w") as f:
            f.write(html_content)


# Placeholder to mark where @media print used to be - now moved to print.css
# The print CSS has been moved to reports/print.css for easier maintenance
if False:
    unused_print_css = """
        @media print {
            /* Scale down overall size for article-like appearance */
            body {
                font-size: 10pt;
                line-height: 1.3;
            }

            /* Reduce container width and margins */
            .container {
                max-width: 100%;
                margin: 0;
                padding: 0.5cm;
            }

            /* Compact headers */
            h1, .display-4 {
                font-size: 18pt;
                margin-bottom: 0.3cm;
            }
            h2, .section-title {
                font-size: 14pt;
                margin-top: 0.4cm;
                margin-bottom: 0.2cm;
            }
            h3 {
                font-size: 12pt;
                margin-top: 0.3cm;
                margin-bottom: 0.15cm;
            }
            h4 {
                font-size: 11pt;
                margin-bottom: 0.15cm;
            }

            /* Compact paragraphs and spacing */
            p {
                margin-bottom: 0.2cm;
                font-size: 9pt;
            }

            /* Compact tables */
            .table {
                font-size: 8pt;
                margin-bottom: 0.3cm;
            }
            .table td,
            .table th {
                padding: 0.1cm 0.15cm;
            }

            /* Compact cards - 2x2 grid (4 per page) */
            .card {
                width: 48%;
                float: left;
                margin-right: 2%;
                margin-bottom: 0.3cm;
                page-break-inside: avoid;
                height: auto;
                max-height: 12cm;
                box-sizing: border-box;
            }
            /* Clear float every 2 cards to create rows */
            .card:nth-of-type(2n) {
                margin-right: 0;
            }
            .card:nth-of-type(2n+1) {
                clear: left;
            }
            /* Force page break and clear floats after every 4th card */
            .card:nth-of-type(4n) {
                page-break-after: always;
                margin-bottom: 0;
            }
            .card:nth-of-type(4n)::after {
                content: "";
                display: table;
                clear: both;
            }
            .card-header {
                padding: 0.2cm 0.3cm;
                font-size: 9pt;
            }
            .card-body {
                padding: 0.25cm;
                font-size: 7pt;
                line-height: 1.3;
                overflow: hidden;
            }
            .card-body::after {
                content: "";
                display: table;
                clear: both;
            }

            /* Compact lists */
            ul, ol {
                margin-bottom: 0.2cm;
                padding-left: 0.8cm;
            }
            li {
                margin-bottom: 0.08cm;
                font-size: 7pt;
                line-height: 1.3;
            }

            /* Compact definition lists - remove column layout for print */
            dl.row {
                margin-bottom: 0.2cm;
                display: block;
                overflow: hidden;
                clear: both;
            }
            dl.row::after {
                content: "";
                display: table;
                clear: both;
            }
            dt {
                padding: 0;
                margin: 0;
                font-size: 7pt;
                line-height: 1.3;
                float: none;
                width: auto;
                display: inline;
                font-weight: 600;
            }
            dd {
                padding: 0;
                margin: 0;
                font-size: 7pt;
                line-height: 1.3;
                float: none;
                width: auto;
                display: inline;
            }
            dt::after {
                content: " ";
            }
            dd::after {
                content: "";
                display: block;
                margin-bottom: 0.05cm;
            }

            /* Reduce image sizes */
            img {
                max-width: 100%;
                max-height: 3.5cm;
                height: auto;
            }

            /* Compact alerts and badges */
            .alert {
                padding: 0.2cm 0.3cm;
                margin-bottom: 0.3cm;
                font-size: 9pt;
            }
            .badge {
                font-size: 7pt;
                padding: 0.1cm 0.15cm;
            }

            /* Hide Bootstrap grid spacing */
            .row {
                margin-left: 0;
                margin-right: 0;
            }

            /* Page break controls */
            .report-section {
                page-break-after: auto;
                page-break-inside: auto;
                overflow: hidden;
            }
            .report-section::after {
                content: "";
                display: table;
                clear: both;
            }
            .report-section:last-of-type {
                page-break-after: auto;
            }
            /* Only prevent page breaks inside non-card sections */
            .report-section:not(:has(.card)) {
                page-break-inside: avoid;
                page-break-after: always;
            }
            .section-title {
                page-break-after: avoid;
            }

            /* Compact header section */
            header {
                margin-bottom: 0.4cm;
                padding-bottom: 0.2cm;
            }

            /* Compact footer */
            footer {
                margin-top: 0.4cm;
                padding-top: 0.2cm;
                font-size: 8pt;
            }

            /* Definitions section */
            .definitions-content {
                font-size: 8pt;
                line-height: 1.3;
            }
            .definitions-content h1 {
                font-size: 14pt;
                margin-bottom: 0.3cm;
            }
            .definitions-content h2 {
                font-size: 12pt;
                margin-top: 0.3cm;
                margin-bottom: 0.2cm;
                page-break-after: avoid;
            }
            .definitions-content h3 {
                font-size: 10pt;
                margin-top: 0.2cm;
                margin-bottom: 0.1cm;
                page-break-after: avoid;
            }
            .definitions-content p {
                margin-bottom: 0.15cm;
            }
        }"""  # End of old print CSS - kept for reference only, not used


def generate_table_sections(categories_html, yearly_html, top_charities_html,
                           one_time, stopped_recurring, config: dict,
                           charity_evaluations=None, builder=None, top_charities_count=10,
                           exclude_definitions=False, top_charities=None):
    sections = config.get("sections", {})
    html_content = ""

    for section in sections:
        section_id = section if isinstance(section, str) else section.get("name")

        # Skip definitions if we're excluding it (will be added manually at the end)
        if exclude_definitions and section_id == "definitions":
            continue
        section_options = section.get("options", {}) if isinstance(section, dict) else {}
        if section_id == "sectors":
            html_content += f"""
    <div class="report-section">
        {categories_html}
    </div>"""
        elif section_id == "yearly":
            html_content += f"""
    <div class="report-section">
        <h2 class="section-title">Yearly Analysis</h2>
        <div style="text-align: center; margin: 20px 0;">
            <img src="images/yearly_amounts.png" alt="Yearly Donation Amounts" style="max-width: 100%; height: auto; margin: 10px;">
            <img src="images/yearly_counts.png" alt="Yearly Donation Counts" style="max-width: 100%; height: auto; margin: 10px;">
        </div>
        {yearly_html}
    </div>"""
        elif section_id == "top_charities":
            html_content += f"""
    <div class="report-section">
        {top_charities_html}
    </div>"""
        elif section_id == "patterns":
            if builder:
                # Get configurable limits from section options
                max_one_time = section_options.get("max_one_time_shown", 20)
                max_stopped = section_options.get("max_stopped_shown", 15)

                one_time_table = builder.generate_one_time_table_bootstrap(one_time, max_shown=max_one_time)
                one_time_total = one_time["Total_Amount"].sum()
                one_time_count = len(one_time)
                overflow_one_time = max(0, one_time_count - max_one_time)

                stopped_table = builder.generate_stopped_table_bootstrap(stopped_recurring, max_shown=max_stopped)
                stopped_total = stopped_recurring["Total_Amount"].sum()
                stopped_count = len(stopped_recurring)
                overflow_stopped = max(0, stopped_count - max_stopped)

                html_content += f"{one_time_table}"
                if overflow_one_time > 0:
                    html_content += f"""
        <p><em>... and {overflow_one_time} more organizations</em></p>"""
                html_content += f"""
        <p style="margin-top: 15px;"><strong>One-time donations total:</strong> ${one_time_total:,.2f}</p>

    {stopped_table}"""
                if overflow_stopped > 0:
                    html_content += f"""
        <p><em>... and {overflow_stopped} more organizations</em></p>"""
                html_content += f"""
        <p style="margin-top: 15px;"><strong>Stopped recurring donations total:</strong> ${stopped_total:,.2f}</p>"""
        elif section_id == "recurring_summary":
            if builder:
                # Get configurable limit from section options
                max_recurring = section_options.get("max_recurring_shown", 20)
                data = builder.prepare_recurring_summary_data(max_shown=max_recurring)
                html_content += builder.generate_recurring_summary_section_html(data)
        elif section_id == "remaining":
            if builder:
                # Get configurable limit from section options
                max_remaining = section_options.get("max_remaining_shown", 100)
                data = builder.prepare_remaining_charities_data(one_time, top_charities, max_shown=max_remaining)
                html_content += builder.generate_remaining_charities_section_html(data)

    return html_content


def generate_definitions_section():
    """Generate the definitions section from markdown file"""
    import os
    from markdown_it import MarkdownIt

    md = MarkdownIt()
    definitions_path = os.path.join(os.path.dirname(__file__), "..", "definitions.md")

    try:
        with open(definitions_path, "r") as f:
            markdown_content = f.read()
            html_definitions = md.render(markdown_content)

        return f"""
    <div class="report-section">
        <div class="definitions-content">
            {html_definitions}
        </div>
    </div>"""
    except FileNotFoundError:
        return """
    <div class="report-section">
        <h2 class="section-title">Definitions</h2>
        <p><em>Definitions file not found.</em></p>
    </div>"""