# =============================================================================
# tree_node.py - Tree Node Module / Ağaç Düğümü Modülü
# =============================================================================
# This module defines the TreeNode class which represents a single
# file or directory in the file system tree.
#
# Bu modül, dosya sistemi ağacında tek bir dosya veya klasörü temsil
# eden TreeNode sınıfını tanımlar.
# =============================================================================


class TreeNode:
    """
    Represents a file or directory in the tree.
    Ağaçtaki bir dosya veya klasörü temsil eder.
    """

    def __init__(self, name, path, is_dir):
        """
        Creates a new TreeNode.
        Yeni bir TreeNode oluşturur.

        Args:
            name (str): File/directory name. / Dosya/klasör adı.
            path (str): Full path. / Tam yol.
            is_dir (bool): True = directory, False = file. / True = klasör, False = dosya.
        """
        self.name = name        # Name / Ad
        self.path = path        # Full path / Tam yol
        self.is_dir = is_dir    # Is directory? / Klasör mü?
        self.children = []      # Child nodes / Alt düğümler
        self.loaded = False     # Children loaded? / Alt düğümler yüklendi mi?

    def add_child(self, child_node):
        """
        Adds a child node.
        Alt düğüm ekler.
        """
        self.children.append(child_node)

    def sort_children(self):
        """
        Sorts children: directories first, then files. Alphabetical in each group.
        Alt düğümleri sıralar: önce klasörler, sonra dosyalar. Her grup alfabetik.
        """
        # We use a helper function instead of a lambda for clarity
        # Anlaşılırlık için lambda yerine yardımcı fonksiyon kullanıyoruz
        def sort_key(node):
            # Directories come first (False < True, so "not is_dir" puts dirs first)
            # Klasörler önce gelir (False < True, "not is_dir" klasörleri öne alır)
            is_file = not node.is_dir
            lowercase_name = node.name.lower()
            return (is_file, lowercase_name)

        self.children.sort(key=sort_key)
