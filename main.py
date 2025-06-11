#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Icon Craft — Convertidor de Imágenes a Iconos (.ico)
Autor: [Tu Nombre]
Requisitos:
    pip install pillow tkinterdnd2
Opcional:
    Carpeta ./assets/ con:
      - upload.png, convert.png (botones)
      - IconCraft.png       (logo principal en la cabecera)
      - IconCraftLogo.ico   (icono de la ventana y ejecutable)
      - eureka.png         (imagen de éxito en diálogo)
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, UnidentifiedImageError
from typing import Optional, List, Sequence

# Selección de filtro de remuestreo
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS  # type: ignore


class IconCraft(TkinterDnD.Tk):
    # Atributos para el analizador estático
    max_images: int
    images: List[str]

    def __init__(self):
        super().__init__()

        self.title("Icon Craft")
        self.geometry("900x600")
        self.configure(bg="#f5f5f5")

        self.max_images = 40
        self.images = []

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(base_dir, "assets")
        self.ico_path = os.path.join(self.assets_dir, "IconCraftLogo.ico")

        if os.path.isfile(self.ico_path):
            self.iconbitmap(self.ico_path)

        self.eureka_image: Optional[ImageTk.PhotoImage] = None
        eureka_path = os.path.join(self.assets_dir, "eureka.png")
        if os.path.isfile(eureka_path):
            try:
                img_e = Image.open(eureka_path)
                w, h = img_e.size
                new_w = 200
                new_h = int(h * (new_w / w))
                img_e = img_e.resize((new_w, new_h), RESAMPLE)
                self.eureka_image = ImageTk.PhotoImage(img_e)
            except (UnidentifiedImageError, OSError):
                pass

        logo_path = os.path.join(self.assets_dir, "IconCraft.png")
        if os.path.isfile(logo_path):
            try:
                logo_img = Image.open(logo_path)
                w, h = logo_img.size
                new_w = 150
                new_h = int(h * (new_w / w))
                logo_img = logo_img.resize((new_w, new_h), RESAMPLE)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(
                    self,
                    image=self.logo_photo,
                    background="#f5f5f5"
                )
                logo_label.pack(pady=(15, 5))
            except (UnidentifiedImageError, OSError):
                pass

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure(
            'Header.TLabel',
            font=('Segoe UI', 18, 'bold'),
            background='#f5f5f5'
        )
        style.configure(
            'Icon.TButton',
            font=('Segoe UI', 11),
            padding=8
        )

        header = ttk.Label(
            self,
            text="Icon Craft",
            style='Header.TLabel'
        )
        header.pack(pady=(5, 10))

        ctrl_frame = ttk.Frame(self, padding=10)
        ctrl_frame.pack(fill=tk.X)
        self.upload_icon = self._load_icon("upload.png")
        self.convert_icon = self._load_icon("convert.png")

        upload_button = ttk.Button(
            ctrl_frame,
            text=" Subir Imágenes",
            image=self.upload_icon,
            compound=tk.LEFT if self.upload_icon else None,
            style='Icon.TButton',
            command=self.upload_images
        )
        upload_button.pack(side=tk.LEFT, padx=(0, 10))

        convert_button = ttk.Button(
            ctrl_frame,
            text=" Convertir a .ico",
            image=self.convert_icon,
            compound=tk.LEFT if self.convert_icon else None,
            style='Icon.TButton',
            command=self.convert_icons
        )
        convert_button.pack(side=tk.LEFT)

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

        self.inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )

        for widget in (self, self.canvas, self.inner):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self.drop_images)

    @staticmethod
    def _load_icon(filename: str) -> Optional[ImageTk.PhotoImage]:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            filename
        )
        try:
            img = Image.open(path)
            img = img.resize((24, 24), RESAMPLE)
            return ImageTk.PhotoImage(img)
        except (FileNotFoundError, UnidentifiedImageError, OSError):
            return None

    def upload_images(self) -> None:
        files = filedialog.askopenfilenames(
            filetypes=[("Imágenes PNG/JPG", "*.png *.jpg *.jpeg")]
        )
        self.add_images(list(files))

    def drop_images(self, event) -> None:
        files = self.tk.splitlist(event.data)
        self.add_images(list(files))

    def add_images(self, paths: Sequence[str]) -> None:
        for path in paths:
            if len(self.images) >= self.max_images:
                messagebox.showwarning(
                    "Límite alcanzado",
                    f"Máximo {self.max_images} imágenes permitidas."
                )
                return

            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    image = Image.open(path)
                    image.thumbnail((80, 80), RESAMPLE)
                    thumb = ImageTk.PhotoImage(image)
                    label = ttk.Label(
                        self.inner,
                        image=thumb
                    )
                    label.image = thumb
                    label.pack(side=tk.LEFT, padx=5, pady=5)
                    self.images.append(path)
                except (UnidentifiedImageError, OSError) as err:
                    messagebox.showerror(
                        "Error al cargar imagen",
                        f"{path}\n{err}"
                    )

        self.canvas.update_idletasks()

    def convert_icons(self) -> None:
        if not self.images:
            messagebox.showinfo(
                "Sin imágenes",
                "No hay nada que convertir."
            )
            return

        destination = filedialog.askdirectory(
            title="Selecciona carpeta destino"
        )
        if not destination:
            return

        created = 0
        for src in self.images:
            name = os.path.splitext(os.path.basename(src))[0]
            output = os.path.join(
                destination,
                f"{name}.ico"
            )
            try:
                Image.open(src).save(
                    output,
                    format='ICO',
                    sizes=[(256, 256), (128, 128), (64, 64)]
                )
                created += 1
            except OSError as err:
                messagebox.showerror(
                    "Error al convertir icono",
                    f"{src}\n{err}"
                )

        dialog = tk.Toplevel(self)
        dialog.title("¡Éxito!")
        dialog.configure(bg="#f5f5f5")
        dialog.transient(self)
        dialog.grab_set()

        if os.path.isfile(self.ico_path):
            dialog.iconbitmap(self.ico_path)

        if self.eureka_image:
            tk.Label(
                dialog,
                image=self.eureka_image,
                bg="#f5f5f5"
            ).pack(pady=(20, 10))

        msg = (
            f"¡Eureka!\n"
            f"Se han guardado {created} iconos en:\n"
            f"{destination}"
        )
        tk.Label(
            dialog,
            text=msg,
            font=('Segoe UI', 12),
            bg="#f5f5f5",
            justify=tk.CENTER
        ).pack(padx=20)

        ttk.Button(
            dialog,
            text="Volver al caldero",
            command=dialog.destroy
        ).pack(pady=(10, 20))

        dialog.update_idletasks()
        pw = self.winfo_width()
        ph = self.winfo_height()
        px = self.winfo_x()
        py = self.winfo_y()
        dw = dialog.winfo_width()
        dh = dialog.winfo_height()
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2
        dialog.geometry(f"{dw}x{dh}+{x}+{y}")

        dialog.wait_window()

        self.images.clear()

        for child in self.inner.winfo_children():
            child.destroy()

        self.canvas.update_idletasks()


if __name__ == "__main__":
    app = IconCraft()
    app.mainloop()
