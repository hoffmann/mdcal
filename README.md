# mdcal - Markdown Calendar Generator

A Python tool that parses markdown event files and generates interactive HTML calendars and iCal files.

## Features

- Parse events from markdown files
- Generate iCal (.ics) files for calendar imports
- Generate interactive HTML calendars with tag filtering
- Support for single-day and multi-day events
- Tag-based event filtering
- Responsive design

## Event Format

Events are written in markdown with the following format:

```markdown
# Event Title
DD.MM.YYYY
#tag1 #tag2

Optional description text

https://optional-link.com
```

### Date Formats

- Single day: `15.12.2025`
- Date range: `15.12.2025 - 20.12.2025`

### Tags

Tags are optional and start with `#` followed by alphanumeric characters, hyphens, or underscores:
- `#trailrun`
- `#ski-touring`
- `#competition_2026`

## Usage

### Command Line

```bash
# Generate both HTML and iCal files
python3 mdcal.py "events.md"

# Specify custom output name
python3 mdcal.py "events.md" -o my_calendar

# Generate only iCal
python3 mdcal.py "events.md" --ical-only

# Generate only HTML
python3 mdcal.py "events.md" --html-only
```

### GitHub Actions

The repository includes a GitHub Action that automatically generates calendar files:

- **On every commit** to markdown files or mdcal.py
- **Daily at midnight UTC**
- **Manual trigger** via workflow_dispatch

Generated files (.html and .ics) are automatically committed back to the repository.

#### Setup

1. Push the `.github/workflows/generate-calendar.yml` file to your repository
2. Ensure mdcal.py is in the repository root
3. Add your markdown event files to the repository
   - **Important**: The actual markdown files must be committed to the repository
   - Symlinks will not work in GitHub Actions (they work locally though)
4. The action will run automatically on push or daily

The workflow excludes common documentation files (README.md, LICENSE.md, etc.) from processing and properly handles filenames with spaces or special characters.

## HTML Features

The generated HTML calendar includes:

- **Responsive design** - Works on desktop and mobile
- **Tag filtering** - Click tags to filter events
- **Toggle filtering** - Click active tag again to show all events
- **Download link** - Direct link to download the iCal file
- **Modern styling** - Clean, professional appearance

## iCal Features

The generated iCal files include:

- Standard RFC 5545 format
- Compatible with all major calendar applications
- Event categories (tags)
- Multi-day event support
- URLs and descriptions

## Example

See `2026 Outdoor Termine.md` for an example event file.

## Requirements

- Python 3.11+
- No external dependencies required

## License

This tool is provided as-is for personal and commercial use.
