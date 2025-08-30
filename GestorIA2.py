import os
from collections import defaultdict

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
    # Representa en B, KB, MB, GB, TB
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

def normalize_base(base_path: str) -> str:
    # Limpia errores típicos al pegar ruta desde terminal
    base = base_path.strip().strip('"').strip("'").rstrip(">")  # quita comillas y '>'
    # Normaliza y quita separador final redundante
    return os.path.normpath(base)

def scan_directory(base_path: str, top_n_folders: int = 15, top_n_files: int = 20):
    base = normalize_base(base_path)

    if not os.path.isdir(base):
        print(f"❌ Ruta no válida: {base}\nSugerencia: copia la ruta desde el Explorador (barra de direcciones) o quita el símbolo '>' del prompt.")
        return

    # Para comparar padres dentro del árbol base
    base_normcase = os.path.normcase(base)

    folder_sizes = defaultdict(int)   # Tamaño recursivo por carpeta
    category_sizes = defaultdict(int) # Tamaño acumulado por categoría
    files_info = []                   # (path, size, category)
    errors = 0

    for dirpath, dirnames, filenames in os.walk(base, onerror=lambda e: None, followlinks=False):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            size = safe_getsize(fp)
            if size == 0:
                # Puede ser error o archivo vacío; no contamos como error si realmente es 0 bytes.
                try:
                    if os.path.getsize(fp) != 0:
                        errors += 1
                except Exception:
                    errors += 1

            cat = get_category(name)
            category_sizes[cat] += size
            files_info.append((fp, size, cat))

            # Acumular tamaño a esta carpeta y a todos los padres dentro del base
            current = dirpath
            while True:
                folder_sizes[current] += size
                parent = os.path.dirname(current)
                if not parent or os.path.normcase(parent) == os.path.normcase(current):
                    break
                # Detener cuando salgamos del árbol base
                if not os.path.normcase(parent).startswith(base_normcase):
                    break
                current = parent

    # TOP carpetas
    top_folders = sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)[:top_n_folders]
    # TOP archivos
    top_files = sorted(files_info, key=lambda x: x[1], reverse=True)[:top_n_files]
    # Categorías
    cat_breakdown = sorted(category_sizes.items(), key=lambda x: x[1], reverse=True)

    # ----------- Salida ----------
    print("\n=== TOP Carpetas más pesadas (recursivo) ===")
    for path, size in top_folders:
        print(f"{path} | {fmt_size(size)}")

    print("\n=== TOP Archivos más pesados ===")
    for path, size, cat in top_files:
        print(f"{path} | {fmt_size(size)} | {cat}")

    print("\n=== Uso por Categorías ===")
    for cat, size in cat_breakdown:
        print(f"{cat}: {fmt_size(size)}")

    if errors:
        print(f"\n⚠️ Archivos omitidos por permisos/errores: {errors}")

if __name__ == "__main__":
    ruta = input("👉 Ingresa la ruta a analizar: ")
    scan_directory(ruta)
