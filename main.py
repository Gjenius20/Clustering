import pandas as pd
import numpy as np


df = pd.read_csv("H:\Kuliah\Matrfor\Clustering\Data.csv")

print(df.columns)

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

data_pengeluaran = df[
    ["transportasi", "konsumsi", "hiburan", "komunikasi"]
]

print(data_pengeluaran.head())


def konversi_pengeluaran(nilai):
    nilai = str(nilai)

    nilai = nilai.replace("&lt;", "<")
    nilai = nilai.replace("—", "–")
    nilai = nilai.strip()

    mapping = {
        "< Rp10.000": 1,
        "Rp10.000 – Rp20.000": 2,
        "Rp21.000 – Rp35.000": 3,
        "Rp36.000 – Rp50.000": 4,
        "> Rp50.000": 5
    }

    return mapping.get(nilai, 0)


kolom = [
    "transportasi",
    "konsumsi",
    "hiburan",
    "komunikasi"
]

for k in kolom:
    df[k] = df[k].apply(konversi_pengeluaran)


# centroid awal (5 cluster)
centroids = [
    [1,3,5,5],
    [1,2,5,4],
    [2,3,3,3],
    [1,2,1,1],
    [2,2,5,3]
]


def euclidean(data, centroid):
    return np.sqrt(
        np.sum(
            (np.array(data)-np.array(centroid))**2
        )
    )


fitur = [
    "transportasi",
    "konsumsi",
    "hiburan",
    "komunikasi"
]


riwayat_centroid=[]


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



def hitung_centroid(df, fitur):

    centroid_baru=[]

    for i in range(1,6):

        cluster_i=df[df["cluster"]==i]

        # jika cluster kosong
        if len(cluster_i)==0:

            centroid_baru.append(
                centroids[i-1]
            )

        else:

            mean=cluster_i[fitur].mean()

            centroid_baru.append(
                mean.tolist()
            )

    return centroid_baru


# iterasi K-Means

maks_iterasi = 100

for iterasi in range(maks_iterasi):

    print(f"\nIterasi ke-{iterasi+1}")

    cluster_hasil=[]

    for _, row in df[fitur].iterrows():

        data=row.tolist()

        jarak=[]

        for c in centroids:

            d=euclidean(data,c)

            jarak.append(d)

        cluster=jarak.index(
            min(jarak)
        )+1

        cluster_hasil.append(
            cluster
        )

    df["cluster"]=cluster_hasil

    centroid_baru = hitung_centroid(
        df,
        fitur
    )

    print("Centroid:")
    print(np.array(centroid_baru))


    for i,c in enumerate(centroid_baru):

        riwayat_centroid.append({

            "Iterasi":iterasi+1,

            "Cluster":f"C{i+1}",

            "Transportasi":
            round(c[0],2),

            "Konsumsi":
            round(c[1],2),

            "Hiburan":
            round(c[2],2),

            "Komunikasi":
            round(c[3],2),

            "Kategori Transportasi":
            interpretasi(c[0]),

            "Kategori Konsumsi":
            interpretasi(c[1]),

            "Kategori Hiburan":
            interpretasi(c[2]),

            "Kategori Komunikasi":
            interpretasi(c[3])

        })


    if np.allclose(
        centroids,
        centroid_baru
    ):

        print(
            "\nCentroid konvergen"
        )

        break

    centroids=centroid_baru



for i,c in enumerate(centroids):

    nama_kolom=f"Jarak_C{i+1}"

    df[nama_kolom]=df[fitur].apply(
        lambda row:
        euclidean(
            row.tolist(),
            c
        ),
        axis=1
    )


nama_file="H:\Kuliah\Matrfor\Clustering\hasil_clustering.xlsx"

df_centroid=pd.DataFrame(
    riwayat_centroid
)


ringkasan=[]

for i,c in enumerate(centroids):

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


df_ringkasan=pd.DataFrame(
    ringkasan
)


with pd.ExcelWriter(
    nama_file,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Hasil Cluster",
        index=False
    )

    df_centroid.to_excel(
        writer,
        sheet_name="Centroid Iterasi",
        index=False
    )

    df_ringkasan.to_excel(
        writer,
        sheet_name="Interpretasi",
        index=False
    )


print(
    f"\nFile berhasil disimpan: {nama_file}"
)

print("\nCentroid akhir:")
print(np.array(centroids))
