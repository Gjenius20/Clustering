

# Import library yang dibutuhkan
import pandas as pd
import numpy as np

# Membaca file CSV yang berisi data responden
df = pd.read_csv("H:\Kuliah\Matrfor\Clustering\Data.csv")

# Menampilkan nama kolom asli dari file CSV
print(df.columns)

# Mengganti nama kolom agar lebih mudah digunakan
df.columns = [
    "timestamp",
    "email",
    "nama",
    "angkatan",
    "transportasi",
    "konsumsi",
    "hiburan",
    "komunikasi"
]

# Mengambil hanya kolom pengeluaran yang akan digunakan
# sebagai fitur clustering
data_pengeluaran = df[
    ["transportasi", "konsumsi", "hiburan", "komunikasi"]
]

# Menampilkan 5 data pertama
print(data_pengeluaran.head())


# =====================================================
# Fungsi untuk mengubah kategori pengeluaran menjadi angka
# =====================================================
def konversi_pengeluaran(nilai):

    # Mengubah nilai menjadi string
    nilai = str(nilai)

    # Membersihkan karakter yang mungkin berubah saat import data
    nilai = nilai.replace("&lt;", "<")
    nilai = nilai.replace("—", "–")
    nilai = nilai.strip()

    # Mapping kategori pengeluaran ke angka
    mapping = {
        "< Rp10.000": 1,
        "Rp10.000 – Rp20.000": 2,
        "Rp21.000 – Rp35.000": 3,
        "Rp36.000 – Rp50.000": 4,
        "> Rp50.000": 5
    }

    # Jika tidak ditemukan, kembalikan 0
    return mapping.get(nilai, 0)


# Daftar kolom yang akan dikonversi
kolom = [
    "transportasi",
    "konsumsi",
    "hiburan",
    "komunikasi"
]

# Mengubah seluruh data kategori menjadi numerik
for k in kolom:
    df[k] = df[k].apply(konversi_pengeluaran)


# =====================================================
# Menentukan centroid awal untuk 5 cluster
# =====================================================
centroids = [
    [1, 1, 1, 1],
    [2, 2, 2, 2],
    [3, 3, 3, 3],
    [4, 4, 4, 4],
    [5, 5, 5, 5]
]


# =====================================================
# Fungsi menghitung jarak Euclidean
# =====================================================
def euclidean(data, centroid):

    return np.sqrt(
        np.sum(
            (np.array(data) - np.array(centroid)) ** 2
        )
    )


# Fitur yang digunakan dalam clustering
fitur = [
    "transportasi",
    "konsumsi",
    "hiburan",
    "komunikasi"
]

# Menyimpan riwayat perubahan centroid setiap iterasi
riwayat_centroid = []


# =====================================================
# Fungsi interpretasi nilai centroid
# =====================================================
def interpretasi(nilai):

    if nilai < 1.5:
        return "Sangat Irit"

    elif nilai < 2.5:
        return "Irit"

    elif nilai < 3.5:
        return "Sedang"

    elif nilai < 4.5:
        return "Boros"

    else:
        return "Sangat Boros"


# Keterangan skala:
# 1 = Sangat Irit
# 2 = Irit
# 3 = Sedang
# 4 = Boros
# 5 = Sangat Boros


# =====================================================
# Fungsi menghitung centroid baru
# =====================================================
def hitung_centroid(df, fitur):

    centroid_baru = []

    # Perulangan untuk setiap cluster
    for i in range(1, 6):

        # Mengambil anggota cluster ke-i
        cluster_i = df[df["cluster"] == i]

        # Jika cluster kosong
        if len(cluster_i) == 0:

            # Gunakan centroid lama
            centroid_baru.append(
                centroids[i - 1]
            )

        else:

            # Hitung rata-rata setiap fitur
            mean = cluster_i[fitur].mean()

            centroid_baru.append(
                mean.tolist()
            )

    return centroid_baru


# =====================================================
# Proses utama algoritma K-Means
# =====================================================

# Maksimum iterasi
maks_iterasi = 100

# Perulangan iterasi K-Means
for iterasi in range(maks_iterasi):

    print(f"\nIterasi ke-{iterasi+1}")

    # Menyimpan hasil cluster setiap data
    cluster_hasil = []

    # Loop setiap baris data
    for _, row in df[fitur].iterrows():

        # Mengubah baris menjadi list
        data = row.tolist()

        # Menyimpan jarak ke semua centroid
        jarak = []

        # Menghitung jarak ke setiap centroid
        for c in centroids:

            d = euclidean(data, c)

            jarak.append(d)

        # Menentukan cluster dengan jarak minimum
        cluster = jarak.index(
            min(jarak)
        ) + 1

        cluster_hasil.append(
            cluster
        )

    # Menyimpan hasil cluster ke dataframe
    df["cluster"] = cluster_hasil

    # Menghitung centroid baru
    centroid_baru = hitung_centroid(
        df,
        fitur
    )

    # Menampilkan centroid hasil iterasi
    print("Centroid:")
    print(np.array(centroid_baru))

    # Menyimpan riwayat centroid
    for i, c in enumerate(centroid_baru):

        riwayat_centroid.append({

            "Iterasi": iterasi + 1,

            "Cluster": f"C{i+1}",

            "Transportasi":
            round(c[0], 2),

            "Konsumsi":
            round(c[1], 2),

            "Hiburan":
            round(c[2], 2),

            "Komunikasi":
            round(c[3], 2),
        })

    # Mengecek apakah centroid sudah minim eror
    if np.allclose(
        centroids,
        centroid_baru
    ):

        print(
            "\nCentroid konvergen"
        )

        break

    # Update centroid untuk iterasi berikutnya
    centroids = centroid_baru


# =====================================================
# Menghitung jarak akhir setiap data ke seluruh centroid
# =====================================================
for i, c in enumerate(centroids):

    nama_kolom = f"Jarak_C{i+1}"

    df[nama_kolom] = df[fitur].apply(
        lambda row:
        euclidean(
            row.tolist(),
            c
        ),
        axis=1
    )
    
df_jarak = df[
    [
        "nama",
        "cluster",
        "Jarak_C1",
        "Jarak_C2",
        "Jarak_C3",
        "Jarak_C4",
        "Jarak_C5"
    ]
]


# Lokasi file output Excel
nama_file = "H:\Kuliah\Matrfor\Clustering\hasil_clustering.xlsx"


# =====================================================
# Membuat DataFrame riwayat centroid
# =====================================================
df_centroid = pd.DataFrame(
    riwayat_centroid
)


# =====================================================
# Membuat ringkasan interpretasi cluster
# =====================================================
ringkasan = []

for i, c in enumerate(centroids):

    ringkasan.append({

        "Cluster":
        f"C{i+1}",

        "Transportasi":
        interpretasi(c[0]),

        "Konsumsi":
        interpretasi(c[1]),

        "Hiburan":
        interpretasi(c[2]),

        "Komunikasi":
        interpretasi(c[3])

    })

# DataFrame hasil interpretasi cluster
df_ringkasan = pd.DataFrame(
    ringkasan
)

# =====================================================
# Menyimpan hasil ke file Excel
# =====================================================
with pd.ExcelWriter(
    nama_file,
    engine="openpyxl"
) as writer:

    # Sheet hasil clustering
    df.drop(
    columns=[
        "Jarak_C1",
        "Jarak_C2",
        "Jarak_C3",
        "Jarak_C4",
        "Jarak_C5",
        "cluster"
    ]
    ).to_excel(
        writer,
        sheet_name="Hasil Cluster",
        index=False
    )

    # Sheet riwayat centroid setiap iterasi
    df_centroid.to_excel(
        writer,
        sheet_name="Centroid Iterasi",
        index=False
    )

    # Sheet interpretasi cluster
    df_ringkasan.to_excel(
        writer,
        sheet_name="Interpretasi",
        index=False
    )
    
    df_jarak.to_excel(
        writer,
        sheet_name="Jarak Euclidean",
        index=False
    )


# =====================================================
# Menampilkan informasi akhir
# =====================================================
print(
    f"\nFile berhasil disimpan: {nama_file}"
)

print("\nCentroid akhir:")
print(np.array(centroids))