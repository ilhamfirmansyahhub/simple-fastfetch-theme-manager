#!/usr/bin/env python3
import json
import re
import shutil
import subprocess
import sys
import os
import glob
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontMetrics, QImage, QPixmap, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider, QFileDialog, QCheckBox, QGroupBox, QMessageBox,
    QSpinBox, QFrame, QGridLayout, QPlainTextEdit, QDialog, QDialogButtonBox,
    QFormLayout
)

APP_NAME = "Fastfetch GUI"
FF_DIR = Path.home() / ".config" / "fastfetch"
CONFIG_PATH = FF_DIR / "config.jsonc"
ASSET_DIR = FF_DIR / "assets"
KITTY_CONF = Path.home() / ".config" / "kitty" / "kitty.conf"

MODULES = [
    ("OS", "os"), ("Kernel", "kernel"), ("Uptime", "uptime"),
    ("Packages", "packages"), ("Shell", "shell"), ("Display", "display"),
    ("DE", "de"), ("WM", "wm"), ("Theme", "theme"), ("Icons", "icons"),
    ("Terminal", "terminal"), ("CPU", "cpu"), ("GPU", "gpu"),
    ("Memory", "memory"), ("Disk", "disk"),
]

ANSI_RE = re.compile(r"\x1b\[([0-9;]*)m")


def strip_jsonc(text: str) -> str:
    out, i, n = [], 0, len(text)
    in_string = False
    escape = False
    line = block = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if line:
            if c in "\r\n":
                line = False
                out.append(c)
            else:
                out.append(" ")
            i += 1
            continue
        if block:
            if c == "*" and nxt == "/":
                out.extend("  ")
                i += 2
                block = False
            else:
                out.append("\n" if c == "\n" else " ")
                i += 1
            continue
        if in_string:
            out.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
        elif c == "/" and nxt == "/":
            out.extend("  ")
            i += 2
            line = True
            continue
        elif c == "/" and nxt == "*":
            out.extend("  ")
            i += 2
            block = True
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def read_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(strip_jsonc(CONFIG_PATH.read_text(encoding="utf-8")))
    except Exception:
        return {}


def read_config_raw() -> str:
    if not CONFIG_PATH.exists():
        return json.dumps({"logo": {}, "modules": []}, indent=2) + "\n"
    try:
        return CONFIG_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def module_key(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        value = item.get("type") or item.get("name")
        return value if isinstance(value, str) else None
    return None


def kitty_settings():
    bg = "#1d2528"
    fg = "#d8d4c8"
    font_name = "Monospace"
    font_size = 14
    if KITTY_CONF.exists():
        try:
            for raw in KITTY_CONF.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 1)
                if len(parts) != 2:
                    continue
                key, val = parts
                val = val.strip()
                if key == "background":
                    bg = val
                elif key == "foreground":
                    fg = val
                elif key == "font_family":
                    font_name = val.split(",")[0].strip()
                elif key == "font_size":
                    try:
                        font_size = float(val)
                    except ValueError:
                        pass
        except OSError:
            pass
    return bg, fg, font_name, font_size


def resolve_logo_source(source):
    if not isinstance(source, str) or not source:
        return None
    expanded = os.path.expanduser(os.path.expandvars(source.strip()))
    p = Path(expanded)
    if p.is_file():
        return p
    if not p.is_absolute():
        for base in (Path.cwd(), FF_DIR, Path.home()):
            candidate = base / p
            if candidate.is_file():
                return candidate
    try:
        matches = [Path(x) for x in glob.glob(expanded, recursive=True) if Path(x).is_file()]
    except (OSError, re.error):
        matches = []
    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
    for match in sorted(matches, key=lambda x: str(x)):
        if match.suffix.lower() in image_exts:
            return match
    return matches[0] if matches else None


def ansi_spans(line: str, default: QColor):
    spans = []
    pos = 0
    color = QColor(default)
    bold = False
    ansi_basic = [
        "#000000", "#cc4444", "#55aa55", "#c0b060",
        "#6688cc", "#aa66aa", "#55aaaa", "#d7d7d7"
    ]
    ansi_bright = [
        "#555555", "#ff6666", "#77dd77", "#e8db78",
        "#79a7ff", "#df82df", "#73d8d8", "#ffffff"
    ]
    for m in ANSI_RE.finditer(line):
        if m.start() > pos:
            spans.append((line[pos:m.start()], QColor(color), bold))
        codes = [int(x) for x in m.group(1).split(";") if x != ""] or [0]
        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                color = QColor(default); bold = False
            elif c == 1:
                bold = True
            elif c == 22:
                bold = False
            elif c == 39:
                color = QColor(default)
            elif 30 <= c <= 37:
                color = QColor(ansi_basic[c - 30])
            elif 90 <= c <= 97:
                color = QColor(ansi_bright[c - 90])
            elif c == 38 and i + 4 < len(codes) and codes[i + 1] == 2:
                color = QColor(codes[i + 2], codes[i + 3], codes[i + 4]); i += 4
            elif c == 38 and i + 2 < len(codes) and codes[i + 1] == 5:
                idx = max(0, min(255, codes[i + 2]))
                color = QColor.fromHsv((idx * 137) % 360, 180, 230); i += 2
            i += 1
        pos = m.end()
    if pos < len(line):
        spans.append((line[pos:], QColor(color), bold))
    return spans


class TerminalPreview(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(760, 500)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMouseTracking(True)
        self.image = None
        self.logo_left = 0
        self.logo_top = 0
        self.logo_width = 40
        self.logo_height = 22
        self.logo_right = 4
        self.logo_ratio = None
        self.lines = []
        self.error = None
        self.drag_offset = None
        self.background = QColor("#1d2528")
        self.foreground = QColor("#d8d4c8")
        self.font_family = "Monospace"
        self.font_size = 14
        self.show_grid = False
        self.edit_mode = False
        self.text_editor = QPlainTextEdit(self)
        self.text_editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.text_editor.setFrameShape(QFrame.NoFrame)
        self.text_editor.hide()
        self.text_editor.textChanged.connect(self._edited_text_changed)
        self.cols = 160
        self.rows = 50
        self.setStyleSheet("border: 1px solid #3b4448; border-radius: 8px;")

    def _edited_text_changed(self):
        if self.edit_mode:
            self.window().manual_text_changed(self.text_editor.toPlainText())

    def set_edit_mode(self, enabled, text=None):
        self.edit_mode = bool(enabled)
        if self.edit_mode:
            if text is not None:
                self.text_editor.blockSignals(True)
                self.text_editor.setPlainText(text)
                self.text_editor.blockSignals(False)
            self.text_editor.show()
            self._position_text_editor()
            self.text_editor.raise_()
            self.update()
        else:
            self.text_editor.hide()
            self.update()

    def edited_text(self):
        return self.text_editor.toPlainText()

    def _position_text_editor(self):
        if not self.edit_mode:
            return
        _, cw, ch = self._metrics()
        scale, cw, ch = self._scale()
        ox, oy = self._terminal_origin(cw, ch, scale)
        x = self._text_origin_x(ox, cw, scale) if self.image is not None else ox
        y = oy
        width = max(120, int(self.width() - x - 10))
        height = max(80, int(self.rows * ch * scale))
        self.text_editor.setGeometry(round(x), round(y), width, height)
        font, _, _ = self._metrics()
        font.setPointSizeF(font.pointSizeF() * scale)
        self.text_editor.setFont(font)
        self.text_editor.setStyleSheet(
            f"QPlainTextEdit {{ background: transparent; color: {self.foreground.name()}; border: none; padding: 0; selection-background-color: rgba(120, 150, 180, 90); }}"
        )

    def set_theme(self, bg, fg, font_name, font_size):
        self.background = QColor(bg) if QColor(bg).isValid() else QColor("#1d2528")
        self.foreground = QColor(fg) if QColor(fg).isValid() else QColor("#d8d4c8")
        self.font_family = font_name or "Monospace"
        self.font_size = max(8.0, min(30.0, float(font_size)))
        self.update()

    def set_image(self, path):
        img = QImage(str(path))
        if img.isNull():
            self.image = None
            return False
        self.image = img
        self.logo_ratio = img.width() / max(1, img.height())
        self.update()
        return True

    def set_geometry(self, left, top, width, height, right):
        self.logo_left = int(left)
        self.logo_top = int(top)
        self.logo_width = max(1, int(width))
        self.logo_height = max(1, int(height))
        self.logo_right = max(0, int(right))
        self.update()

    def set_lines(self, lines):
        self.lines = lines
        self.update()

    def _metrics(self):
        font = QFont(self.font_family)
        font.setStyleHint(QFont.Monospace)
        font.setPointSizeF(self.font_size)
        fm = QFontMetrics(font)
        return font, max(6.0, float(fm.horizontalAdvance("M"))), max(10.0, float(fm.lineSpacing()))

    def _height_for_width(self, width):
        if not self.logo_ratio:
            return 1
        _, cw, ch = self._metrics()
        physical_width = max(1.0, float(width) * cw)
        physical_height = physical_width / self.logo_ratio
        return max(1, round(physical_height / max(1.0, ch)))

    def _scale(self):
        _, cw, ch = self._metrics()
        content_w = min(self.width() - 18, self.cols * cw)
        content_h = min(self.height() - 18, self.rows * ch)
        if content_w <= 0 or content_h <= 0:
            return 1.0, cw, ch
        return min(content_w / (self.cols * cw), content_h / (self.rows * ch), 1.0), cw, ch

    def _terminal_origin(self, cw, ch, scale):
        scaled_w = self.cols * cw * scale
        scaled_h = self.rows * ch * scale
        return (self.width() - scaled_w) / 2, (self.height() - scaled_h) / 2

    def _logo_rect(self, ox, oy, cw, ch, scale):
        return (
            ox + self.logo_left * cw * scale,
            oy + self.logo_top * ch * scale,
            self.logo_width * cw * scale,
            self.logo_height * ch * scale,
        )

    def _text_origin_x(self, ox, cw, scale):
        return ox + (self.logo_left + self.logo_width + self.logo_right) * cw * scale

    def _draw_logo(self, painter, ox, oy, cw, ch, scale):
        if self.image is None:
            return
        x, y, w, h = self._logo_rect(ox, oy, cw, ch, scale)
        pix = QPixmap.fromImage(self.image).scaled(
            max(1, round(w)), max(1, round(h)),
            Qt.KeepAspectRatio, Qt.SmoothTransformation,
        )
        painter.drawPixmap(round(x), round(y), pix)

    def _draw_text(self, painter, ox, oy, cw, ch, scale):
        font, _, _ = self._metrics()
        font.setPointSizeF(font.pointSizeF() * scale)
        painter.setFont(font)
        fm = QFontMetrics(font)
        base_x = self._text_origin_x(ox, cw, scale) if self.image is not None else ox
        baseline = oy + fm.ascent()
        for row, raw in enumerate(self.lines[:self.rows]):
            y = baseline + row * ch * scale
            x = base_x
            for text, color, bold in ansi_spans(raw, self.foreground):
                if not text:
                    continue
                f = QFont(font)
                f.setBold(bold)
                painter.setFont(f)
                painter.setPen(color)
                painter.drawText(round(x), round(y), text)
                x += QFontMetrics(f).horizontalAdvance(text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_text_editor()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), self.background)
        _, cw, ch = self._metrics()
        scale, cw, ch = self._scale()
        ox, oy = self._terminal_origin(cw, ch, scale)
        self._draw_logo(painter, ox, oy, cw, ch, scale)
        if not self.edit_mode:
            self._draw_text(painter, ox, oy, cw, ch, scale)
        if self.show_grid and self.image is not None:
            pen = QPen(QColor(255, 220, 120, 190)); pen.setWidth(1); painter.setPen(pen)
            x, y, w, h = self._logo_rect(ox, oy, cw, ch, scale)
            painter.drawRect(round(x), round(y), round(w), round(h))
            gap_x = x + w + self.logo_right * cw * scale
            painter.drawLine(round(gap_x), round(oy), round(gap_x), round(oy + self.rows * ch * scale))
        if self.error:
            painter.setPen(QColor("#e57373"))
            painter.drawText(12, self.height() - 14, self.error[:180])

    def _cell_at(self, p):
        _, cw, ch = self._metrics()
        scale, cw, ch = self._scale()
        ox, oy = self._terminal_origin(cw, ch, scale)
        return ((p.x() - ox) / (cw * scale), (p.y() - oy) / (ch * scale))

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or self.image is None:
            return super().mousePressEvent(event)
        cx, cy = self._cell_at(event.position())
        if self.logo_left <= cx < self.logo_left + self.logo_width and self.logo_top <= cy < self.logo_top + self.logo_height:
            self.drag_offset = (cx - self.logo_left, cy - self.logo_top)
            self.show_grid = True
            self.update(); event.accept(); return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None:
            cx, cy = self._cell_at(event.position())
            left = round(cx - self.drag_offset[0]); top = round(cy - self.drag_offset[1])
            self.logo_left = left; self.logo_top = top
            self.update()
            self.window().logo_drag_changed(self.logo_left, self.logo_top)
            event.accept(); return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = None
            QTimer.singleShot(150, self._hide_grid)
        super().mouseReleaseEvent(event)

    def _hide_grid(self):
        if self.drag_offset is None:
            self.show_grid = False; self.update()

    def wheelEvent(self, event):
        if self.image is None:
            return super().wheelEvent(event)
        delta = 1 if event.angleDelta().y() > 0 else -1
        new_w = max(1, min(10000, self.logo_width + delta))
        new_h = self._height_for_width(new_w)
        self.logo_width = new_w; self.logo_height = min(10000, new_h)
        self.show_grid = True; self.update()
        self.window().logo_size_changed(self.logo_width, self.logo_height)
        event.accept()


class ConfigEditor(QDialog):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setWindowTitle("Edit Fastfetch config")
        self.resize(900, 700)
        layout = QVBoxLayout(self)
        self.editor = QPlainTextEdit(); self.editor.setPlainText(text)
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("Monospace"); font.setStyleHint(QFont.Monospace); font.setPointSize(10)
        self.editor.setFont(font); layout.addWidget(self.editor)
        hint = QLabel("Edit the real ~/.config/fastfetch/config.jsonc. JSON comments are allowed.")
        hint.setStyleSheet("color: #8b9399;"); layout.addWidget(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def text(self): return self.editor.toPlainText()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 800); self.setMinimumSize(1120, 700)
        self.syncing = False
        self.config = read_config(); self.logo_path = None
        self.manual_text = None; self.manual_editing = False
        bg, fg, font_name, font_size = kitty_settings()
        root = QWidget(); self.setCentralWidget(root)
        main = QHBoxLayout(root); main.setContentsMargins(14,14,14,14); main.setSpacing(12)
        side = QVBoxLayout();
        logo_box = QGroupBox("Logo"); logo_form = QVBoxLayout(logo_box)
        upload = QPushButton("Upload image"); upload.clicked.connect(self.upload_image); logo_form.addWidget(upload)
        reset = QPushButton("Reset"); reset.clicked.connect(self.reset_logo); logo_form.addWidget(reset)
        grid = QGridLayout()
        self.x_spin = self.spin(); self.y_spin = self.spin(); self.w_spin = self.spin(1,10000,40); self.h_spin = self.spin(1,10000,22); self.gap_spin = self.spin(0,10000,4)
        for label, widget, row, col in [("X",self.x_spin,0,0),("Y",self.y_spin,0,2),("W",self.w_spin,1,0),("H",self.h_spin,1,2),("Gap",self.gap_spin,2,0)]:
            grid.addWidget(QLabel(label),row,col); grid.addWidget(widget,row,col+1)
        logo_form.addLayout(grid)
        self.scale = QSlider(Qt.Horizontal); self.scale.setRange(1,300); self.scale.setValue(20); logo_form.addWidget(QLabel("Scale")); logo_form.addWidget(self.scale)
        side.addWidget(logo_box)
        mod_box = QGroupBox("Modules"); mod_layout = QVBoxLayout(mod_box)
        self.checks = {}
        for label, key in MODULES:
            cb = QCheckBox(label); self.checks[key] = cb; cb.stateChanged.connect(self.module_changed); mod_layout.addWidget(cb)
        side.addWidget(mod_box)
        edit_btn = QPushButton("Edit displayed text"); edit_btn.clicked.connect(self.toggle_text_edit); side.addWidget(edit_btn)
        cfg_btn = QPushButton("Edit config manually"); cfg_btn.clicked.connect(self.edit_config); side.addWidget(cfg_btn)
        save_btn = QPushButton("Save config"); save_btn.clicked.connect(self.save_config); side.addWidget(save_btn)
        side.addStretch(1)
        main.addLayout(side, 0)
        right = QVBoxLayout(); title = QHBoxLayout(); title.addWidget(QLabel("Current Fastfetch")); title.addStretch(1)
        refresh = QPushButton("Refresh"); refresh.clicked.connect(self.refresh); title.addWidget(refresh); right.addLayout(title)
        self.preview = TerminalPreview(); self.preview.set_theme(bg,fg,font_name,font_size); right.addWidget(self.preview,1)
        self.status = QLabel(); self.status.setStyleSheet("color:#8b9399;"); right.addWidget(self.status)
        main.addLayout(right,1)
        for spin in (self.x_spin,self.y_spin,self.w_spin,self.h_spin,self.gap_spin): spin.valueChanged.connect(self.geometry_changed)
        self.load_from_config()

    def spin(self, low=-10000, high=10000, value=0):
        s=QSpinBox(); s.setRange(low,high); s.setValue(value); return s

    def load_from_config(self):
        cfg=self.config
        logo=cfg.get("logo",{}) if isinstance(cfg,dict) else {}
        self.logo_path=resolve_logo_source(logo.get("source"))
        if self.logo_path: self.preview.set_image(self.logo_path)
        pad=logo.get("padding",{}) if isinstance(logo,dict) else {}
        self.x_spin.setValue(int(pad.get("left",0) or 0)); self.y_spin.setValue(int(pad.get("top",0) or 0)); self.gap_spin.setValue(int(pad.get("right",4) or 4))
        self.w_spin.setValue(int(logo.get("width",40) or 40)); self.h_spin.setValue(int(logo.get("height",22) or 22))
        mods=cfg.get("modules",[]) if isinstance(cfg,dict) else []
        active={module_key(x) for x in mods}
        for key,cb in self.checks.items(): cb.blockSignals(True); cb.setChecked(key in active); cb.blockSignals(False)
        self.reload_fastfetch()

    def upload_image(self):
        p,_=QFileDialog.getOpenFileName(self,"Choose logo",str(Path.home()),"Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)")
        if not p: return
        ASSET_DIR.mkdir(parents=True,exist_ok=True); dest=ASSET_DIR/Path(p).name; shutil.copy2(p,dest); self.logo_path=dest; self.preview.set_image(dest); self.status.setText(f"Logo: {dest}")

    def reset_logo(self):
        self.x_spin.setValue(0); self.y_spin.setValue(0); self.w_spin.setValue(40); self.h_spin.setValue(22); self.gap_spin.setValue(4)

    def geometry_changed(self):
        if self.syncing:return
        self.preview.set_geometry(self.x_spin.value(),self.y_spin.value(),self.w_spin.value(),self.h_spin.value(),self.gap_spin.value()); self.status.setText(f"Logo position • X {self.x_spin.value()} • Y {self.y_spin.value()}")

    def logo_drag_changed(self,x,y): self.syncing=True; self.x_spin.setValue(x); self.y_spin.setValue(y); self.syncing=False; self.status.setText(f"Logo position • X {x} • Y {y}")
    def logo_size_changed(self,w,h): self.syncing=True; self.w_spin.setValue(w); self.h_spin.setValue(h); self.syncing=False
    def module_changed(self): self.reload_fastfetch()

    def build_command(self): return ["fastfetch", "--logo", "none"]

    def reload_fastfetch(self):
        try:
            # Render text from the installed Fastfetch without its logo; the GUI draws the actual logo.
            p=subprocess.run(self.build_command(),capture_output=True,text=True,timeout=5)
            if p.returncode==0:
                self.preview.set_lines(p.stdout.rstrip("\n").splitlines()); self.status.setText(f"Live preview • {len(self.preview.lines)} lines from your installed Fastfetch")
            else: self.preview.error=p.stderr.strip(); self.preview.update()
        except Exception as e:
            self.preview.error=str(e); self.preview.update()

    def refresh(self):
        self.config=read_config(); self.load_from_config()

    def manual_text_changed(self,text): self.manual_text=text

    def toggle_text_edit(self):
        if not self.manual_editing:
            text="\n".join(self.preview.lines)
            self.preview.set_edit_mode(True,text); self.manual_editing=True; self.status.setText("Editing displayed text")
        else:
            self.manual_text=self.preview.edited_text(); self.preview.set_edit_mode(False); self.manual_editing=False; self.status.setText("Displayed text edited")

    def edit_config(self):
        dlg=ConfigEditor(self,read_config_raw())
        if dlg.exec()==QDialog.Accepted:
            FF_DIR.mkdir(parents=True,exist_ok=True); CONFIG_PATH.write_text(dlg.text(),encoding="utf-8"); self.config=read_config(); self.load_from_config()

    def save_config(self):
        FF_DIR.mkdir(parents=True,exist_ok=True)
        cfg=dict(self.config) if isinstance(self.config,dict) else {}
        logo=dict(cfg.get("logo",{}) or {})
        if self.logo_path: logo["source"]=str(self.logo_path)
        # Fastfetch padding cannot be negative, so clamp only when serializing.
        logo["padding"]={"left":max(0,self.x_spin.value()),"top":max(0,self.y_spin.value()),"right":max(0,self.gap_spin.value())}
        logo["width"]=self.w_spin.value(); logo["height"]=self.h_spin.value(); cfg["logo"]=logo
        modules=[]
        for _,key in MODULES:
            if self.checks[key].isChecked(): modules.append(key)
        if modules: cfg["modules"]=modules
        if self.manual_text is not None:
            lines=self.manual_text.splitlines(); cfg["modules"]= [{"type":"custom","format":line} for line in lines if line != ""]
        CONFIG_PATH.write_text(json.dumps(cfg,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        self.config=cfg; QMessageBox.information(self,"Saved",f"Saved to {CONFIG_PATH}")


def main():
    app=QApplication(sys.argv); w=MainWindow(); w.show(); sys.exit(app.exec())

if __name__=="__main__": main()
