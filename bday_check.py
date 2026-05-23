import os
import yaml
import requests
from datetime import datetime, date

# --- CONFIGURATION HUB ---
CHARACTER_DIR = "docs/celesta-public-archive"
PUBLIC_CELEBRATION_WEBHOOK = "https://discord.com/api/webhooks/1476473537681162300/l9NP-zJH3Xa-UXwFIgymu2SFb8oMf0-ftu0VGqJtFZj-xnCqquOd9mn89K3qzN7Fhc1w?thread_id=1476475882658074655"
YOUR_NAME = "Jeremy David Peifer"
SITE_BASE_URL = "https://spiro9-peef.github.io/s9-storywiki-pages/"  # Your automated site deployment base URL

def parse_date(date_input):
    if not date_input: return None
    if isinstance(date_input, str):
        try: return datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError: return None
    if isinstance(date_input, (date, datetime)):
        return date_input if isinstance(date_input, date) else date_input.date()
    return None

def execute_anniversary_run():
    today = date.today()
    public_embeds = []

    if not os.path.exists(CHARACTER_DIR):
        print(f"Error: Target directory '{CHARACTER_DIR}' could not be located.")
        return

    for root, _, files in os.walk(CHARACTER_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if not content.startswith('---'): continue
                        
                        parts = content.split('---', 2)
                        meta = yaml.safe_load(parts[1])
                        
                        if not meta or meta.get('universe') != 'rotc' or 'dob' not in meta:
                            continue

                        birth_date = parse_date(meta.get('dob'))
                        death_date = parse_date(meta.get('dod'))
                        age_offset = int(meta.get('age_offset', 0))
                        
                        # Correct alignment: Focus strictly on title metadata for the character's name
                        name = meta.get('title', meta.get('sidebar', file.replace('.md', '')))

                        if birth_date and birth_date.month == today.month and birth_date.day == today.day:
                            
                            # Chronological Age Calculation
                            end_point = death_date if death_date else today
                            chron_years = end_point.year - birth_date.year
                            if (today.month < birth_date.month or 
                               (today.month == birth_date.month and today.day < birth_date.day)):
                                chron_years -= 1
                                
                            bio_years = chron_years + age_offset
                            fmt = lambda d: f"{d.month}/{d.day}/{d.year}"
                            ref_str = f"(b. {fmt(birth_date)}{' - d. ' + fmt(death_date) if death_date else ''})"
                            
                            # Automate site link creation based entirely on relative path location
                            relative_path = os.path.relpath(file_path, "docs/").replace(".md", "/").replace("\\", "/")
                            wiki_url = f"{SITE_BASE_URL.rstrip('/')}/{relative_path.lstrip('/')}"

                            # Public Webhook Structural Arrays (Using safe native .append methods)
                            if name != YOUR_NAME:
                                if death_date:
                                    public_embeds.append({
                                        "title": f"In Memoriam: {name}",
                                        "description": f"Today marks the birth anniversary of {name}. Though no longer with us, their legacy remains in the Archive.",
                                        "url": wiki_url,
                                        "color": 6323558,
                                        "fields": [
                                            { "name": "Final Age", "value": f"{chron_years} years", "inline": True },
                                            { "name": "Life Record", "value": ref_str, "inline": True }
                                        ]
                                    })
                                else:
                                    public_embeds.append({
                                        "title": f"Happy Birthday to: {name}",
                                        "description": f"Wishing a happy birthday to **{name}**! They have officially turned **{bio_years}** today.",
                                        "url": wiki_url,
                                        "color": 16766720,
                                        "fields": [
                                            { "name": "Current Chronological Age", "value": f"{chron_years} years", "inline": True },
                                            { "name": "Bio Age", "value": f"{bio_years} years", "inline": True }
                                        ]
                                    })
                except Exception as e:
                    print(f"Skipping malformed profile asset {file}: {e}")

    if public_embeds:
        payload = {"content": "🎊 **Archive Anniversary Detected!**", "embeds": public_embeds}
        requests.post(PUBLIC_CELEBRATION_WEBHOOK, json=payload)

if __name__ == "__main__":
    execute_anniversary_run()