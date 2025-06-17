import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'dipa4527c5' 

# --- KELAS NODE ---
class Node:
    def __init__(self, nim, nama, jurusan):
        self.nim = nim
        self.nama = nama
        self.jurusan = jurusan
        self.left = None
        self.right = None
        self.height = 0 

    # --- Metode Pembantu untuk AVL ---
    @staticmethod
    def _get_height(node):
        """
        Mengembalikan tinggi node, atau -1 jika node None (representasi daun atau subtree kosong).
        Ini dipanggil dengan Node._get_height(some_node)
        """
        return node.height if node else -1

    @staticmethod
    def _get_balance(node):
        """
        Menghitung faktor keseimbangan node, atau 0 jika node None.
        Ini dipanggil dengan Node._get_balance(some_node)
        """
        return Node._get_height(node.left) - Node._get_height(node.right) if node else 0

    def update_height(self):
        """
        Memperbarui tinggi node berdasarkan tinggi anak-anaknya.
        Menggunakan _get_height untuk menangani anak None dengan aman.
        """
        self.height = 1 + max(Node._get_height(self.left), Node._get_height(self.right))

    # --- Metode Rotasi ---
    def rotate_right(self):
        new_root = self.left
        self.left = new_root.right
        new_root.right = self
        
        # Penting: Perbarui tinggi node lama (self) terlebih dahulu, baru root baru
        self.update_height()
        new_root.update_height()
        return new_root

    def rotate_left(self):
        new_root = self.right
        self.right = new_root.left
        new_root.left = self

        # Penting: Perbarui tinggi node lama (self) terlebih dahulu, baru root baru
        self.update_height()
        new_root.update_height()
        return new_root

    # --- Implementasi insert AVL ---
    def insert(self, new_nim, new_nama, new_jurusan):
        if new_nim < self.nim:
            if self.left is None:
                self.left = Node(new_nim, new_nama, new_jurusan)
            else:
                self.left = self.left.insert(new_nim, new_nama, new_jurusan)
        elif new_nim > self.nim:
            if self.right is None:
                self.right = Node(new_nim, new_nama, new_jurusan)
            else:
                self.right = self.right.insert(new_nim, new_nama, new_jurusan)
        else: # NIM sudah ada
            return self

        self.update_height() # Perbarui tinggi node saat kembali dari rekursi
        
        balance = Node._get_balance(self) # Gunakan static method untuk mendapatkan balance

        # Lakukan rotasi jika terjadi imbalance (4 kasus)
        # Kasus Kiri-Kiri
        if balance > 1 and new_nim < self.left.nim:
            return self.rotate_right()

        # Kasus Kiri-Kanan
        if balance > 1 and new_nim > self.left.nim: # Perbaiki kondisi new_nim > self.left.nim
            self.left = self.left.rotate_left()
            return self.rotate_right()

        # Kasus Kanan-Kanan
        if balance < -1 and new_nim > self.right.nim:
            return self.rotate_left()

        # Kasus Kanan-Kiri
        if balance < -1 and new_nim < self.right.nim: # Perbaiki kondisi new_nim < self.right.nim
            self.right = self.right.rotate_right()
            return self.rotate_left()

        return self

    # --- Metode Pencarian dan Traversal ---
    def search(self, target_nim):
        if self.nim == target_nim:
            return self 
        
        if self.left and self.nim > target_nim:
            return self.left.search(target_nim)

        if self.right and self.nim < target_nim:
            return self.right.search(target_nim)

        return None 

    def traverseInorderCollect(self, mahasiswa_list):
        if self.left:
            self.left.traverseInorderCollect(mahasiswa_list)
        
        mahasiswa_list.append({'nim': self.nim, 'nama': self.nama, 'jurusan': self.jurusan})

        if self.right:
            self.right.traverseInorderCollect(mahasiswa_list)
        return mahasiswa_list

    def findMinNode(self):
        current = self
        while current.left is not None:
            current = current.left
        return current 

    # --- Implementasi delNode AVL ---
    def delNode(self, target_nim):
        # 1. Lakukan penghapusan standar BST secara rekursif
        if target_nim < self.nim:
            if self.left:
                self.left = self.left.delNode(target_nim)
        elif target_nim > self.nim:
            if self.right:
                self.right = self.right.delNode(target_nim)
        else: # self.nim == target_nim, node ini akan dihapus
            if self.left is None and self.right is None: # Node daun
                return None # Node ini dihapus, kembalikan None ke parent
            elif self.left is None: # Hanya punya anak kanan
                return self.right
            elif self.right is None: # Hanya punya anak kiri
                return self.left
            else: # Punya dua anak
                min_node_obj = self.right.findMinNode() # Cari successor
                self.nim = min_node_obj.nim
                self.nama = min_node_obj.nama
                self.jurusan = min_node_obj.jurusan
                # Hapus successor dari subtree kanan
                self.right = self.right.delNode(min_node_obj.nim)
        
        
        # 2. Perbarui tinggi node saat kembali dari rekursi
        self.update_height()

        # 3. Dapatkan faktor keseimbangan node saat ini
        balance = Node._get_balance(self) # Gunakan static method untuk mendapatkan balance

        # 4. Lakukan Rotasi jika ada imbalance setelah penghapusan (4 kasus)
        # Penting: Gunakan Node._get_balance(self.left/right) untuk menghindari NoneType error
        
        # Kasus Kiri-Kiri
        if balance > 1 and Node._get_balance(self.left) >= 0: 
            return self.rotate_right()

        # Kasus Kiri-Kanan
        if balance > 1 and Node._get_balance(self.left) < 0:
            self.left = self.left.rotate_left()
            return self.rotate_right()

        # Kasus Kanan-Kanan
        if balance < -1 and Node._get_balance(self.right) <= 0:
            return self.rotate_left()

        # Kasus Kanan-Kiri
        if balance < -1 and Node._get_balance(self.right) > 0:
            self.right = self.right.rotate_right()
            return self.rotate_left()

        return self

    def update_mahasiswa(self, target_nim, new_nama=None, new_jurusan=None):
        if self.nim == target_nim:
            updated = False
            if new_nama is not None and new_nama.strip() != "":
                self.nama = new_nama
                updated = True
            if new_jurusan is not None and new_jurusan.strip() != "":
                self.jurusan = new_jurusan
                updated = True
            return updated 
        
        if self.left and self.nim > target_nim:
            return self.left.update_mahasiswa(target_nim, new_nama, new_jurusan)

        if self.right and self.nim < target_nim:
            return self.right.update_mahasiswa(target_nim, new_nama, new_jurusan)

        return False

    def get_node_html(self):
        """Mengembalikan representasi HTML rekursif dari node dan anak-anaknya."""
        html = f'<li><span class="node-data">NIM: {self.nim}, Nama: {self.nama}, H:{self.height}, B:{Node._get_balance(self)}</span>'
        children_html = []
        
        if self.left:
            children_html.append(self.left.get_node_html())
        else:
            children_html.append('<li class="empty-node">_</li>') # Representasi node kosong
        
        if self.right:
            children_html.append(self.right.get_node_html())
        else:
            children_html.append('<li class="empty-node">_</li>') # Representasi node kosong
        
        html += '<ul>' + ''.join(children_html) + '</ul>'
        html += '</li>'
        return html


# --- KELAS TREE ---
class Tree:
    def __init__(self, root_nim=None, root_nama=None, root_jurusan=None, name=''):
        if root_nim is not None:
            self.root = Node(root_nim, root_nama, root_jurusan)
        else:
            self.root = None
        self.name = name

    def insert(self, nim, nama, jurusan):
        # Cek duplikasi sebelum mencoba insert
        if self.search(nim):
            return False

        if self.root is None:
            self.root = Node(nim, nama, jurusan)
        else:
            self.root = self.root.insert(nim, nama, jurusan)
        return True

    def search(self, target_nim):
        if self.root is None:
            return None
        return self.root.search(target_nim)

    def getAllMahasiswa(self):
        mahasiswa_list = []
        if self.root:
            self.root.traverseInorderCollect(mahasiswa_list)
        return mahasiswa_list
    
    def delNode(self, target_nim):
        if self.root is None:
            return False, "Tree kosong. Tidak ada mahasiswa untuk dihapus."
        
        initial_search_result = self.search(target_nim)
        if initial_search_result is None:
            return False, f"Mahasiswa dengan NIM {target_nim} tidak ditemukan."

        # Panggil delNode AVL dari root
        self.root = self.root.delNode(target_nim)
        
        # Setelah penghapusan, cek lagi apakah node masih ada
        if self.search(target_nim) is None: 
            return True, f"Mahasiswa dengan NIM {target_nim} berhasil dihapus."
        else:
            return False, f"Mahasiswa dengan NIM {target_nim} gagal dihapus (mungkin masalah internal atau kondisi kompleks)."
            

    def update_mahasiswa(self, target_nim, new_nama=None, new_jurusan=None):
        if self.root is None:
            return False

        return self.root.update_mahasiswa(target_nim, new_nama, new_jurusan)

    def getTreeHtml(self):
        if self.root is None:
            return "<p>Tree kosong. Tidak ada struktur untuk ditampilkan.</p>"
        
        return f'<ul class="tree-view">{self.root.get_node_html()}</ul>'

    def save_data(self, filename="mahasiswa_data.json"):
        data_to_save = self.getAllMahasiswa() 
        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"Data mahasiswa berhasil disimpan ke {filename}")
            return True
        except Exception as e:
            print(f"Gagal menyimpan data: {e}")
            return False

    def load_data(self, filename="mahasiswa_data.json"):
        if not os.path.exists(filename):
            print(f"File data '{filename}' tidak ditemukan. Memulai dengan tree kosong.")
            return False
        
        try:
            with open(filename, 'r') as f:
                loaded_data = json.load(f)
            
            self.root = None 
            for mhs_dict in loaded_data:
                self.insert(mhs_dict['nim'], mhs_dict['nama'], mhs_dict['jurusan'])
            print(f"Data mahasiswa berhasil dimuat dari {filename}")
            return True
        except Exception as e:
            print(f"Gagal memuat data: {e}. File mungkin korup atau formatnya salah.")
            return False


# Inisialisasi tree dan muat data
my_mahasiswa_tree = Tree(name='Sistem Manajemen Mahasiswa')
my_mahasiswa_tree.load_data()

# cumqk data dummy klo tree nya ksong
if not my_mahasiswa_tree.getAllMahasiswa(): 
    print("Menambahkan data dummy karena file data kosong atau tidak ditemukan.")
    my_mahasiswa_tree.insert(101, "Budi Santoso", "Teknik Informatika")
    my_mahasiswa_tree.insert(55, "Ani Wijaya", "Sistem Informasi")
    my_mahasiswa_tree.insert(120, "Citra Lestari", "Ilmu Komunikasi")
    my_mahasiswa_tree.insert(70, "Dewi Purnama", "Desain Grafis")
    my_mahasiswa_tree.insert(30, "Eka Putri", "Akuntansi")
    my_mahasiswa_tree.insert(10, "Fajar Alam", "Manajemen")
    my_mahasiswa_tree.insert(5, "Gita Kirana", "Sastra Inggris")
    my_mahasiswa_tree.insert(1, "Hari Subagio", "Kedokteran")
    my_mahasiswa_tree.save_data()


# --- ROUTES FLASK  ---
@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'nim')
    sort_order = request.args.get('sort_order', 'asc')

    mahasiswa_list = my_mahasiswa_tree.getAllMahasiswa()

    if mahasiswa_list:
        if sort_by == 'nim':
            mahasiswa_list.sort(key=lambda mhs: mhs['nim'], reverse=(sort_order == 'desc'))
        elif sort_by == 'nama':
            mahasiswa_list.sort(key=lambda mhs: mhs['nama'].lower(), reverse=(sort_order == 'desc'))
        elif sort_by == 'jurusan':
            mahasiswa_list.sort(key=lambda mhs: mhs['jurusan'].lower(), reverse=(sort_order == 'desc'))

    tree_html = my_mahasiswa_tree.getTreeHtml() 

    return render_template('index.html', 
                           mahasiswa_list=mahasiswa_list, 
                           tree_html=tree_html,
                           current_sort_by=sort_by,
                           current_sort_order=sort_order)

@app.route('/add', methods=['POST'])
def add_mahasiswa():
    try:
        nim = int(request.form['nim'])
        nama = request.form['nama'].strip()
        jurusan = request.form['jurusan'].strip()

        if nim <= 0:
            flash("NIM harus angka positif.", "error")
        elif not nama:
            flash("Nama tidak boleh kosong.", "error")
        elif not jurusan:
            flash("Jurusan tidak boleh kosong.", "error")
        else:
            if my_mahasiswa_tree.insert(nim, nama, jurusan):
                flash(f"Mahasiswa {nama} (NIM: {nim}) berhasil ditambahkan.", "success")
                my_mahasiswa_tree.save_data()
            else:
                flash(f"Error: Mahasiswa dengan NIM {nim} sudah ada.", "error")
    except ValueError:
        flash("NIM harus berupa angka.", "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('index'))

@app.route('/edit/<int:nim>')
def edit_mahasiswa_form(nim):
    mahasiswa = my_mahasiswa_tree.search(nim)
    if mahasiswa:
        return render_template('edit.html', mahasiswa=mahasiswa)
    else:
        flash(f"Mahasiswa dengan NIM {nim} tidak ditemukan.", "error")
        return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update_mahasiswa_data():
    try:
        nim = int(request.form['nim'])
        new_nama = request.form['nama'].strip()
        new_jurusan = request.form['jurusan'].strip()

        if not new_nama:
            new_nama = None # klo nama kosong, anggap aja gk ada perubahan nama
        if not new_jurusan:
            new_jurusan = None # klo jurusan kosong, anggap aja gk ada perubahan jurusan

        if my_mahasiswa_tree.update_mahasiswa(nim, new_nama, new_jurusan):
            flash(f"Data mahasiswa NIM {nim} berhasil diperbarui.", "success")
            my_mahasiswa_tree.save_data()
        else:
            flash(f"Mahasiswa dengan NIM {nim} tidak ditemukan atau tidak ada perubahan data.", "error")
    except ValueError:
        flash("NIM harus berupa angka.", "error")
    except Exception as e:
        flash(f"Terjadi kesalahan saat update: {e}", "error")
    return redirect(url_for('index'))


@app.route('/delete/<int:nim>')
def delete_mahasiswa(nim):
    success, message = my_mahasiswa_tree.delNode(nim)
    if success:
        flash(message, "success")
        my_mahasiswa_tree.save_data()
    else:
        flash(message, "error")
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search_mahasiswa():
    query_nim_str = request.args.get('nim')
    if not query_nim_str:
        flash("Mohon masukkan NIM untuk pencarian.", "error")
        return redirect(url_for('index'))
    
    try:
        query_nim = int(query_nim_str)
        mahasiswa = my_mahasiswa_tree.search(query_nim)
        if mahasiswa:
            flash(f"Ditemukan: NIM {mahasiswa.nim}, Nama {mahasiswa.nama}, Jurusan {mahasiswa.jurusan}", "info")
        else:
            flash(f"Mahasiswa dengan NIM {query_nim} tidak ditemukan.", "warning")
    except ValueError:
        flash("NIM harus berupa angka.", "error")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)