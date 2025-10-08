#!/usr/bin/env python3
"""Report formatters for different output formats.

These classes handle ONLY formatting - no business logic.
"""

from abc import ABC, abstractmethod
import pandas as pd
from tables.great_tables_builder import create_gt_recurring_donations_table


class ReportFormatter(ABC):
    """Abstract base formatter - defines interface"""

    @abstractmethod
    def format_recurring_section(self, data):
        """Format recurring donations section with prepared data"""
        pass

    @abstractmethod
    def format_charity_detail_section(self, data):
        """Format charity detail section with prepared data"""
        pass


class HTMLFormatter(ReportFormatter):
    """HTML-specific formatting"""

    def format_recurring_section(self, data):
        """Format recurring donations as HTML table"""
        if data is None:
            return """
    <div class="report-section">
        <h2 class="section-title">Recurring Donations</h2>
        <p>No recurring donations found.</p>
    </div>"""

        table_html = """
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <thead>
            <tr style="background: #f8f9fa; border-bottom: 2px solid #333;">
                <th style="padding: 10px; text-align: left;">EIN</th>
                <th style="padding: 10px; text-align: left;">Organization</th>
                <th style="padding: 10px; text-align: center;">First Year</th>
                <th style="padding: 10px; text-align: center;">Years</th>
                <th style="padding: 10px; text-align: right;">Amount</th>
                <th style="padding: 10px; text-align: right;">Total Ever Donated</th>
                <th style="padding: 10px; text-align: left;">Last Donation</th>
            </tr>
        </thead>
        <tbody>"""

        for i, row in enumerate(data['rows']):
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            table_html += f"""
            <tr style="background: {bg_color}; border-bottom: 1px solid #ddd;">
                <td style="padding: 8px;">{row['ein']}</td>
                <td style="padding: 8px;">{row['organization']}</td>
                <td style="padding: 8px; text-align: center;">{row['first_year']}</td>
                <td style="padding: 8px; text-align: center;">{row['years']}</td>
                <td style="padding: 8px; text-align: right;">${row['amount']:,.2f}</td>
                <td style="padding: 8px; text-align: right;">${row['total_ever']:,.2f}</td>
                <td style="padding: 8px;">{row['last_date'].strftime('%Y-%m-%d')}</td>
            </tr>"""

        table_html += """
        </tbody>
    </table>"""

        more_text = ""
        if data['overflow_count'] > 0:
            more_text = f"<p><em>... and {data['overflow_count']} more organizations</em></p>"

        totals = data['totals']
        return f"""
    <div class="report-section">
        <h2 class="section-title">Recurring Donations</h2>
        <p>Organizations with recurring donation schedules ({data['org_count']} organizations):</p>
        {table_html}
        {more_text}
        <p style="margin-top: 15px;"><strong>Total annual recurring donations:</strong> ${totals['total_recurring']:,.2f}</p>
        <p style="margin-top: 5px;"><strong>Total ever donated to recurring causes:</strong> ${totals['total_ever']:,.2f}</p>
    </div>"""

    def format_charity_detail_section(self, data):
        """Format charity detail section as HTML"""
        section = f"<div><h3>{data['index']}. {data['org_name']}</h3>"

        if data['has_graph']:
            section += f"""
        <table style="width: 100%; margin: 10px 0;">
            <tr>
                <td style="width: 60%; vertical-align: top;">
                    <strong>Tax ID:</strong> {data['tax_id']}<br>
                    <strong>Sector:</strong> {data['sector']}<br>
                    <strong>Total Donated:</strong> ${data['total_donated']:,.2f}<br>
                    <strong>Number of Donations:</strong> {data['donation_count']}
                </td>
                <td style="width: 40%; text-align: center;">
                    <img src="{data['graph_filename']}" alt="Trend" style="max-width: 100%; height: auto;">
                </td>
            </tr>
        </table>"""
        else:
            section += f"""
        <p>
            <strong>Tax ID:</strong> {data['tax_id']}<br>
            <strong>Sector:</strong> {data['sector']}<br>
            <strong>Total Donated:</strong> ${data['total_donated']:,.2f}<br>
            <strong>Number of Donations:</strong> {data['donation_count']}<br>
            <em>No donations in last 10 years</em>
        </p>"""

        if data['description']:
            section += f"<p><em>{data['description']}</em></p>"

        if data['evaluation']:
            section += f"""
        <p><strong>Charity Evaluation:</strong><br>
        ⭐ Outstanding: {data['evaluation'].outstanding_count} metrics<br>
        ✓ Acceptable: {data['evaluation'].acceptable_count} metrics<br>
        ⚠ Unacceptable: {data['evaluation'].unacceptable_count} metrics</p>"""

            score = data['evaluation'].alignment_score
            if score >= 90:
                alignment_label = "⭐ Excellent alignment"
            elif score >= 70:
                alignment_label = "✓ Good alignment"
            elif score >= 50:
                alignment_label = "~ Moderate alignment"
            elif score >= 30:
                alignment_label = "⚠ Limited alignment"
            elif score > 0:
                alignment_label = "✗ Poor alignment"
            else:
                alignment_label = "No alignment data"

            section += f"""
        <p><strong>Alignment with Your Goals: {data['evaluation'].alignment_score}/100</strong><br>
        {alignment_label}</p>
        <p><em>{data['evaluation'].summary}</em></p>"""

        section += "</div>"
        return section


class MarkdownFormatter(ReportFormatter):
    """Markdown-specific formatting"""

    def format_recurring_section(self, data):
        """Format recurring donations as Markdown table"""
        if data is None:
            return "\n## Recurring Donations\n\nNo recurring donations found.\n"

        section = f"\n## Recurring Donations\n\n"
        section += f"Organizations with recurring donations (4+ years) ({data['org_count']} organizations):\n\n"
        # Include Period column now that recurring analysis supplies it
        section += "| EIN | Organization | First Year | Years | Period | Amount | Total Ever Donated | Last Donation |\n"
        section += "|:----|:-------------|:----------:|:-----:|:------:|-------:|------------------:|:-------------|\n"

        for row in data['rows']:
            period = row.get('period', 'Unknown')
            section += f"| {row['ein']} | {row['organization']} | {row['first_year']} | {row['years']} | {period} | ${row['amount']:,.2f} | ${row['total_ever']:,.2f} | {row['last_date'].strftime('%Y-%m-%d')} |\n"

        if data['overflow_count'] > 0:
            section += f"\n*... and {data['overflow_count']} more organizations*\n"

        totals = data['totals']
        section += f"\n**Total annual recurring donations:** ${totals['total_recurring']:,.2f}\n"
        section += f"**Total ever donated to recurring causes:** ${totals['total_ever']:,.2f}\n"

        return section

    def format_charity_detail_section(self, data):
        """Format charity detail section as Markdown"""
        section = f"#### {data['index']}. {data['org_name']}\n\n"

        if data['has_graph']:
            section += f"| Charity Details | 10-Year Trend |\n"
            section += f"|:----------------|:-------------:|\n"
            section += f"| **Tax ID:** {data['tax_id']}<br>**Sector:** {data['sector']}<br>**Total Donated:** ${data['total_donated']:,.2f}<br>**Number of Donations:** {data['donation_count']} | ![10-year trend]({data['graph_filename']}) |\n\n"
        else:
            section += f"| Charity Details |\n"
            section += f"|:----------------|\n"
            section += f"| **Tax ID:** {data['tax_id']}<br>**Sector:** {data['sector']}<br>**Total Donated:** ${data['total_donated']:,.2f}<br>**Number of Donations:** {data['donation_count']}<br>*No donations in last 10 years* |\n\n"

        if data['description']:
            section += f"*{data['description']}*\n\n"

        if data['evaluation']:
            section += "**Charity Evaluation:**\n\n"
            section += f"- ⭐ Outstanding: {data['evaluation'].outstanding_count} metrics\n"
            section += f"- ✓ Acceptable: {data['evaluation'].acceptable_count} metrics\n"
            section += f"- ⚠ Unacceptable: {data['evaluation'].unacceptable_count} metrics\n\n"

            score = data['evaluation'].alignment_score
            if score >= 90:
                alignment_label = "⭐ Excellent alignment"
            elif score >= 70:
                alignment_label = "✓ Good alignment"
            elif score >= 50:
                alignment_label = "~ Moderate alignment"
            elif score >= 30:
                alignment_label = "⚠ Limited alignment"
            elif score > 0:
                alignment_label = "✗ Poor alignment"
            else:
                alignment_label = "No alignment data"

            section += f"**Alignment with Your Goals: {data['evaluation'].alignment_score}/100** - {alignment_label}\n\n"
            section += f"*{data['evaluation'].summary}*\n\n"

        return section


class TextFormatter(ReportFormatter):
    """Plain text formatting"""

    def format_recurring_section(self, data):
        """Format recurring donations as plain text table"""
        if data is None:
            return f"""RECURRING DONATIONS
{'-' * 80}

No recurring donations found.

"""

        section = f"""RECURRING DONATIONS
{'-' * 80}

Organizations with recurring donation schedules ({data['org_count']} organizations):

"""

        from tabulate import tabulate
        table_data = []
        for row in data['rows']:
            table_data.append([
                row['ein'],
                row['organization'][:40],
                row['first_year'],
                row['years'],
                f"${row['amount']:,.2f}",
                f"${row['total_ever']:,.2f}",
                row['last_date'].strftime('%Y-%m-%d')
            ])

        section += tabulate(table_data,
                           headers=['EIN', 'Organization', 'First Year', 'Years', 'Amount', 'Total Ever', 'Last Donation'],
                           tablefmt='simple')
        section += "\n"

        if data['overflow_count'] > 0:
            section += f"\n... and {data['overflow_count']} more organizations\n"

        totals = data['totals']
        section += f"\nTotal annual recurring donations: ${totals['total_recurring']:,.2f}\n"
        section += f"Total ever donated to recurring causes: ${totals['total_ever']:,.2f}\n\n"

        return section

    def format_charity_detail_section(self, data):
        """Format charity detail section as plain text"""
        section = f"""{data['index']}. {data['org_name']}
{'-' * 80}
Tax ID:              {data['tax_id']}
Sector:              {data['sector']}
Total Donated:       ${data['total_donated']:,.2f}
Number of Donations: {data['donation_count']}
"""

        if data['has_graph']:
            section += f"10-Year Trend:       {data['graph_filename']}\n"
        else:
            section += f"10-Year Trend:       No donations in last 10 years\n"

        if data['description']:
            section += f"\n{data['description']}\n"

        if data['evaluation']:
            section += f"\nCharity Evaluation:\n"
            section += f"  Outstanding:    {data['evaluation'].outstanding_count} metrics\n"
            section += f"  Acceptable:     {data['evaluation'].acceptable_count} metrics\n"
            section += f"  Unacceptable:   {data['evaluation'].unacceptable_count} metrics\n"

            score = data['evaluation'].alignment_score
            if score >= 90:
                alignment_label = "⭐ Excellent alignment"
            elif score >= 70:
                alignment_label = "✓ Good alignment"
            elif score >= 50:
                alignment_label = "~ Moderate alignment"
            elif score >= 30:
                alignment_label = "⚠ Limited alignment"
            elif score > 0:
                alignment_label = "✗ Poor alignment"
            else:
                alignment_label = "No alignment data"

            section += f"\nAlignment with Your Goals: {data['evaluation'].alignment_score}/100 ({alignment_label})\n"
            section += f"\n{data['evaluation'].summary}\n\n"

        return section
