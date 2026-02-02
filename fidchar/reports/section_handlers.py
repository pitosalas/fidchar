#!/usr/bin/env python3
"""Section handler functions for HTML report generation.

Contains all standalone handler functions that generate specific report sections. Each handler takes a builder instance and section options, returning HTML content.

Author: Pito Salas and Claude Code
Open Source Under MIT license
"""

from fidchar.reports import html_templates as templates
from fidchar.core import analysis as an


def _extract_section_options(section):
    """Extract options from section config, supporting both nested and flat structure."""
    if not isinstance(section, dict):
        return {}

    # If there's an explicit 'options' key, use it
    if 'options' in section:
        return section.get('options', {})

    # Otherwise, treat all keys except 'name' as options (flat structure)
    return {k: v for k, v in section.items() if k != 'name'}


def _add_section_class(html: str, section_name: str) -> str:
    """Add a specific section CSS class to HTML."""
    return html.replace('class="report-section"', f'class="report-section section-{section_name}"', 1)

def _create_high_alignment_filter(min_alignment: int):
    """Create filter function for high-alignment non-recurring charities.
    """
    def filter_high_alignment_non_recurring(_ein, _in_csv, in_rule, evaluation):
        # Must NOT be rule-based recurring
        if in_rule:
            return False
        # Must have evaluation with alignment score >= threshold
        if evaluation and hasattr(evaluation, 'alignment_score'):
            return evaluation.alignment_score >= min_alignment
        return False
    return filter_high_alignment_non_recurring


def _handle_sectors(builder, section_options):
    """Generate sectors section with categories and yearly graphs."""
    show_percentages = section_options.get("show_percentages", False)
    categories_html = builder.generate_category_table_bootstrap(
        builder.category_totals,
        builder.total_amount,
        show_percentages
    )

    return templates.sectors_section(categories_html=categories_html)


def _handle_yearly(builder, _section_options):
    """Generate yearly table section."""
    yearly_html = builder.generate_yearly_table_bootstrap(
        builder.yearly_amounts,
        builder.yearly_counts
    )
    return templates.yearly_section(yearly_html=yearly_html)


def _handle_top_charities(builder, section_options):
    """Generate charities section."""
    max_shown = section_options.get("max_shown", None)
    charities_to_show = builder.charities.head(max_shown) if max_shown else builder.charities
    charities_html = builder.generate_top_charities_bootstrap(charities_to_show)
    return templates.top_charities_section(top_charities_html=charities_html)


def _handle_patterns(builder, section_options):
    """Generate Patterns section."""
    max_one_time = section_options.get("max_one_time_shown", 20)
    max_stopped = section_options.get("max_stopped_shown", 15)

    one_time_table = builder.generate_one_time_table_bootstrap(builder.one_time, max_shown=max_one_time)
    overflow_one_time = max(0, builder.one_time_count - max_one_time)

    stopped_table = builder.generate_stopped_table_bootstrap(builder.stopped_recurring, max_shown=max_stopped)
    overflow_stopped = max(0, builder.stopped_count - max_stopped)

    return templates.patterns_section(
        one_time_table=one_time_table,
        one_time_total=builder.one_time_total,
        one_time_overflow=overflow_one_time,
        stopped_table=stopped_table,
        stopped_total=builder.stopped_total,
        stopped_overflow=overflow_stopped
    )


def _handle_recurring_summary(builder, section_options):
    """Generate Recurring Summary section."""
    max_recurring = section_options.get("max_recurring_shown", 20)
    data = builder.prepare_recurring_summary_data(max_shown=max_recurring)
    summary_html = builder.generate_recurring_summary_section_html(data)
    return _add_section_class(summary_html, "recurring-summary")


def _handle_csv_recurring(builder, section_options, csv_recurring_df):
    """Generate CSV Recurring section."""
    max_shown = section_options.get("max_shown", 100)
    csv_html = builder.generate_csv_recurring_section_html(csv_recurring_df, max_shown)
    return _add_section_class(csv_html, "csv-recurring")


def _handle_combined_recurring(builder, section_options, csv_recurring_df):
    """Generate Combined Recurring section."""
    max_shown = section_options.get("max_shown", 100)
    combined_df = builder.prepare_combined_recurring_data(csv_recurring_df, max_shown)
    combined_html = builder.generate_combined_recurring_section_html(combined_df, max_shown)
    return _add_section_class(combined_html, "combined-recurring")


def _handle_remaining(builder, section_options):
    """Generate Remaining Charities section."""
    max_remaining = section_options.get("max_remaining_shown", 100)
    data = builder.prepare_remaining_charities_data(builder.one_time, builder.charities, max_shown=max_remaining)
    remaining_html = builder.generate_remaining_charities_section_html(data)
    return _add_section_class(remaining_html, "remaining")


def _handle_all_charities(builder, section_options, csv_recurring_df):
    """Generate All Charities section."""
    max_shown = section_options.get("max_shown", None)
    all_charities_df = builder.prepare_all_charities_data(csv_recurring_df, max_shown)
    all_charities_html = builder.generate_all_charities_section_html(all_charities_df, max_shown)
    return _add_section_class(all_charities_html, "all-charities")


def _handle_high_alignment_opportunities(builder, section_options, csv_recurring_df):
    """Generate High Alignment Opportunities section."""
    max_shown = section_options.get("max_shown", None)
    min_alignment = section_options.get("min_alignment_score", 80)

    filter_func = _create_high_alignment_filter(min_alignment)
    opportunities_df = builder.prepare_all_charities_data(
        csv_recurring_df, max_shown, filter_func=filter_func
    )

    # Create custom subtitle for high alignment opportunities
    total_count = len(opportunities_df) if opportunities_df is not None and not opportunities_df.empty else 0
    showing_text = f"showing all {total_count}" if max_shown is None else f"showing top {min(max_shown, total_count)} of {total_count}"
    subtitle = f"High-quality charities with ≥{min_alignment}% alignment that are not currently recurring donations ({showing_text}). These represent potential candidates for recurring support."

    opportunities_html = builder.generate_all_charities_section_html(
        opportunities_df, max_shown,
        title=f"High Alignment Opportunities",
        subtitle=subtitle
    )
    return _add_section_class(opportunities_html, "high-alignment")


def generate_table_sections(config: dict, builder=None, exclude_definitions=False):
    """Generate all report sections based on configuration.

    This function dispatches to specialized handlers for each section type.
    All handlers access data through the builder instance.
    """
    sections = config.get("sections", {})
    html_content = ""

    # Compute csv_recurring_df once (used by multiple sections)
    csv_recurring_df = None
    if builder:
        csv_recurring_df = an.get_csv_recurring_details(builder.df)

    for section in sections:
        section_id = section if isinstance(section, str) else section.get("name")

        # Skip definitions if we're excluding it (will be added manually at the end)
        if exclude_definitions and section_id == "definitions":
            continue

        section_options = _extract_section_options(section)

        # Check include flag: defaults to True if not specified
        # include: true  -> include section
        # include: false -> skip section
        # (no include)   -> include section (default)
        include = section_options.get("include", True)
        if include == False:
            continue

        # All sections now use handlers
        if builder:
            # Create handler map with closures capturing needed variables
            handlers = {
                "sectors": lambda: _handle_sectors(builder, section_options),
                "yearly": lambda: _handle_yearly(builder, section_options),
                "top_charities": lambda: _handle_top_charities(builder, section_options),
                "patterns": lambda: _handle_patterns(builder, section_options),
                "recurring_summary": lambda: _handle_recurring_summary(builder, section_options),
                "csv_recurring": lambda: _handle_csv_recurring(builder, section_options, csv_recurring_df),
                "combined_recurring": lambda: _handle_combined_recurring(builder, section_options, csv_recurring_df),
                "remaining": lambda: _handle_remaining(builder, section_options),
                "all_charities": lambda: _handle_all_charities(builder, section_options, csv_recurring_df),
                "high_alignment_opportunities": lambda: _handle_high_alignment_opportunities(builder, section_options, csv_recurring_df),
            }

            handler = handlers.get(section_id)
            if handler:
                html_content += handler()

    return html_content


def generate_definitions_section():
    """Generate the definitions section from markdown file."""
    import os
    from markdown_it import MarkdownIt

    md = MarkdownIt()
    definitions_path = os.path.join(os.path.dirname(__file__), "..", "definitions.md")

    try:
        with open(definitions_path, "r") as f:
            markdown_content = f.read()

        # Process magic strings for column layout
        markdown_content = markdown_content.replace(
            ':begin-left',
            '<div class="row border-bottom">\n<div class="col-md-6 border-end border-dark">'
        )
        markdown_content = markdown_content.replace(':end-left', '</div>')
        markdown_content = markdown_content.replace(':begin-right', '<div class="col-md-6">')
        markdown_content = markdown_content.replace(':end-right', '</div>\n</div>')

        html_definitions = md.render(markdown_content)

        return f"""
    <div class="report-section section-definitions">
        {html_definitions}
    </div>"""

    except FileNotFoundError:
        return """
    <div class="report-section section-definitions">
        <h2 class="section-title">Definitions</h2>
        <p>Definitions file not found.</p>
    </div>"""
