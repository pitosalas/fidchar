#!/usr/bin/env python3
"""Report formatters for different output formats.

These classes handle ONLY formatting - no business logic.
"""

from abc import ABC, abstractmethod
import pandas as pd


class ReportFormatter(ABC):
    """Abstract base formatter - defines interface"""

    @abstractmethod
    def format_charity_detail_section(self, data):
        """Format charity detail section with prepared data"""
        pass

    @abstractmethod
    def format_focus_summary_section(self, data):
        """Format focus charities summary section with prepared data"""
        pass

    def _get_alignment_label(self, score):
        """Map alignment score to label - shared across all formatters"""
        if score >= 90:
            return "⭐ Excellent alignment"
        elif score >= 70:
            return "✓ Good alignment"
        elif score >= 50:
            return "~ Moderate alignment"
        elif score >= 30:
            return "⚠ Limited alignment"
        elif score > 0:
            return "✗ Poor alignment"
        else:
            return "No alignment data"


class HTMLFormatter(ReportFormatter):
    """HTML-specific formatting"""

    def __init__(self, builder=None):
        self.builder = builder

    def _table_start(self, headers):
        """Generate HTML table start with headers"""
        header_cells = ""
        for header_text, align in headers:
            header_cells += f'<th style="padding: 10px; text-align: {align};">{header_text}</th>\n                '

        return f"""    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <thead>
            <tr style="background: #f8f9fa; border-bottom: 2px solid #333;">
                {header_cells}</tr>
        </thead>
        <tbody>"""

    def _table_end(self):
        """Generate HTML table end"""
        return """
        </tbody>
    </table>"""

    def _table_row(self, cells, row_index):
        """Generate HTML table row with alternating colors"""
        bg_color = "#f8f9fa" if row_index % 2 == 0 else "white"
        cell_html = ""
        for content, align in cells:
            cell_html += f'<td style="padding: 8px; text-align: {align};">{content}</td>\n                '

        return f"""            <tr style="background: {bg_color}; border-bottom: 1px solid #ddd;">
                {cell_html}</tr>"""

    def format_charity_detail_section(self, data):
        """Format charity detail section as HTML"""
        charity_info = self.builder.format_charity_info(data['tax_id'], data['org_name'])
        section = f"<div><h3>{data['index']}. {charity_info['html_org']}</h3>"

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

            alignment_label = self._get_alignment_label(data['evaluation'].alignment_score)
            section += f"""
        <p><strong>Alignment with Your Goals: {data['evaluation'].alignment_score}/100</strong><br>
        {alignment_label}</p>
        <p><em>{data['evaluation'].summary}</em></p>"""

        section += "</div>"
        return section

    def format_focus_summary_section(self, data):
        """Format focus charities summary as HTML"""
        if data is None:
            return """
    <div class="report-section">
        <h2 class="section-title">Focus Charities Summary</h2>
        <p>No focus charities identified.</p>
    </div>"""

        table_html = """
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <thead>
            <tr style="background: #f8f9fa; border-bottom: 2px solid #333;">
                <th style="padding: 10px; text-align: left;">EIN</th>
                <th style="padding: 10px; text-align: left;">Organization</th>
                <th style="padding: 10px; text-align: right;">Total Donated</th>
                <th style="padding: 10px; text-align: left;">Last Donation</th>
            </tr>
        </thead>
        <tbody>"""

        for i, row in enumerate(data['rows']):
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'
            table_html += f"""
            <tr style="background: {bg_color}; border-bottom: 1px solid #ddd;">
                <td style="padding: 8px;">{row['ein']}</td>
                <td style="padding: 8px;">{row['organization']}</td>
                <td style="padding: 8px; text-align: right;">${row['total_donated']:,.2f}</td>
                <td style="padding: 8px;">{last_date_str}</td>
            </tr>"""

        table_html += """
        </tbody>
    </table>"""

        return f"""
    <div class="report-section">
        <h2 class="section-title">Focus Charities Summary</h2>
        <p>{data['count']} charities identified as strategic focus based on your donation patterns:</p>
        {table_html}
        <p style="margin-top: 15px;"><strong>Total donated to focus charities:</strong> ${data['total']:,.2f}</p>
    </div>"""

    def format_category_table(self, category_totals, total_amount):
        """Format category table as HTML"""
        headers = [
            ("Charitable Sector", "left"),
            ("Total Amount", "right"),
            ("Percentage", "right")
        ]
        table_html = self._table_start(headers)

        for i, (category, amount) in enumerate(category_totals.items()):
            percentage = (amount / total_amount) * 100
            cells = [
                (category, "left"),
                (f"${amount:,.0f}", "right"),
                (f"{percentage:.1f}%", "right")
            ]
            table_html += "\n" + self._table_row(cells, i)

        table_html += self._table_end()
        return table_html

    def format_yearly_table(self, yearly_amounts, yearly_counts):
        """Format yearly analysis table as HTML"""
        headers = [
            ("Year", "center"),
            ("Total Amount", "right"),
            ("Number of Donations", "right")
        ]
        table_html = self._table_start(headers)

        for i, year in enumerate(sorted(yearly_amounts.index)):
            amount = yearly_amounts[year]
            count = yearly_counts[year]
            cells = [
                (str(year), "center"),
                (f"${amount:,.0f}", "right"),
                (str(count), "right")
            ]
            table_html += "\n" + self._table_row(cells, i)

        table_html += self._table_end()
        return table_html

    def format_top_charities_table(self, top_charities):
        """Format top charities table as HTML"""
        headers = [
            ("Rank", "center"),
            ("Organization", "left"),
            ("Total Amount", "right"),
            ("Tax ID", "center")
        ]
        table_html = self._table_start(headers)

        for i, (tax_id, data) in enumerate(top_charities.iterrows(), 1):
            charity_info = self.builder.format_charity_info(tax_id, data["Organization"])
            tax_id_display = tax_id if pd.notna(tax_id) else "N/A"
            cells = [
                (str(i), "center"),
                (charity_info['html_org'], "left"),
                (f"${data['Amount_Numeric']:,.0f}", "right"),
                (tax_id_display, "center")
            ]
            table_html += "\n" + self._table_row(cells, i - 1)

        table_html += self._table_end()
        return table_html

    def format_one_time_table(self, one_time, max_shown=20):
        """Format one-time donations table as HTML"""
        headers = [
            ("Organization", "left"),
            ("Amount", "right"),
            ("Date", "center")
        ]
        table_html = self._table_start(headers)

        for i, (tax_id, data) in enumerate(one_time.head(max_shown).iterrows()):
            org_name = data["Organization_Name"]
            cells = [
                (org_name, "left"),
                (f"${data['Total_Amount']:,.2f}", "right"),
                (data["First_Date"].strftime("%m/%d/%Y"), "center")
            ]
            table_html += "\n" + self._table_row(cells, i)

        table_html += self._table_end()
        return table_html

    def format_stopped_recurring_table(self, stopped_recurring, max_shown=15):
        """Format stopped recurring donations table as HTML"""
        headers = [
            ("Organization", "left"),
            ("Total Amount", "right"),
            ("Donations", "center"),
            ("First Date", "center"),
            ("Last Date", "center")
        ]
        table_html = self._table_start(headers)

        for i, (tax_id, data) in enumerate(stopped_recurring.head(max_shown).iterrows()):
            org_name = data["Organization_Name"]
            cells = [
                (org_name, "left"),
                (f"${data['Total_Amount']:,.2f}", "right"),
                (str(data["Donation_Count"]), "center"),
                (data["First_Date"].strftime("%m/%d/%Y"), "center"),
                (data["Last_Date"].strftime("%m/%d/%Y"), "center")
            ]
            table_html += "\n" + self._table_row(cells, i)

        table_html += self._table_end()
        return table_html


class MarkdownFormatter(ReportFormatter):
    """Markdown-specific formatting"""

    def __init__(self, builder=None):
        self.builder = builder

    def format_charity_detail_section(self, data):
        """Format charity detail section as Markdown"""
        charity_info = self.builder.format_charity_info(data['tax_id'], data['org_name'])
        section = f"#### {data['index']}. {charity_info['markdown_org']}\n\n"

        if data['has_graph']:
            section += "| Charity Details | 10-Year Trend |\n"
            section += "|:----------------|:-------------:|\n"
            section += f"| **Tax ID:** {data['tax_id']}<br>**Sector:** {data['sector']}<br>**Total Donated:** ${data['total_donated']:,.2f}<br>**Number of Donations:** {data['donation_count']} | ![10-year trend]({data['graph_filename']}) |\n\n"
        else:
            section += "| Charity Details |\n"
            section += "|:----------------|\n"
            section += f"| **Tax ID:** {data['tax_id']}<br>**Sector:** {data['sector']}<br>**Total Donated:** ${data['total_donated']:,.2f}<br>**Number of Donations:** {data['donation_count']}<br>*No donations in last 10 years* |\n\n"

        if data['description']:
            section += f"*{data['description']}*\n\n"

        if data['evaluation']:
            section += "**Charity Evaluation:**\n\n"
            section += f"- ⭐ Outstanding: {data['evaluation'].outstanding_count} metrics\n"
            section += f"- ✓ Acceptable: {data['evaluation'].acceptable_count} metrics\n"
            section += f"- ⚠ Unacceptable: {data['evaluation'].unacceptable_count} metrics\n\n"

            alignment_label = self._get_alignment_label(data['evaluation'].alignment_score)
            section += f"**Alignment with Your Goals: {data['evaluation'].alignment_score}/100** - {alignment_label}\n\n"
            section += f"*{data['evaluation'].summary}*\n\n"

        return section

    def format_focus_summary_section(self, data):
        """Format focus charities summary as Markdown"""
        if data is None:
            return "\n## Focus Charities Summary\n\nNo focus charities identified.\n"

        section = "\n## Focus Charities Summary\n\n"
        section += f"{data['count']} charities identified as strategic focus based on your donation patterns:\n\n"
        section += "| EIN | Organization | Total Donated | Last Donation |\n"
        section += "|:----|:-------------|-------------:|:-------------|\n"

        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'
            section += f"| {row['ein']} | {row['organization']} | ${row['total_donated']:,.2f} | {last_date_str} |\n"

        section += f"\n**Total donated to focus charities:** ${data['total']:,.2f}\n\n"

        return section


class TextFormatter(ReportFormatter):
    """Plain text formatting"""

    def __init__(self, builder=None):
        self.builder = builder

    def format_charity_detail_section(self, data):
        """Format charity detail section as plain text"""
        charity_info = self.builder.format_charity_info(data['tax_id'], data['org_name'])
        section = f"""{data['index']}. {charity_info['text_org']}
{'-' * 80}
Tax ID:              {data['tax_id']}
Sector:              {data['sector']}
Total Donated:       ${data['total_donated']:,.2f}
Number of Donations: {data['donation_count']}
"""

        if data['has_graph']:
            section += f"10-Year Trend:       {data['graph_filename']}\n"
        else:
            section += "10-Year Trend:       No donations in last 10 years\n"

        if data['description']:
            section += f"\n{data['description']}\n"

        if data['evaluation']:
            section += "\nCharity Evaluation:\n"
            section += f"  Outstanding:    {data['evaluation'].outstanding_count} metrics\n"
            section += f"  Acceptable:     {data['evaluation'].acceptable_count} metrics\n"
            section += f"  Unacceptable:   {data['evaluation'].unacceptable_count} metrics\n"

            alignment_label = self._get_alignment_label(data['evaluation'].alignment_score)
            section += f"\nAlignment with Your Goals: {data['evaluation'].alignment_score}/100 ({alignment_label})\n"
            section += f"\n{data['evaluation'].summary}\n\n"

        return section

    def format_focus_summary_section(self, data):
        """Format focus charities summary as plain text"""
        if data is None:
            return f"""FOCUS CHARITIES SUMMARY
{'-' * 80}

No focus charities identified.

"""

        section = f"""FOCUS CHARITIES SUMMARY
{'-' * 80}

{data['count']} charities identified as strategic focus based on your donation patterns:

"""

        from tabulate import tabulate
        table_data = []
        for row in data['rows']:
            last_date_str = row['last_date'].strftime('%Y-%m-%d') if row['last_date'] else 'N/A'
            table_data.append([
                row['ein'],
                row['organization'][:40],
                f"${row['total_donated']:,.2f}",
                last_date_str
            ])

        section += tabulate(table_data,
                           headers=['EIN', 'Organization', 'Total Donated', 'Last Donation'],
                           tablefmt='simple')
        section += "\n"
        section += f"\nTotal donated to focus charities: ${data['total']:,.2f}\n\n"

        return section
