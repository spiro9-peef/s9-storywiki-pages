import os
import re
import sys
from pathlib import Path
from datetime import date

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

def pagemake(firstAttempt = True):
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template not found at {TEMPLATE_PATH.resolve()}")
        return

    if firstAttempt:
        print("--- OC Page Generator ---")
    
    # Prompt for ID
    try:
        id_input = input("Enter Character ID (e.g., 1): ").strip()
        char_id = int(id_input)
    except ValueError:
        print("Error: Invalid ID. Please enter a whole number.")
        pagemake(firstAttempt = False) # Try again.

    # Prompt for Name
    name = input("Enter Character Name (e.g., Jeremy David Peifer): ").strip()
    if not name:
        print("Error: Name cannot be empty.")
        pagemake(firstAttempt = False) # Try again.

    # Prompt for Sex
    sex = input("Sex (e.g. M/F): ").strip()
    if not sex:
        print("Error: Sex cannot be empty.")
        pagemake(firstAttempt = False) # Try again.

    # Pattern for Male (matches: m, M, male, Male, MALE, man)
    if re.fullmatch(r"m(ale)?|man", sex, re.IGNORECASE):
        sex = "M"
    # Pattern for Female (matches: f, F, female, Female, FEMALE, woman)
    elif re.fullmatch(r"f(emale)?|woman", sex, re.IGNORECASE):
        sex = "F"
    else:
        print("Error: Sex value not valid. Must be male or female.")
        pagemake(firstAttempt = False) # Try again.

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
    new_content = new_content.replace("universe: rotc or tsr", "universe: rotc")
    new_content = new_content.replace("sex: N", f"sex: {sex}")
    
    # Write out the new file
    file_path.write_text(new_content, encoding="utf-8")
    print(f"\n[Success] Created new page: {file_path.resolve()}")

def batch_clean_all():
    tp01 = "{% if nicknames != \"N/A\" %}Nickname(s): { nicknames }<br>{% endif %}{% if online_aliases != \"N/A\" %}Alias(es): { online_aliases }<br>{% endif %}"
    rp01 = "{% if nicknames != \"N/A\" %}Nickname(s): { nicknames }<br>{% endif -%}{% if online_aliases != \"N/A\" %}Alias(es): { online_aliases }<br>{% endif -%}"

    tp02 = "universe: rotc or tsr"
    rp02 = "universe: rotc"
    
    tp03 = "{% if current_species.name != \"N/A\" && current_species.url != \"N/A\" %}Current Species: [{ current_species.name }]({ current_species.url })<br>{% endif -%}"
    rp03 = "{% if current_species.name != \"N/A\" and current_species.url != \"N/A\" %}Current Species: [{ current_species.name }]({ current_species.url })<br>{% endif -%}"
    rp03B = "{% if current_species.name is defined and current_species.url is defined and if current_species.name != \"N/A\" and current_species.url != \"N/A\" %}Current Species: [{ current_species.name }]({ current_species.url })<br>{% endif -%}"
    base_dir = Path("docs/celesta-public-archive/characters")
    
    cleaned_count = 0
    for file_path in base_dir.glob("**/*.md"):
        content = file_path.read_text(encoding="utf-8")
        new_content = content
        if tp01 in new_content:
            cleaned_count += 1
            new_content = new_content.replace(tp01, rp01)
        if tp02 in new_content:
            if tp01 not in content:
                cleaned_count += 1
            new_content = new_content.replace(tp02, rp02)

        lines = new_content.splitlines()
        updated_lines = []
        current_species_inserted = False

        if tp03 in new_content:
            if tp01 not in content and tp02 not in content:
                cleaned_count += 1
            new_content = new_content.replace(tp03, rp03)
            lines = new_content.splitlines() # Sanity check
            current_species_inserted = True
        if rp03 in new_content:
            if tp01 not in content and tp02 not in content and not current_species_inserted:
                current_species_inserted = True
                cleaned_count += 1
            new_content = new_content.replace(rp03, rp03B)
            lines = new_content.splitlines() # Sanity check

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.lower().startswith("base species:") and not current_species_inserted:
                updated_lines.append(line)
                line_next = lines[lines.index(line) + 1]
                line_next_stripped = line_next.strip()
                if not line_next_stripped.lower().startswith("{% if current_species.name"):
                    updated_lines.append(rp03B)
                    current_species_inserted = True
                    cleaned_count += 1
                continue
            
            updated_lines.append(line)
        
        # Reassemble the file content safely with correct line breaks
        new_content = "\n".join(updated_lines) + "\n"
        
        file_path.write_text(new_content, encoding="utf-8")
            
    print(f"Run complete: cleaned {cleaned_count} files of bad formatting patterns.")

def get_bool_from_input(prompt, input_str):
    # Pattern for True (matches: t, T, true, True, TRUE)
    if re.fullmatch(r"t(rue)?|y(es)?", input_str, re.IGNORECASE):
        flag = True
    # Pattern for False (matches: f, F, false, False, FALSE)
    elif re.fullmatch(r"f(alse)?|n(o)?", input_str, re.IGNORECASE):
        flag = False
    else:
        print("Error: True or False value not provided. Please try again.")
        flag = get_bool_from_input(prompt, input(prompt))

    return flag

def read_frontmatter_value(file_path: Path, target_key: str):
    # Reads a specific frontmatter key from a markdown file.
    in_frontmatter = False
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_stripped = line.strip()
            
            # Check for frontmatter boundaries
            if line_stripped == "---":
                if in_frontmatter:
                    break # We passed the end of the frontmatter block
                in_frontmatter = True
                continue
            
            if in_frontmatter and ":" in line_stripped:
                key, value = line_stripped.split(":", 1)
                if key.strip() == target_key:
                    return value.strip()
                    
    return None

def get_pages():
    base_dir = Path("docs/celesta-public-archive/characters")

    page_set = []
    for file_path in base_dir.glob("**/*.md"):
        iid = read_frontmatter_value(file_path, "ID")
        page_set.append(int(iid))

    return page_set

def pageedit(firstAttempt = True, doEditCheck = False, IID = None):
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template not found at {TEMPLATE_PATH.resolve()}")
        return

    if firstAttempt:
        print("--- OC Page Editor ---")

    if IID is None:
        # Prompt for ID
        try:
            id_input = input("Enter Character ID (e.g., 1): ").strip()
            char_id = int(id_input)
        except ValueError:
            print("Error: Invalid ID. Please enter a whole number.")
            pageedit(firstAttempt = False, doEditCheck = doEditCheck) # Try again.
    else:
        char_id = int(IID)

    # Formatting
    id_padded_internal = f"{char_id:04d}"

    base_dir = Path("docs/celesta-public-archive/characters")
    for file_path in base_dir.glob(f"**/oc-{id_padded_internal}*.md"):
        content = file_path.read_text(encoding="utf-8")
        print(f"File opened at: {file_path.name}\n")
        name_value = read_frontmatter_value(file_path, "title")
        print(f"--- EDITING: {name_value.upper()} [#{id_padded_internal}] ---")

        fileEditQuery = "Do you wish to edit this file? Answer true or false. "
        valuEditQuery = "    Do you want to edit this value? Answer true or false. "

        assumeEdit = True
        if doEditCheck:
            assumeEdit = get_bool_from_input(fileEditQuery, input(fileEditQuery).strip())
            if not assumeEdit:
                print(f"--- CLOSING: {name_value.upper()} [#{id_padded_internal}] ---")
                return

        if assumeEdit:
            new_content = content
            
            nicks_value = read_frontmatter_value(file_path, "nicknames")
            print(f"    NICKNAMES: {nicks_value}")
            edit_nicks = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
            if edit_nicks:
                new_content = new_content.replace(f"nicknames: {nicks_value}", "nicknames: " + input("  What to? ").strip())
            print("")
                
            alias_value = read_frontmatter_value(file_path, "online_aliases")
            print(f"    ALIASES: {alias_value}")
            edit_alias = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
            if edit_alias:
                new_content = new_content.replace(f"online_aliases: {alias_value}", f"online_aliases: " + input("   What to? ").strip())
            print("")
                
            dob_value = read_frontmatter_value(file_path, "dob")
            dob_ao_value = read_frontmatter_value(file_path, "age_offset")
            print(f"    DOB: {dob_value}")
            edit_dob = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
            if edit_dob:
                new_dob_val = input("   What to? ").strip()
                new_content = new_content.replace(f"dob: {dob_value}", f"dob: {new_dob_val}")
                
                dob_match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$",new_dob_val)
                date_of = date.today()

                age = 0
                if dob_match:
                    birth_year = int(dob_match.group(1))
                    birth_month = int(dob_match.group(2))
                    birth_day = int(dob_match.group(3))

                    try:
                        birth_date = date(birth_year, birth_month, birth_day)
                    except ValueError:
                        sys.exit("Error: date could not be parsed. Terminating to be safe.")

                    # Calculate precise age by checking if their birthday has occurred yet this year
                    age = date_of.year - birth_date.year
                    if (date_of.month, date_of.day) < (birth_date.month, birth_date.day):
                        age -= 1
                
                dob_ao_value_safe = int(dob_ao_value) if dob_ao_value is not None else 0
                print(f"    AGE OFFSET: {dob_ao_value_safe}")
                print(f"    (This makes for an age of {age + dob_ao_value_safe} as of today.)")
                edit_dob_ao = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
                if edit_dob_ao:
                    new_age_offset_val = input("    What to? (Use a negative value to decrease age.) ").strip()
                    
                    # Split content into lines to safely handle structural insertion
                    lines = new_content.splitlines()
                    updated_lines = []
                    note_inserted = False
                    
                    for line in lines:
                        line_stripped = line.strip()
                        
                        # Update the species name line
                        if line_stripped.lower().startswith("dob:"):
                            # Preserve the original key formatting/spacing
                            key_prefix = line.split(":", 1)[0]
                            updated_lines.append(f"{key_prefix}: {new_dob_val}")
                            continue
                        
                        # If we hit height, check if we need to drop in our warning note right above it
                        if line_stripped.lower().startswith("height:") and not note_inserted:
                            updated_lines.append(f"age_offset: {new_age_offset_val}")
                            note_inserted = True
                            updated_lines.append(line)
                            continue
                        elif line_stripped.lower().startswith("age_offset:") and not note_inserted:
                            updated_lines.append(f"age_offset: {new_age_offset_val}")
                            note_inserted = True
                            continue
                        
                        updated_lines.append(line)
                    
                    # Reassemble the file content safely with correct line breaks
                    new_content = "\n".join(updated_lines) + "\n"
                    print(f"        (This value makes the biological age {int(age) + int(new_age_offset_val)}.)")
            print("")
                
            height_value = read_frontmatter_value(file_path, "height")
            print(f"    HEIGHT: {height_value}")
            edit_height = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
            if edit_height:
                new_content = new_content.replace(f"height: {height_value}", f"height: " + input("  What to? ").strip())
            print("")
                
            sex_value = read_frontmatter_value(file_path, "sex")
            print(f"    SEX: {sex_value}")
            edit_sex = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
            if edit_sex:
                new_content = new_content.replace(f"sex: {sex_value}", f"sex: " + input("   What to? ").strip())
            print("")

            species_value = read_frontmatter_value(file_path, "species.name")
            print(f"    SPECIES: {species_value}")
            edit_species = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
            if edit_species:
                new_species_val = input("   What to? ").strip()
                
                # Split content into lines to safely handle structural insertion
                lines = new_content.splitlines()
                updated_lines = []
                note_inserted = False
                
                for line in lines:
                    line_stripped = line.strip()
                    
                    # Update the species name line
                    if line_stripped.lower().startswith("species.name:"):
                        # Preserve the original key formatting/spacing
                        key_prefix = line.split(":", 1)[0]
                        updated_lines.append(f"{key_prefix}: {new_species_val}")
                        continue
                    
                    # If we hit species.url, check if we need to drop in our warning note right above it
                    if line_stripped.lower().startswith("species.url:") and not note_inserted:
                        updated_lines.append("species.note: 'WARNING: URL NEEDS CHECKING'")
                        note_inserted = True
                    
                    updated_lines.append(line)
                
                # Reassemble the file content safely with correct line breaks
                new_content = "\n".join(updated_lines) + "\n"

                current_species_value = read_frontmatter_value(file_path, "current_species.name")
                print(f"    CURRENT SPECIES: {current_species_value}")
                edit_current_species = get_bool_from_input(valuEditQuery, input(valuEditQuery).strip())
                if edit_current_species:
                    new_current_species_val = input("   What to? ").strip()
                    
                    # Split content into lines to safely handle structural insertion
                    lines = new_content.splitlines()
                    updated_lines = []
                    note_inserted = False
                    
                    for line in lines:
                        line_stripped = line.strip()
                        
                        # Update the species name line
                        if line_stripped.lower().startswith("current_species.name:"):
                            # Preserve the original key formatting/spacing
                            key_prefix = line.split(":", 1)[0]
                            updated_lines.append(f"{key_prefix}: {new_current_species_val}")
                            continue

                        if not line_stripped.lower().startswith("---"):
                            line_previous = lines[lines.index(line) - 1]
                            line_previous_stripped = line_previous.strip()

                            if line_previous_stripped.lower().startswith("species.url:"):
                                if not "current_species.name:" in new_content.lower():
                                    updated_lines.append(f"current_species.name: {new_current_species_val}")
                                    
                                if not line_stripped.lower().startswith("current_species.url:") and not note_inserted:
                                    updated_lines.append("current_species.note: 'WARNING: URL NEEDS CHECKING'")
                                    updated_lines.append("current_species.url: N/A")
                                    note_inserted = True
                                    continue
                                # If we hit species.url, check if we need to drop in our warning note right above it
                                elif line_stripped.lower().startswith("current_species.url:") and not note_inserted:
                                    updated_lines.append("current_species.note: 'WARNING: URL NEEDS CHECKING'")
                                    note_inserted = True
                        
                        updated_lines.append(line)
                    
                    # Reassemble the file content safely with correct line breaks
                    new_content = "\n".join(updated_lines) + "\n"
            print("")
            
            file_path.write_text(new_content, encoding="utf-8")
        print(f"--- CLOSING: {name_value.upper()} [#{id_padded_internal}] ---")
        print("")
        print("")

if __name__ == "__main__":
    pageAddQuery = "Do you want to add a page? Answer true or false. "
    pageChangeQuery = "Do you want to edit a page? Answer true or false. "
    allPageChangeQuery = "Do you want to edit all pages? Answer true or false. "
    
    try:
        tryflag1 = get_bool_from_input(pageAddQuery, input(pageAddQuery).strip())
    except ValueError:
        print("Error: True or False value not provided. Please try again.")

    if tryflag1:
        try:
            trycount_in = input("How many times are you planning on running this? ").strip()
            trycount = int(trycount_in)
        except ValueError:
            print("Error: Invalid count. Please enter a whole number.")

        for x in range(trycount):
            pagemake()
            
    try:
        tryflag2 = get_bool_from_input(pageChangeQuery, input(pageChangeQuery).strip())
    except ValueError:
        print("Error: True or False value not provided. Please try again.")

    if tryflag2:
        try:
            tryflag3 = get_bool_from_input(allPageChangeQuery, input(allPageChangeQuery).strip())
        except ValueError:
            print("Error: True or False value not provided. Please try again.")

        if not tryflag3:
            try:
                trycount_in = input("How many times are you planning on running this? ").strip()
                trycount = int(trycount_in)
            except ValueError:
                print("Error: Invalid count. Please enter a whole number.")

            for x in range(trycount):
                pageedit()
        else:
            pageset = get_pages()
            print(f"There are {len(pageset)} pages to be iterated upon.")
            try:
                trystart_in = input("What character ID do you want to start on? ").strip()
                trystart = int(trystart_in)
            except ValueError:
                print("Error: Invalid count. Please enter a whole number.")
                startFullSetQuery = "Alternatively, would you like to start from zero? "
                startFullSet = get_bool_from_input(startFullSetQuery, input(startFullSetQuery).strip())
                if startFullSet:
                    trystart = 0
                else:
                    trystart = -1
                    while trystart == -1 and not startFullSet:    
                        try:
                            trystart_in = input("What character ID do you want to start on? ").strip()
                            trystart = int(trystart_in)
                        except ValueError:
                            print("Error: Invalid count. Please enter a whole number.")
                            startFullSet = get_bool_from_input(startFullSetQuery, input(startFullSetQuery).strip())
            
            for x in range(len(pageset)):
                if trystart in pageset:
                    compare = pageset.index(trystart)
                    if compare <= x:
                        pageedit(doEditCheck = True, IID = pageset[x])

    batch_clean_all()
