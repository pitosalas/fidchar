#!/usr/bin/env python3
"""Report formatters for different output formats.

These classes handle ONLY formatting - no business logic.
"""

from abc import ABC, abstractmethod
import pandas as pd


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
            charity_info = self.builder.format_charity_info(row['ein'], row['organization'])
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            table_html += f"""
            <tr style="background: {bg_color}; border-bottom: 1px solid #ddd;">
                <td style="padding: 8px;">{row['ein']}</td>
                <td style="padding: 8px;">{charity_info['html_org']}</td>
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


class MarkdownFormatter(ReportFormatter):
    """Markdown-specific formatting"""

    def __init__(self, builder=None):
        self.builder = builder

    def format_recurring_section(self, data):
        """Format recurring donations as Markdown table"""
        if data is None:
            return "\n## Recurring Donations\n\nNo recurring donations found.\n"
        section = "\n## Recurring Donations\n\n"
        section += f"Organizations with recurring donations (4+ years) ({data['org_count']} organizations):\n\n"
        # Include Period column now that recurring analysis supplies it
        section += "| EIN | Organization | First Year | Years | Period | Amount | Total Ever Donated | Last Donation |\n"
        section += "|:----|:-------------|:----------:|:-----:|:------:|-------:|------------------:|:-------------|\n"

        for row in data['rows']:
            period = row.get('period', 'Unknown')
            charity_info = self.builder.format_charity_info(row['ein'], row['organization'])
            org_name = charity_info['markdown_org']
            section += f"| {row['ein']} | {org_name} | {row['first_year']} | {row['years']} | {period} | ${row['amount']:,.2f} | ${row['total_ever']:,.2f} | {row['last_date'].strftime('%Y-%m-%d')} |\n"

        if data['overflow_count'] > 0:
            section += f"\n*... and {data['overflow_count']} more organizations*\n"

        totals = data['totals']
        section += f"\n**Total annual recurring donations:** ${totals['total_recurring']:,.2f}\n"
        section += f"**Total ever donated to recurring causes:** ${totals['total_ever']:,.2f}\n"

        return section

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
            charity_info = self.builder.format_charity_info(row['ein'], row['organization'])
            org_name = charity_info['text_org'][:40]
            table_data.append([
                row['ein'],
                org_name,
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
