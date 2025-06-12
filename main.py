#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon Craft — Convertidor de Imágenes a Iconos (.ico)
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, UnidentifiedImageError
from typing import Optional, List, Sequence

# Selecciona el mejor filtro de remuestreo según la versión de PIL
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

# Tamaños para generar el icono .ico
ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

class IconCraft(TkinterDnD.Tk):
    """
    IconCraft: aplicación para convertir imágenes en iconos .ico
    Mantiene la disposición estética: botón subir a la izquierda,
    logo/título en el centro y botón convertir a la derecha.
    """
    BG_COLOR = "#000000"
    WIDGET_BG_COLOR = "#121212"
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
        # Listas para rutas y miniaturas
        self.images: List[str] = []
        self.thumbnail_photos: List[ImageTk.PhotoImage] = []
        # Imágenes de assets
        self.logo_photo: Optional[ImageTk.PhotoImage] = None
        self.upload_icon: Optional[ImageTk.PhotoImage] = None
        self.convert_icon: Optional[ImageTk.PhotoImage] = None
        self.eureka_image: Optional[ImageTk.PhotoImage] = None
        self.no_image_photo: Optional[ImageTk.PhotoImage] = None

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(base_dir, "assets")
        self.ico_path = os.path.join(self.assets_dir, "IconCraftLogo.ico")

        # Configuración ventana
        self.title("Icon Craft")
        self.geometry("1200x700")
        self.configure(bg=self.BG_COLOR, highlightbackground=self.PRIMARY_COLOR, highlightthickness=2)
        if os.path.isfile(self.ico_path):
            self.iconbitmap(self.ico_path)

        # Carga recursos y UI
        self._load_assets()
        self._setup_theme()
        self._create_widgets()
        self._setup_drag_and_drop()
        self.after_idle(lambda: self._center_window(1200, 700))

    def _center_window(self, w: int, h: int):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_theme(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=(self.THEME_FONT, 10))
        style.configure('TFrame', background=self.BG_COLOR)
        style.configure('TLabel', background=self.BG_COLOR, foreground=self.TEXT_COLOR)

    def _load_assets(self):
        # Carga de imágenes de assets con tamaño ajustado
        self.logo_photo = self._load_resized_image("IconCraft.png", (self.LOGO_WIDTH, -1))
        self.eureka_image = self._load_resized_image("eureka.png", (self.EUREKA_WIDTH, -1))
        self.no_image_photo = self._load_resized_image("nohayimagen.png", (self.EUREKA_WIDTH, -1))
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
                size = (new_w, int(h * (new_w / w)))
            img = img.resize(size, RESAMPLE)
            return ImageTk.PhotoImage(img)
        except (UnidentifiedImageError, OSError):
            return None

    def _create_widgets(self):
        # Header con botón subir, logo+título y botón convertir
        header = tk.Frame(self, bg=self.BG_COLOR)
        header.pack(fill=tk.X, pady=10, padx=20)

        left = tk.Frame(header, bg=self.BG_COLOR)
        left.pack(side=tk.LEFT)
        self._build_glowing_button(left, self.upload_icon, "subir imágenes", self.upload_images)

        center = tk.Frame(header, bg=self.BG_COLOR)
        center.pack(side=tk.LEFT, expand=True)
        if self.logo_photo:
            tk.Label(center, image=self.logo_photo, bg=self.BG_COLOR, bd=0).pack()
        tk.Label(center, text="Icon Craft", bg=self.BG_COLOR, fg=self.TEXT_COLOR,
                 font=(self.THEME_FONT, 28, 'bold')).pack(pady=(5,0))

        right = tk.Frame(header, bg=self.BG_COLOR)
        right.pack(side=tk.RIGHT)
        self._build_glowing_button(right, self.convert_icon, "convertir a .ico", self.convert_icons)

        # Canvas para miniaturas
        canvas_frame = tk.Frame(self, bg=self.BG_COLOR)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.canvas = tk.Canvas(canvas_frame, bg=self.WIDGET_BG_COLOR,
                                highlightthickness=2, highlightbackground=self.BORDER_COLOR)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.scroll_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))
        self.canvas.configure(xscrollcommand=self.scroll_x.set)
        self.inner = ttk.Frame(self.canvas)
        self.canvas.create_window((10,10), window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

    def _build_glowing_button(self, parent, image, text, cmd):
        frm = tk.Frame(parent, bg=self.BG_COLOR)
        frm.pack(padx=10)
        btn = tk.Button(frm, image=image, text=text, compound=tk.TOP,
                        fg=self.TEXT_COLOR, bg=self.BG_COLOR, bd=0,
                        activebackground=self.BG_COLOR, cursor="hand2",
                        font=(self.THEME_FONT,11), command=cmd)
        btn.pack()
        btn.bind("<Enter>", lambda e: frm.config(highlightthickness=6, highlightbackground=self.PRIMARY_COLOR))
        btn.bind("<Leave>", lambda e: frm.config(highlightthickness=0))

    def _setup_drag_and_drop(self):
        for w in (self, self.canvas, self.inner):
            w.drop_target_register(DND_FILES)
            w.dnd_bind('<<Drop>>', self.drop_images)

    def drop_images(self, event):
        paths = self.tk.splitlist(event.data) if hasattr(event,'data') else []
        self.add_images(paths)

    def upload_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Imágenes","*.png *.jpg *.jpeg *.bmp *.webp")])
        if files:
            self.add_images(files)

    def add_images(self, paths: Sequence[str]):
        for p in paths:
            if len(self.images) >= self.MAX_IMAGES:
                messagebox.showwarning("Límite alcanzado", f"No puedes añadir más de {self.MAX_IMAGES} imágenes.")
                break
            if not p.lower().endswith(('.png','.jpg','.jpeg','.bmp','.webp')):
                continue
            try:
                img = Image.open(p).convert('RGBA')
                img.thumbnail(self.THUMBNAIL_SIZE, RESAMPLE)
                thumb = ImageTk.PhotoImage(img)
            except Exception:
                continue
            self.images.append(p)
            self.thumbnail_photos.append(thumb)
            idx = len(self.thumbnail_photos) - 1
            lbl = tk.Label(self.inner, image=thumb, bg=self.WIDGET_BG_COLOR)
            lbl.grid(row=0, column=idx, padx=5, pady=5)

    def convert_icons(self):
        # Si no hay imágenes, mostrar popup de error
        if not self.images:
            self._show_no_image_dialog()
            return
        # Selección de carpeta destino
        destination = filedialog.askdirectory(title="Selecciona carpeta de destino")
        if not destination:
            return
        created_count = 0
        for src_path in self.images:
            base_name = os.path.splitext(os.path.basename(src_path))[0]
            output_path = os.path.join(destination, f"{base_name}.ico")
            try:
                Image.open(src_path).save(output_path, format='ICO', sizes=ICO_SIZES)
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

        ok_button = tk.Button(dialog, text="Volver al caldero", font=(self.THEME_FONT, 10),
                              bg=self.WIDGET_BG_COLOR, fg=self.TEXT_COLOR, relief='flat',
                              activebackground=self.PRIMARY_COLOR, bd=0, highlightthickness=0,
                              command=dialog.destroy, cursor="hand2")
        ok_button.pack(pady=(20, 20), ipadx=10, ipady=5)

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.wait_window()

    def _show_no_image_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Error")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=self.BG_COLOR)

        if os.path.isfile(self.ico_path):
            dialog.iconbitmap(self.ico_path)

        if self.no_image_photo:
            tk.Label(dialog, image=self.no_image_photo, bg=self.BG_COLOR, bd=0).pack(pady=(20, 10))

        message = "No has subido ninguna imagen.\nPor favor, sube al menos una antes de convertir."
        tk.Label(dialog, text=message, font=(self.THEME_FONT, 12), fg=self.TEXT_COLOR, bg=self.BG_COLOR,
                 justify=tk.CENTER).pack(padx=30)

        btn = tk.Button(dialog, text="Cerrar", font=(self.THEME_FONT, 10),
                        bg=self.WIDGET_BG_COLOR, fg=self.TEXT_COLOR, relief='flat',
                        activebackground=self.PRIMARY_COLOR, bd=0, highlightthickness=0,
                        command=dialog.destroy, cursor="hand2")
        btn.pack(pady=(20, 20), ipadx=10, ipady=5)

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
