import os

# Categorías según extensiones
CATEGORIES = {
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Música": [".mp3", ".wav", ".flac"],
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Documentos": [".pdf", ".docx", ".xlsx", ".pptx", ".txt"],
}

def get_category(filename):
    ext = os.path.splitext(filename)[1].lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Otros"

def get_size(path):
    """Obtiene el tamaño de un archivo o carpeta"""
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except:
                pass
    return total

def scan_directory(base_path):
    data = []
    for dirpath, dirnames, filenames in os.walk(base_path):
        folder_size = sum(get_size(os.path.join(dirpath, f)) for f in filenames)
        
        # Guardar info de carpeta
        data.append((dirpath, folder_size, "Carpeta"))

        # Guardar info de archivos
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                size = os.path.getsize(fp)
                category = get_category(f)
                data.append((fp, size, category))
            except:
                pass

    # Ordenar por tamaño (descendente)
    data.sort(key=lambda x: x[1], reverse=True)
    return data

if __name__ == "__main__":
    ruta = input("👉 Ingresa la ruta a analizar: ")
    resultados = scan_directory(ruta)

    print("\n=== Archivos y Carpetas más pesados ===\n")
    for path, size, category in resultados[:20]:  # Mostrar solo top 20
        print(f"{path} | {size/1024/1024:.2f} MB | {category}")
