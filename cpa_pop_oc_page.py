import os
from pathlib import Path

# --- CONFIGURATION ---
TEMPLATE_PATH = Path("_Templates/oc-xxxx-first-middle-last.md")
BASE_CHAR_DIR = Path("docs/celesta-public-archive/characters")

def ensure_nav_file(folder_path: Path, title_text: str):
    #Ensures a nav.yml file exists inside the given directory.
    nav_file = folder_path / "nav.yml"
    if not nav_file.exists():
        nav_content = f'title: "{title_text}"\n'
        nav_file.write_text(nav_content, encoding="utf-8")
        print(f"[NAV CREATED] {nav_file.resolve().relative_to(Path.cwd().resolve())}")

def get_batch_folder(char_id: int) -> Path:
    # Calculates the correct 100-block and 10-block subdirectories, 
    # ensuring both directories and their respective nav.yml files exist.
    
    # 1. Determine the 100-block (e.g., 001-100)
    hundred_start = ((char_id - 1) // 100) * 100 + 1
    hundred_end = hundred_start + 99
    hundred_folder_name = f"{hundred_start:03d}-{hundred_end:03d}"
    hundred_dir = BASE_CHAR_DIR / hundred_folder_name
    
    hundred_dir.mkdir(parents=True, exist_ok=True)
    # Automatically generate nav.yml for the 100-block
    ensure_nav_file(hundred_dir, f"ID #{hundred_start:03d}-{hundred_end:03d}")

    # 2. Determine the 10-block (e.g., 011-020)
    ten_start = ((char_id - 1) // 10) * 10 + 1
    ten_end = ten_start + 9
    ten_folder_name = f"{ten_start:03d}-{ten_end:03d}"
    ten_dir = hundred_dir / ten_folder_name
    
    ten_dir.mkdir(parents=True, exist_ok=True)
    # Automatically generate nav.yml for the 10-block
    ensure_nav_file(ten_dir, f"ID #{ten_start:03d}-{ten_end:03d}")
    
    return BASE_CHAR_DIR / hundred_folder_name / ten_folder_name

def main():
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template not found at {TEMPLATE_PATH.resolve()}")
        return

    print("--- OC Page Generator ---")
    
    # Prompt for ID
    try:
        id_input = input("Enter Character ID (e.g., 1): ").strip()
        char_id = int(id_input)
    except ValueError:
        print("Error: Invalid ID. Please enter a whole number.")
        return

    # Prompt for Name
    name = input("Enter Character Name (e.g., Jeremy David Peifer): ").strip()
    if not name:
        print("Error: Name cannot be empty.")
        return

    # Formatting
    id_padded_internal = f"{char_id:04d}"
    id_padded_frontfacing = f"{char_id:03d}"
    # Replaces existing hyphens with null to match the Rowan-Bay sisters
    # Also replaces parentheses as idiotproofing
    slug = name.lower().replace("'", "-").replace("(", ")").replace(")", "").replace("-", "").replace(" ", "-")
    filename = f"oc-{id_padded_internal}-{slug}.md"
    
    # Determine directory and ensure it exists (handled in func)
    target_dir = get_batch_folder(char_id)
    file_path = target_dir / filename
    
    # Prevent overwrites
    if file_path.exists():
        print(f"\n[SKIPPED] Character file already exists:")
        print(f" -> {file_path.resolve()}")
        return
        
    # Read template and replace variables
    template_content = TEMPLATE_PATH.read_text(encoding="utf-8")
    new_content = template_content
    new_content = new_content.replace("Raw Character Name", name)
    new_content = new_content.replace("ID: 0", f"ID: {char_id}")
    new_content = new_content.replace("sidebar: NNN", f"sidebar: {id_padded_frontfacing}")
    
    # Write out the new file
    file_path.write_text(new_content, encoding="utf-8")
    print(f"\n[Success] Created new page: {file_path.resolve()}")
    

if __name__ == "__main__":
    try:
        trycount_in = input("How many times are you planning on running this? ").strip()
        trycount = int(trycount_in)
    except ValueError:
        print("Error: Invalid count. Please enter a whole number.")

    for x in range(trycount):
        main()
