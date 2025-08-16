# %%
import xarray as xr
import pandas as pd
from pathlib import Path

#define tanggal
tanggal_proses = "20201101"

# File paths using f-strings for easy formatting
file_paths = {
    "areaSS": f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/areaSS_dayfldmean_{tanggal_proses}.nc",  
}

# Initialize an empty DataFrame to hold combined data
combined_df = pd.DataFrame()

# Loop through each file, extract vs and angin (assuming variable names)
for label, path in file_paths.items():
    try:
        # Check if the file exists before trying to open it
        p = Path(path)
        if not p.exists():
            print(f"⚠️ Warning: File not found, skipping: {path}")
            continue # Skip to the next file if it doesn't exist

        ds = xr.open_dataset(path)

        # Auto-detect likely variable names for hs
        varnames = list(ds.data_vars)
        vwnd_var = next((v for v in varnames if "vwnd" in v.lower()), None)

        if vwnd_var is None:
            print(f"⚠️ Warning: 'vs' variable not found in {path}. Using first variable: {varnames[0]}")
            vwnd_var = varnames[0] # Use the first variable as a fallback

        # Convert to pandas
        vwnd = ds[vwnd_var].mean(dim=["lon", "lat"]).to_pandas()

        df = pd.DataFrame({
            f"{label}_vwnd": vwnd,
        })

        # Check if combined_df is empty before concatenating
        if combined_df.empty:
            combined_df = df
        else:
            combined_df = pd.concat([combined_df, df], axis=1)

    except Exception as e:
        print(f"❌ Error processing file {path}: {e}")


# Reset index and export to Excel if the DataFrame is not empty
if not combined_df.empty:
    output_path_str = f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/perbandingan_vs_areaSS_{tanggal_proses}.xlsx"
    output_path = Path(output_path_str)

    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    combined_df.index.name = "time"
    combined_df.reset_index(inplace=True)
    combined_df.to_excel(output_path, index=False)

    print(f"✅ Data successfully exported to: {output_path.name}")
else:
    print("❌ No data was processed. Output file not created.")

# %%
import pandas as pd
from pathlib import Path

# 1. Tentukan direktori dasar tempat folder tanggal berada
base_dir = Path("D:/anto/proposal/modulskripsi/gelombang/reg")

# 2. Tentukan nama file output
output_file = base_dir / "gabungan_perbandingan_vwnd_all_areaSS.xlsx"

# 3. Temukan semua file Excel yang cocok di semua subfolder
excel_files = list(base_dir.rglob("perbandingan_vs_areaSS_*.xlsx"))

# 4. Buat objek ExcelWriter untuk menulis ke beberapa sheet
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    # 5. Loop melalui setiap file Excel yang ditemukan
    for file_path in excel_files:
        try:
            # Ekstrak nama folder (yang merupakan tanggal_proses)
            # asumsikan struktur D:/.../202001/file.xlsx
            sheet_name = file_path.parent.name

            # Baca file Excel
            df = pd.read_excel(file_path)

            # Tulis DataFrame ke sheet baru dengan nama tanggal_proses
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"✅ Berhasil memproses: {file_path.name} -> Sheet: {sheet_name}")

        except Exception as e:
            print(f"❌ Gagal memproses {file_path.name}: {e}")

print(f"\n🎉 Semua file berhasil digabungkan ke: {output_file}")

# %%
import pandas as pd

# Load the uploaded Excel file
file_path = "D:/anto/proposal/modulskripsi/gelombang/reg/gabungan_perbandingan_vwnd_all_areaSS.xlsx"
xls = pd.ExcelFile(file_path)

# Tampilkan nama-nama sheet untuk memilih
sheet_names = xls.sheet_names
sheet_names

# Fungsi konversi knot ke m/s
def knot_to_ms(knot):
    return knot * 0.514444

# Proses semua sheet
updated_dfs = {}
for sheet in sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)
    
    # Cek apakah kolom 'areaSS_vwnd' ada
    if 'areaSS_vwnd' in df.columns:
        # Tambahkan kolom baru dengan satuan m/s
        df['areaSS_vwnd_ms'] = knot_to_ms(df['areaSS_vwnd'])
    
    updated_dfs[sheet] = df

# Simpan ke file Excel baru
output_path = "D:/anto/proposal/modulskripsi/gelombang/reg/gabungan_perbandingan_vwnd_all_areaSS_ms.xlsx"
with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    for sheet, df in updated_dfs.items():
        df.to_excel(writer, sheet_name=sheet, index=False)

output_path


# %%
# Load kedua file Excel
file_kejadian_path = "D:/anto/proposal/modulskripsi/gelombang/reg/angin_per_kejadian_modif.xlsx"
file_areaSS_path = "D:/anto/proposal/modulskripsi/gelombang/reg/gabungan_perbandingan_vwnd_all_areaSS_ms.xlsx"

xls_kejadian = pd.ExcelFile(file_kejadian_path)
xls_areaSS = pd.ExcelFile(file_areaSS_path)

# Dapatkan nama-nama sheet yang tersedia
sheet_kejadian = xls_kejadian.sheet_names
sheet_areaSS = xls_areaSS.sheet_names

# Cari sheet yang ada di kedua file
common_sheets = list(set(sheet_kejadian).intersection(sheet_areaSS))
common_sheets.sort()
common_sheets

# Gabungkan setiap sheet berdasarkan kolom 'v_850_areaSS' dan 'areaSS_vwnd_ms'
merged_dfs = {}

for sheet in common_sheets:
    df_kejadian = pd.read_excel(xls_kejadian, sheet_name=sheet)
    df_areaSS = pd.read_excel(xls_areaSS, sheet_name=sheet)

    # Ambil hanya kolom 'v_850_areaSS' dan 'areaSS_vwnd_ms'
    v_col = df_kejadian[['v_850_areaSS']] if 'v_850_areaSS' in df_kejadian.columns else pd.DataFrame()
    vwnd_col = df_areaSS[['areaSS_vwnd_ms']] if 'areaSS_vwnd_ms' in df_areaSS.columns else pd.DataFrame()

    # Gabungkan secara kolom (axis=1)
    merged_df = pd.concat([v_col, vwnd_col], axis=1)
    merged_dfs[sheet] = merged_df

# Simpan hasil penggabungan ke file baru
output_merged_path = "D:/anto/proposal/modulskripsi/gelombang/reg/gabungan_v_dan_areaSS_vwnd_ms.xlsx"
with pd.ExcelWriter(output_merged_path, engine='xlsxwriter') as writer:
    for sheet, df in merged_dfs.items():
        df.to_excel(writer, sheet_name=sheet, index=False)

output_merged_path


# %%
import pandas as pd
import matplotlib.pyplot as plt

# Path ke file Excel gabungan angin
excel_path = r'D:\anto\proposal\modulskripsi\gelombang\reg\gabungan_v_dan_areaSS_vwnd_ms_modif.xlsx'

# Tentukan sheet yang dipakai (hanya 1 kejadian: 20201101)
sheet_name = '20201101'

# Baca sheet langsung
df = pd.read_excel(excel_path, sheet_name=sheet_name)

# Kolom yang akan dibandingkan
kolom_dibandingkan = ['v_850_areaSS', 'vwnd_areaSS_ms']

# Buat figure
plt.figure(figsize=(10, 6))

# Pastikan ada kolom 'time' untuk sumbu-x
if 'time' in df.columns:
    x = df['time']
else:
    x = df.index  # fallback jika tidak ada kolom waktu

# Flag apakah ada data yang berhasil diplot
ada_plot = False

# Plot tiap kolom yang dipilih
for kolom in kolom_dibandingkan:
    if kolom in df.columns:
        plt.plot(x, df[kolom], marker='o', label=kolom)
        ada_plot = True
    else:
        print(f"⚠️ Kolom '{kolom}' tidak ditemukan di sheet {sheet_name}")

# Tambahkan judul dan label
plt.title(f'Perbandingan Angin Meridional 850 hPa dan Permukaan saat Kejadian SS {sheet_name}')
plt.xlabel('Waktu (relatif)')
plt.ylabel('Kecepatan Angin')
if ada_plot:
    plt.legend(loc='upper right')
plt.grid(True)

plt.tight_layout()
plt.show()



