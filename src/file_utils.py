# =============================================================================
# file_utils.py - File Utility Functions / Dosya Yardımcı Fonksiyonları
# =============================================================================
# Helper functions for file operations: icons, hidden file check, size format.
#
# Dosya işlemleri için yardımcı fonksiyonlar: ikonlar, gizli dosya kontrolü,
# boyut formatlama.
# =============================================================================

import os  # For file system operations / Dosya sistemi işlemleri için


# --- Emoji icons for file types / Dosya türleri için emoji ikonlar ---
EMOJI_ICONS = {
    "directory": "📁",
    "file": "📄",
    "text": "📝",
    "image": "🖼️",
    "code": "💻",
    "pdf": "📕",
    "video": "🎬",
    "audio": "🎵",
    "archive": "🗄️",
    "unknown": "❓",
}

# --- File extension categories / Dosya uzantısı kategorileri ---
# Each list maps file extensions to a category name
# Her liste, dosya uzantılarını bir kategori adına eşler
TEXT_EXTENSIONS = [".txt", ".md", ".log", ".ini", ".cfg", ".json", ".xml", ".csv"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"]
CODE_EXTENSIONS = [".py", ".js", ".html", ".css", ".java", ".c", ".cpp",
                   ".cs", ".php", ".rb", ".go", ".swift", ".kt"]
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"]
AUDIO_EXTENSIONS = [".mp3", ".wav", ".ogg", ".aac", ".flac"]
ARCHIVE_EXTENSIONS = [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"]


def get_file_icon(file_path):
    """
    Returns an emoji icon based on file type.
    Dosya türüne göre emoji ikon döndürür.

    Args:
        file_path (str): Path to the file. / Dosya yolu.
    Returns:
        str: Emoji icon. / Emoji ikon.
    """
    # Check if file exists / Dosya var mı kontrol et
    if not os.path.exists(file_path):
        return EMOJI_ICONS["unknown"]

    # Directory check / Klasör kontrolü
    if os.path.isdir(file_path):
        return EMOJI_ICONS["directory"]

    # Get file extension and convert to lowercase
    # Dosya uzantısını al ve küçük harfe çevir
    file_name, extension = os.path.splitext(file_path)
    extension = extension.lower()

    # Match extension to category / Uzantıyı kategori ile eşleştir
    if extension in TEXT_EXTENSIONS:
        return EMOJI_ICONS["text"]

    if extension in IMAGE_EXTENSIONS:
        return EMOJI_ICONS["image"]

    if extension in CODE_EXTENSIONS:
        return EMOJI_ICONS["code"]

    if extension == ".pdf":
        return EMOJI_ICONS["pdf"]

    if extension in VIDEO_EXTENSIONS:
        return EMOJI_ICONS["video"]

    if extension in AUDIO_EXTENSIONS:
        return EMOJI_ICONS["audio"]

    if extension in ARCHIVE_EXTENSIONS:
        return EMOJI_ICONS["archive"]

    # Default: generic file icon / Varsayılan: genel dosya ikonu
    return EMOJI_ICONS["file"]


def is_hidden(path):
    """
    Checks if a file/directory is hidden (OS-specific).
    Dosya/klasörün gizli olup olmadığını kontrol eder (İşletim sistemine göre).

    Args:
        path (str): File path. / Dosya yolu.
    Returns:
        bool: True if hidden. / Gizli ise True.
    """
    # Unix/macOS: files starting with '.' are hidden
    # Unix/macOS: '.' ile başlayan dosyalar gizlidir
    if os.name == "posix":
        file_name = os.path.basename(path)
        return file_name.startswith(".")

    # Windows: check the hidden attribute
    # Windows: gizli dosya özniteliğini kontrol et
    if os.name == "nt":
        import stat
        try:
            file_attributes = os.stat(path).st_file_attributes
            is_hidden_file = bool(file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            return is_hidden_file
        except (FileNotFoundError, OSError):
            return False

    # Other OS: not hidden by default / Diğer OS: varsayılan olarak gizli değil
    return False


def format_size(size_bytes):
    """
    Converts bytes to human-readable format (KB, MB, GB...).
    Byte'ı okunabilir formata çevirir (KB, MB, GB...).

    Args:
        size_bytes (int): Size in bytes. / Byte cinsinden boyut.
    Returns:
        str: Formatted size (e.g. "4.5 MB"). / Formatlanmış boyut.
    """
    # Empty file / Boş dosya
    if size_bytes == 0:
        return "0 B"

    # Unit names / Birim adları
    units = ("B", "KB", "MB", "GB", "TB")

    # Find the right unit by dividing by 1024
    # 1024'e bölerek doğru birimi bul
    index = 0
    current_size = float(size_bytes)

    while current_size >= 1024 and index < len(units) - 1:
        current_size = current_size / 1024.0
        index = index + 1

    # Format with 2 decimal places / 2 ondalık basamakla formatla
    result = f"{current_size:.2f}"

    # Clean up trailing zeros / Sondaki gereksiz sıfırları temizle
    if result.endswith(".00"):
        result = result[:-3]    # Remove ".00" / ".00" kaldır
    elif result.endswith("0"):
        result = result[:-1]    # Remove trailing "0" / Sondaki "0" kaldır

    return result + " " + units[index]


def filter_hidden_items(items, parent_path):
    """
    Filters out hidden files from a list of file names.
    Dosya adları listesinden gizli dosyaları filtreler.

    Args:
        items (list): List of file/directory names. / Dosya/klasör adları listesi.
        parent_path (str): Parent directory path. / Üst dizin yolu.
    Returns:
        list: Filtered list without hidden files. / Gizli dosyalar olmadan filtrelenmiş liste.
    """
    visible_items = []
    for item in items:
        full_path = os.path.join(parent_path, item)
        if not is_hidden(full_path):
            visible_items.append(item)
    return visible_items


def sort_items_by_type(items, parent_path):
    """
    Sorts items: directories first, then files. Alphabetical in each group.
    Öğeleri sıralar: önce klasörler, sonra dosyalar. Her grup alfabetik.

    Args:
        items (list): List of file/directory names. / Dosya/klasör adları listesi.
        parent_path (str): Parent directory path. / Üst dizin yolu.
    Returns:
        list: Sorted list. / Sıralanmış liste.
    """
    def sort_key(item_name):
        item_path = os.path.join(parent_path, item_name)
        is_file = not os.path.isdir(item_path)
        return (is_file, item_name.lower())

    items.sort(key=sort_key)
    return items
