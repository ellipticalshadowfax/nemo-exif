#!/usr/bin/env python3
import sys
import os
import traceback

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

    try:
        dlg = ExifEditorDialog(filepaths)
        resp = dlg.run()

        if resp == Gtk.ResponseType.OK:
            saved = dlg.apply()
            if saved:
                pass

        dlg.destroy()
    except Exception as e:
        tb = traceback.format_exc()
        dlg = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="EXIF Editor Error",
        )
        dlg.format_secondary_text(str(e))
        dlg.run()
        dlg.destroy()
        print(tb, file=sys.stderr)


if __name__ == "__main__":
    main()
