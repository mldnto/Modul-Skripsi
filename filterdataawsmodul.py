# %%
import pandas as pd
import os
import glob
from collections import defaultdict

# Konfigurasi direktori dan pola file
base_dir = r"D:\anto\proposal\modulskripsi\verifikasi\dataaws"
file_prefix = "access_data_STA2201_20250815"
file_pattern = os.path.join(base_dir, f"{file_prefix}*.xlsx")

# Buat folder output jika belum ada
output_folder = os.path.join(base_dir, "output_merged_excel_by_station")
os.makedirs(output_folder, exist_ok=True)

# Kolom tetap
static_columns = ["ID Stasiun", "Nama Stasiun", "Latitude", "Longitude", "Tanggal"]

# Dictionary untuk menampung data per stasiun
station_data = defaultdict(list)

# Proses semua file
for file_path in glob.glob(file_pattern):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Gagal membaca {file_path}: {e}")
        continue

    # Koreksi nama kolom jika ada typo
    if "Lattitude" in df.columns:
        df.rename(columns={"Lattitude": "Latitude"}, inplace=True)

    # Pilih kolom angin
    wind_columns = [col for col in df.columns if col.startswith("ws_avg") or col.startswith("wd_avg")]

    # Pilih kolom yang diperlukan
    selected_columns = [col for col in static_columns if col in df.columns] + wind_columns
    df = df[selected_columns]

    # Ubah Tanggal ke datetime dan hilangkan timezone
    try:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors='coerce').dt.tz_localize(None)
    except Exception as e:
        print(f"Error parsing Tanggal di {file_path}: {e}")
        continue

    # Filter hanya jam kelipatan 3 dan menit == 0
    df_filtered = df[(df["Tanggal"].dt.hour % 3 == 0) & (df["Tanggal"].dt.minute == 0)].copy()

    # Ambil nama stasiun (diasumsikan 1 stasiun per file)
    station_name = df_filtered["Nama Stasiun"].iloc[0] if not df_filtered.empty else "UnknownStation"
    safe_station_name = station_name.replace(" ", "_").replace("/", "_")

    # Simpan ke dalam dict
    station_data[safe_station_name].append(df_filtered)

# Simpan ke file Excel per stasiun
for station_name, dataframes in station_data.items():
    output_file = os.path.join(output_folder, f"{station_name}_merged.xlsx")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for i, df in enumerate(dataframes):
            sheet_name = f"Sheet{i+1}"  # Bisa pakai nama file juga kalau mau
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"✅ Data untuk stasiun '{station_name}' disimpan di: {output_file}")



