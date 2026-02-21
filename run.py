# =============================================================================
# run.py - Application Entry Point / Uygulama Giriş Noktası
# =============================================================================
# This is the main entry point for the File Explorer application.
# Run this file to start the application.
#
# Bu dosya, FileExplorerApp uygulamasının ana giriş noktasıdır.
# Uygulamayı başlatmak için bu dosyayı çalıştırın.
#
# Usage / Kullanım:
#   python run.py                  -> Opens with home directory / Ev dizini ile açar
#   python run.py /path/to/dir     -> Opens with specified directory / Belirtilen dizin ile açar
# =============================================================================

import sys                              # For command-line arguments / Komut satırı argümanları için
import tkinter as tk                    # For the main window / Ana pencere için
from src.file_explorer import FileExplorerApp   # Main application class / Ana uygulama sınıfı


def main():
    """
    Creates the main window and starts the File Explorer application.
    Ana pencereyi oluşturur ve FileExplorerApp uygulamasını başlatır.
    """
    # Create the main Tkinter window / Ana Tkinter penceresini oluştur
    root = tk.Tk()

    # Check if a starting directory was provided as a command-line argument
    # Komut satırı argümanı olarak başlangıç dizini verilip verilmediğini kontrol et
    if len(sys.argv) > 1:
        initial_directory = sys.argv[1]
    else:
        initial_directory = None

    # Create the File Explorer application / FileExplorerApp uygulamasını oluştur
    app = FileExplorerApp(root, directory=initial_directory)

    # Start the Tkinter event loop (keeps the window open and processes events)
    # Tkinter olay döngüsünü başlat (pencereyi açık tutar ve olayları işler)
    root.mainloop()


# This block runs only when the script is executed directly (not imported)
# Bu blok sadece script doğrudan çalıştırıldığında çalışır (import edildiğinde değil)
if __name__ == "__main__":
    main()
