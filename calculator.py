
import tkinter as tk
import math
import ast
import operator

# ==========================================
# 1. MEMBUAT JENDELA
# ==========================================

root = tk.Tk()
root.title("Scientific Calculator")
root.geometry("400x600")
root.resizable(False, False)

ekspresi = ""
layar = tk.StringVar()


# ==========================================
# 2. FUNGSI INPUT
# ==========================================

def tekan(nilai):
    global ekspresi

    ekspresi += str(nilai)
    layar.set(ekspresi)


def hapus():
    global ekspresi

    ekspresi = ""
    layar.set("")


def hapus_satu():
    global ekspresi

    ekspresi = ekspresi[:-1]
    layar.set(ekspresi)


# ==========================================
# 3. FUNGSI MATEMATIKA
# ==========================================

def sin(x):
    return math.sin(math.radians(x))


def cos(x):
    return math.cos(math.radians(x))


def tan(x):
    # Tan 90 + k*180 derajat tidak terdefinisi
    if math.isclose(
        (x - 90) % 180,
        0,
        abs_tol=1e-10
    ):
        raise ValueError("Tan tidak terdefinisi")

    return math.tan(math.radians(x))


def akar(x):
    if x < 0:
        raise ValueError("Akar negatif tidak real")

    return math.sqrt(x)


# ==========================================
# 4. PARSER EKSPRESI MATEMATIKA
# ==========================================

# Operator yang diizinkan
operator_aman = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Fungsi matematika yang diizinkan
fungsi_aman = {
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "sqrt": akar,
}


def evaluasi(node):

    # Angka
    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Input tidak valid")

        return node.value

    # Operasi matematika: +, -, *, /
    elif isinstance(node, ast.BinOp):

        tipe = type(node.op)

        if tipe not in operator_aman:
            raise ValueError("Operator tidak diizinkan")

        kiri = evaluasi(node.left)
        kanan = evaluasi(node.right)

        # Mencegah pangkat yang terlalu besar
        if tipe == ast.Pow and abs(kanan) > 1000:
            raise ValueError("Pangkat terlalu besar")

        hasil = operator_aman[tipe](kiri, kanan)

        if isinstance(hasil, complex):
            raise ValueError("Hasil bukan bilangan real")

        return hasil

    # Bilangan negatif atau positif
    elif isinstance(node, ast.UnaryOp):

        tipe = type(node.op)

        if tipe not in operator_aman:
            raise ValueError("Operator tidak diizinkan")

        return operator_aman[tipe](
            evaluasi(node.operand)
        )

    # Fungsi sin(), cos(), tan(), sqrt()
    elif isinstance(node, ast.Call):

        if not isinstance(node.func, ast.Name):
            raise ValueError("Fungsi tidak diizinkan")

        nama = node.func.id

        if nama not in fungsi_aman:
            raise ValueError("Fungsi tidak dikenal")

        if len(node.args) != 1 or node.keywords:
            raise ValueError("Gunakan satu angka")

        angka = evaluasi(node.args[0])

        return fungsi_aman[nama](angka)

    else:
        raise ValueError("Ekspresi tidak valid")


def hitung():
    global ekspresi

    try:
        # Mengubah simbol pangkat ^ menjadi **
        rumus = ekspresi.replace("^", "**")

        # Mengubah teks menjadi struktur ekspresi Python
        pohon = ast.parse(rumus, mode="eval")

        # Menghitung hanya operasi yang diizinkan
        hasil = evaluasi(pohon.body)

        layar.set(str(hasil))
        ekspresi = str(hasil)

    except ZeroDivisionError:
        layar.set("Tidak bisa dibagi 0")
        ekspresi = ""

    except Exception:
        layar.set("Error")
        ekspresi = ""


# ==========================================
# 5. LAYAR KALKULATOR
# ==========================================

entry = tk.Entry(
    root,
    textvariable=layar,
    font=("Arial", 22),
    justify="right",
    state="readonly"
)

entry.pack(
    fill="both",
    padx=10,
    pady=15,
    ipady=15
)


# ==========================================
# 6. FRAME TOMBOL
# ==========================================

frame = tk.Frame(root)
frame.pack(
    expand=True,
    fill="both",
    padx=10,
    pady=5
)


# ==========================================
# 7. DAFTAR TOMBOL
# ==========================================

tombol = [
    ("sin", 0, 0), ("cos", 0, 1),
    ("tan", 0, 2), ("C", 0, 3),

    ("(", 1, 0), (")", 1, 1),
    ("^", 1, 2), ("DEL", 1, 3),

    ("sqrt(", 2, 0), ("/", 2, 1),
    ("*", 2, 2), ("-", 2, 3),

    ("7", 3, 0), ("8", 3, 1),
    ("9", 3, 2), ("+", 3, 3),

    ("4", 4, 0), ("5", 4, 1),
    ("6", 4, 2), (".", 4, 3),

    ("1", 5, 0), ("2", 5, 1),
    ("3", 5, 2), ("0", 5, 3),

    ("=", 6, 0)
]


# ==========================================
# 8. MEMBUAT TOMBOL
# ==========================================

for teks, baris, kolom in tombol:

    if teks == "C":
        perintah = hapus

    elif teks == "DEL":
        perintah = hapus_satu

    elif teks == "=":
        perintah = hitung

    elif teks in ("sin", "cos", "tan"):
        perintah = lambda t=teks: tekan(t + "(")

    else:
        perintah = lambda t=teks: tekan(t)

    btn = tk.Button(
        frame,
        text=teks,
        font=("Arial", 14),
        command=perintah
    )

    if teks == "=":
        btn.config(bg="lightblue")

        btn.grid(
            row=6,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=3,
            pady=3
        )

    else:
        btn.grid(
            row=baris,
            column=kolom,
            sticky="nsew",
            padx=3,
            pady=3
        )


# ==========================================
# 9. MENGATUR UKURAN TOMBOL
# ==========================================

for i in range(7):
    frame.rowconfigure(i, weight=1)

for i in range(4):
    frame.columnconfigure(i, weight=1)


# ==========================================
# 10. MENJALANKAN APLIKASI
# ==========================================

root.mainloop()