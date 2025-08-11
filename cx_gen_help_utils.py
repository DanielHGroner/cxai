import re

# --- Utility Functions ---
# convert some strings to boolean (support CLI)
def str2bool(v):
    return str(v).lower() in ("yes", "y", "true", "t", "1")

# load the prompt template file
def load_prompt_template(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

# substitute certain items in the proompt template
def apply_prompt_substitutions(template, code_lines, include_long, spoken_language):
    code_with_numbers = "\n".join(
        f"{str(i+1).zfill(3)}|{line}" for i, line in enumerate(code_lines)
    )
    
    lang_block = "" if spoken_language.lower() == "english" \
        else f"Please write all responses in {spoken_language}."

    return template.replace("{numbered_code}", code_with_numbers) \
                   .replace("{spokenLanguageBlock}", lang_block)

# convert string to list of strings
def str_to_list(source):
    return [line for line in source.splitlines()]

# TODO - add comment here
def parse_ai_help_text(text):
    help_data = {}
    for line in text.splitlines():
        #print(line)
        if not re.match(r'^\d{3}\|', line):
            continue
        parts = line.strip().rstrip(';').split('|')
        if len(parts) < 2:
            continue
        line_number = parts[0]
        short = parts[1].strip()
        long = parts[2].strip() if len(parts) > 2 else ""
        help_data[line_number] = {"short": short, "long": long}
    return help_data
