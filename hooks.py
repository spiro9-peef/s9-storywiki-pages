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

# --- 3. CONDITIONAL PARSER ENGINE ---
def evaluate_condition(cond, context):
    """
    Evaluates condition strings against the page context.
    Supports:
      - 'key' (checks if key is truthy)
      - 'key == "value"' or 'key == value'
      - 'key != "value"'
      - 'not key' or '!key'
    """
    cond = cond.strip()
    
    # Check for equality mapping
    if '==' in cond:
        left, right = cond.split('==', 1)
        left = left.strip()
        right = right.strip().strip("'\"")
        val = context.get(left)
        return str(val).strip() == right if val is not None else right == 'None'
        
    # Check for inequality mapping
    elif '!=' in cond:
        left, right = cond.split('!=', 1)
        left = left.strip()
        right = right.strip().strip("'\"")
        val = context.get(left)
        return str(val).strip() != right if val is not None else right != 'None'
        
    # Check for negation operators
    elif cond.startswith('not '):
        key = cond[4:].strip()
        return not bool(context.get(key))
    elif cond.startswith('!'):
        key = cond[1:].strip()
        return not bool(context.get(key))
        
    # Fallback to direct truthy evaluation
    return bool(context.get(cond))

def process_conditionals(text, context):
    """
    Replaces {% if condition %}...{% endif %} blocks dynamically.
    Loops recursively to support nested statements safely.
    """
    pattern = r'{%\s*if\s+(.*?)\s*%\}([\s\S]*?){%\s*endif\s*%}'
    
    def replace_match(match):
        cond = match.group(1)
        content = match.group(2)
        if evaluate_condition(cond, context):
            return content
        return ""
        
    old_text = None
    while old_text != text:
        old_text = text
        text = re.sub(pattern, replace_match, text)
    return text

def process_variables(text, context):
    """
    Substitutes all standard {{ key }} wrappers using the context data map.
    """
    for key, value in context.items():
        if value is None:
            display_value = ""
        elif isinstance(value, (date, datetime)):
            display_value = value.strftime("%Y-%m-%d")
        else:
            display_value = str(value)
            
        placeholder = rf'{{\s*{re.escape(key)}\s*}}'
        text = re.sub(placeholder, display_value.strip(), text)
    return text

# --- 4. MARKDOWN PARSING HOOK ---
def on_page_markdown(markdown, page, config, files):
    meta = page.meta
    
    # 1. Build a unified variable context map for this page
    context = {}
    if meta:
        context.update(meta)

    # 2. Safely calculate dynamic age fields if both dob & universe are present
    universe = meta.get('universe') if meta else None
    dob = meta.get('dob') if meta else None

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
                context['age'] = bio_years
                context['bio_age'] = bio_years
                context['chronological_age'] = chron_years

    # 3. Split the document by code elements to shield backticks and codeblocks
    parts = re.split(r'(```[\s\S]*?```|`[^`\n]+`)', markdown)
    
    for i in range(len(parts)):
        # If this segment is raw markdown prose (not starting with a backtick boundary)...
        if not parts[i].startswith('`'):
            # First clean up conditional structures
            parts[i] = process_conditionals(parts[i], context)
            # Then perform variable replacements inside links, templates, and text flow
            parts[i] = process_variables(parts[i], context)
            
    return "".join(parts)