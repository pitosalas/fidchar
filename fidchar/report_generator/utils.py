from typing import List, Dict, Any


def render_html_document(sections_html: str, doc_title: str, container_class: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="{container_class}">
{sections_html}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def render_html_with_extras(base_html: str, custom_styles: str, css_files: List[str]) -> str:
    styles_block = f"<style>\n{custom_styles}\n</style>"
    css_links = "\n  ".join(f'<link rel="stylesheet" href="{css_file}">' for css_file in css_files)
    head_close = "</head>"
    return base_html.replace(head_close, f"  {css_links}\n  {styles_block}\n{head_close}")


def wrap_with_header_footer(content_html: str, header_html: str, footer_html: str) -> str:
    return f"{header_html}\n{content_html}\n{footer_html}"


def render_profile_card(profile: Dict[str, Any]) -> str:
    eval_html = "".join(
        f"<li>{k}: {v} metrics</li>" for k, v in profile["evaluation"].items()
    )
    notes_html = "".join(f"<li>{note}</li>" for note in profile["notes"])
    return f"""
<div class="card mb-4">
  <div class="card-header"><strong>{profile['name']}</strong></div>
  <div class="card-body">
    <p><strong>Tax ID:</strong> {profile['tax_id']}<br>
       <strong>Sector:</strong> {profile['sector']}<br>
       <strong>Total Donations:</strong> {profile['total_donations']}<br>
       <strong>Number of Donations:</strong> {profile['num_donations']}<br>
       <strong>Alignment with Your Goals:</strong> {profile['alignment']}/100</p>
    <p><strong>Charity Evaluation:</strong></p>
    <ul>{eval_html}</ul>
    <p><strong>Additional Notes:</strong></p>
    <ul>{notes_html}</ul>
  </div>
</div>
"""


def render_profile_html(profiles: List[Dict[str, Any]], section_title: str) -> str:
    cards = [render_profile_card(p) for p in profiles]
    return f"<h2 class='mb-3'>{section_title}</h2>" + "\n".join(cards)