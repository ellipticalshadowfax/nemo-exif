# nemo-exif

A Nemo file manager plugin for editing EXIF metadata on images and camera RAW files. Right-click any image in Nemo and choose **Edit EXIF…** to open a modal editor dialog.

## Features

- **Modal editor dialog** — select one or more images, right-click, choose "Edit EXIF…"
- **Lossless editing** — uses exiftool for in-place metadata writes; thumbnails, ICC profiles, and MakerNotes are preserved
- **RAW support** — CR2, CR3, NEF, ARW, DNG, ORF, RAF, RW2, PEF, and more
- **Diff-based writes** — only changed fields are written to the file; untouched metadata is never touched
- **Clear all fields** — toggle to strip all existing metadata and write only your chosen values
- **Configurable field visibility** — add, remove, or hide fields via an in-dialog picker or by editing `~/.config/exif-editor/fields.json`
- **Multi-select** — batch-apply edits across multiple files at once

## Requirements

- Nemo file manager (tested on 6.6.3)
- Python 3 with GObject Introspection and GTK 3 bindings (`python3-gi`)
- exiftool (`libimage-exiftool-perl`)

## Install

```bash
bash install.sh
```

The install script:
1. Installs `libimage-exiftool-perl` via apt (if not already present)
2. Copies extension files to `~/.local/share/nemo/extensions/`
3. Seeds the default field config to `~/.config/exif-editor/fields.json`
4. Restarts Nemo

## Usage

1. In Nemo, select one or more image/RAW files
2. Right-click and choose **Edit EXIF…**
3. Edit fields in the dialog — changed fields are marked with a blue `*`
4. Click **Save** to write changes

### Fields picker

Click the **Fields…** button in the editor to show/hide fields. Changes persist to `~/.config/exif-editor/fields.json`.

### Clear all fields

Tick **Clear all fields before writing** to strip all metadata from the selected files and write only the values shown in the dialog. Use this to reset or anonymize files.

## Field configuration

Edit `~/.config/exif-editor/fields.json` to customise the editor. Each field entry:

```json
{
  "id": "make",
  "label": "Camera Make",
  "tag": "Make",
  "type": "text",
  "visible": true
}
```

| Key | Description |
|---|---|
| `id` | Unique identifier (used internally) |
| `label` | Display name shown in the editor dialog |
| `tag` | [exiftool tag name](https://exiftool.org/TagNames/) |
| `type` | `text`, `number`, or `date` |
| `visible` | Whether the field is shown by default (`true`/`false`) |

### Supported tags

The default config includes: Make, Model, LensMake, LensModel, FocalLength, FocalLengthIn35mmFormat, ISO, DateTimeOriginal, ImageDescription, Artist, Copyright, UserComment (Film Type), GPSLatitude, GPSLongitude.

Any exiftool tag can be added — see [exiftool Tag Names](https://exiftool.org/TagNames/) for the full list.

## Architecture

```
exif_editor_extension.py   Nemo MenuProvider (registers context menu item)
exif_editor_launch.py      Subprocess launcher (isolates GTK from Nemo process)
exif_editor/
  editor.py                GTK3 modal dialog, field rows, Fields picker
  exif_lib.py              exiftool read/write, diff engine, config loader
```

The extension spawns a subprocess for the editor dialog so it never blocks Nemo's main loop. Communication with exiftool uses JSON output (`exiftool -json -a`) for reads and direct flag arguments for writes (`exiftool -overwrite_original_in_place`).

## Network / GVFS mounts (SMB, NFS, etc.)

The plugin works on GVFS-mounted network shares (SMB/SFTP/etc.), but writes use a copy-to-temp-edit-copy-back strategy because exiftool cannot write directly to GVFS-FUSE mounts. Each file is transferred over the network twice (once to read, once to write back).

**Per-file overhead:**
- Network: 2x file size (1 read + 1 write)
- Temp disk: ~2x file size peak, cleaned between files
- RAM: ~2x file size peak (original + modified held briefly)

| Files | Avg size | Network | Time (50 MB/s) |
|---|---|---|---|
| 36 | 4.5 MB (JPEG) | 324 MB | ~21 s |
| 2,000 | 4.5 MB (JPEG) | 17.6 GB | ~10 min |
| 36 | 50 MB (RAW) | 3.6 GB | ~2.4 min |
| 2,000 | 50 MB (RAW) | 200 GB | ~2.2 hours |

For local files, writes are in-place with no overhead. To avoid network overhead on large batches, consider editing files locally first, then copying them to the share.

## Uninstall

```bash
rm ~/.local/share/nemo/extensions/exif_editor_extension.py
rm ~/.local/share/nemo/extensions/exif_editor_launch.py
rm -rf ~/.local/share/nemo/extensions/exif_editor/
nemo -q
```

The config at `~/.config/exif-editor/fields.json` is left in place. Remove it manually if desired.
