import os
from collections import defaultdict
import matplotlib.pyplot as plt

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
    folder_sizes = defaultdict(int)
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

            # Acumular tamaño en carpeta
            folder_sizes[base_path] += size

    # Top archivos
    top_files = sorted(files_info, key=lambda x: x[1], reverse=True)[:top_n_files]
    total_size = sum(folder_sizes.values())

    return total_size, top_files, category_sizes, errors

if __name__ == "__main__":
    user = os.getlogin()
    base_user = os.path.join("C:\\Users", user)

    # Carpetas a analizar
    target_folders = {
        "Descargas": os.path.join(base_user, "Downloads"),
        "Imágenes": os.path.join(base_user, "Pictures"),
        "Escritorio": os.path.join(base_user, "Desktop"),
        "Documentos": os.path.join(base_user, "Documents"),
        "Música": os.path.join(base_user, "Music"),
        "Videos": os.path.join(base_user, "Videos"),
    }

    print(f"\n🔎 Analizando carpetas principales del usuario: {user}\n")

    resumen = []
    categorias_global = defaultdict(int)

    for nombre, ruta in target_folders.items():
        if os.path.exists(ruta):
            total, top_files, cats, errors = scan_directory(ruta)

            print(f"\n📂 {nombre} ({ruta})")
            print(f"   ➡️ Tamaño total: {fmt_size(total)}")
            
            print("   ➡️ TOP archivos más pesados:")
            for path, size, cat in top_files:
                print(f"      {fmt_size(size)} | {cat} | {os.path.basename(path)}")
            
            print("   ➡️ Uso por categorías:")
            for cat, size in sorted(cats.items(), key=lambda x: x[1], reverse=True):
                if size > 0:
                    print(f"      {cat}: {fmt_size(size)}")
                    categorias_global[cat] += size

            if errors:
                print(f"   ⚠️ Archivos omitidos por permisos/errores: {errors}")

            resumen.append((nombre, total))
        else:
            print(f"\n📂 {nombre} ({ruta}) ➡️ No existe en este sistema.")

    print("\n=== RESUMEN GENERAL ===")
    for nombre, total in sorted(resumen, key=lambda x: x[1], reverse=True):
        print(f"{nombre}: {fmt_size(total)}")

    # ------------------ Gráficos ------------------

    # Gráfico 1: Uso por carpeta
    labels = [nombre for nombre, _ in resumen]
    sizes = [total for _, total in resumen]

    plt.figure(figsize=(8,6))
    plt.pie(sizes, labels=labels, autopct=lambda p: f'{p:.1f}%\n({fmt_size(int(p*sum(sizes)/100))})')
    plt.title("Distribución de espacio por carpetas principales")
    plt.show()

    # Gráfico 2: Uso global por categorías
    if categorias_global:
        labels_c = list(categorias_global.keys())
        sizes_c = list(categorias_global.values())

        plt.figure(figsize=(8,6))
        plt.pie(sizes_c, labels=labels_c, autopct=lambda p: f'{p:.1f}%\n({fmt_size(int(p*sum(sizes_c)/100))})')
        plt.title("Distribución de espacio por categorías (global)")
        plt.show()
