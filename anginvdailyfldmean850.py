# %%
# Uban dari nc ke excel
import xarray as xr
import pandas as pd

# Path file input dan output
input_path = r'D:\anto\proposal\modulskripsi\angin850\daily_fldmean_angin_v_850.nc'
output_path = r'D:\anto\proposal\modulskripsi\angin850\dayfldmean_anginv_850.xlsx'

# Membuka file .nc
ds = xr.open_dataset(input_path)

# Melihat struktur dataset
print(ds)

# Mengambil variabel 'v' dan ubah ke DataFrame
df = ds['v'].to_dataframe().reset_index()

# Tampilkan tabel contoh
print(df.head())

# Simpan ke Excel
df.to_excel(output_path, index=False)

print(f"Data berhasil disimpan ke '{output_path}'")


# %%
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Defining function to safely parse dates
def parse_date(date_str):
    try:
        return pd.to_datetime(date_str)
    except (ValueError, TypeError):
        return pd.NaT

# Creating directory for plots
plot_dir = r"D:\anto\proposal\modulskripsi\angin850"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# Loading data
file_path = r"D:\anto\proposal\modulskripsi\angin850\dayfldmean_anginv_850.xlsx"
try:
    df = pd.read_excel(file_path, sheet_name="Sheet1")
except FileNotFoundError:
    print(f"Error: File {file_path} not found. Please check the path.")
    exit(1)

# Converting dates and wind speed
df['valid_time'] = df['valid_time'].apply(parse_date)
df['v'] = pd.to_numeric(df['v'], errors='coerce')

# Dropping rows with invalid dates or wind speed
df = df.dropna(subset=['valid_time', 'v'])

# Filtering data for 2020–2020
start_date = datetime(2020, 1, 1)
end_date = datetime(2020, 12, 31)
df = df[(df['valid_time'] >= start_date) & (df['valid_time'] <= end_date)]

if df.empty:
    print("Error: No data available for 2019–2023 after filtering.")
    exit(1)

# Creating time series plot
plt.figure(figsize=(12, 6))
plt.plot(df['valid_time'], df['v'], color='blue', label='Kecepatan Angin (v)', linewidth=1)

# Adding category threshold lines
plt.axhline(y=11.1, color='green', linestyle='--', label='Lemah (11.1 m/s)', alpha=0.7)
plt.axhline(y=12.1, color='orange', linestyle='--', label='Sedang (12.1 m/s)', alpha=0.7)
plt.axhline(y=13.1, color='red', linestyle='--', label='Kuat (13.1 m/s)', alpha=0.7)

# Shading category regions
plt.axhspan(11.1, 12.0, facecolor='green', alpha=0.1, label='Lemah (11.1–12 m/s)')
plt.axhspan(12.1, 13.0, facecolor='orange', alpha=0.1, label='Sedang (12.1–13 m/s)')
plt.axhspan(13.1, df['v'].max() + 1, facecolor='red', alpha=0.1, label='Kuat (>13.1 m/s)')

# Setting labels and title
plt.xlabel('Tahun')
plt.ylabel('Kecepatan Angin (m/s)')
plt.title('Angin Meridional Rata-Rata Harian Wilayah Indeks Southerly Surge Periode 2020')
plt.grid(True, linestyle='--', alpha=0.7)

# Formatting x-axis dates
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())

# Adding legend in lower right
plt.legend(loc='lower right', fontsize=10)

# Adjusting layout
plt.tight_layout()

# Saving plot
output_path = os.path.join(plot_dir, 'wind_timeseries_2020.png')
plt.savefig(output_path)
plt.show()

print(f"Plot saved at {output_path}")

# %%
# Mengelompokkan per kategori

import pandas as pd
import matplotlib.pyplot as plt

# Path to the uploaded file
file_path = 'D:/anto/proposal/modulskripsi/angin850/dayfldmean_anginv_850.xlsx'

# Read the Excel file
data = pd.ExcelFile(file_path)

# Load the first sheet
first_sheet = data.parse(data.sheet_names[0])

# Ensure the date column is in datetime format
first_sheet['valid_time'] = pd.to_datetime(first_sheet['valid_time'])

# Categorize wind speed based on intensity
conditions = [
    (first_sheet['v'] >= 11.1) & (first_sheet['v'] < 12.0),  # Lemah
    (first_sheet['v'] >= 12.1) & (first_sheet['v'] < 13.0),  # Sedang
    (first_sheet['v'] > 13.1),                                   # Kuat
]
categories = ['Lemah', 'Sedang', 'Kuat']
first_sheet['kategori'] = pd.Series(None, index=first_sheet.index)
first_sheet.loc[conditions[0], 'kategori'] = 'Lemah'
first_sheet.loc[conditions[1], 'kategori'] = 'Sedang'
first_sheet.loc[conditions[2], 'kategori'] = 'Kuat'

# Split the data into separate DataFrames for each category
kategori_lemah = first_sheet[first_sheet['kategori'] == 'Lemah'][['valid_time', 'v']]
kategori_sedang = first_sheet[first_sheet['kategori'] == 'Sedang'][['valid_time', 'v']]
kategori_kuat = first_sheet[first_sheet['kategori'] == 'Kuat'][['valid_time', 'v']]

# Save each category to separate sheets in an Excel file
output_path = 'D:/anto/proposal/modulskripsi/angin850/angin_v_per_kategori.xlsx'
with pd.ExcelWriter(output_path) as writer:
    kategori_lemah.to_excel(writer, sheet_name='Lemah', index=False)
    kategori_sedang.to_excel(writer, sheet_name='Sedang', index=False)
    kategori_kuat.to_excel(writer, sheet_name='Kuat', index=False)

# Display the head of each category as a preview
kategori_lemah.head(), kategori_sedang.head(), kategori_kuat.head()



