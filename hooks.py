import os
import yaml
import re
import json
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
    for item in items:
        if isinstance(page := item, Page):
            meta = read_front_matter(page.file.abs_src_path)
            if 'sidebar' in meta: 
                page.title = str(meta['sidebar'])
            elif 'title' in meta: 
                page.title = str(meta['title'])
        elif isinstance(section := item, Section):
            if section.children:
                fix_navigation_titles_inplace(section.children)

def on_nav(nav, config, files):
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

# --- 3. CONDITIONAL PARSER ENGINE ---
def evaluate_condition(cond, context):
    cond = cond.strip()
    if '==' in cond:
        left, right = cond.split('==', 1)
        val = context.get(left.strip())
        return str(val).strip() == right.strip().strip("'\"") if val is not None else right.strip().strip("'\"") == 'None'
    elif '!=' in cond:
        left, right = cond.split('!=', 1)
        val = context.get(left.strip())
        return str(val).strip() != right.strip().strip("'\"") if val is not None else right.strip().strip("'\"") != 'None'
    elif cond.startswith('not ') or cond.startswith('!'):
        key = cond[4:].strip() if cond.startswith('not ') else cond[1:].strip()
        return not bool(context.get(key))
    return bool(context.get(cond))

def process_conditionals(text, context):
    pattern = r'{%\s*if\s+(.*?)\s*%\}([\s\S]*?){%\s*endif\s*%}'
    def replace_match(match):
        return match.group(2) if evaluate_condition(match.group(1), context) else ""
    
    old_text = None
    while old_text != text:
        old_text = text
        text = re.sub(pattern, replace_match, text)
    return text

def process_variables(text, context):
    for key, value in context.items():
        display_value = value.strftime("%Y-%m-%d") if isinstance(value, (date, datetime)) else str(value) if value is not None else ""
        placeholder = rf'{{\s*{re.escape(str(key))}\s*}}'
        text = re.sub(placeholder, display_value.strip(), text)
    return text

# --- 4. MARKDOWN PARSING HOOK ---
def get_palette_config(theme_key):
    try:
        with open('docs/javascripts/theme-lookup.json', 'r') as f:
            palettes = json.load(f)
            return palettes.get(theme_key, palettes.get('default'))
    except Exception:
        return None

def on_page_markdown(markdown, page, config, files):
    meta = page.meta
    context = dict(meta) if meta else {}

    # --- NEW: AUTOMATIC DIRECTORY DETECTION ---
    # Only assign a theme if the user hasn't explicitly set one in frontmatter
    theme_key = meta.get('page_theme')
    
    if not theme_key:
        path = page.file.src_path.lower()
        if "celesta-public-archive" in path:
            theme_key = "celesta-archive"
        elif "stellar-republic-database" in path:
            theme_key = "stellar-republic"
        else:
            theme_key = "default"

    # 1. Age Calculation Logic
    universe = meta.get('universe')
    dob = meta.get('dob')
    if universe and dob:
        timeline_years = config.get('extra', {}).get('timeline_years', {})
        universe_setting = timeline_years.get(universe)
        birth_date = parse_date(dob)
        death_date = parse_date(meta.get('dod'))
        age_offset = int(meta.get('age_offset', 0))

        if birth_date:
            chron_years = calculate_chronological_years(birth_date, death_date, universe_setting)
            if chron_years is not None:
                bio_years = chron_years + age_offset
                context.update({'age': bio_years, 'bio_age': bio_years, 'chronological_age': chron_years})

    # 2. Theme Injection
    if theme_key:
        palette = get_palette_config(theme_key)
        if palette:
            style_injection = f"""
            <style>
            :root {{
                --md-primary-fg-color: {palette['primary']} !important;
                --md-primary-fg-color--light: {palette['light']} !important;
                --md-primary-fg-color--dark: {palette['dark']} !important;
                --md-default-bg-color: {palette['bg']} !important;
                --custom-nav-text-color: {palette['text']} !important;
            }}
            </style>
            """
            markdown = style_injection + "\n" + markdown

    # 3. Processing Markdown content (shielding code blocks)
    parts = re.split(r'(```[\s\S]*?```|`[^`\n]+`)', markdown)
    for i in range(len(parts)):
        if not parts[i].startswith('`'):
            parts[i] = process_conditionals(parts[i], context)
            parts[i] = process_variables(parts[i], context)
            
    return "".join(parts)