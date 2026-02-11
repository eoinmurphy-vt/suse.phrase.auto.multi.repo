import os
import re
import datetime
import chardet
from pathlib import Path

# --- CONFIGURATION ---
SRC_DIR = os.getenv("SRC_DIR", "translated")
DST_DIR = os.getenv("DST_DIR", "final")
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DST_DIR, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
run_id = os.getenv("GITHUB_RUN_ID", "local")
LOG_FILE = f"{LOG_DIR}/postprocess_log_{timestamp}_{run_id}.txt"

stats = {"processed": 0, "errors": 0, "skipped": 0, "cleaned": 0}

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def detect_and_convert_to_utf8(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()
    info = chardet.detect(raw)
    encoding = info.get("encoding") or "utf-8"
    try:
        text = raw.decode(encoding)
    except Exception:
        stats["errors"] += 1
        log(f"⚠ Decode failed for {file_path}, forcing UTF-8")
        text = raw.decode("utf-8", errors="replace")
    return text

def cleanup_text(text):
    before = text
    # Revert entities and wrappers
    text = re.sub(r'&quot;\`\+([^\`\n]+)\+\`&quot;', r'"`\1`"', text)
    text = re.sub(r'&apos;\`\+([^\`\n]+)\+\`&apos;', r"'`\1`'", text)
    text = re.sub(r'\`\+([^\`\n]+)\+\`', r'`\1`', text)
    text = re.sub(r'\[literal\]#([^#]+)#', r'[monospaced]#\1#', text, flags=re.IGNORECASE)
    text = re.sub(r'\+([A-Za-z0-9/_\.-]+)\+', r'\1', text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r'[ ]{2,}$', '', text, flags=re.MULTILINE)
    
    if text != before: stats["cleaned"] += 1
    return text

def map_output_path(src_path: str, rel: str) -> str:
    """
    Input:  translated/REPO_ID/de_de/docs/.../modules/en/pages/file.adoc
    Output: final/REPO_ID/docs/.../modules/de/pages/file.adoc
    """
    parts = rel.split(os.sep)
    # Expected: [RepoID, LangFolder, ...path...]
    if len(parts) < 3: 
        log(f"⚠ Skipping invalid path depth: {rel}")
        return None

    repo_id = parts[0]
    lang_folder = parts[1]
    lang_code = lang_folder.split("_")[0] # de_de -> de

    # Rebuild path skipping repo_id (0) and lang_folder (1)
    remainder = os.path.join(*parts[2:])
    
    # Replace 'modules/en' with 'modules/target_lang'
    # Adjust this logic if your source paths differ
    if "/modules/en/" in remainder:
        remainder = remainder.replace("/modules/en/", f"/modules/{lang_code}/")
    elif remainder.startswith("modules/en/"):
        remainder = remainder.replace("modules/en/", f"modules/{lang_code}/", 1)

    return os.path.join(DST_DIR, repo_id, remainder)

# --- MAIN ---
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"Postprocess started: {datetime.datetime.now()}\n\n")

for path in Path(SRC_DIR).rglob("*.adoc"):
    src_path = str(path)
    rel = os.path.relpath(src_path, SRC_DIR)
    dst_path = map_output_path(src_path, rel)

    if not dst_path:
        stats["skipped"] += 1
        continue

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    text = detect_and_convert_to_utf8(src_path)
    text = cleanup_text(text)
    
    with open(dst_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    
    stats["processed"] += 1
    log(f"✓ {dst_path}")

log(f"\nSummary: Processed={stats['processed']}, Cleaned={stats['cleaned']}, Errors={stats['errors']}")