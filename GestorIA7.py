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
    errors = 0

    for dirpath, _, filenames in os.walk(base_path, onerror=lambda e: None, followlinks=False):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            size = safe_getsize(fp)
            if size == 0:
                try:
                    if os.path.getsize(fp) != 0:
                        errors += 1
                except Exception:
                    errors += 1

            cat = get_category(name)
            category_sizes[cat] += size
            files_info.append((fp, size, cat))

    # Top archivos
    top_files = sorted(files_info, key=lambda x: x[1], reverse=True)[:top_n_files]
    total_size = sum(category_sizes.values())

    return total_size, top_files, category_sizes, errors

class GestorArchivosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Archivos con Estadísticas")
        self.current_view = "main"

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

        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_main_view()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def build_main_view(self):
        self.clear_frame()
        self.current_view = "main"

        resumen = []
        for nombre, ruta in self.target_folders.items():
            if os.path.exists(ruta):
                total, _, _, _ = scan_directory(ruta)
                resumen.append((nombre, total))

        if not resumen:
            tk.Label(self.frame, text="No se encontraron carpetas para analizar").pack()
            return

        labels = [nombre for nombre, _ in resumen]
        sizes = [total for _, total in resumen]

        fig, ax = plt.subplots(figsize=(5, 5))
        wedges, texts, autotexts = ax.pie(
            sizes,
            autopct='%1.1f%%',
            textprops=dict(color="w")
        )

        # Corregimos el texto para incluir nombre + porcentaje
        for i, a in enumerate(autotexts):
            a.set_text(f"{labels[i]} {a.get_text()}")

        ax.legend(wedges, labels, title="Carpetas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title("Uso de espacio por carpetas principales")

        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Detectar clic en porción del pastel
        def on_click(event):
            if event.inaxes == ax:
                for i, wedge in enumerate(wedges):
                    if wedge.contains_point([event.x, event.y]):
                        self.show_folder_view(labels[i])
                        return

        fig.canvas.mpl_connect("button_press_event", on_click)

    def show_folder_view(self, folder_name):
        self.clear_frame()
        self.current_view = "folder"

        ruta = self.target_folders[folder_name]
        if not os.path.exists(ruta):
            tk.Label(self.frame, text=f"La carpeta {folder_name} no existe.").pack()
            return

        total, top_files, cats, errors = scan_directory(ruta)

        labels = list(cats.keys())
        sizes = list(cats.values())

        if not sizes or sum(sizes) == 0:
            tk.Label(self.frame, text=f"No se encontraron archivos en {folder_name}.").pack()
        else:
            fig, ax = plt.subplots(figsize=(5, 5))
            wedges, texts, autotexts = ax.pie(
                sizes,
                autopct='%1.1f%%',
                textprops=dict(color="w")
            )

            for i, a in enumerate(autotexts):
                a.set_text(f"{labels[i]} {a.get_text()}")

            ax.legend(wedges, labels, title="Categorías", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            ax.set_title(f"Uso de espacio en {folder_name}")

            canvas = FigureCanvasTkAgg(fig, master=self.frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        tk.Label(self.frame, text=f"TOP archivos más pesados en {folder_name}:").pack(pady=5)
        for path, size, cat in top_files:
            tk.Label(self.frame, text=f"{fmt_size(size)} | {cat} | {os.path.basename(path)}").pack(anchor="w")

        ttk.Button(self.frame, text="⬅️ Volver", command=self.build_main_view).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = GestorArchivosApp(root)
    root.mainloop()
