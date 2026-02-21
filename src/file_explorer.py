# =============================================================================
# file_explorer.py - Main Application / Ana Uygulama
# =============================================================================
# This module contains the FileExplorerApp class which creates the GUI
# and handles user interactions for the file explorer.
#
# Bu modül, dosya gezgini için GUI oluşturan ve kullanıcı etkileşimlerini
# yöneten FileExplorerApp sınıfını içerir.
# =============================================================================

import os           # File/directory operations / Dosya/klasör işlemleri
import sys          # System parameters / Sistem parametreleri
import time         # Time operations / Zaman işlemleri
import subprocess   # For opening files / Dosya açmak için
import tkinter as tk                            # GUI library / GUI kütüphanesi
from tkinter import ttk, messagebox, filedialog # Widgets, dialogs / Widget'lar, iletişim kutuları

# Import project modules / Proje modüllerini içe aktar
from .tree_node import TreeNode
from .file_utils import get_file_icon, is_hidden, format_size
from .file_utils import filter_hidden_items, sort_items_by_type


class FileExplorerApp:
    """
    Main file explorer application.
    Ana dosya gezgini uygulaması.
    """

    def __init__(self, root, directory=None):
        """
        Initializes the application.
        Uygulamayı başlatır.

        Args:
            root (tk.Tk): Main window. / Ana pencere.
            directory (str, optional): Starting directory. / Başlangıç dizini.
        """
        self.root = root

        # Set starting directory (default: home directory)
        # Başlangıç dizinini ayarla (varsayılan: ev dizini)
        if directory is None:
            self.root_dir = os.path.expanduser("~")
        else:
            self.root_dir = directory

        # Window title and size / Pencere başlığı ve boyutu
        self.root.title("FileExplorerApp")
        self.root.geometry("900x650")

        # Apply theme / Temayı uygula
        self._set_theme()

        # Hidden files toggle / Gizli dosya göster/gizle
        self.show_hidden = tk.BooleanVar(value=False)

        # Build the UI / Arayüzü oluştur
        self._setup_ui()

        # Maps Treeview IDs to TreeNode objects
        # Treeview ID'lerini TreeNode nesnelerine eşler
        self.nodes = {}

        # Load starting directory / Başlangıç dizinini yükle
        self._populate_root()

    # =========================================================================
    # Theme / Tema
    # =========================================================================

    def _set_theme(self):
        """
        Sets the visual theme.
        Görsel temayı ayarlar.
        """
        style = ttk.Style()

        # Use 'clam' theme if available / 'clam' teması varsa kullan
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")

        # Treeview style / Ağaç stili
        style.configure("Treeview",
                         background="#f5f5f5",
                         foreground="black",
                         rowheight=25,
                         fieldbackground="#f5f5f5")

        # Selected item style / Seçili öğe stili
        style.map("Treeview",
                   background=[("selected", "#4a6984")],
                   foreground=[("selected", "white")])

        # Button style / Buton stili
        style.configure("TButton",
                         padding=6,
                         relief="flat",
                         background="#4a6984",
                         foreground="white")

        # Frame and Label / Çerçeve ve Etiket
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5", padding=5)

        # Status bar / Durum çubuğu
        style.configure("Status.TLabel",
                         background="#e1e1e1",
                         foreground="#333333",
                         padding=5)

    # =========================================================================
    # User Interface / Kullanıcı Arayüzü
    # =========================================================================

    def _setup_ui(self):
        """
        Creates all UI elements.
        Tüm arayüz elemanlarını oluşturur.
        """
        self._create_menu()
        self._create_status_bar()
        self._create_toolbar()
        self._create_main_frame()
        self._create_treeview()

        # Backspace = go to parent directory / Backspace = üst dizine git
        self.root.bind("<BackSpace>", self._on_backspace)

    def _on_backspace(self, event):
        """
        Handles Backspace key press: navigates to parent directory.
        Backspace tuşuna basıldığında üst dizine gider.
        """
        self.go_up_directory()

    def _create_menu(self):
        """
        Creates the menu bar.
        Menü çubuğunu oluşturur.
        """
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu / Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Dizin Seç", command=self.select_directory)
        file_menu.add_command(label="Yenile", command=self.refresh_view)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)

        # View menu / Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        view_menu.add_checkbutton(label="Gizli Dosyaları Göster",
                                   variable=self.show_hidden,
                                   command=self.refresh_view)
        view_menu.add_separator()
        view_menu.add_command(label="Tümünü Genişlet", command=self.expand_all)
        view_menu.add_command(label="Tümünü Daralt", command=self.collapse_all)

        # Help menu / Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Hakkında", command=self._show_about)

    def _create_status_bar(self):
        """
        Creates the status bar at the bottom.
        Alt kısımda durum çubuğunu oluşturur.
        """
        self.status_bar = ttk.Label(self.root,
                                     text="Hazır",
                                     relief="groove",
                                     anchor="w",
                                     style="Status.TLabel")
        self.status_bar.pack(side="bottom", fill="x")

    def _create_toolbar(self):
        """
        Creates the toolbar with buttons.
        Butonları içeren araç çubuğunu oluşturur.
        """
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side="top", fill="x", padx=5, pady=5)

        # Navigation buttons / Gezinme butonları
        up_button = ttk.Button(self.toolbar,
                                text="⬆ Üst Dizin",
                                command=self.go_up_directory)
        up_button.pack(side="left", padx=5, pady=5)

        dir_button = ttk.Button(self.toolbar,
                                 text="📂 Dizin Seç",
                                 command=self.select_directory)
        dir_button.pack(side="left", padx=5, pady=5)

        refresh_button = ttk.Button(self.toolbar,
                                     text="🔄 Yenile",
                                     command=self.refresh_view)
        refresh_button.pack(side="left", padx=5, pady=5)

        # Hidden files checkbox / Gizli dosya onay kutusu
        hidden_check = ttk.Checkbutton(self.toolbar,
                                        text="Gizli Dosyaları Göster",
                                        variable=self.show_hidden,
                                        command=self.refresh_view)
        hidden_check.pack(side="left", padx=10, pady=5)

        # Current path display / Mevcut yol gösterimi
        self.current_dir_var = tk.StringVar(value=self.root_dir)

        path_frame = ttk.Frame(self.toolbar)
        path_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        path_label = ttk.Label(path_frame, text="Konum:", anchor="w")
        path_label.pack(side="left")

        dir_label = ttk.Label(path_frame,
                               textvariable=self.current_dir_var,
                               anchor="w",
                               foreground="#0066cc")
        dir_label.pack(side="left", fill="x", expand=True)

    def _create_main_frame(self):
        """
        Creates the main content frame.
        Ana içerik çerçevesini oluşturur.
        """
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _create_treeview(self):
        """
        Creates the Treeview with scrollbars.
        Kaydırma çubuklariyla Treeview oluşturur.
        """
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill="both", expand=True)

        # Treeview widget
        self.treeview = ttk.Treeview(tree_frame, show="tree")

        # Vertical scrollbar / Dikey kaydırma
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                                  command=self.treeview.yview)
        y_scroll.pack(side="right", fill="y")

        # Horizontal scrollbar / Yatay kaydırma
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal",
                                  command=self.treeview.xview)
        x_scroll.pack(side="bottom", fill="x")

        # Connect scrollbars / Kaydırma çubuklarını bağla
        self.treeview.configure(yscrollcommand=y_scroll.set,
                                 xscrollcommand=x_scroll.set)
        self.treeview.pack(side="left", fill="both", expand=True)

        # Column width / Sütun genişliği
        self.treeview.column("#0", width=300, minwidth=150, stretch=True)

        # Bind events / Olayları bağla
        self.treeview.bind("<Double-1>", self._on_double_click)
        self.treeview.bind("<Button-3>", self._on_right_click)
        self.treeview.bind("<<TreeviewOpen>>", self._on_treeview_open)

    # =========================================================================
    # Directory Operations / Dizin İşlemleri
    # =========================================================================

    def go_up_directory(self):
        """
        Goes to the parent directory.
        Üst dizine gider.
        """
        parent_dir = os.path.dirname(self.root_dir)

        # Check if already at root / Zaten kökte miyiz kontrol et
        if parent_dir == self.root_dir:
            self._show_status("Kök dizindesiniz.")
            return

        self.root_dir = parent_dir
        self.current_dir_var.set(self.root_dir)
        self.refresh_view()
        self._show_status("Üst dizine gidildi: " + self.root_dir)

    def select_directory(self):
        """
        Opens a directory picker dialog.
        Dizin seçme penceresi açar.
        """
        directory = filedialog.askdirectory(initialdir=self.root_dir)

        if directory:
            self.root_dir = directory
            self.current_dir_var.set(directory)
            self.refresh_view()

    def refresh_view(self):
        """
        Refreshes the tree view.
        Ağaç görünümünü yeniler.
        """
        self._show_status("Görünüm yenileniyor...")

        # Delete all items / Tüm öğeleri sil
        all_items = self.treeview.get_children()
        for item in all_items:
            self.treeview.delete(item)

        # Clear node dictionary / Düğüm sözlüğünü temizle
        self.nodes.clear()

        # Reload / Yeniden yükle
        self._populate_root()
        self._show_status("Görünüm yenilendi.")

    def _populate_root(self):
        """
        Loads the root directory into the tree.
        Kök dizini ağaca yükler.
        """
        try:
            # Get directory name / Dizin adını al
            root_name = os.path.basename(self.root_dir)
            if root_name == "":
                root_name = self.root_dir

            # Create root node / Kök düğüm oluştur
            root_node = TreeNode(root_name, self.root_dir, True)
            icon = get_file_icon(self.root_dir)

            # Insert into treeview / Treeview'a ekle
            display_text = icon + " " + root_name
            root_id = self.treeview.insert("", "end", text=display_text, open=False)
            self.nodes[root_id] = root_node

            # Load children / Alt öğeleri yükle
            self._load_children(root_id)

            # Open root by default / Kökü varsayılan olarak aç
            self.treeview.item(root_id, open=True)

        except Exception as error:
            self._show_status("Hata: Dizin yüklenemedi - " + str(error))
            messagebox.showerror("Hata", "Dizin yüklenemedi: " + str(error))

    def _load_children(self, parent_id):
        """
        Loads child items for a parent node.
        Bir ebeveyn düğümün alt öğelerini yükler.

        Args:
            parent_id (str): Treeview item ID. / Treeview öğe ID'si.
        """
        parent_node = self.nodes.get(parent_id)

        # Skip if not valid / Geçerli değilse atla
        if parent_node is None:
            return
        if not parent_node.is_dir:
            return
        if parent_node.loaded:
            return

        try:
            # List directory contents / Dizin içeriğini listele
            items = os.listdir(parent_node.path)

            # Filter hidden files if needed / Gerekirse gizli dosyaları filtrele
            if not self.show_hidden.get():
                items = filter_hidden_items(items, parent_node.path)

            # Sort: directories first, then files / Sırala: önce klasörler, sonra dosyalar
            items = sort_items_by_type(items, parent_node.path)

            # Add each item to the tree / Her öğeyi ağaca ekle
            for item_name in items:
                item_path = os.path.join(parent_node.path, item_name)
                item_is_dir = os.path.isdir(item_path)

                # Create node / Düğüm oluştur
                node = TreeNode(item_name, item_path, item_is_dir)
                parent_node.add_child(node)

                # Get icon / İkon al
                icon = get_file_icon(item_path)

                # Insert into treeview / Treeview'a ekle
                display_text = icon + " " + item_name
                item_id = self.treeview.insert(parent_id, "end",
                                                text=display_text, open=False)
                self.nodes[item_id] = node

                # If directory, add a placeholder for lazy loading
                # Klasörse, tembel yükleme için yer tutucu ekle
                if item_is_dir:
                    self._add_placeholder_if_not_empty(item_id, item_path)

            # Mark as loaded / Yüklenmiş olarak işaretle
            parent_node.loaded = True

        except PermissionError:
            self._show_status("Erişim izni yok: " + parent_node.path)
            self.treeview.insert(parent_id, "end", text="⚠️ Erişim izni yok")

        except Exception as error:
            error_msg = "Hata: " + parent_node.path + " yüklenirken - " + str(error)
            self._show_status(error_msg)
            self.treeview.insert(parent_id, "end", text="❌ Hata: " + str(error))

    def _add_placeholder_if_not_empty(self, item_id, dir_path):
        """
        Adds a 'Loading...' placeholder if the directory is not empty.
        Klasör boş değilse 'Yükleniyor...' yer tutucusu ekler.

        Args:
            item_id (str): Treeview item ID. / Treeview öğe ID'si.
            dir_path (str): Directory path. / Dizin yolu.
        """
        try:
            contents = os.listdir(dir_path)

            # Filter hidden files if needed / Gerekirse gizli dosyaları filtrele
            if not self.show_hidden.get():
                contents = filter_hidden_items(contents, dir_path)

            # Only add placeholder if directory has items
            # Sadece klasör öğe içeriyorsa yer tutucu ekle
            if len(contents) > 0:
                self.treeview.insert(item_id, "end", text="Yükleniyor...")

        except (PermissionError, OSError):
            # Cannot access directory, skip / Dizine erişilemedi, atla
            pass

    def _remove_dummy_nodes(self, parent_id):
        """
        Removes placeholder nodes when a folder is expanded.
        Klasör açıldığında yer tutucu düğümleri kaldırır.

        Args:
            parent_id (str): Treeview item ID. / Treeview öğe ID'si.
        """
        children = self.treeview.get_children(parent_id)

        for child_id in children:
            item_text = self.treeview.item(child_id, "text")

            # Check if it is a placeholder / Yer tutucu mu kontrol et
            if "Yükleniyor..." in item_text:
                self.treeview.delete(child_id)
            elif "Hata:" in item_text:
                self.treeview.delete(child_id)
            elif "Erişim izni yok" in item_text:
                self.treeview.delete(child_id)

    # =========================================================================
    # Event Handlers / Olay Yöneticileri
    # =========================================================================

    def _on_treeview_open(self, event):
        """
        Called when a folder is expanded.
        Klasör açıldığında çağrılır.
        """
        item_id = self.treeview.focus()

        if item_id:
            self._remove_dummy_nodes(item_id)
            self._load_children(item_id)

    def _on_double_click(self, event):
        """
        Called when an item is double-clicked.
        Bir öğeye çift tıklandığında çağrılır.
        """
        item_id = self.treeview.identify_row(event.y)

        # Clicked on empty area / Boş alana tıklandı
        if not item_id:
            return

        node = self.nodes.get(item_id)
        if node is None:
            return

        if node.is_dir:
            # Toggle folder open/close / Klasörü aç/kapat
            is_open = self.treeview.item(item_id, "open")
            self.treeview.item(item_id, open=not is_open)
        else:
            # Open the file / Dosyayı aç
            self._show_status("Dosya açılıyor: " + node.path)
            self._open_file(node.path)

    def _open_file(self, file_path):
        """
        Opens a file with the default system application.
        Dosyayı varsayılan sistem uygulamasıyla açar.

        Args:
            file_path (str): Path to the file. / Dosya yolu.
        """
        try:
            # Windows
            if sys.platform == "win32":
                os.startfile(file_path)

            # macOS
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path], check=True)

            # Linux
            else:
                subprocess.run(["xdg-open", file_path], check=True)

            self._show_status("Dosya açıldı: " + file_path)

        except Exception as error:
            self._show_status("Dosya açılamadı: " + str(error))
            messagebox.showerror("Hata", "Dosya açılamadı: " + str(error))

    def _on_right_click(self, event):
        """
        Called when right-clicking an item. Shows context menu.
        Sağ tıklandığında çağrılır. Bağlam menüsü gösterir.
        """
        item_id = self.treeview.identify_row(event.y)
        if not item_id:
            return

        self.treeview.selection_set(item_id)
        self._show_context_menu(event, item_id)

    def _show_context_menu(self, event, item_id):
        """
        Creates and shows the right-click context menu.
        Sağ tıklama bağlam menüsünü oluşturur ve gösterir.
        """
        node = self.nodes.get(item_id)
        if node is None:
            return

        menu = tk.Menu(self.root, tearoff=0)

        # Directory options / Klasör seçenekleri
        if node.is_dir:
            menu.add_command(label="🔍 Aç",
                              command=lambda: self.treeview.item(item_id, open=True))
            menu.add_command(label="🔄 Bu Klasörü Yenile",
                              command=lambda: self._refresh_node(item_id))
            menu.add_separator()

        # Common options / Ortak seçenekler
        menu.add_command(label="📋 Yolu Kopyala",
                          command=lambda: self._copy_path(node.path))
        menu.add_command(label="ℹ️ Bilgileri Göster",
                          command=lambda: self._show_file_info(node.path))

        # File option / Dosya seçeneği
        if not node.is_dir:
            menu.add_command(label="📄 Dosyayı Aç",
                              command=lambda: self._open_file(node.path))

        # Show menu at cursor / Menüyü imleçte göster
        menu.tk_popup(event.x_root, event.y_root)

    def _refresh_node(self, item_id):
        """
        Refreshes a single folder node.
        Tek bir klasör düğümünü yeniler.
        """
        node = self.nodes.get(item_id)
        if node is None:
            return
        if not node.is_dir:
            return

        # Delete current children / Mevcut alt öğeleri sil
        children = self.treeview.get_children(item_id)
        for child_id in children:
            if child_id in self.nodes:
                del self.nodes[child_id]
            self.treeview.delete(child_id)

        # Reset and reload / Sıfırla ve yeniden yükle
        node.children.clear()
        node.loaded = False
        self._remove_dummy_nodes(item_id)
        self._load_children(item_id)
        self.treeview.item(item_id, open=True)
        self._show_status("'" + node.name + "' yenilendi.")

    def _copy_path(self, file_path):
        """
        Copies a path to the clipboard.
        Yolu panoya kopyalar.
        """
        self.root.clipboard_clear()
        self.root.clipboard_append(file_path)
        self.root.update()
        self._show_status("Yol panoya kopyalandı: " + file_path)

    # =========================================================================
    # File Info Window / Dosya Bilgi Penceresi
    # =========================================================================

    def _show_file_info(self, file_path):
        """
        Shows file/directory info in a new window.
        Dosya/klasör bilgisini yeni pencerede gösterir.
        """
        try:
            # Check if exists / Var mı kontrol et
            if not os.path.exists(file_path):
                messagebox.showerror("Hata", "Dosya veya klasör bulunamadı.")
                return

            # Get file size / Boyut al
            file_size = os.path.getsize(file_path)
            size_text = format_size(file_size)

            # Get file type info / Dosya türü bilgisi al
            type_text = self._get_type_info(file_path)

            # Get timestamps / Zaman damgaları al
            mod_time = os.path.getmtime(file_path)
            create_time = os.path.getctime(file_path)
            mod_text = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(mod_time))
            create_text = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(create_time))

            # Hidden status / Gizli durumu
            if is_hidden(file_path):
                hidden_text = "Evet"
            else:
                hidden_text = "Hayır"

            # Create info window / Bilgi penceresi oluştur
            info_window = tk.Toplevel(self.root)
            info_window.title("Bilgi: " + os.path.basename(file_path))
            info_window.geometry("450x300")
            info_window.resizable(False, False)

            frame = ttk.Frame(info_window, padding="10")
            frame.pack(fill="both", expand=True)

            # Add info rows / Bilgi satırları ekle
            self._add_info_row(frame, "Ad:", os.path.basename(file_path), 0)
            self._add_info_row(frame, "Tam Yol:", file_path, 1)
            self._add_info_row(frame, "Tür:", type_text, 2)
            self._add_info_row(frame, "Boyut:", size_text, 3)
            self._add_info_row(frame, "Oluşturulma Tarihi:", create_text, 4)
            self._add_info_row(frame, "Değiştirilme Tarihi:", mod_text, 5)
            self._add_info_row(frame, "Gizli mi?:", hidden_text, 6)

            # Close button / Kapat butonu
            close_btn = ttk.Button(frame, text="Kapat", command=info_window.destroy)
            close_btn.grid(row=7, column=0, columnspan=2, pady=15)

        except Exception as error:
            messagebox.showerror("Hata", "Dosya bilgileri alınamadı: " + str(error))

    def _get_type_info(self, file_path):
        """
        Returns a description string for the file/directory type.
        Dosya/klasör türü için açıklama metni döndürür.

        Args:
            file_path (str): File path. / Dosya yolu.
        Returns:
            str: Type description. / Tür açıklaması.
        """
        if os.path.isdir(file_path):
            try:
                dir_items = os.listdir(file_path)
                if not self.show_hidden.get():
                    dir_items = filter_hidden_items(dir_items, file_path)
                item_count = len(dir_items)
                return "Klasör (" + str(item_count) + " öğe)"
            except PermissionError:
                return "Klasör (İçerik okunamadı)"
            except Exception:
                return "Klasör"
        else:
            file_name, extension = os.path.splitext(file_path)
            if extension:
                return "Dosya (" + extension.upper() + ")"
            else:
                return "Dosya"

    def _add_info_row(self, parent_frame, label_text, value_text, row_number):
        """
        Adds a label-value pair to the info window.
        Bilgi penceresine etiket-değer satırı ekler.
        """
        # Label (bold, right-aligned) / Etiket (kalın, sağa yaslı)
        label = ttk.Label(parent_frame,
                           text=label_text,
                           font=("Helvetica", 10, "bold"),
                           anchor="e")
        label.grid(row=row_number, column=0, sticky="e", padx=5, pady=3)

        # Value (left-aligned) / Değer (sola yaslı)
        value = ttk.Label(parent_frame,
                           text=value_text,
                           anchor="w",
                           wraplength=300)
        value.grid(row=row_number, column=1, sticky="w", padx=5, pady=3)

    # =========================================================================
    # Expand / Collapse / Genişlet / Daralt
    # =========================================================================

    def expand_all(self):
        """
        Expands all folders (up to depth 3).
        Tüm klasörleri genişletir (maksimum derinlik 3).
        """
        self._show_status("Tüm klasörler genişletiliyor...")

        top_items = self.treeview.get_children("")
        for item_id in top_items:
            self._expand_recursive(item_id, 0, 3)

        self._show_status("Tüm klasörler genişletildi.")

    def _expand_recursive(self, item_id, current_depth, max_depth):
        """
        Recursively expands folders up to max_depth.
        Klasörleri max_depth'e kadar rekürsif genişletir.
        """
        # Stop at max depth / Maksimum derinlikte dur
        if current_depth >= max_depth:
            return

        node = self.nodes.get(item_id)

        # Only expand directories / Sadece klasörleri genişlet
        if node is None:
            return
        if not node.is_dir:
            return

        # Load if not loaded / Yüklenmemişse yükle
        if not node.loaded:
            self._remove_dummy_nodes(item_id)
            self._load_children(item_id)

        # Open this folder / Bu klasörü aç
        self.treeview.item(item_id, open=True)

        # Expand children / Alt öğeleri genişlet
        children = self.treeview.get_children(item_id)
        for child_id in children:
            child_text = self.treeview.item(child_id, "text")

            # Skip placeholders / Yer tutucuları atla
            if "Yükleniyor..." in child_text:
                continue
            if "Erişim izni yok" in child_text:
                continue
            if "Hata:" in child_text:
                continue

            self._expand_recursive(child_id, current_depth + 1, max_depth)

    def collapse_all(self):
        """
        Collapses all folders.
        Tüm klasörleri daraltır.
        """
        self._show_status("Tüm klasörler daraltılıyor...")

        top_items = self.treeview.get_children("")
        for item_id in top_items:
            self.treeview.item(item_id, open=False)

        self._show_status("Tüm klasörler daraltıldı.")

    # =========================================================================
    # About Window / Hakkında Penceresi
    # =========================================================================

    def _show_about(self):
        """
        Shows the About dialog.
        Hakkında penceresini gösterir.
        """
        about = tk.Toplevel(self.root)
        about.title("FileExplorerApp Hakkında")
        about.geometry("350x220")
        about.resizable(False, False)
        about.transient(self.root)

        frame = ttk.Frame(about, padding="15")
        frame.pack(fill="both", expand=True)

        # Title / Başlık
        title_label = ttk.Label(frame,
                                 text="FileExplorerApp",
                                 font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Version / Versiyon
        version_label = ttk.Label(frame, text="Versiyon: 1.0.0")
        version_label.pack(pady=2)

        # Developer / Geliştirici
        dev_label = ttk.Label(frame,
                               text="Geliştirici: Ali Mustafa Ekmen",
                               foreground="gray")
        dev_label.pack(pady=2)

        # Tech info / Teknoloji bilgisi
        tech_label = ttk.Label(frame,
                                text="Python ve Tkinter kullanılarak geliştirilmiştir.")
        tech_label.pack(pady=(10, 5))

        # Copyright / Telif
        copy_label = ttk.Label(frame, text="© 2024-2025", foreground="gray")
        copy_label.pack(pady=2)

        # OK button / Tamam butonu
        ok_button = ttk.Button(frame, text="Tamam", command=about.destroy)
        ok_button.pack(pady=(15, 0))

    # =========================================================================
    # Status Bar / Durum Çubuğu
    # =========================================================================

    def _show_status(self, message):
        """
        Shows a message in the status bar.
        Durum çubuğunda mesaj gösterir.
        """
        self.status_bar.config(text=message)
