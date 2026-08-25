import json
import os
import shutil
import subprocess

CONFIG_DIR = os.path.expanduser("~/.config/exif-editor")
CONFIG_PATH = os.path.join(CONFIG_DIR, "fields.json")
SEED_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fields.json")


def _config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_fields():
    _config_dir()
    if not os.path.isfile(CONFIG_PATH) and os.path.isfile(SEED_PATH):
        shutil.copy2(SEED_PATH, CONFIG_PATH)
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("fields", [])
    if os.path.isfile(SEED_PATH):
        with open(SEED_PATH, "r") as f:
            return json.load(f).get("fields", [])
    return []


def save_fields(fields):
    _config_dir()
    with open(CONFIG_PATH, "w") as f:
        json.dump({"fields": fields}, f, indent=2)


def visible_tags(fields):
    return [f["tag"] for f in fields if f.get("visible", True)]


def _run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "exiftool failed")
    return result.stdout


def read_exif(filepath, tags):
    if not tags:
        return {}
    args = ["exiftool", "-json", "-a"] + [f"-{t}" for t in tags] + [filepath]
    out = _run(args)
    data = json.loads(out)
    if not data:
        return {}
    record = data[0]
    flat = {}
    for fdef in fields_map(load_fields()).values():
        tag = fdef["tag"]
        val = record.get(tag, record.get(tag.replace(" ", ""), None))
        if val is None:
            flat[fdef["id"]] = ""
        else:
            flat[fdef["id"]] = _unify_value(val)
    return flat


def read_exif_batch(filepaths, tags):
    results = {}
    for fp in filepaths:
        results[fp] = read_exif(fp, tags)
    return results


def _unify_value(val):
    if isinstance(val, list):
        return "; ".join(str(v) for v in val)
    return str(val)


def fields_map(fields):
    return {f["id"]: f for f in fields}


def compute_diff(original, current, fields):
    diff = {}
    fmap = fields_map(fields)
    for fid, orig_val in original.items():
        cur_val = current.get(fid, "")
        if cur_val != orig_val:
            diff[fid] = cur_val
    return diff


def write_exif(filepath, diff, fields, clear_all=False):
    fmap = fields_map(fields)
    args = ["exiftool", "-overwrite_original_in_place"]

    if clear_all:
        args.append("-all=")

    for fid, val in diff.items():
        if fid not in fmap:
            continue
        tag = fmap[fid]["tag"]
        if val:
            args.append(f"-{tag}={val}")
        else:
            args.append(f"-{tag}=")

    args.append(filepath)
    _run(args)


def write_exif_batch(filepaths, diff, fields, clear_all=False):
    fmap = fields_map(fields)
    for fp in filepaths:
        write_exif(fp, diff, fields, clear_all=clear_all)


def can_edit(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return ext in _SUPPORTED_EXTENSIONS


_SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tiff", ".tif",
    ".heic", ".heif", ".webp",
    ".cr2", ".cr3", ".nef", ".arw", ".orf", ".raf",
    ".dng", ".rw2", ".pef", ".srw", ".3fr", ".mef",
}
