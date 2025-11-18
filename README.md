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

# Generate an index page listing all calendars
python3 mdcal.py --generate-index
```

### GitHub Actions

The repository includes a GitHub Action that automatically generates calendar files:

- **On every commit** to markdown files or mdcal.py
- **Daily at midnight UTC**
- **Manual trigger** via workflow_dispatch
- **Automatic deployment** to GitHub Pages

Generated files (.html and .ics) are automatically committed and deployed to GitHub Pages.

#### Setup

1. **Enable GitHub Pages in your repository:**
   - Go to your repository on GitHub
   - Navigate to **Settings** → **Pages**
   - Under "Build and deployment"
   - Set **Source** to "GitHub Actions"
   - Click **Save**

2. **Push the workflow and files:**
   ```bash
   git add .github/workflows/generate-calendar.yml
   git add mdcal.py
   git commit -m "Add calendar generator with GitHub Pages deployment"
   git push origin main
   ```

3. **Add your markdown event files to the repository**
   - **Important**: The actual markdown files must be committed to the repository
   - Symlinks will not work in GitHub Actions (they work locally though)

4. **Access your calendars:**
   - After the action runs, visit: `https://[your-username].github.io/[repository-name]/`
   - You'll see an index page listing all your calendars
   - Each calendar can be viewed online or downloaded as an iCal file

The workflow:
- Excludes common documentation files (README.md, LICENSE.md, etc.)
- Properly handles filenames with spaces or special characters
- Generates an index.html page listing all calendars
- Deploys everything to GitHub Pages automatically

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

See `2026 Outdoor Termine.md` for an example event file. The results can be viewed at <https://hoffmann.github.io/mdcal/>

## Requirements

- Python 3.11+
- No external dependencies required

## License

This tool is provided as-is for personal and commercial use.
