# =====================================================
# Import library yang dibutuhkan
# =====================================================
import pandas as pd                  # Untuk manipulasi data tabular
import numpy as np                   # Untuk operasi numerik dan array
import matplotlib.pyplot as plt      # Untuk visualisasi grafik
import os                            # Untuk membuat folder output


# =====================================================
# Membaca dan menyiapkan data
# =====================================================
df = pd.read_csv("H:\Kuliah\Matrfor\Clustering\Data.csv")  # Membaca file CSV hasil kuesioner

df.columns = [                       # Mengganti nama kolom agar lebih mudah digunakan
    "timestamp",
    "email",
    "nama",
    "angkatan",
    "transportasi",
    "konsumsi",
    "hiburan",
    "komunikasi"
]

df_asli = df.copy()                  # Menyimpan salinan data asli sebelum dimodifikasi


# =====================================================
# Fungsi konversi kategori pengeluaran → angka (1–5)
# =====================================================
def konversi_pengeluaran(nilai):
    nilai = str(nilai).replace("&lt;", "<").replace("—", "–").strip()  # Bersihkan karakter anomali dari import

    mapping = {                      # Peta kategori ke nilai numerik
        "< Rp10.000":           1,   # Sangat Irit
        "Rp10.000 – Rp20.000":  2,   # Irit
        "Rp21.000 – Rp35.000":  3,   # Sedang
        "Rp36.000 – Rp50.000":  4,   # Boros
        "> Rp50.000":           5    # Sangat Boros
    }
    return mapping.get(nilai, 0)     # Kembalikan 0 jika kategori tidak dikenali


# Terapkan konversi ke semua kolom pengeluaran
fitur = ["transportasi", "konsumsi", "hiburan", "komunikasi"]
for k in fitur:
    df[k] = df[k].apply(konversi_pengeluaran)


# =====================================================
# Fungsi interpretasi nilai centroid → label teks
# =====================================================
def interpretasi(nilai):
    if   nilai < 1.5: return "Sangat Irit"
    elif nilai < 2.5: return "Irit"
    elif nilai < 3.5: return "Sedang"
    elif nilai < 4.5: return "Boros"
    else:             return "Sangat Boros"


# =====================================================
# Fungsi menghitung jarak Euclidean antar dua titik
# =====================================================
def euclidean(data, centroid):
    return np.sqrt(np.sum((np.array(data) - np.array(centroid)) ** 2))


# =====================================================
# Fungsi menghitung centroid baru dari rata-rata anggota cluster
# =====================================================
def hitung_centroid(df, fitur):
    centroid_baru = []
    for i in range(1, 6):
        cluster_i = df[df["cluster"] == i]          # Ambil anggota cluster ke-i
        if len(cluster_i) == 0:
            centroid_baru.append(centroids[i - 1])  # Pertahankan centroid lama jika cluster kosong
        else:
            centroid_baru.append(cluster_i[fitur].mean().tolist())  # Rata-rata semua fitur
    return centroid_baru


# =====================================================
# Fungsi menghitung Silhouette Score per data dan per cluster
# =====================================================
def hitung_silhouette(df, fitur):
    X      = df[fitur].values
    labels = df["cluster"].values
    silhouette_values = []

    for i in range(len(X)):
        c_now = labels[i]

        # a(i): rata-rata jarak ke sesama anggota cluster
        a = np.mean([
            euclidean(X[i], X[j])
            for j in range(len(X))
            if i != j and labels[j] == c_now
        ]) if np.sum(labels == c_now) > 1 else 0

        # b(i): rata-rata jarak minimum ke cluster tetangga terdekat
        b = min(
            np.mean([euclidean(X[i], X[j]) for j in range(len(X)) if labels[j] == c_lain])
            for c_lain in np.unique(labels) if c_lain != c_now
        )

        s = 0 if max(a, b) == 0 else (b - a) / max(a, b)  # Silhouette tiap titik
        silhouette_values.append(s)

    df["silhouette"] = silhouette_values
    return (
        np.mean(silhouette_values),                                         # Skor global
        df.groupby("cluster")["silhouette"].mean().round(4).to_dict()      # Skor per cluster
    )


# =====================================================
# Fungsi menyimpan diagram batang distribusi cluster
# =====================================================
def simpan_diagram_iterasi(df, iterasi, folder_output):
    jumlah_iter = df["cluster"].value_counts().sort_index()
    warna       = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

    plt.figure(figsize=(7, 5))
    bars = plt.bar(
        [f"C{c}" for c in jumlah_iter.index],  # Label sumbu X
        jumlah_iter.values,
        color=warna[:len(jumlah_iter)]          # Warna sesuai jumlah cluster aktif
    )

    # Tampilkan angka jumlah mahasiswa di atas tiap batang
    for bar in bars:
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # Posisi X tengah batang
            bar.get_height() + 0.2,              # Posisi Y sedikit di atas batang
            str(int(bar.get_height())),
            ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    plt.title(f"Distribusi Cluster — Iterasi ke-{iterasi}", fontsize=13, fontweight="bold")
    plt.xlabel("Cluster")
    plt.ylabel("Jumlah Mahasiswa")
    plt.ylim(0, max(jumlah_iter.values) + 3)    # Beri ruang di atas batang tertinggi
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()

    # Simpan sebagai file PNG dengan nama sesuai nomor iterasi
    nama_file_gambar = os.path.join(folder_output, f"iterasi_{iterasi:02d}.png")
    plt.savefig(nama_file_gambar, dpi=150)
    plt.close()                                  # Tutup figure agar tidak menumpuk di memori
    print(f"  → Diagram disimpan: {nama_file_gambar}")


# =====================================================
# Centroid awal untuk 5 cluster (ditentukan manual)
# =====================================================
centroids = [
    [1, 3, 5, 5],  # C1
    [1, 2, 5, 4],  # C2
    [2, 3, 3, 3],  # C3
    [1, 2, 1, 1],  # C4
    [2, 2, 5, 3]   # C5
]


# =====================================================
# Buat folder untuk menyimpan diagram iterasi
# =====================================================
folder_diagram = r"H:\Kuliah\Matrfor\Clustering\diagram_iterasi"
os.makedirs(folder_diagram, exist_ok=True)       # Buat folder jika belum ada


# =====================================================
# Proses utama K-Means: iterasi assignment + update centroid
# =====================================================
maks_iterasi     = 100  # Batas maksimum iterasi
riwayat_centroid = []   # Untuk menyimpan riwayat centroid tiap iterasi

for iterasi in range(maks_iterasi):
    print(f"\nIterasi ke-{iterasi + 1}")

    # Assignment: tentukan cluster terdekat untuk setiap data
    cluster_hasil = []
    for _, row in df[fitur].iterrows():
        data  = row.tolist()
        jarak = [euclidean(data, c) for c in centroids]   # Hitung jarak ke semua centroid
        cluster_hasil.append(jarak.index(min(jarak)) + 1) # Pilih cluster dengan jarak terkecil

    df["cluster"] = cluster_hasil  # Simpan hasil assignment ke dataframe

    # Hitung silhouette pada iterasi saat ini (global dan per cluster)
    silhouette_iterasi, silhouette_per_cluster_iter = hitung_silhouette(df.copy(), fitur)

    # Hitung centroid baru
    centroid_baru = hitung_centroid(df, fitur)

    print("Centroid:")
    print(np.array(centroid_baru))
    print(f"Silhouette Score: {silhouette_iterasi:.4f}")

    # Hitung jumlah mahasiswa per cluster pada iterasi ini
    jumlah_per_cluster_iter = df["cluster"].value_counts().to_dict()

    # Simpan riwayat centroid iterasi ini
    for i, c in enumerate(centroids):
        riwayat_centroid.append({
            "Iterasi":          iterasi + 1,
            "Cluster":          f"C{i+1}",
            "Jumlah Mahasiswa": jumlah_per_cluster_iter.get(i + 1, 0),
            "Transportasi":     round(c[0], 2),
            "Konsumsi":         round(c[1], 2),
            "Hiburan":          round(c[2], 2),
            "Komunikasi":       round(c[3], 2),
            "Silhouette":       silhouette_per_cluster_iter.get(i + 1, 0)
        })

    # Simpan diagram batang iterasi ini sebagai file gambar
    simpan_diagram_iterasi(df, iterasi + 1, folder_diagram)

    # Cek konvergensi: hentikan jika centroid tidak berubah signifikan
    if np.allclose(centroids, centroid_baru):
        print("\nCentroid konvergen"); break

    centroids = centroid_baru  # Update centroid untuk iterasi berikutnya


# =====================================================
# Hitung jarak akhir setiap data ke seluruh centroid
# =====================================================
for i, c in enumerate(centroids):
    df[f"Jarak_C{i+1}"] = df[fitur].apply(lambda row: euclidean(row.tolist(), c), axis=1)

df_jarak = df[["nama", "cluster", "Jarak_C1", "Jarak_C2", "Jarak_C3", "Jarak_C4", "Jarak_C5"]]

# Hitung Silhouette Score keseluruhan dan per cluster
silhouette_score, silhouette_cluster = hitung_silhouette(df, fitur)


# =====================================================
# Menyusun DataFrame output untuk ekspor ke Excel
# =====================================================
df_centroid = pd.DataFrame(riwayat_centroid)  # Riwayat centroid tiap iterasi

jumlah_cluster = df["cluster"].value_counts().sort_index()  # Jumlah anggota per cluster

# Ringkasan interpretasi tiap cluster
ringkasan = [
    {
        "Cluster":          f"C{i+1}",
        "Jumlah Mahasiswa": jumlah_cluster.get(i + 1, 0),
        "Silhouette":       silhouette_cluster.get(i + 1, 0),
        "Transportasi":     interpretasi(c[0]),
        "Konsumsi":         interpretasi(c[1]),
        "Hiburan":          interpretasi(c[2]),
        "Komunikasi":       interpretasi(c[3])
    }
    for i, c in enumerate(centroids)
]

# Tambahkan baris total di akhir ringkasan
ringkasan.append({
    "Cluster": "TOTAL", "Jumlah Mahasiswa": len(df),
    "Silhouette": round(silhouette_score, 4),
    "Transportasi": "-", "Konsumsi": "-", "Hiburan": "-", "Komunikasi": "-"
})

df_ringkasan = pd.DataFrame(ringkasan)
df_cluster   = df[["nama", "cluster"]]


# =====================================================
# Ekspor semua hasil ke file Excel (multi-sheet)
# =====================================================
nama_file = r"H:\Kuliah\Matrfor\Clustering\hasil_clustering.xlsx"

with pd.ExcelWriter(nama_file, engine="openpyxl") as writer:

    # Sheet 1: Data asli dari kuesioner (belum dikonversi)
    df_asli[["nama", "transportasi", "konsumsi", "hiburan", "komunikasi"]].to_excel(
        writer, sheet_name="Data Asli", index=False)

    # Sheet 2: Data setelah konversi kategori ke angka
    df.drop(columns=["timestamp", "email", "angkatan",
                      "Jarak_C1", "Jarak_C2", "Jarak_C3", "Jarak_C4", "Jarak_C5", "cluster", "silhouette"]
            ).to_excel(writer, sheet_name="Hasil Konversi", index=False)

    # Sheet 3: Jarak Euclidean tiap data ke semua centroid akhir
    df_jarak[["nama", "Jarak_C1", "Jarak_C2", "Jarak_C3", "Jarak_C4", "Jarak_C5"]].to_excel(
        writer, sheet_name="Jarak Euclidean", index=False)

    # Sheet 4: Riwayat perubahan centroid setiap iterasi
    df_centroid.to_excel(writer, sheet_name="Hasil Iterasi", index=False)

    # Sheet 5: Hasil penugasan cluster tiap mahasiswa
    df_cluster.to_excel(writer, sheet_name="Hasil Cluster", index=False)

    # Sheet 6: Interpretasi dan statistik ringkasan per cluster
    df_ringkasan.to_excel(writer, sheet_name="Interpretasi", index=False)


# =====================================================
# Visualisasi akhir: diagram batang jumlah anggota per cluster
# =====================================================
plt.figure(figsize=(7, 5))
plt.bar(jumlah_cluster.index, jumlah_cluster.values,
        color=["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"])
plt.title("Jumlah Anggota Setiap Cluster (Hasil Akhir)", fontsize=13, fontweight="bold")
plt.xlabel("Cluster")
plt.ylabel("Jumlah Mahasiswa")
plt.xticks(jumlah_cluster.index)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()

# Simpan diagram akhir
nama_diagram_akhir = r"H:\Kuliah\Matrfor\Clustering\diagram_akhir.png"
plt.savefig(nama_diagram_akhir, dpi=150)
plt.show()


# =====================================================
# Output informasi akhir ke konsol
# =====================================================
print(f"\nFile Excel berhasil disimpan : {nama_file}")
print(f"Diagram iterasi disimpan di  : {folder_diagram}")
print(f"Diagram akhir disimpan di    : {nama_diagram_akhir}")
print("\nCentroid akhir:")
print(np.array(centroids))