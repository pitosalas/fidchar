#!/usr/bin/env python3
"""Great Tables builder for creating beautiful HTML tables.

Provides typeset-quality table generation using Great Tables.
"""

import pandas as pd
from great_tables import GT


def create_gt_category_table(category_totals, total_amount):
    """Create category summary table using Great Tables"""
    # Convert to DataFrame
    category_data = []
    for category, amount in category_totals.items():
        percentage = (amount / total_amount) * 100
        category_data.append([category, amount, percentage])

    df = pd.DataFrame(category_data, columns=["Charitable Sector", "Total Amount", "Percentage"])

    # Create Great Table with compact Tufte styling
    gt_table = (
        GT(df)
        .tab_header(
            title="Donations by Charitable Sector",
            subtitle=f"Total: ${total_amount:,.0f}"
        )
        .fmt_currency(columns="Total Amount", currency="USD", decimals=0)
        .fmt_percent(columns="Percentage", scale_values=False, decimals=1)
        .cols_align(align="left", columns="Charitable Sector")
        .cols_align(align="right", columns=["Total Amount", "Percentage"])
        .tab_options(
            table_font_size="13px",
            heading_title_font_size="16px",
            heading_subtitle_font_size="12px",
            data_row_padding="4px",
            table_width="450px",
            # Tufte-style minimal borders
            table_border_top_style="none",
            table_border_bottom_style="solid",
            table_border_bottom_width="1px",
            column_labels_border_bottom_style="solid",
            column_labels_border_bottom_width="1px",
            table_body_hlines_style="none"
        )
    )

    return gt_table


def create_gt_yearly_table(yearly_amounts, yearly_counts):
    """Create yearly analysis table using Great Tables"""
    # Convert to DataFrame
    yearly_data = []
    for year in sorted(yearly_amounts.index):
        amount = yearly_amounts[year]
        count = yearly_counts[year]
        yearly_data.append([year, amount, count])

    df = pd.DataFrame(yearly_data, columns=["Year", "Total Amount", "Number of Donations"])

    gt_table = (
        GT(df)
        .tab_header(title="Yearly Donation Analysis")
        .fmt_currency(columns="Total Amount", currency="USD", decimals=0)
        .cols_align(align="center", columns="Year")
        .cols_align(align="right", columns=["Total Amount", "Number of Donations"])
        .tab_options(
            table_font_size="12px",
            heading_title_font_size="15px",
            data_row_padding="3px",
            table_width="400px",
            table_border_top_style="none",
            table_border_bottom_style="solid",
            table_border_bottom_width="1px",
            column_labels_border_bottom_style="solid",
            column_labels_border_bottom_width="1px",
            table_body_hlines_style="none"
        )
    )

    return gt_table


def create_gt_consistent_donors_table(consistent_donors):
    """Create consistent donors table using Great Tables"""
    # Convert to DataFrame
    data_rows = []
    for tax_id, donor_info in consistent_donors.items():
        data_rows.append([
            donor_info['organization'],
            tax_id,
            donor_info['sector'],
            donor_info['total_5_year'],
            donor_info['average_per_year']
        ])

    df = pd.DataFrame(data_rows, columns=[
        "Organization", "Tax ID", "Sector", "5-Year Total", "Average/Year"
    ])

    # Sort by 5-Year Total in descending order
    df = df.sort_values("5-Year Total", ascending=False)

    gt_table = (
        GT(df)
        .tab_header(
            title="Consistent Donors (Last 5 Years)",
            subtitle="Organizations with $500+ annually for 5 consecutive years"
        )
        .fmt_currency(columns=["5-Year Total", "Average/Year"], currency="USD", decimals=0)
        .cols_align(align="left", columns=["Organization", "Sector"])
        .cols_align(align="center", columns="Tax ID")
        .cols_align(align="right", columns=["5-Year Total", "Average/Year"])
        .tab_options(
            table_font_size="12px",
            heading_title_font_size="15px",
            heading_subtitle_font_size="11px",
            data_row_padding="3px",
            table_width="700px",
            table_border_top_style="none",
            table_border_bottom_style="solid",
            table_border_bottom_width="1px",
            column_labels_border_bottom_style="solid",
            column_labels_border_bottom_width="1px",
            table_body_hlines_style="none"
        )
    )

    return gt_table


def create_gt_top_charities_table(top_charities):
    """Create top charities table using Great Tables"""
    # Convert to DataFrame
    data_rows = []
    for i, (tax_id, data) in enumerate(top_charities.iterrows(), 1):
        org_name = data["Organization"]
        tax_id_display = tax_id if pd.notna(tax_id) else "N/A"
        data_rows.append([i, org_name, data["Amount_Numeric"], tax_id_display])

    df = pd.DataFrame(data_rows, columns=["Rank", "Organization", "Total Amount", "Tax ID"])

    gt_table = (
        GT(df)
        .tab_header(title="Top 10 Charities by Total Donations")
        .fmt_currency(columns="Total Amount", currency="USD", decimals=0)
        .cols_align(align="center", columns="Rank")
        .cols_align(align="left", columns="Organization")
        .cols_align(align="right", columns="Total Amount")
        .cols_align(align="center", columns="Tax ID")
        .tab_options(
            table_font_size="12px",
            heading_title_font_size="15px",
            data_row_padding="3px",
            table_width="600px",
            table_border_top_style="none",
            table_border_bottom_style="solid",
            table_border_bottom_width="1px",
            column_labels_border_bottom_style="solid",
            column_labels_border_bottom_width="1px",
            table_body_hlines_style="none"
        )
    )

    return gt_table


def create_comprehensive_html_report(category_totals, yearly_amounts, yearly_counts,
                                   consistent_donors, top_charities, total_amount, df,
                                   one_time, stopped_recurring, charity_details=None,
                                   charity_descriptions=None, graph_info=None, config=None):
    """Create a comprehensive HTML report with all tables"""
    from comprehensive_report import (
        create_comprehensive_html_report as create_report,
        add_table_sections_to_report, add_detailed_charity_analysis
    )

    # Create all tables
    gt_categories = create_gt_category_table(category_totals, total_amount)
    gt_yearly = create_gt_yearly_table(yearly_amounts, yearly_counts)
    gt_consistent = create_gt_consistent_donors_table(consistent_donors)
    gt_top_charities = create_gt_top_charities_table(top_charities)

    # Generate initial HTML structure
    html_content = create_report(
        category_totals, yearly_amounts, yearly_counts, consistent_donors,
        top_charities, total_amount, df, one_time, stopped_recurring
    )

    # Add table sections
    consistent_total = sum(donor['total_5_year'] for donor in consistent_donors.values())
    html_content = add_table_sections_to_report(
        html_content, gt_consistent, gt_categories, gt_yearly, gt_top_charities, consistent_total, config
    )

    # Add detailed charity analysis if data is provided
    if charity_details and charity_descriptions and graph_info:
        html_content = add_detailed_charity_analysis(
            html_content, top_charities, charity_details, charity_descriptions, graph_info
        )
    else:
        html_content += """
</body>
</html>"""

    return html_content


def save_all_gt_tables(category_totals, yearly_amounts, yearly_counts,
                      consistent_donors, top_charities, total_amount, df=None,
                      one_time=None, stopped_recurring=None, charity_details=None,
                      charity_descriptions=None, graph_info=None):
    """Generate and save all Great Tables as HTML files"""

    # Create all tables
    gt_categories = create_gt_category_table(category_totals, total_amount)
    gt_yearly = create_gt_yearly_table(yearly_amounts, yearly_counts)
    gt_consistent = create_gt_consistent_donors_table(consistent_donors)
    gt_top_charities = create_gt_top_charities_table(top_charities)

    # Save individual HTML files
    try:
        # Use as_raw_html() method to get HTML content and write to files
        with open("../output/gt_categories.html", "w") as f:
            f.write(gt_categories.as_raw_html())
        with open("../output/gt_yearly.html", "w") as f:
            f.write(gt_yearly.as_raw_html())
        with open("../output/gt_consistent_donors.html", "w") as f:
            f.write(gt_consistent.as_raw_html())
        with open("../output/gt_top_charities.html", "w") as f:
            f.write(gt_top_charities.as_raw_html())

        # Create comprehensive HTML report
        if df is not None and one_time is not None and stopped_recurring is not None:
            comprehensive_html = create_comprehensive_html_report(
                category_totals, yearly_amounts, yearly_counts,
                consistent_donors, top_charities, total_amount, df,
                one_time, stopped_recurring, charity_details,
                charity_descriptions, graph_info, config
            )
        else:
            # Fallback to basic version if data not provided
            comprehensive_html = create_comprehensive_html_report(
                category_totals, yearly_amounts, yearly_counts,
                consistent_donors, top_charities, total_amount, df or pd.DataFrame(),
                one_time or pd.DataFrame(), stopped_recurring or pd.DataFrame(), config=config
            )

        with open("../output/comprehensive_report.html", "w") as f:
            f.write(comprehensive_html)

        return {
            "categories": "gt_categories.html",
            "yearly": "gt_yearly.html",
            "consistent": "gt_consistent_donors.html",
            "top_charities": "gt_top_charities.html",
            "comprehensive": "comprehensive_report.html"
        }
    except Exception as e:
        print(f"Warning: Could not save Great Tables HTML files: {e}")
        return None