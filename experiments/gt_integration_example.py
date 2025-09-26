#!/usr/bin/env python3
"""
Example showing how to integrate Great Tables into the main donation analysis program
"""

import pandas as pd
from great_tables import GT

def create_gt_category_table(category_totals, total_amount):
    """Convert category analysis to Great Tables format"""

    # Convert your existing category_totals Series to DataFrame format
    category_data = []
    for category, amount in category_totals.items():
        percentage = (amount / total_amount) * 100
        category_data.append([category, amount, percentage])

    df = pd.DataFrame(category_data, columns=['Charitable Sector', 'Total Amount', 'Percentage'])

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
            table_font_size="11px",
            heading_title_font_size="14px",
            heading_subtitle_font_size="10px",
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

def create_gt_top_charities_table(top_charities):
    """Convert top charities analysis to Great Tables format"""

    # Convert your existing top_charities DataFrame
    charity_data = []
    for i, (tax_id, data) in enumerate(top_charities.iterrows(), 1):
        org_name = data['Organization']
        tax_id_display = tax_id if pd.notna(tax_id) else 'N/A'
        charity_data.append([i, org_name, data['Amount_Numeric'], tax_id_display])

    df = pd.DataFrame(charity_data, columns=['Rank', 'Organization', 'Total Amount', 'Tax ID'])

    # Create Great Table
    gt_table = (
        GT(df)
        .tab_header(title="Top 10 Charities by Total Donations")
        .fmt_currency(columns="Total Amount", currency="USD", decimals=0)
        .cols_align(align="center", columns="Rank")
        .cols_align(align="left", columns="Organization")
        .cols_align(align="right", columns="Total Amount")
        .cols_align(align="center", columns="Tax ID")
        .tab_options(
            table_font_size="10px",
            heading_title_font_size="13px",
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

# INTEGRATION EXAMPLE: How to modify your existing generate_markdown_report function

def generate_markdown_report_with_gt(category_totals, yearly_amounts, yearly_counts, df,
                                   one_time, stopped_recurring, top_charities,
                                   charity_details, charity_descriptions, graph_info):
    """Modified version showing Great Tables integration"""

    total_amount = category_totals.sum()
    total_donations = len(df)

    # Start building report as before
    report = f'''# Charitable Donation Analysis Report

*Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}*

## Summary

- **Total Donations:** {total_donations:,} donations
- **Total Amount:** ${total_amount:,.2f}
- **Years Covered:** {df['Year'].min()} - {df['Year'].max()}

'''

    # OPTION 1: Save Great Tables as HTML files and reference them
    print("Creating Great Tables...")

    # Create category table
    gt_categories = create_gt_category_table(category_totals, total_amount)
    gt_categories.save("../output/gt_categories.html")

    # Create top charities table
    gt_charities = create_gt_top_charities_table(top_charities)
    gt_charities.save("../output/gt_charities.html")

    # Reference them in markdown
    report += '''## Donations by Charitable Sector

See the interactive table: [Category Breakdown](gt_categories.html)

'''

    # OPTION 2: Fall back to tabulate for inline markdown tables
    # (Keep your existing tabulate code for markdown compatibility)
    from tabulate import tabulate

    category_data = []
    for category, amount in category_totals.items():
        percentage = (amount / total_amount) * 100
        category_data.append([category, f"${amount:,.0f}", f"{percentage:.1f}%"])

    category_table = tabulate(category_data,
                            headers=["Charitable Sector", "Total Amount", "Percentage"],
                            tablefmt="simple")

    report += "### Text Version\n\n"
    report += category_table
    report += f"\n\n**Total:** ${total_amount:,.2f}\n\n"

    # Continue with rest of report...
    report += '''## Top Charities

See the interactive table: [Top Charities](gt_charities.html)

'''

    # Save the markdown report
    with open('../output/donation_analysis.md', 'w') as f:
        f.write(report)

    print("✅ Report generated with Great Tables!")
    print("📊 Interactive tables saved as HTML files")
    print("📄 Markdown report with links created")

# Example usage showing how simple the integration is:
if __name__ == "__main__":
    # Simulate your existing data structures
    import pandas as pd

    # Sample data (this would be your real category_totals from analyze_by_category)
    sample_categories = pd.Series({
        'Arts and Culture': 900600.00,
        'Society Benefit': 268225.00,
        'Environment and Animals': 211900.00,
        'Human Services': 209330.00,
        'International Affairs': 189250.00
    })

    # Show how easy it is to create Great Tables
    gt_table = create_gt_category_table(sample_categories, sample_categories.sum())

    print("INTEGRATION SUMMARY:")
    print("====================")
    print("✅ Add Great Tables import: from great_tables import GT")
    print("✅ Create helper functions (like above)")
    print("✅ Call gt_table.save() to export HTML")
    print("✅ Reference HTML files in your markdown")
    print("✅ Keep tabulate as fallback for inline tables")
    print("")
    print("EFFORT LEVEL: ⭐⭐ (Easy)")
    print("- Add ~50 lines of helper functions")
    print("- Modify generate_markdown_report() slightly")
    print("- Your existing data structures work as-is!")