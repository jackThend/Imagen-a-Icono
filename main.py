#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Icon Craft — Convertidor de Imágenes a Iconos (.ico)
Creado por Jack Thend

"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, UnidentifiedImageError
from typing import Optional, List, Sequence

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS


class IconCraft(TkinterDnD.Tk):
    BG_COLOR = "#000000"
    WIDGET_BG_COLOR = "#121212"
    SHADOW_COLOR = "#000000"
    PRIMARY_COLOR = "#76ff03"
    TEXT_COLOR = "#ffffff"
    BORDER_COLOR = "#1f1f1f"
    THEME_FONT = "Segoe UI"

    MAX_IMAGES = 40
    THUMBNAIL_SIZE = (96, 96)
    BUTTON_ICON_SIZE = (160, 160)
    LOGO_WIDTH = 320
    EUREKA_WIDTH = 200

    def __init__(self):
        super().__init__()
        self.images: List[str] = []
        self.logo_photo: Optional[ImageTk.PhotoImage] = None
        self.upload_icon: Optional[ImageTk.PhotoImage] = None
        self.convert_icon: Optional[ImageTk.PhotoImage] = None
        self.eureka_image: Optional[ImageTk.PhotoImage] = None

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(base_dir, "assets")
        self.ico_path = os.path.join(self.assets_dir, "IconCraftLogo.ico")

        self.title("Icon Craft")
        self.geometry("1100x850")
        self.configure(bg=self.BG_COLOR, highlightbackground=self.PRIMARY_COLOR, highlightthickness=2)

        if os.path.isfile(self.ico_path):
            self.iconbitmap(self.ico_path)

        self._load_assets()
        self._setup_theme()
        self._create_widgets()
        self._setup_drag_and_drop()

    def _setup_theme(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=(self.THEME_FONT, 10))
        style.configure('TFrame', background=self.BG_COLOR)
        style.configure('TLabel', background=self.BG_COLOR, foreground=self.TEXT_COLOR)

    def _load_assets(self):
        self.logo_photo = self._load_resized_image("IconCraft.png", (self.LOGO_WIDTH, -1))
        self.eureka_image = self._load_resized_image("eureka.png", (self.EUREKA_WIDTH, -1))
        self.upload_icon = self._load_resized_image("upload.png", self.BUTTON_ICON_SIZE)
        self.convert_icon = self._load_resized_image("convert.png", self.BUTTON_ICON_SIZE)

    def _load_resized_image(self, filename: str, size: tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
        path = os.path.join(self.assets_dir, filename)
        if not os.path.isfile(path):
            return None
        try:
            img = Image.open(path).convert("RGBA")
            if size[1] == -1:
                w, h = img.size
                new_w = size[0]
                new_h = int(h * (new_w / w)) if w > 0 else 0
                size = (new_w, new_h)
            img = img.resize(size, RESAMPLE)
            return ImageTk.PhotoImage(img)
        except (UnidentifiedImageError, OSError, FileNotFoundError):
            return None

    def _create_widgets(self):
        top_frame = tk.Frame(self, bg=self.BG_COLOR)
        top_frame.pack(pady=(20, 0))

        if self.logo_photo:
            logo_label = tk.Label(top_frame, image=self.logo_photo, bg=self.BG_COLOR, bd=0, highlightthickness=0)
            logo_label.pack()

        header = ttk.Label(top_frame, text="Icon Craft", background=self.BG_COLOR, font=(self.THEME_FONT, 28, 'bold'))
        header.pack(pady=(5, 20))

        ctrl_panel = tk.Frame(self, bg=self.BG_COLOR)
        ctrl_panel.pack(pady=(10, 30))

        def build_glowing_button(parent, image, text, command):
            glow = tk.Frame(parent, bg=self.BG_COLOR, highlightthickness=0)
            glow.pack(side=tk.LEFT, padx=100)

            button = tk.Button(
                glow,
                image=image,
                compound=tk.TOP,
                text=text,
                font=(self.THEME_FONT, 11),
                fg=self.TEXT_COLOR,
                bg=self.BG_COLOR,
                activebackground=self.BG_COLOR,
                bd=0,
                highlightthickness=0,
                command=command,
                cursor="hand2"
            )
            button.pack()

            def on_enter(e):
                glow.config(highlightthickness=6, highlightbackground=self.PRIMARY_COLOR)

            def on_leave(e):
                glow.config(highlightthickness=0)

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        build_glowing_button(ctrl_panel, self.upload_icon, "subir imagenes", self.upload_images)
        build_glowing_button(ctrl_panel, self.convert_icon, "convertir a .ico", self.convert_icons)

        canvas_frame = tk.Frame(self, bg=self.BG_COLOR)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.WIDGET_BG_COLOR,
            highlightthickness=2,
            highlightbackground=self.BORDER_COLOR,
            relief='flat',
            bd=0
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.scroll_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.canvas.configure(xscrollcommand=self.scroll_x.set)

        self.inner = ttk.Frame(self.canvas)
        self.canvas.create_window((10, 10), window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

    def _setup_drag_and_drop(self):
        for widget in (self.canvas, self.inner, self):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self.drop_images)

    def drop_images(self, event):
        if hasattr(event, 'data'):
            files = self.tk.splitlist(event.data)
            self.add_images(list(files))

    def upload_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if files:
            self.add_images(list(files))

    def add_images(self, paths: Sequence[str]):
        for path in paths:
            if len(self.images) >= self.MAX_IMAGES:
                messagebox.showwarning("Límite alcanzado", f"No puedes añadir más de {self.MAX_IMAGES} imágenes.")
                break
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                try:
                    image = Image.open(path)
                    image.thumbnail(self.THUMBNAIL_SIZE, RESAMPLE)
                    thumb = ImageTk.PhotoImage(image)
                    shadow_frame = tk.Frame(self.inner, bg=self.SHADOW_COLOR)
                    shadow_frame.pack(side=tk.LEFT, padx=10, pady=10)
                    label = tk.Label(shadow_frame, image=thumb, bg=self.WIDGET_BG_COLOR, bd=0)
                    label.image = thumb
                    label.pack(padx=2, pady=2)
                    self.images.append(path)
                except (UnidentifiedImageError, OSError) as err:
                    messagebox.showerror("Error al cargar imagen", f"No se pudo cargar:\n{path}\n\nError: {err}")
        self.canvas.update_idletasks()
        self.canvas.xview_moveto(1.0)

    def convert_icons(self):
        if not self.images:
            messagebox.showinfo("Sin imágenes", "Añade imágenes para convertirlas en iconos.")
            return
        destination = filedialog.askdirectory(title="Selecciona dónde guardar los iconos")
        if not destination:
            return
        created_count = 0
        for src_path in self.images:
            base_name = os.path.splitext(os.path.basename(src_path))[0]
            output_path = os.path.join(destination, f"{base_name}.ico")
            try:
                Image.open(src_path).save(output_path, format='ICO',
                                          sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
                created_count += 1
            except OSError as err:
                messagebox.showerror("Error de conversión", f"No se pudo convertir:\n{src_path}\n\nError: {err}")
        if created_count > 0:
            self._show_success_dialog(created_count, destination)
        self._reset_ui()

    def _show_success_dialog(self, count: int, path: str):
        dialog = tk.Toplevel(self)
        dialog.title("¡Éxito!")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=self.BG_COLOR)

        if os.path.isfile(self.ico_path):
            dialog.iconbitmap(self.ico_path)

        if self.eureka_image:
            tk.Label(dialog, image=self.eureka_image, bg=self.BG_COLOR, bd=0).pack(pady=(20, 10))

        msg = f"¡Eureka!\nSe han creado {count} iconos en:\n{os.path.normpath(path)}"
        tk.Label(dialog, text=msg, font=(self.THEME_FONT, 12), fg=self.TEXT_COLOR, bg=self.BG_COLOR,
                 justify=tk.CENTER).pack(padx=30)

        ok_button = tk.Button(dialog, text="Volver al caldero", font=(self.THEME_FONT, 10), bg=self.WIDGET_BG_COLOR,
                              fg=self.TEXT_COLOR, relief='flat', activebackground=self.PRIMARY_COLOR,
                              bd=0, highlightthickness=0, command=dialog.destroy, cursor="hand2")
        ok_button.pack(pady=(20, 20), ipadx=10, ipady=5)

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.wait_window()

    def _reset_ui(self):
        self.images.clear()
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.update_idletasks()


if __name__ == "__main__":
    app = IconCraft()
    app.mainloop()