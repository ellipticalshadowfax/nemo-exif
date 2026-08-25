import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import exif_lib


class FieldEditorRow:
    def __init__(self, field_def):
        self.field_def = field_def
        self.fid = field_def["id"]
        self.original_value = ""
        self.label = Gtk.Label(label=field_def["label"], xalign=0)
        self.label.set_size_request(140, -1)

        ftype = field_def.get("type", "text")
        if ftype == "date":
            self.entry = Gtk.Entry()
            self.entry.set_placeholder_text("YYYY:MM:DD HH:MM:SS")
        elif ftype == "number":
            self.entry = Gtk.SpinButton.new_with_range(0, 99999, 1)
            self.entry.set_numeric(False)
        else:
            self.entry = Gtk.Entry()

        self.changed_indicator = Gtk.Label(label="")
        self.changed_indicator.set_markup("")

        self.grid = Gtk.Grid(column_spacing=8, row_spacing=4)
        self.grid.attach(self.label, 0, 0, 1, 1)
        self.grid.attach(self.entry, 1, 0, 1, 1)
        self.grid.attach(self.changed_indicator, 2, 0, 1, 1)

    def set_value(self, val):
        self.original_value = val
        if isinstance(self.entry, Gtk.SpinButton):
            try:
                self.entry.set_value(float(val))
            except (ValueError, TypeError):
                self.entry.set_value(0)
        else:
            self.entry.set_text(val or "")
        self._refresh_indicator()

    def get_value(self):
        if isinstance(self.entry, Gtk.SpinButton):
            v = self.entry.get_value()
            return "" if v == 0 else str(v)
        return self.entry.get_text()

    def is_changed(self):
        return self.get_value() != self.original_value

    def _refresh_indicator(self):
        if self.is_changed():
            self.changed_indicator.set_markup("<span color='blue'>*</span>")
        else:
            self.changed_indicator.set_markup("")

    def connect_change(self):
        if isinstance(self.entry, Gtk.SpinButton):
            self.entry.connect("value-changed", lambda *_: self._refresh_indicator())
        else:
            self.entry.connect("changed", lambda *_: self._refresh_indicator())


class FieldsPickerDialog(Gtk.Dialog):
    def __init__(self, parent, fields):
        super().__init__(
            title="Visible Fields",
            transient_for=parent,
            modal=True,
        )
        self.fields = fields
        self.checks = []

        self.add_buttons("Close", Gtk.ResponseType.CLOSE)
        box = self.get_content_area()
        box.set_spacing(4)

        label = Gtk.Label(label="Tick the fields you want visible in the editor:")
        label.set_xalign(0)
        box.pack_start(label, False, False, 4)

        for f in self.fields:
            cb = Gtk.CheckButton.new_with_label(f"{f['label']}  ({f['tag']})")
            cb.set_active(f.get("visible", True))
            cb.field_id = f["id"]
            self.checks.append(cb)
            box.pack_start(cb, False, False, 2)

        self.set_default_size(400, -1)
        self.show_all()

    def get_visibility(self):
        return {cb.field_id: cb.get_active() for cb in self.checks}


class ExifEditorDialog(Gtk.Dialog):
    def __init__(self, filepaths, parent=None):
        self.filepaths = filepaths
        self.fields = exif_lib.load_fields()
        self.rows = []
        self.originals = {}

        window_title = "Edit EXIF"
        if len(filepaths) == 1:
            window_title += f" — {filepaths[0].split('/')[-1]}"
        else:
            window_title += f" — {len(filepaths)} files"

        super().__init__(
            title=window_title,
            transient_for=parent,
            modal=True,
        )
        self.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Save", Gtk.ResponseType.OK,
        )

        self._build_ui()
        self._load_values()
        self.set_default_size(520, -1)
        self.show_all()

    def _build_ui(self):
        box = self.get_content_area()
        box.set_spacing(6)

        toolbar = Gtk.Grid(column_spacing=8)
        self.clear_all_check = Gtk.CheckButton.new_with_label("Clear all fields before writing")
        toolbar.attach(self.clear_all_check, 0, 0, 1, 1)
        fields_btn = Gtk.Button(label="Fields\u2026")
        fields_btn.connect("clicked", self._on_fields_picker)
        toolbar.attach(fields_btn, 1, 0, 1, 1)
        box.pack_start(toolbar, False, False, 4)

        self.fields_grid = Gtk.Grid(column_spacing=8, row_spacing=4)
        box.pack_start(self.fields_grid, False, False, 4)

        visible = [f for f in self.fields if f.get("visible", True)]
        for i, fdef in enumerate(visible):
            row = FieldEditorRow(fdef)
            row.connect_change()
            self.rows.append(row)
            self.fields_grid.attach(row.grid, 0, i, 1, 1)

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        box.pack_start(self.status_label, False, False, 2)

    def _load_values(self):
        tags = exif_lib.visible_tags(self.fields)
        first_data = exif_lib.read_exif(self.filepaths[0], tags)
        self.originals = dict(first_data)

        for row in self.rows:
            row.set_value(first_data.get(row.fid, ""))

        if len(self.filepaths) > 1:
            self.status_label.set_text(
                f"Loaded from {self.filepaths[0].split('/')[-1]}; "
                "save will apply changes to all {0} files".format(len(self.filepaths))
            )
        else:
            self.status_label.set_text("")

    def _on_fields_picker(self, _btn):
        dlg = FieldsPickerDialog(self, self.fields)
        resp = dlg.run()
        if resp == Gtk.ResponseType.CLOSE:
            visibility = dlg.get_visibility()
            for f in self.fields:
                if f["id"] in visibility:
                    f["visible"] = visibility[f["id"]]
            exif_lib.save_fields(self.fields)
            self._rebuild_rows()
        dlg.destroy()

    def _rebuild_rows(self):
        for row in self.rows:
            self.fields_grid.remove(row.grid)
        self.rows.clear()

        visible = [f for f in self.fields if f.get("visible", True)]
        for i, fdef in enumerate(visible):
            row = FieldEditorRow(fdef)
            row.connect_change()
            row.set_value(self.originals.get(fdef["id"], ""))
            self.rows.append(row)
            self.fields_grid.attach(row.grid, 0, i, 1, 1)

        self.fields_grid.show_all()

    def get_diff(self):
        current = {row.fid: row.get_value() for row in self.rows}
        return exif_lib.compute_diff(self.originals, current, self.fields)

    def is_clear_all(self):
        return self.clear_all_check.get_active()

    def apply(self):
        diff = self.get_diff()
        clear_all = self.is_clear_all()

        if clear_all:
            non_empty = {fid: val for fid, val in diff.items() if val}
            if not non_empty:
                return False
            exif_lib.write_exif_batch(self.filepaths, non_empty, self.fields, clear_all=True)
        else:
            if not diff:
                return False
            exif_lib.write_exif_batch(self.filepaths, diff, self.fields, clear_all=False)

        return True
