# %%
import os
import xarray as xr
import pandas as pd
import numpy as np

# === Definisi Nama AWS dan Parameter ===
nama_aws = "AWS Maritim Cilacap"  # Ganti nama stasiun di sini
tahun_bulan = "202011"  # Ganti tahun dan bulan di sini
target_lat = -7.724845  # Ganti latitude di sini
target_lon = 109.023  # Ganti longitude di sini

# === Konversi derajat ke arah mata angin ===
def deg_to_compass(deg):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = int((deg + 11.25) / 22.5) % 16
    return dirs[ix]

# Fungsi untuk menghitung kecepatan dan arah angin
def calculate_wind_speed_and_direction(uwnd, vwnd):
    speed_knots = np.sqrt(uwnd**2 + vwnd**2)
    speed_ms = speed_knots * 0.514444  # konversi ke m/s
    dir_deg = (270 - np.arctan2(vwnd, uwnd) * 180 / np.pi) % 360
    return speed_knots, speed_ms, dir_deg

# === Baca file NetCDF ===
file_path = f"D:/anto/proposal/modulskripsi/gelombang/hindcast/{tahun_bulan}/hasil_gabungan_{tahun_bulan}.nc"
ds = xr.open_dataset(file_path)

# Ambil dimensi
lats = ds['lat'].values
lons = ds['lon'].values
times = ds['time'].values

# Temukan indeks terdekat untuk latitude dan longitude
lat_idx = np.abs(ds['lat'].values - target_lat).argmin()
lon_idx = np.abs(ds['lon'].values - target_lon).argmin()

# ** Menggunakan Titik Terdekat **
uwnd_nearest = ds['uwnd'][:, lat_idx, lon_idx]
vwnd_nearest = ds['vwnd'][:, lat_idx, lon_idx]

# Hitung kecepatan dan arah angin dengan titik terdekat
speed_knots_nearest, speed_ms_nearest, dir_deg_nearest = calculate_wind_speed_and_direction(uwnd_nearest, vwnd_nearest)

# Ambil latitude dan longitude dari titik terdekat
nearest_lat = ds['lat'].values[lat_idx]
nearest_lon = ds['lon'].values[lon_idx]

# Bangun DataFrame untuk data titik terdekat
records_nearest = []
for t_idx, t_val in enumerate(times):
    u = float(uwnd_nearest[t_idx])
    v = float(vwnd_nearest[t_idx])
    s_knots = float(speed_knots_nearest[t_idx])
    s_ms = float(speed_ms_nearest[t_idx])
    d_deg = float(dir_deg_nearest[t_idx])

    # Cek jika d_deg adalah NaN
    if np.isnan(d_deg):
        compass = "Unknown"  # Atau bisa diisi dengan nilai default lainnya
    else:
        compass = deg_to_compass(d_deg)

    records_nearest.append({
        'time': pd.to_datetime(t_val),
        'lat': nearest_lat,  # Menggunakan lat dari titik terdekat
        'lon': nearest_lon,  # Menggunakan lon dari titik terdekat
        'nama_aws': nama_aws,
        'uwnd': u,
        'vwnd': v,
        'wind_speed_knots': s_knots,
        'wind_speed_ms': s_ms,
        'wind_dir_deg': d_deg,
        'wind_dir_compass': compass
    })

df_nearest = pd.DataFrame(records_nearest)


# === Simpan ke Excel ===
output_folder = f"D:/anto/proposal/modulskripsi/verifikasi/dataanginmodel/{nama_aws.replace(' ', '_')}/"
os.makedirs(output_folder, exist_ok=True)  # Membuat folder jika belum ada

output_file = f"{output_folder}wind_data_{tahun_bulan}.xlsx"

with pd.ExcelWriter(output_file) as writer:
    df_nearest.to_excel(writer, sheet_name='Titik Terdekat', index=False)

print(f"Ekspor ke {output_file} selesai.")





