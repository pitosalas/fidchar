#!/usr/bin/env python3
"""HTML templates for report generation.

This module contains all HTML template functions to separate presentation
from business logic in the report builder.
"""


def recurring_charities_section(min_years, min_amount, count, total, columns_html):
    """Template for recurring charities summary section."""
    return f"""
    <div class="report-section">
        <h2 class="section-title">Recurring Charities (≥{min_years} years, ≥${min_amount:,}/year)</h2>
        <p>{count} charities meeting recurring threshold - at least {min_years} years with ${min_amount:,}+ donations:</p>
{columns_html}
        <p class="fw-bold mt-4">
            Total donated to recurring charities: ${total:,.2f}
        </p>
    </div>"""


def csv_recurring_section(csv_count, display_count, table_html, total_amount):
    """Template for CSV-based recurring charities section."""
    return f"""
    <div class="report-section">
        <h2 class="section-title">CSV-Based Recurring Charities</h2>
        <p>Charities marked as recurring in Fidelity's export (from "Recurring" field)</p>
        <p>{csv_count} total recurring charities (showing top {display_count})</p>
        {table_html}
        <p class="fw-bold mt-4">
            Total donated to CSV-based recurring charities: ${total_amount:,.2f}
        </p>
    </div>"""


def combined_recurring_section(min_years, min_amount, total_count, display_count,
                               active_count, breakdown, table_html, total_amount):
    """Template for combined recurring charities section."""
    return f"""
    <div class="report-section">
        <h2 class="section-title">Recurring Charities</h2>
        <p>Combines charities from rule-based detection (≥{min_years} years, ≥${min_amount:,}/year), CSV field (Fidelity's recurring marker), and stopped recurring donations</p>
        <p>{total_count} total charities (showing top {display_count}): {active_count} active ({breakdown})</p>
        {table_html}
        <p class="fw-bold mt-4">
            Total donated to all listed charities: ${total_amount:,.2f}
        </p>
    </div>"""


def all_charities_section(title, subtitle, table_html, total_amount):
    """Template for all charities section with configurable subtitle."""
    return f"""
    <div class="report-section">
        <h2 class="section-title">{title}</h2>
        <p>{subtitle}</p>
        {table_html}
        <p class="fw-bold mt-4">
            Total donated to all charities: ${total_amount:,.2f}
        </p>
    </div>"""


def remaining_charities_section(count, min_years, min_amount, columns_html, total):
    """Template for remaining charities section."""
    return f"""
    <div class="report-section">
        <h2 class="section-title">Remaining Charities ({count} organizations)</h2>
        <p>Multi-year, multi-donation charities that don't meet the recurring threshold ({min_years} years with ${min_amount:,}+ each year). These represent sustained giving relationships at lower amounts or fewer qualifying years.</p>
{columns_html}
        <p class="fw-bold mt-4">
            Total donated to remaining charities: ${total:,.2f}
        </p>
    </div>"""


def sectors_section(categories_html):
    """Template for sectors section with categories and yearly graphs."""
    return f"""
    <div class="report-section section-sectors">
        <div class="row">
            <div class="col-md-5">
                {categories_html}
            </div>
            <div class="col-md-7">
                <h2 class="section-title">Yearly Analysis</h2>
                <div class="text-center">
                    <img src="images/yearly_amounts.png" alt="Yearly Donation Amounts" class="img-fluid mb-2" style="max-width: 100%;">
                    <img src="images/yearly_counts.png" alt="Yearly Donation Counts" class="img-fluid" style="max-width: 100%;">
                </div>
            </div>
        </div>
    </div>"""


def yearly_section(yearly_html):
    """Template for yearly table section."""
    return f"""
    <div class="report-section section-yearly">
        {yearly_html}
    </div>"""


def top_charities_section(top_charities_html):
    """Template for top charities section."""
    return f"""
    <div class="report-section section-top-charities">
        {top_charities_html}
    </div>"""


def patterns_section(one_time_table, one_time_total, one_time_overflow,
                     stopped_table, stopped_total, stopped_overflow):
    """Template for patterns section with one-time and stopped donations."""
    html = f"""
    <div class="report-section section-patterns">
        {one_time_table}"""

    if one_time_overflow > 0:
        html += f"""
        <p><em>... and {one_time_overflow} more organizations</em></p>"""

    html += f"""
        <p class="mt-3"><strong>One-time donations total:</strong> ${one_time_total:,.2f}</p>

        {stopped_table}"""

    if stopped_overflow > 0:
        html += f"""
        <p><em>... and {stopped_overflow} more organizations</em></p>"""

    html += f"""
        <p class="mt-3"><strong>Stopped recurring donations total:</strong> ${stopped_total:,.2f}</p>
    </div>"""

    return html


def no_recurring_charities():
    """Template for when no recurring charities are found."""
    return """
    <div class="report-section">
        <h2 class="section-title">Recurring Charities Summary</h2>
        <p>No recurring charities identified.</p>
    </div>"""


def no_csv_recurring_charities():
    """Template for when no CSV recurring charities are found."""
    return """
    <div class="report-section">
        <h2 class="section-title">CSV-Based Recurring Charities</h2>
        <p>No CSV-based recurring charities found.</p>
    </div>"""


def no_combined_recurring_charities():
    """Template for when no combined recurring charities are found."""
    return """
    <div class="report-section">
        <h2 class="section-title">Recurring Charities</h2>
        <p>No recurring charities found.</p>
    </div>"""


def no_all_charities():
    """Template for when no charities are found."""
    return """
    <div class="report-section">
        <h2 class="section-title">All Charities</h2>
        <p>No charities found.</p>
    </div>"""


def no_remaining_charities():
    """Template for when no remaining charities are found."""
    return """
    <div class="report-section">
        <h2 class="section-title">Remaining Charities</h2>
        <p>No remaining charities to display.</p>
    </div>"""
