from report_generator.models import ReportTable, ReportCard, CardSection

class TableRenderer:
    def render(self, table: ReportTable) -> str:
        raise NotImplementedError

class HTMLSectionRenderer(TableRenderer):
    def render(self, table: ReportTable) -> str:
        html: list[str] = []
        if table.title:
            html.append(f"<h2 class='mb-3'>{table.title}</h2>")
        html.append("<div class='table-responsive mb-4'>")
        html.append("<table class='table table-bordered table-striped'>")
        html.append("<thead class='table-dark'><tr>" + "".join(f"<th>{c}</th>" for c in table.columns) + "</tr></thead>")
        html.append("<tbody>")
        for i, row in enumerate(table.rows):
            cells = []
            for j, cell in enumerate(row):
                if j == 0:
                    # Add RECURRING badge if applicable
                    if table.recurring_flags and i < len(table.recurring_flags) and table.recurring_flags[i]:
                        cell = f"{cell} <span class='badge bg-warning text-dark ms-2'>RECURRING</span>"
                    # Add alignment badge if applicable
                    if table.alignment_flags and i < len(table.alignment_flags):
                        if table.alignment_flags[i] == 'Yes':
                            cell = f"{cell} <span class='badge bg-success ms-2'>ALIGNED</span>"
                        elif table.alignment_flags[i] == 'No':
                            cell = f"{cell} <span class='badge bg-danger ms-2'>NOT ALIGNED</span>"
                cells.append(f"<td>{cell}</td>")
            html.append("<tr>" + "".join(cells) + "</tr>")
        html.append("</tbody></table></div>")
        if table.footnotes:
            html.append("<div class='mb-4'><strong>Footnotes:</strong><ul>")
            for note in table.footnotes:
                html.append(f"<li>{note}</li>")
            html.append("</ul></div>")
        if table.source:
            html.append(f"<div class='mb-4'><em>Source: {table.source}</em></div>")
        return "\n".join(html)


class HTMLCardRenderer:
    """Render Bootstrap card component - general purpose, data-driven"""

    def __init__(self):
        # Dispatch table for section rendering
        self._section_renderers = {
            "text": self._render_text_section,
            "key_value": self._render_key_value_section,
            "list": self._render_list_section,
            "progress_bar": self._render_progress_section,
            "table": self._render_table_section,
        }

    def render(self, card: ReportCard) -> str:
        html = []
        html.append("<div class='card mb-4'>")

        header_class = "card-header bg-primary text-white"
        badge_html = f" <span class='badge bg-warning text-dark float-end'>{card.badge}</span>" if card.badge else ""
        html.append(f"<div class='{header_class}'><h4 class='mb-0'>{card.title}{badge_html}</h4></div>")

        html.append("<div class='card-body'>")

        if card.image_url and card.image_position in ["top"]:
            html.append(f"<img src='{card.image_url}' class='img-fluid mb-3' alt='Visual'>")

        if card.image_url and card.image_position in ["left", "right"]:
            html.append("<div class='row'>")
            content_col = "col-md-8" if card.image_position == "right" else "col-md-8 order-md-2"
            image_col = "col-md-4" if card.image_position == "right" else "col-md-4 order-md-1"
            html.append(f"<div class='{content_col}'>")

        for section in card.sections:
            html.append(self._render_section(section))

        if card.image_url and card.image_position in ["left", "right"]:
            html.append("</div>")
            html.append(f"<div class='{image_col}'><img src='{card.image_url}' class='img-fluid' alt='Visual'></div>")
            html.append("</div>")

        if card.image_url and card.image_position == "bottom":
            html.append(f"<img src='{card.image_url}' class='img-fluid mt-3' alt='Visual'>")

        html.append("</div>")
        html.append("</div>")
        return "\n".join(html)

    def _render_section(self, section: CardSection) -> str:
        """Dispatch to appropriate section renderer based on type"""
        renderer = self._section_renderers.get(section.section_type)
        return renderer(section) if renderer else ""

    def _render_text_section(self, section: CardSection) -> str:
        """Render plain text section"""
        html = []
        if section.title:
            html.append(f"<strong>{section.title}</strong>")
        html.append(f"<p class='text-muted'>{section.content}</p>")
        return "\n".join(html)

    def _render_key_value_section(self, section: CardSection) -> str:
        """Render key-value pairs as definition list"""
        html = []
        if section.title:
            html.append(f"<h5>{section.title}</h5>")
        html.append("<dl class='row'>")
        for key, value in section.content.items():
            html.append(f"<dt class='col-sm-4'>{key}:</dt>")
            html.append(f"<dd class='col-sm-8'>{value}</dd>")
        html.append("</dl>")
        return "\n".join(html)

    def _render_list_section(self, section: CardSection) -> str:
        """Render list of items"""
        html = []
        if section.title:
            html.append(f"<strong>{section.title}</strong>")
        html.append("<ul class='mb-2'>")
        for item in section.content:
            html.append(f"<li>{item}</li>")
        html.append("</ul>")
        return "\n".join(html)

    def _render_progress_section(self, section: CardSection) -> str:
        """Render progress bar - content should have 'label', 'value', 'max', 'color'"""
        value = section.content.get('value', 0)
        max_val = section.content.get('max', 100)
        label = section.content.get('label', '')
        color = section.content.get('color', 'primary')
        percentage = (value / max_val * 100) if max_val > 0 else 0

        html = []
        if section.title:
            html.append(f"<strong>{section.title}</strong>")
        if label:
            html.append(f"<p class='mb-1'>{label}</p>")
        html.append("<div class='progress' style='height: 20px;'>")
        html.append(f"<div class='progress-bar bg-{color}' style='width: {percentage}%'>{value}/{max_val}</div>")
        html.append("</div>")
        return "\n".join(html)

    def _render_table_section(self, section: CardSection) -> str:
        """Render small inline table - content should have 'headers' and 'rows'"""
        html = []
        if section.title:
            html.append(f"<h5>{section.title}</h5>")
        html.append("<table class='table table-sm'>")
        if 'headers' in section.content:
            html.append("<thead><tr>")
            for header in section.content['headers']:
                html.append(f"<th>{header}</th>")
            html.append("</tr></thead>")
        html.append("<tbody>")
        for row in section.content.get('rows', []):
            html.append("<tr>")
            for cell in row:
                html.append(f"<td>{cell}</td>")
            html.append("</tr>")
        html.append("</tbody></table>")
        return "\n".join(html)
