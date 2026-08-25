#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from exif_editor.editor import ExifEditorDialog


def main():
    if len(sys.argv) < 2:
        print("Usage: exif_editor_launch.py <file> [file ...]", file=sys.stderr)
        sys.exit(1)

    filepaths = sys.argv[1:]

    dlg = ExifEditorDialog(filepaths)
    resp = dlg.run()

    if resp == Gtk.ResponseType.OK:
        saved = dlg.apply()
        if saved:
            pass

    dlg.destroy()


if __name__ == "__main__":
    main()
