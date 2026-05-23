import os
import yaml

def on_nav(nav, config, files):
    # Loop through every single page MkDocs auto-discovered in your folders
    for page in nav.pages:
        # Get the actual absolute path to the markdown file on your disk
        file_path = page.file.abs_src_path
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check if the file has front-matter block ---
                if content.startswith('---'):
                    try:
                        # Split off the front-matter block
                        _, front_matter, _ = content.split('---', 2)
                        meta = yaml.safe_load(front_matter)
                        
                        # If a custom title exists in the front-matter, force the sidebar to use it
                        if meta and 'title' in meta:
                            page.title = meta['title']
                    except Exception:
                        pass # Skip files with broken front-matter formatting
    return nav