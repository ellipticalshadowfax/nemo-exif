#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_EXT="$HOME/.local/share/nemo/extensions"
DEST_CONF="$HOME/.config/exif-editor"
SEED="$SCRIPT_DIR/fields.json"

echo "Installing Nemo EXIF Editor plugin..."

# Install exiftool if missing
if ! command -v exiftool &>/dev/null; then
    echo "Installing libimage-exiftool-perl..."
    sudo apt install -y libimage-exiftool-perl
else
    echo "exiftool already installed: $(exiftool -ver)"
fi

# Copy extension files
mkdir -p "$DEST_EXT"
cp "$SCRIPT_DIR/extension/exif_editor_extension.py" "$DEST_EXT/"
cp "$SCRIPT_DIR/extension/exif_editor_launch.py" "$DEST_EXT/"
cp -r "$SCRIPT_DIR/extension/exif_editor" "$DEST_EXT/"

# Copy default fields config if not present
mkdir -p "$DEST_CONF"
if [ ! -f "$DEST_CONF/fields.json" ]; then
    cp "$SEED" "$DEST_CONF/fields.json"
    echo "Default fields config written to $DEST_CONF/fields.json"
else
    echo "Fields config already exists at $DEST_CONF/fields.json (not overwritten)"
fi

# Restart Nemo
if command -v nemo &>/dev/null; then
    nemo -q 2>/dev/null || true
    echo "Nemo restarted."
fi

echo ""
echo "Done. Right-click an image in Nemo and choose 'Edit EXIF…'."
