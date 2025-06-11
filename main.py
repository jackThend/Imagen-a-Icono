#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon Craft — Convertidor de Imágenes a Iconos (.ico)
Autor: [Tu Nombre]
Requisitos:
    pip install pillow tkinterdnd2
Opcional:
    Carpeta ./assets/ con upload.png y convert.png para botones
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, UnidentifiedImageError

# Elegimos el filtro LANCZOS de forma compatible con distintas versiones de Pillow
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS  # type: ignore


class IconCraft(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Icon Craft")
        self.geometry("900x500")
        self.configure(bg="#f5f5f5")

        self.max_images = 40
        self.images = []

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), background='#f5f5f5')
        style.configure('Icon.TButton', font=('Segoe UI', 11), padding=8)

        header = ttk.Label(self, text="Icon Craft", style='Header.TLabel')
        header.pack(pady=(10, 5))

        ctrl_frame = ttk.Frame(self, padding=10)
        ctrl_frame.pack(fill=tk.X)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")

        self.upload_icon = self._load_icon(assets_dir, "upload.png")
        self.convert_icon = self._load_icon(assets_dir, "convert.png")

        upload_btn = ttk.Button(
            ctrl_frame,
            text=" Subir Imágenes",
            image=self.upload_icon,
            compound=tk.LEFT if self.upload_icon else None,
            style='Icon.TButton',
            command=self.upload_images
        )
        upload_btn.pack(side=tk.LEFT, padx=(0, 10))

        convert_btn = ttk.Button(
            ctrl_frame,
            text=" Convertir a .ico",
            image=self.convert_icon,
            compound=tk.LEFT if self.convert_icon else None,
            style='Icon.TButton',
            command=self.convert_icons
        )
        convert_btn.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(
            self,
            bg="#ffffff",
            height=120,
            highlightthickness=1,
            highlightbackground="#ccc"
        )
        self.canvas.pack(fill=tk.X, padx=10, pady=10)

        self.scroll_x = ttk.Scrollbar(
            self,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )
        self.scroll_x.pack(fill=tk.X, padx=10)
        self.canvas.configure(xscrollcommand=self.scroll_x.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        for widget in (self, self.canvas, self.inner_frame):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self.drop_images)

    @staticmethod
    def _load_icon(assets_dir, filename):
        """Intenta cargar un PNG de botón; devuelve PhotoImage o None."""
        path = os.path.join(assets_dir, filename)
        try:
            img = Image.open(path)
            img = img.resize((24, 24), RESAMPLE)
            return ImageTk.PhotoImage(img)
        except (FileNotFoundError, UnidentifiedImageError, OSError):
            return None

    def upload_images(self):
        """Carga imágenes vía diálogo de archivos."""
        paths = filedialog.askopenfilenames(
            filetypes=[("Imágenes PNG/JPG", "*.png *.jpg *.jpeg")]
        )
        self.add_images(paths)

    def drop_images(self, event):
        """Maneja archivos dejados sobre la ventana/canvas/frame."""
        files = self.tk.splitlist(event.data)
        self.add_images(files)

    def add_images(self, paths):
        """Añade rutas e inserta miniaturas en la interfaz."""
        for path in paths:
            if len(self.images) >= self.max_images:
                messagebox.showwarning(
                    "Límite alcanzado",
                    f"Máximo {self.max_images} imágenes permitidas."
                )
                break

            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    img = Image.open(path)
                    img.thumbnail((80, 80), RESAMPLE)
                    thumb = ImageTk.PhotoImage(img)
                    lbl = ttk.Label(self.inner_frame, image=thumb)
                    lbl.image = thumb
                    lbl.pack(side=tk.LEFT, padx=5, pady=5)
                    self.images.append(path)
                except (UnidentifiedImageError, OSError) as e:
                    messagebox.showerror(
                        "Error al cargar imagen",
                        f"{path}\n{e}"
                    )

        self.canvas.update_idletasks()

    def convert_icons(self):
        """Convierte las imágenes cargadas a archivos .ico y limpia la interfaz."""
        if not self.images:
            messagebox.showinfo("Sin imágenes", "No hay nada que convertir.")
            return

        dest = filedialog.askdirectory(title="Selecciona carpeta destino")
        if not dest:
            return

        for src in self.images:
            base = os.path.splitext(os.path.basename(src))[0]
            out = os.path.join(dest, base + ".ico")
            try:
                img = Image.open(src)
                img.save(out, format='ICO', sizes=[(256, 256), (128, 128), (64, 64)])
            except OSError as e:
                messagebox.showerror(
                    "Error al convertir a icono",
                    f"{src}\n{e}"
                )

        messagebox.showinfo(
            "¡Listo!",
            f"{len(self.images)} iconos guardados en:\n{dest}"
        )
        self.images.clear()
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.canvas.update_idletasks()


if __name__ == "__main__":
    app = IconCraft()
    app.mainloop()
