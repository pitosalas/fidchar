#!/usr/bin/env python3

import pandas as pd
from great_tables import GT

# Sample data from your donation analysis
category_data = {
    'Charitable Sector': [
        'Arts and Culture',
        'Society Benefit',
        'Environment and Animals',
        'Human Services',
        'International Affairs'
    ],
    'Total Amount': [900600.00, 268225.00, 211900.00, 209330.00, 189250.00],
    'Percentage': [40.5, 12.1, 9.5, 9.4, 8.5]
}

df = pd.DataFrame(category_data)

# Create a beautiful Great Table
gt_table = (
    GT(df)
    .tab_header(
        title="Charitable Donations by Sector",
        subtitle="Elegant typeset presentation"
    )
    .fmt_currency(columns="Total Amount", currency="USD")
    .fmt_percent(columns="Percentage", scale_values=False, decimals=1)
    .cols_align(align="left", columns="Charitable Sector")
    .cols_align(align="right", columns=["Total Amount", "Percentage"])
)

# Save as HTML file you can open
try:
    gt_table.save("output/great_tables_demo.html")
    print("✅ Great Tables demo saved!")
    print("Open this file in your browser:")
    print("output/great_tables_demo.html")
    print("\nThis will show you the beautiful typeset table with:")
    print("- Professional typography")
    print("- Perfect currency formatting")
    print("- Clean borders and spacing")
    print("- Title and subtitle")
    print("- Publication-quality appearance")
except Exception as e:
    print(f"Error saving HTML: {e}")
    print("But we can still show you the table structure...")

# Also show the raw HTML to see what it generates
print("\n=== RAW HTML OUTPUT (first 500 chars) ===")
html_output = gt_table._render_as_html()
print(html_output[:500] + "...")