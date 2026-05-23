import os
import yaml
from mkdocs.structure.nav import Section, Page

def read_front_matter_title(abs_path):
    """Safely extracts the title from a markdown file's front-matter."""
    if not os.path.exists(abs_path):
        return None
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    meta = yaml.safe_load(parts[1])
                    if meta and 'title' in meta:
                        return str(meta['title'])
    except Exception:
        pass
    return None

def process_items(items):
    """Recursively walks through sections and overrides page titles."""
    for item in items:
        if isinstance(item, Page):
            custom_title = read_front_matter_title(item.file.abs_src_path)
            if custom_title:
                item.title = custom_title
        elif isinstance(item, Section):
            # Recursively handle nested files inside directories
            process_items(item.children)

def on_nav(nav, config, files):
    """Intercepts the final navigation tree before it renders."""
    process_items(nav.items)
    return nav