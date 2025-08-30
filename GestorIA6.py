import os
import tkinter as tk
from tkinter import ttk
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ------------------ Config categorías ------------------
CATEGORIES = {
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".mpeg", ".mpg"},
    "Música": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma"},
    "Imágenes": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic"},
    "Documentos": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".md"},
    "Comprimidos": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Instaladores": {".exe", ".msi", ".apk", ".dmg", ".pkg"},
}

def get_category(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Otros"

def fmt_size(bytes_: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_)
    for u in units:
        if size < 1024 or u == units[-1]:
            return f"{size:.2f} {u}"
        size /= 1024.0

def safe_getsize(path: str) -> int:
    try:
        return os.path.getsize(path)
    except (FileNotFoundError, PermissionError, OSError):
        return 0

def scan_directory(base_path: str, top_n_files: int = 10):
    category_sizes = defaultdict(int)
    files_info = []

    for dirpath, _, filenames in os.walk(base_path, onerror=lambda e: None, followlinks=False):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            size = safe_getsize(fp)
            if size == 0:
                continue

            cat = get_category(name)
            category_sizes[cat] += size
            files_info.append((fp, size, cat))

    # Top archivos
    top_files = sorted(files_info, key=lambda x: x[1], reverse=True)[:top_n_files]
    total_size = sum(size for _, size, _ in files_info)

    return total_size, top_files, category_sizes

# ------------------ Interfaz ------------------
class GestorArchivosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Archivos IA")
        self.root.geometry("900x700")

        user = os.getlogin()
        base_user = os.path.join("C:\\Users", user)

        self.target_folders = {
            "Descargas": os.path.join(base_user, "Downloads"),
            "Imágenes": os.path.join(base_user, "Pictures"),
            "Escritorio": os.path.join(base_user, "Desktop"),
            "Documentos": os.path.join(base_user, "Documents"),
            "Música": os.path.join(base_user, "Music"),
            "Videos": os.path.join(base_user, "Videos"),
        }

        self.resumen = []
        self.build_main_view()

    def build_main_view(self):
        """Pantalla principal con gráfico de carpetas"""
        for w in self.root.winfo_children():
            w.destroy()

        self.resumen = []
        for nombre, ruta in self.target_folders.items():
            if os.path.exists(ruta):
                total, _, _ = scan_directory(ruta)
                self.resumen.append((nombre, total, ruta))

        labels = [n for n, _, _ in self.resumen]
        sizes = [t for _, t, _ in self.resumen]

        fig, ax = plt.subplots(figsize=(7,6))
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct=lambda p: f'{p:.1f}%',
            textprops=dict(color="w")
        )
        ax.set_title("Uso de espacio en carpetas principales")

        # Activar click en porciones
        for w in wedges:
            w.set_picker(True)

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Vincular evento de click
        def on_pick(event):
            wedge = event.artist
            index = wedges.index(wedge)
            nombre, _, ruta = self.resumen[index]
            self.show_folder_view(nombre, ruta)

        fig.canvas.mpl_connect("pick_event", on_pick)

    def show_folder_view(self, nombre, ruta):
        """Vista de análisis de una carpeta en detalle"""
        for w in self.root.winfo_children():
            w.destroy()

        total, top_files, cats = scan_directory(ruta)

        lbl = ttk.Label(self.root, text=f"📂 {nombre} ({ruta})\nTamaño total: {fmt_size(total)}", font=("Arial", 14))
        lbl.pack(pady=10)

        # Gráfico de categorías
        if cats:
            labels_c = list(cats.keys())
            sizes_c = list(cats.values())
            fig, ax = plt.subplots(figsize=(7,6))
            ax.pie(sizes_c, labels=labels_c, autopct=lambda p: f'{p:.1f}%', textprops=dict(color="w"))
            ax.set_title(f"Distribución de espacio en {nombre}")
            canvas = FigureCanvasTkAgg(fig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().pack()

        # TOP archivos
        frame = ttk.LabelFrame(self.root, text="Top archivos más pesados")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(frame, columns=("size", "cat", "name"), show="headings")
        tree.heading("size", text="Tamaño")
        tree.heading("cat", text="Categoría")
        tree.heading("name", text="Archivo")
        tree.pack(fill="both", expand=True)

        for path, size, cat in top_files:
            tree.insert("", "end", values=(fmt_size(size), cat, os.path.basename(path)))

        # Botón volver
        back_btn = ttk.Button(self.root, text="⬅️ Volver", command=self.build_main_view)
        back_btn.pack(pady=10)

# ------------------ Run App ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GestorArchivosApp(root)
    root.mainloop()
