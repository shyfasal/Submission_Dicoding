# Proyek Analisis Data E-Commerce

## Deskripsi
Proyek ini merupakan proyek analisis data e-commerce yang bertujuan untuk memperoleh insight dari data transaksi pelanggan. Analisis dilakukan untuk memahami pola transaksi, karakteristik pelanggan, serta performa penjualan. Hasil analisis kemudian disajikan dalam bentuk dashboard interaktif menggunakan Streamlit.

---

## Dataset
Dataset yang digunakan merupakan dataset e-commerce yang terdiri dari beberapa tabel, antara lain:
- Data pelanggan
- Data pesanan
- Data item pesanan
- Data pembayaran
- Data produk

Seluruh dataset mentah disimpan pada folder `data`, sedangkan data hasil pengolahan yang digunakan untuk dashboard disimpan dalam file `main_data.csv`.

---

## Tahapan Analisis Data
Analisis data dilakukan melalui beberapa tahapan sebagai berikut:

1. **Gathering Data**  
   Mengumpulkan seluruh dataset yang dibutuhkan untuk analisis.

2. **Data Cleaning**  
   Membersihkan data dari nilai yang hilang, duplikasi data, serta melakukan penyesuaian tipe data.

3. **Exploratory Data Analysis (EDA)**  
   Melakukan eksplorasi data untuk menemukan pola, tren, dan hubungan antar variabel menggunakan visualisasi data.

4. **Explanatory Analysis & Insight**  
   Menarik kesimpulan dan insight berdasarkan hasil analisis untuk menjawab tujuan analisis yang telah ditetapkan.

---

## Dashboard
Dashboard dibuat menggunakan Streamlit dan berfungsi untuk menampilkan hasil analisis data dalam bentuk visualisasi interaktif. Dashboard menggunakan file `main_data.csv` sebagai sumber data utama.

---

## Cara Menjalankan Dashboard
1. Install seluruh dependency yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
2. Masuk ke folder dashboard:
    ```bash
    cd dashboard

3. Jalankan dashboard dengan perintah:
    ```bash
    streamlit run dashboard.py