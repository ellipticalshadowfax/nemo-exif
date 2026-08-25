import re
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, GLib, Pango, Gdk

from . import exif_lib

DATE_RE = re.compile(r"^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}$")

FILM_SEED = [
    "Kentmere 100", "Kentmere 200", "Kentmere 400",
    "Fomapan 100", "Fomapan 200", "Fomapan 400",
    "Kodak Tri-X 400", "Kodak TMAX 100", "Kodak TMAX 400",
    "Kodak Ektar 100", "Kodak Gold 200", "Kodak Gold 400",
    "Kodak Portra 160", "Kodak Portra 400", "Kodak Portra 800",
    "Kodak ColorPlus 200", "Kodak ProImage 100",
    "Ilford FP4 125", "Ilford HP5 400", "Ilford Delta 100",
    "Ilford Delta 400", "Ilford Delta 3200", "Ilford XP2 400",
    "Ilford Pan F 50", "Ilford Ortho Plus 80",
    "Fuji Superia 400", "Fuji Superia X-TRA 400",
    "Fuji Velvia 50", "Fuji Velvia 100", "Fuji Provia 100F",
    "Fuji Pro 400H", "Fuji C200", "Fuji Natura 1600",
    "Harman ARCOS 100", "Harman Phoenix 200",
    "Cinestill 800T", "Cinestill 50D",
    "Lomography 800", "Lomography 400", "Lomography 100",
    "Rollei RPX 25", "Rollei RPX 100", "Rollei RPX 400",
    "Bergger Pancro 400", "Adox CMS 20", "Adox Silvermax",
]

MAKE_SEED = [
    "Nikon", "Canon", "Pentax", "Honeywell",
    "Mamiya", "Zeiss", "Kodak", "Voigtländer", "Voigtlander",
    "Leica", "Hasselblad", "Bronica", "Zenza Bronica",
    "Rollei", "Minolta", "Olympus", "Yashica", "Fujifilm",
    "Konica", "Sigma", "Ricoh",
]

MODEL_SEED = [
    "Nikon F", "Nikon F Photomic", "Nikon F2", "Nikon F2S", "Nikon F2SB",
    "Nikon F2A", "Nikon F2AS", "Nikon F3", "Nikon F3HP", "Nikon F3T",
    "Nikon F3P", "Nikon FM", "Nikon FE", "Nikon FA", "Nikon FG",
    "Nikon FG20", "Nikon EM", "Nikon FM2", "Nikon FM2n", "Nikon FE2",
    "Nikon FM10", "Nikon FE10", "Nikon FM3a", "Nikon F4", "Nikon F4s",
    "Nikon F4e", "Nikon F5", "Nikon F6", "Nikon N2000", "Nikon N2020",
    "Nikon N4004", "Nikon N6000", "Nikon N6006", "Nikon N8008",
    "Nikon N8008s", "Nikon N90", "Nikon N90s", "Nikon F50", "Nikon F60",
    "Nikon F65", "Nikon F70", "Nikon F75", "Nikon F80", "Nikon F100",
    "Canon 7", "Canon Canonet QL17", "Canon AE-1", "Canon AE-1 Program",
    "Canon A-1", "Canon AT-1", "Canon AV-1", "Canon F-1", "Canon New F-1",
    "Canon T50", "Canon T70", "Canon T80", "Canon T90", "Canon EF",
    "Canon EOS 1", "Canon EOS 10", "Canon EOS 100", "Canon EOS 5",
    "Canon EOS 300", "Canon EOS 1000",
    "Pentax K1000", "Pentax Spotmatic", "Pentax Spotmatic II",
    "Pentax Spotmatic F", "Pentax ES", "Pentax ES II", "Pentax KM",
    "Pentax KX", "Pentax MX", "Pentax ME", "Pentax ME Super",
    "Pentax MV", "Pentax MV1", "Pentax LX", "Pentax MZ-5",
    "Pentax MZ-6", "Pentax 17", "Pentax 67", "Pentax 645",
    "Honeywell Pentax SPOTMATIC",
    "Mamiya 645", "Mamiya M645", "Mamiya M645 1000S", "Mamiya M645J",
    "Mamiya 645 Super", "Mamiya 645 Pro", "Mamiya 645 Pro-TL",
    "Mamiya 645E", "Mamiya RB67", "Mamiya RZ67", "Mamiya 7",
    "Mamiya 7 II", "Mamiya C330", "Mamiya C220",
    "Zeiss Ikon Contaflex", "Zeiss Ikon Contarex", "Contax RTS",
    "Contax RTS II", "Contax RTS III", "Contax AX", "Contax RX",
    "Contax G1", "Contax G2", "Contax T2", "Contax T3",
    "Kodak Retina", "Kodak Retina II", "Kodak Retina III",
    "Kodak Retina IIIc", "Kodak Retinette", "Kodak Ektra",
    "Kodak Medalist", "Kodak 35",
    "Voigtländer Bessa", "Voigtländer Bessa I", "Voigtländer Bessa II",
    "Voigtländer Bessa 66", "Voigtländer Bessa R", "Voigtländer Bessa R2",
    "Voigtländer Bessa R3", "Voigtländer Bessa R4", "Voigtländer Bessa L",
    "Voigtländer Vito", "Voigtländer Vito B", "Voigtländer Vito BL",
    "Voigtländer Vitessa", "Voigtländer Vitessa T",
    "Voigtländer Prominent", "Voigtländer Bessamatic",
    "Voigtländer Ultramatic", "Voigtländer Perkeo",
    "Leica M3", "Leica M2", "Leica M1", "Leica M4", "Leica M4-2",
    "Leica M4-P", "Leica M5", "Leica M6", "Leica M6 TTL", "Leica M7",
    "Leica M8", "Leica M9", "Leica MP", "Leica MA", "Leica CL",
    "Leica IIIf", "Leica IIIg", "Leica R3", "Leica R4", "Leica R5",
    "Leica R6", "Leica R7", "Leica R8", "Leica R9",
    "Hasselblad 500C", "Hasselblad 500C/M", "Hasselblad 500EL",
    "Hasselblad 503CW", "Hasselblad 555ELD", "Hasselblad 2000FC",
    "Hasselblad 2003FCW", "Hasselblad Xpan", "Hasselblad Xpan II",
    "Zenza Bronica ETR", "Zenza Bronica ETRSi", "Zenza Bronica SQ",
    "Zenza Bronica SQ-A", "Zenza Bronica SQ-B", "Zenza Bronica GS-1",
    "Zenza Bronica RF645", "Zenza Bronica S2",
    "Rolleiflex 2.8F", "Rolleiflex T", "Rolleiflex 6000",
    "Rolleiflex 6008", "Rolleiflex 2000FC", "Rollei 35",
    "Rollei 35S", "Rollei 35T", "Rollei B35", "Rollei C35",
    "Rolleicord",
    "Minolta SR-T 101", "Minolta SR-T 100", "Minolta SR-T 201",
    "Minolta SR-T 303", "Minolta X-700", "Minolta X-370",
    "Minolta XG7", "Minolta XG9", "Minolta XG1", "Minolta CLE",
    "Minolta Alpha 7000", "Minolta Maxxum 7000",
    "Olympus OM-1", "Olympus OM-1N", "Olympus OM-2", "Olympus OM-2N",
    "Olympus OM-2S", "Olympus OM-3", "Olympus OM-3T", "Olympus OM-4",
    "Olympus OM-4T", "Olympus OM-10", "Olympus OM-20", "Olympus OM-30",
    "Olympus OM-40", "Olympus Pen EE", "Olympus Pen D",
    "Olympus Pen FT", "Olympus 35RC", "Olympus 35SP",
    "Yashica Electro 35", "Yashica Electro 35 GSN",
    "Yashica Mat 124G", "Yashica Mat LM", "Yashica T4", "Yashica T5",
    "Yashica FX-3", "Yashica FR", "Yashica Samurai",
    "Fujifilm GW670", "Fujifilm GW690", "Fujifilm GA645",
    "Fujifilm GA645i", "Fujifilm TX-1", "Fujifilm TX-2",
    "Fujifilm Klasse", "Fujifilm Natura Black",
    "Konica Autoreflex T3", "Konica Autoreflex TC", "Konica FS-1",
    "Konica FT-1", "Konica Hexar RF", "Konica Hexar",
]

FILM_CAMERA_TAGS = {
    "Make", "Model",
    "LensMake", "LensModel", "LensInfo",
    "FocalLength", "FocalLengthIn35mmFormat",
    "ISO", "ISO2",
    "FNumber", "ExposureTime", "ExposureProgram",
    "ExposureCompensation", "MeteringMode",
    "Flash", "WhiteBalance",
    "DateTimeOriginal", "CreateDate", "ModifyDate",
    "Artist", "Copyright",
    "ImageDescription", "UserComment",
    "XPAuthor", "XPTitle", "XPComment",
    "GPSLatitude", "GPSLongitude", "GPSAltitude",
    "GPSLatitudeRef", "GPSLongitudeRef",
    "BodySerialNumber", "LensSerialNumber", "OwnerName",
    "LensID", "LensSpec",
    "FilmType", "FilmStock", "FilmMode", "FilmGrain",
}


class FieldEditorRow:
    _TAG_SEEDS = {
        "FilmType": FILM_SEED,
        "FilmStock": FILM_SEED,
        "UserComment": FILM_SEED,
        "Make": MAKE_SEED,
        "LensMake": MAKE_SEED,
        "Model": MODEL_SEED,
        "LensModel": MODEL_SEED,
    }

    def __init__(self, field_def):
        self.field_def = field_def
        self.fid = field_def["id"]
        self.original_value = ""
        self.is_date = field_def.get("type") == "date"
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

        tag = field_def.get("tag")
        seeds = self._TAG_SEEDS.get(tag)
        if seeds and isinstance(self.entry, Gtk.Entry):
            completion = Gtk.EntryCompletion()
            completion.set_model(Gtk.ListStore(str))
            for s in seeds:
                completion.get_model().append([s])
            completion.set_text_column(0)
            completion.set_match_func(self._completion_match)
            self.entry.set_completion(completion)

        self.changed_indicator = Gtk.Label(label="")
        self.changed_indicator.set_markup("")

        self.grid = Gtk.Grid(column_spacing=8, row_spacing=4)
        self.grid.attach(self.label, 0, 0, 1, 1)
        self.grid.attach(self.entry, 1, 0, 1, 1)
        self.grid.attach(self.changed_indicator, 2, 0, 1, 1)

    def _completion_match(self, completion, key, iter, data=None):
        model = completion.get_model()
        row_text = model.get_value(iter, 0).lower()
        return key.lower() in row_text

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

    def is_valid(self):
        if self.is_date:
            val = self.get_value()
            if not val:
                return True
            return DATE_RE.match(val) is not None
        return True

    def _refresh_indicator(self):
        if self.is_date and not self.is_valid():
            self.changed_indicator.set_markup("<span color='red'>!</span>")
            self.entry.set_name("invalid-entry")
        else:
            self.entry.set_name("")
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
            title="Add / Remove Fields",
            transient_for=parent,
            modal=True,
        )
        self.fields = list(fields)
        self.all_tags = exif_lib.load_all_tags()
        self.tag_rows = []

        self.add_buttons("Close", Gtk.ResponseType.CLOSE)
        box = self.get_content_area()
        box.set_spacing(4)

        search_box = Gtk.Box(spacing=6)
        search_label = Gtk.Label(label="Search:")
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Filter tags\u2026")
        self.search_entry.connect("search-changed", self._on_search)
        search_box.pack_start(search_label, False, False, 0)
        search_box.pack_start(self.search_entry, True, True, 0)
        box.pack_start(search_box, False, False, 4)

        self.configured_tags = {f["tag"]: f for f in self.fields}
        self.list_box = Gtk.ListBox()
        self.list_box.set_filter_func(self._filter_func)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(400)
        scroll.set_max_content_height(600)
        scroll.add(self.list_box)
        box.pack_start(scroll, True, True, 0)

        self._populate_list()
        self.set_default_size(500, -1)
        self.show_all()

    def _populate_list(self):
        shown = set()
        for tag_def in sorted(self.all_tags, key=lambda t: (
            t["tag"] not in FILM_CAMERA_TAGS,
            t["tag"] not in self.configured_tags,
            t["tag"].lower(),
        )):
            tag = tag_def["tag"]
            if tag in shown:
                continue
            shown.add(tag)
            desc = tag_def.get("description", "")
            cfg = self.configured_tags.get(tag)
            active = cfg.get("visible", True) if cfg else False

            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            cb = Gtk.CheckButton()
            cb.set_active(active)
            cb.tag_name = tag
            cb.field_def = cfg

            label_text = tag
            if desc and desc != tag:
                label_text = f"{tag}  —  {desc}"
            if cfg:
                label_text += "  [configured]"

            lbl = Gtk.Label(label=label_text, xalign=0)
            lbl.set_ellipsize(3)  # Pango.EllipsizeMode.END
            row_box.pack_start(cb, False, False, 0)
            row_box.pack_start(lbl, True, True, 0)

            row = Gtk.ListBoxRow()
            row.add(row_box)
            self.list_box.add(row)
            self.tag_rows.append((row, cb, tag.lower(), desc.lower()))

        self.list_box.show_all()

    def _filter_func(self, row):
        query = self.search_entry.get_text().strip().lower()
        if not query:
            return True
        for r, cb, tag_lower, desc_lower in self.tag_rows:
            if r == row:
                return query in tag_lower or query in desc_lower
        return False

    def _on_search(self, _entry):
        self.list_box.invalidate_filter()

    def get_result(self):
        active_tags = {}
        for r, cb, _, _ in self.tag_rows:
            if cb.get_active():
                active_tags[cb.tag_name] = cb.field_def
        return active_tags


class ExifEditorDialog(Gtk.Dialog):
    def __init__(self, filepaths, parent=None):
        self.filepaths = filepaths
        self.fields = exif_lib.load_fields()
        self.rows = []
        self.originals = {}

        window_title = "Edit EXIF"
        if len(filepaths) == 1:
            window_title += f" \u2014 {filepaths[0].split('/')[-1]}"
        else:
            window_title += f" \u2014 {len(filepaths)} files"

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
        self.set_default_size(580, 600)
        self.show_all()

    def _build_ui(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"#invalid-entry { border: 2px solid red; }")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

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

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(300)
        scroll.add(self.fields_grid)
        box.pack_start(scroll, True, True, 0)

        visible = [f for f in self.fields if f.get("visible", True)]
        for i, fdef in enumerate(visible):
            row = FieldEditorRow(fdef)
            row.connect_change()
            self.rows.append(row)
            self.fields_grid.attach(row.grid, 0, i, 1, 1)

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        box.pack_start(self.status_label, False, False, 2)

        self.progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_label = Gtk.Label()
        self.progress_label.set_xalign(0)
        self.progress_box.pack_start(self.progress_label, False, False, 0)
        self.progress_box.pack_start(self.progress_bar, False, False, 0)
        self.progress_box.set_no_show_all(True)
        box.pack_start(self.progress_box, False, False, 2)

    def _load_values(self):
        tags = exif_lib.visible_tags(self.fields)
        first_data = exif_lib.read_exif(self.filepaths[0], tags)
        self.originals = dict(first_data)

        for row in self.rows:
            row.set_value(first_data.get(row.fid, ""))

        if len(self.filepaths) > 1:
            self.status_label.set_text(
                f"Loaded from {self.filepaths[0].split('/')[-1]}; "
                f"save will apply changes to all {len(self.filepaths)} files"
            )
        else:
            self.status_label.set_text("")

    def _on_fields_picker(self, _btn):
        dlg = FieldsPickerDialog(self, self.fields)
        resp = dlg.run()
        if resp == Gtk.ResponseType.CLOSE:
            active = dlg.get_result()
            new_fields = []
            for f in self.fields:
                if f["tag"] in active:
                    f["visible"] = True
                    new_fields.append(f)
                else:
                    f["visible"] = False
                    new_fields.append(f)
            for tag, cfg in active.items():
                if cfg is None:
                    new_fields.append({
                        "id": tag.lower().replace(" ", "_"),
                        "label": tag,
                        "tag": tag,
                        "type": "text",
                        "visible": True,
                    })
            self.fields = new_fields
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
        invalid = [row for row in self.rows if not row.is_valid()]
        if invalid:
            dlg = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="Invalid date format",
            )
            dlg.format_secondary_text(
                "Date fields must be in YYYY:MM:DD HH:MM:SS format.\n"
                "Leave empty to clear, or fix the highlighted field(s)."
            )
            dlg.run()
            dlg.destroy()
            return False

        diff = self.get_diff()
        clear_all = self.is_clear_all()

        if clear_all:
            non_empty = {fid: val for fid, val in diff.items() if val}
            if not non_empty:
                return False
            diff = non_empty
        else:
            if not diff:
                return False

        if len(self.filepaths) > 1:
            self.progress_box.show_all()
            self.progress_label.set_text(f"Writing 0/{len(self.filepaths)} files\u2026")
            self.progress_bar.set_fraction(0.0)

        def _on_progress(current, total, filepath):
            if total > 1:
                name = filepath.split("/")[-1] if filepath else ""
                self.progress_label.set_text(
                    f"Writing {current}/{total}: {name}\u2026" if current < total
                    else f"Done \u2014 {total} files written"
                )
                self.progress_bar.set_fraction(current / total if total else 1.0)
            while Gtk.events_pending():
                Gtk.main_iteration()

        exif_lib.write_exif_batch(
            self.filepaths, diff, self.fields,
            clear_all=clear_all, progress_cb=_on_progress,
        )

        if len(self.filepaths) > 1:
            self.progress_box.hide()

        return True
