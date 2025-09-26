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
        'International Affairs',
        'Religion',
        'Education',
        'Health'
    ],
    'Total Amount': [900600.00, 268225.00, 211900.00, 209330.00, 189250.00, 182210.00, 140280.00, 107525.00],
    'Percentage': [40.5, 12.1, 9.5, 9.4, 8.5, 8.2, 6.3, 4.8]
}

df = pd.DataFrame(category_data)

# Create a compact, Tufte-style Great Table
gt_compact = (
    GT(df)
    .tab_header(
        title="Charitable Donations by Sector",
        subtitle="Compact, elegant presentation"
    )
    .fmt_currency(columns="Total Amount", currency="USD", decimals=0)  # No decimals for cleaner look
    .fmt_percent(columns="Percentage", scale_values=False, decimals=1)
    .cols_align(align="left", columns="Charitable Sector")
    .cols_align(align="right", columns=["Total Amount", "Percentage"])
    .tab_options(
        # Compact font sizes
        table_font_size="11px",
        heading_title_font_size="14px",
        heading_subtitle_font_size="10px",
        column_labels_font_size="10px",

        # Tighter spacing
        data_row_padding="4px",
        data_row_padding_horizontal="6px",
        heading_padding="2px",
        column_labels_padding="3px",

        # Minimal borders (Tufte style)
        table_border_top_style="none",
        table_border_bottom_style="solid",
        table_border_bottom_width="1px",
        table_border_bottom_color="#000000",

        # Clean column headers
        column_labels_border_top_style="none",
        column_labels_border_bottom_style="solid",
        column_labels_border_bottom_width="1px",
        column_labels_border_bottom_color="#000000",

        # Remove row lines for cleaner look
        table_body_hlines_style="none",

        # Compact table width
        table_width="400px"
    )
)

# Save compact version
html_output = gt_compact._render_as_html()

# Create complete HTML document
complete_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Compact Great Tables Demo</title>
    <style>
        body {{
            font-family: Georgia, serif;
            margin: 20px;
            background-color: #fafafa;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Compact Great Tables Example</h2>
        <p>This shows how Great Tables can be styled for compact, Tufte-inspired presentation:</p>
        {html_output}

        <h3>Styling Features:</h3>
        <ul>
            <li><strong>Smaller fonts:</strong> 11px body text, 14px title</li>
            <li><strong>Tighter spacing:</strong> Reduced padding throughout</li>
            <li><strong>Minimal borders:</strong> Only essential lines (Tufte principle)</li>
            <li><strong>Clean currency:</strong> No decimals for whole amounts</li>
            <li><strong>Compact width:</strong> 400px for embedding</li>
            <li><strong>Professional typography:</strong> Clean alignment and spacing</li>
        </ul>

        <p><em>This table could be embedded as an image alongside your Tufte-style graphs for a cohesive, elegant report.</em></p>
    </div>
</body>
</html>"""

with open("output/compact_great_tables_demo.html", "w") as f:
    f.write(complete_html)

print("✅ Compact Great Tables demo created!")
print("Open this file to see the compact, Tufte-style table:")
print("output/compact_great_tables_demo.html")
print("\nKey compact features:")
print("- 11px font size (down from 16px)")
print("- Minimal padding and spacing")
print("- Clean borders (Tufte style)")
print("- 400px width for easy embedding")
print("- No decimal places on whole dollar amounts")
print("- Professional typography with tight spacing")