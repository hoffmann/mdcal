#!/usr/bin/env python3
"""
mdcal - Parse markdown events and generate iCal and HTML outputs
"""

import re
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path


class Event:
    """Represents a single event"""
    def __init__(self, title, start_date, end_date=None, description="", link="", tags=None):
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.link = link
        self.tags = tags if tags is not None else []

    def __repr__(self):
        return f"Event({self.title}, {self.start_date}, {self.end_date}, tags={self.tags})"


def is_heading(line):
    """Check if a line is a markdown heading (# followed by space)"""
    stripped = line.strip()
    return bool(re.match(r'^#+\s', stripped))

def is_tag_line(line):
    """Check if a line contains tags (starts with # followed by alphanumeric, - or _)"""
    return bool(re.match(r'^#[a-zA-Z0-9_-]', line))


def parse_tags(line):
    """Parse tags from a line. Tags start with # and contain alphanumeric, - or _"""
    # Find all tags in the line
    tag_pattern = r'#([a-zA-Z0-9_-]+)'
    matches = re.findall(tag_pattern, line)
    return matches


def parse_date(date_str):
    """Parse date string in format DD.MM.YYYY or DD.MM.YYYY - DD.MM.YYYY"""
    date_str = date_str.strip()

    # Check for date range
    if '-' in date_str:
        parts = date_str.split('-')
        start_str = parts[0].strip()
        end_str = parts[1].strip()

        start_date = datetime.strptime(start_str, '%d.%m.%Y')
        end_date = datetime.strptime(end_str, '%d.%m.%Y')

        return start_date, end_date
    else:
        # Single date
        date = datetime.strptime(date_str, '%d.%m.%Y')
        return date, None


def parse_markdown(file_path):
    """Parse markdown file and extract events"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    events = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Check if this is a heading (event title)
        if is_heading(line):
            title = line.lstrip('#').strip()
            i += 1

            # Parse date (next non-empty line)
            while i < len(lines) and not lines[i].strip():
                i += 1

            if i >= len(lines):
                break

            date_line = lines[i].strip()
            start_date, end_date = parse_date(date_line)
            i += 1

            # Parse optional tags, description and link
            tags = []
            description = ""
            link = ""

            # Collect lines until next heading or end of file
            content_lines = []
            while i < len(lines) and not is_heading(lines[i]):
                content_lines.append(lines[i].strip())
                i += 1

            # Separate tags, description and link
            for content_line in content_lines:
                if content_line.startswith('http://') or content_line.startswith('https://'):
                    link = content_line
                elif content_line and is_tag_line(content_line):
                    # Parse tags from this line
                    tags.extend(parse_tags(content_line))
                elif content_line:
                    if description:
                        description += "\n"
                    description += content_line

            event = Event(title, start_date, end_date, description.strip(), link, tags)
            events.append(event)
        else:
            i += 1

    return events


def generate_ical(events, output_path):
    """Generate iCal file from events"""
    lines = []
    lines.append("BEGIN:VCALENDAR")
    lines.append("VERSION:2.0")
    lines.append("PRODID:-//mdcal//mdcal//EN")
    lines.append("CALSCALE:GREGORIAN")
    lines.append("METHOD:PUBLISH")

    # Sort events by start date
    sorted_events = sorted(events, key=lambda e: e.start_date)

    for event in sorted_events:
        lines.append("BEGIN:VEVENT")

        # Generate UID
        uid = f"{event.start_date.strftime('%Y%m%d')}-{event.title.replace(' ', '-')}@mdcal"
        lines.append(f"UID:{uid}")

        # Add dates
        if event.end_date:
            # Multi-day event
            lines.append(f"DTSTART;VALUE=DATE:{event.start_date.strftime('%Y%m%d')}")
            # iCal end date is exclusive, so add 1 day
            end_date_ical = event.end_date + timedelta(days=1)
            lines.append(f"DTEND;VALUE=DATE:{end_date_ical.strftime('%Y%m%d')}")
        else:
            # Single day event
            lines.append(f"DTSTART;VALUE=DATE:{event.start_date.strftime('%Y%m%d')}")
            end_date_ical = event.start_date + timedelta(days=1)
            lines.append(f"DTEND;VALUE=DATE:{end_date_ical.strftime('%Y%m%d')}")

        # Add title
        lines.append(f"SUMMARY:{escape_ical_text(event.title)}")

        # Add categories (tags)
        if event.tags:
            categories = ','.join([escape_ical_text(tag) for tag in event.tags])
            lines.append(f"CATEGORIES:{categories}")

        # Add description and link
        description_parts = []
        if event.description:
            description_parts.append(event.description)
        if event.link:
            description_parts.append(f"Link: {event.link}")

        if description_parts:
            description = "\\n".join(description_parts)
            lines.append(f"DESCRIPTION:{escape_ical_text(description)}")

        if event.link:
            lines.append(f"URL:{event.link}")

        # Add timestamp
        now = datetime.now(timezone.utc)
        lines.append(f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}")

        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def escape_ical_text(text):
    """Escape special characters for iCal format"""
    text = text.replace('\\', '\\\\')
    text = text.replace(',', '\\,')
    text = text.replace(';', '\\;')
    text = text.replace('\n', '\\n')
    return text


def generate_html(events, output_path, ical_filename=None, calendar_title="Events Calendar"):
    """Generate HTML file from events"""
    # Sort events by start date
    sorted_events = sorted(events, key=lambda e: e.start_date)

    # Collect all unique tags
    all_tags = sorted(set(tag for event in sorted_events for tag in event.tags))

    # Generate download link HTML if provided
    download_link_html = f'<a href="{escape_html(ical_filename)}" class="download-link" download>📅 Download iCal</a>' if ical_filename else ''

    # Generate tag filter section HTML
    filter_tags_html = ''
    if all_tags:
        filter_tags = '\n'.join([
            f'        <span class="filter-tag" data-tag="{escape_html(tag)}" onclick="filterByTag(\'{escape_html(tag)}\')">#{escape_html(tag)}</span>'
            for tag in all_tags
        ])
        filter_tags_html = f'''    <div class="tag-filter-section">
{filter_tags}
    </div>'''

    # Generate events HTML
    events_html = []
    for event in sorted_events:
        tags_attr = ','.join(event.tags) if event.tags else ''
        date_str = f"{event.start_date.strftime('%d.%m.%Y')} - {event.end_date.strftime('%d.%m.%Y')}" if event.end_date else event.start_date.strftime('%d.%m.%Y')

        # Generate tags HTML for this event
        event_tags_html = ''
        if event.tags:
            tags_items = '\n'.join([
                f'                <span class="tag" onclick="filterByTag(\'{escape_html(tag)}\')">#{escape_html(tag)}</span>'
                for tag in event.tags
            ])
            event_tags_html = f'''            <div class="event-tags">
{tags_items}
            </div>'''

        description_html = f'        <div class="event-description">{escape_html(event.description)}</div>' if event.description else ''
        link_html = f'        <div class="event-link">🔗 <a href="{escape_html(event.link)}" target="_blank">{escape_html(event.link)}</a></div>' if event.link else ''

        event_html = f'''    <div class="event" data-tags="{escape_html(tags_attr)}">
        <div class="event-title">{escape_html(event.title)}</div>
        <div class="event-date-tags">
            <span class="event-date">📅 {escape_html(date_str)}</span>
{event_tags_html}
        </div>
{description_html}
{link_html}
    </div>'''
        events_html.append(event_html)

    events_section = '\n'.join(events_html)

    # Generate complete HTML document
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(calendar_title)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
            gap: 20px;
            flex-wrap: wrap;
        }}
        h1 {{
            color: #2c3e50;
            margin: 0;
            flex: 1;
        }}
        .download-link {{
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            display: inline-block;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: background 0.3s;
            white-space: nowrap;
        }}
        .download-link:hover {{
            background: #2980b9;
        }}
        .event {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .event-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
            margin: 0 0 10px 0;
        }}
        .event-date-tags {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin: 5px 0;
        }}
        .event-date {{
            color: #7f8c8d;
            font-size: 0.95em;
        }}
        .event-description {{
            margin: 10px 0;
            color: #555;
        }}
        .event-link {{
            margin: 10px 0;
        }}
        .event-link a {{
            color: #3498db;
            text-decoration: none;
            word-break: break-all;
        }}
        .event-link a:hover {{
            text-decoration: underline;
        }}
        .event-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .tag {{
            background: #e8f4f8;
            color: #2980b9;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }}
        .tag:hover {{
            background: #d0e9f2;
        }}
        .tag-filter-section {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }}
        .filter-tag {{
            background: #e8f4f8;
            color: #2980b9;
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 0.9em;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }}
        .filter-tag:hover {{
            background: #d0e9f2;
        }}
        .filter-tag.active {{
            background: #3498db;
            color: white;
        }}
        .event.hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{escape_html(calendar_title)}</h1>
        {download_link_html}
    </div>
{filter_tags_html}
{events_section}
    <script>
        let currentFilter = null;

        function filterByTag(tag) {{
            // If clicking on the already active tag, deselect it
            if (currentFilter === tag) {{
                clearFilter();
                return;
            }}

            currentFilter = tag;
            const events = document.querySelectorAll('.event');

            events.forEach(event => {{
                const tags = event.getAttribute('data-tags');
                if (tags && tags.split(',').includes(tag)) {{
                    event.classList.remove('hidden');
                }} else {{
                    event.classList.add('hidden');
                }}
            }});

            // Update active state of filter tags
            document.querySelectorAll('.filter-tag').forEach(filterTag => {{
                if (filterTag.getAttribute('data-tag') === tag) {{
                    filterTag.classList.add('active');
                }} else {{
                    filterTag.classList.remove('active');
                }}
            }});

            // Scroll to top
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function clearFilter() {{
            currentFilter = null;
            const events = document.querySelectorAll('.event');

            events.forEach(event => {{
                event.classList.remove('hidden');
            }});

            // Remove active state from all filter tags
            document.querySelectorAll('.filter-tag').forEach(filterTag => {{
                filterTag.classList.remove('active');
            }});
        }}
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def escape_html(text):
    """Escape special characters for HTML"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    return text


def main():
    parser = argparse.ArgumentParser(
        description='Parse markdown events and generate iCal and HTML outputs'
    )
    parser.add_argument(
        'input',
        help='Input markdown file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output base name (without extension)',
        default=None
    )
    parser.add_argument(
        '--ical-only',
        action='store_true',
        help='Generate only iCal output'
    )
    parser.add_argument(
        '--html-only',
        action='store_true',
        help='Generate only HTML output'
    )

    args = parser.parse_args()

    # Determine output base name and calendar title
    input_path = Path(args.input)
    if args.output:
        output_base = args.output
        calendar_title = Path(args.output).name
    else:
        output_base = input_path.stem
        calendar_title = input_path.stem

    # Parse markdown
    print(f"Parsing {args.input}...")
    events = parse_markdown(args.input)
    print(f"Found {len(events)} events")

    # Generate outputs
    ical_filename = None
    if not args.html_only:
        ical_path = f"{output_base}.ics"
        ical_filename = Path(ical_path).name
        print(f"Generating {ical_path}...")
        generate_ical(events, ical_path)
        print(f"✓ iCal file created: {ical_path}")

    if not args.ical_only:
        html_path = f"{output_base}.html"
        print(f"Generating {html_path}...")
        generate_html(events, html_path, ical_filename, calendar_title)
        print(f"✓ HTML file created: {html_path}")


if __name__ == '__main__':
    main()
