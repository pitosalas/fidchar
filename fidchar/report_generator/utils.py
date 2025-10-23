from typing import List
from report_generator.models import ReportTable
from report_generator.renderers import HTMLSectionRenderer
from report_generator.profiles import get_charity_profiles

def render_html_document(tables: List[ReportTable], doc_title="Donation Reports",
                         custom_header=None, custom_footer=None, custom_styles=None,
                         css_files=None, container_class="container my-4") -> str:
    """Render a complete HTML document with Bootstrap CSS.

    Args:
        tables: List of ReportTable objects to render
        doc_title: HTML document title
        custom_header: Optional HTML to insert after opening container div
        custom_footer: Optional HTML to insert before closing container div
        custom_styles: Optional CSS to include in <style> tag
        css_files: Optional list of paths to external CSS files
        container_class: CSS classes for main container div

    Returns:
        Complete HTML document string
    """
    hr = HTMLSectionRenderer()
    sections = "\n".join(hr.render(t) for t in tables)

    styles_block = f"<style>\n{custom_styles}\n</style>" if custom_styles else ""
    css_links = "\n  ".join(f'<link rel="stylesheet" href="{css_file}">' for css_file in (css_files or []))
    header_block = custom_header if custom_header else ""
    footer_block = custom_footer if custom_footer else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  {css_links}
  {styles_block}
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


def render_profile_html() -> str:
    profiles = get_charity_profiles()
    cards = []
    for p in profiles:
        eval_html = "".join(f"<li>{k}: {v} metrics</li>" for k, v in p["evaluation"].items())
        notes_html = "".join(f"<li>{note}</li>" for note in p["notes"])
        card = f"""
<div class="card mb-4">
  <div class="card-header"><strong>{p['name']}</strong></div>
  <div class="card-body">
    <p><strong>Tax ID:</strong> {p['tax_id']}<br>
       <strong>Sector:</strong> {p['sector']}<br>
       <strong>Total Donations:</strong> {p['total_donations']}<br>
       <strong>Number of Donations:</strong> {p['num_donations']}<br>
       <strong>Alignment with Your Goals:</strong> {p['alignment']}/100</p>
    <p><strong>Charity Evaluation:</strong></p>
    <ul>{eval_html}</ul>
    <p><strong>Additional Notes:</strong></p>
    <ul>{notes_html}</ul>
  </div>
</div>
"""
        cards.append(card)
    return "<h2 class='mb-3'>Charity Evaluation Profiles</h2>" + "\n".join(cards)