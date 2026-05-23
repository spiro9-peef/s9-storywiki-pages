import os
import yaml
from mkdocs.structure.nav import Section, Page

def read_front_matter(abs_path):
    """Extracts front-matter dict from a markdown file."""
    if not os.path.exists(abs_path):
        return {}
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    meta = yaml.safe_load(parts[1])
                    if isinstance(meta, dict):
                        return meta
    except Exception:
        pass
    return {}

def process_and_flatten(items):
    """Applies distinct sidebar titles and flattens folder duplicates."""
    cleaned_items = []
    for item in items:
        if isinstance(page := item, Page):
            meta = read_front_matter(page.file.abs_src_path)

            # Overwrite ONLY the sidebar node text if 'sidebar' metadata is specified
            if 'sidebar' in meta:
                page.title = str(meta['sidebar'])
            # Fallback: If no explicit sidebar tag, use standard front-matter title
            elif 'title' in meta:
                page.title = str(meta['title'])

            cleaned_items.append(page)

        elif isinstance(section := item, Section):
            section.children = process_and_flatten(section.children)

            if len(section.children) == 1 and isinstance(section.children[0], Section):
                sub_section = section.children[0]
                section.children = sub_section.children

            cleaned_items.append(section)

    return cleaned_items

def on_nav(nav, config, files):
    nav.items = process_and_flatten(nav.items)
    return nav