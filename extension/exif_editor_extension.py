import subprocess
import os

import gi
gi.require_version("Nemo", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Nemo, GObject

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class ExifEditorExtension(GObject.GObject, Nemo.MenuProvider):

    def get_file_items(self, *args):
        if len(args) == 2:
            window, files = args
        elif len(args) == 1:
            files = args[0]
            window = None
        else:
            return []

        image_files = [f for f in files if self._is_image(f)]
        if not image_files:
            return []

        item = Nemo.MenuItem(
            name="ExifEditor::edit_exif",
            label="Edit EXIF\u2026",
            tip="Edit EXIF metadata for selected image(s)",
            icon="image-x-generic",
        )
        item.connect("activate", self._on_activate, image_files)
        return [item]

    def _on_activate(self, menu, files):
        paths = [f.get_location().get_path() for f in files]
        if not paths:
            return
        subprocess.Popen(
            ["python3", os.path.join(_SCRIPT_DIR, "exif_editor_launch.py")] + paths,
            close_fds=True,
        )

    def _is_image(self, nemo_file):
        uri = nemo_file.get_uri_scheme()
        if uri and uri.startswith("file://"):
            mime = nemo_file.get_mime_type() or ""
            if mime.startswith("image/"):
                return True
            ext = os.path.splitext(nemo_file.get_name())[1].lower()
            if ext in {
                ".jpg", ".jpeg", ".png", ".tiff", ".tif",
                ".heic", ".heif", ".webp",
                ".cr2", ".cr3", ".nef", ".arw", ".orf", ".raf",
                ".dng", ".rw2", ".pef", ".srw",
            }:
                return True
        return False
