import os
import yaml
import re
from datetime import datetime, date
from mkdocs.structure.nav import Section, Page

# --- 1. SIDEBAR NAME & FOLDER DUPLICATION CLEANUP ---
def read_front_matter(abs_path):
    if not os.path.exists(abs_path): return {}
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    meta = yaml.safe_load(parts[1])
                    if isinstance(meta, dict): return meta
    except Exception: pass
    return {}

def fix_navigation_titles_inplace(items):
    """
    Safely updates display titles directly on existing objects.
    Does NOT alter array structures, preserving the top navbar layout.
    """
    for item in items:
        if isinstance(page := item, Page):
            meta = read_front_matter(page.file.abs_src_path)
            # Apply your naming rules cleanly without moving the page object
            if 'sidebar' in meta: 
                page.title = str(meta['sidebar'])
            elif 'title' in meta: 
                page.title = str(meta['title'])
        elif isinstance(section := item, Section):
            if section.children:
                fix_navigation_titles_inplace(section.children)

def on_nav(nav, config, files):
    # Only change properties inside the elements; do not assign a new list layout
    fix_navigation_titles_inplace(nav.items)
    return nav


# --- 2. IN-UNIVERSE TIMELINE MATH ---
def parse_date(date_input):
    if not date_input: return None
    if isinstance(date_input, str):
        try: return datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError: return None
    if isinstance(date_input, (date, datetime)):
        return date_input if isinstance(date_input, date) else date_input.date()
    return None

def calculate_chronological_years(birth_date, death_date, current_year_setting):
    """Calculates elapsed timeline years up to today or a frozen checkpoint."""
    if str(current_year_setting).lower() == 'dynamic':
        end_date = death_date if death_date else date.today()
        has_had_birthday = (end_date.month, end_date.day) >= (birth_date.month, birth_date.day)
        return end_date.year - birth_date.year - (0 if has_had_birthday else 1)
    else:
        try:
            target_year = int(current_year_setting)
            if death_date and death_date.year < target_year:
                return death_date.year - birth_date.year
            return target_year - birth_date.year
        except (ValueError, TypeError):
            return None

def on_page_markdown(markdown, page, config, files):
    meta = page.meta
    if not meta or 'dob' not in meta or 'universe' not in meta:
        return markdown

    universe = meta['universe']
    timeline_years = config.get('extra', {}).get('timeline_years', {})
    universe_setting = timeline_years.get(universe)
    
    birth_date = parse_date(meta.get('dob'))
    death_date = parse_date(meta.get('dod'))
    age_offset = int(meta.get('age_offset', 0))

    if birth_date:
        chron_years = calculate_chronological_years(birth_date, death_date, universe_setting)
        
        if chron_years is not None:
            # Bio Age = Chronological Years + Age Offset
            bio_years = chron_years + age_offset
            
            # Inject standard text substitutions inline
            markdown = re.sub(r'{{\s*age\s*}}', str(bio_years), markdown)
            markdown = re.sub(r'{{\s*bio_age\s*}}', str(bio_years), markdown)
            markdown = re.sub(r'{{\s*chronological_age\s*}}', str(chron_years), markdown)

    # Clean up secondary structural field keys
    for key, value in meta.items():
        if isinstance(value, (str, int, float, date, datetime)):
            display_value = value.strftime("%Y-%m-%d") if isinstance(value, (date, datetime)) else str(value)
            placeholder = rf'{{\s*{re.escape(key)}\s*}}'
            markdown = re.sub(placeholder, display_value.strip(), markdown)

    return markdown