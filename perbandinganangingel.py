# %%
import xarray as xr
import pandas as pd
from pathlib import Path

#define tanggal
tanggal_proses = "202011"

# File paths using f-strings for easy formatting
file_paths = {
    "sampelA": f"D:/anto/proposal/modulskripsi/gelombang/hindcast/{tanggal_proses}/sampelA_dayfldmean_{tanggal_proses}.nc",
    "sampelB": f"D:/anto/proposal/modulskripsi/gelombang/hindcast/{tanggal_proses}/sampelB_dayfldmean_{tanggal_proses}.nc",
    "sampelC": f"D:/anto/proposal/modulskripsi/gelombang/hindcast/{tanggal_proses}/sampelC_dayfldmean_{tanggal_proses}.nc",
    "sampelD": f"D:/anto/proposal/modulskripsi/gelombang/hindcast/{tanggal_proses}/sampelD_dayfldmean_{tanggal_proses}.nc",
    # Add sampelC and sampelD here when available
}

# Initialize an empty DataFrame to hold combined data
combined_df = pd.DataFrame()

# Loop through each file, extract hs and angin (assuming variable names)
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
        hs_var = next((v for v in varnames if "hs" in v.lower()), None)

        if hs_var is None:
            print(f"⚠️ Warning: 'hs' variable not found in {path}. Using first variable: {varnames[0]}")
            hs_var = varnames[0] # Use the first variable as a fallback

        # Convert to pandas
        hs = ds[hs_var].mean(dim=["lon", "lat"]).to_pandas()

        df = pd.DataFrame({
            f"{label}_hs": hs,
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
    output_path_str = f"D:/anto/proposal/modulskripsi/gelombang/hindcast/{tanggal_proses}/perbandingan_hs_sampelA-D_{tanggal_proses}.xlsx"
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
base_dir = Path("D:/anto/proposal/modulskripsi/gelombang/hindcast")

# 2. Tentukan nama file output
output_file = base_dir / "gabungan_perbandingan_hs_all.xlsx"

# 3. Temukan semua file Excel yang cocok di semua subfolder
excel_files = list(base_dir.rglob("perbandingan_hs_sampelA-D_*.xlsx"))

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
import matplotlib.pyplot as plt
import os

# Defining function to safely parse dates
def parse_date(date_str):
    try:
        return pd.to_datetime(date_str)
    except (ValueError, TypeError):
        return pd.NaT

# Creating directory for plots
plot_dir = r"D:\anto\proposal\modulskripsi\gelombang\hindcast\plots"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# Loading data files
wind_data = pd.read_excel(r"D:\anto\proposal\modulskripsi\angin850\angin_per_kejadian.xlsx", sheet_name=None)
wave_data = pd.read_excel(r"D:\anto\proposal\modulskripsi\gelombang\hindcast\gabungan_perbandingan_hs_all.xlsx", sheet_name=None)

# Ambil tanggal kejadian (time ke-3) dari setiap sheet untuk dijadikan referensi nama kejadian
kejadian_dates = {}

for sheet_name in wave_data.keys():
    if sheet_name in wind_data:
        df = wind_data[sheet_name]
        df['valid_time'] = pd.to_datetime(df['valid_time'], errors='coerce')
        df = df.dropna(subset=['valid_time'])
        if len(df) >= 3:
            kejadian_dates[sheet_name] = df.iloc[2]['valid_time'].date()

kejadian_dates

# --- Graphs for gabungan_perbandingan_hs_all.xlsx ---
for sheet_name in wave_data.keys():
    if sheet_name not in wind_data:
        print(f"Warning: Sheet {sheet_name} not found in wind data. Skipping.")
        continue
    
    # Loading wind and wave data
    wind_df = wind_data[sheet_name]
    wave_df = wave_data[sheet_name]
    
    # Converting dates to datetime
    wind_df['valid_time'] = wind_df['valid_time'].apply(parse_date)
    wave_df['time'] = wave_df['time'].apply(parse_date)
    
    # Dropping rows with invalid dates
    wind_df = wind_df.dropna(subset=['valid_time'])
    wave_df = wave_df.dropna(subset=['time'])
    
    # Converting to numeric
    wind_df['v'] = pd.to_numeric(wind_df['v'], errors='coerce')
    wave_df['sampelA_hs'] = pd.to_numeric(wave_df['sampelA_hs'], errors='coerce')
    wave_df['sampelB_hs'] = pd.to_numeric(wave_df['sampelB_hs'], errors='coerce')
    wave_df['sampelC_hs'] = pd.to_numeric(wave_df['sampelC_hs'], errors='coerce')
    wave_df['sampelD_hs'] = pd.to_numeric(wave_df['sampelD_hs'], errors='coerce')
    
    # Dropping rows with NaN values
    wind_df = wind_df.dropna(subset=['v'])
    wave_df = wave_df.dropna(subset=['sampelA_hs', 'sampelB_hs', 'sampelC_hs', 'sampelD_hs'])
    
    # Aligning data by date
    wind_df['date'] = wind_df['valid_time'].dt.date
    wave_df['date'] = wave_df['time'].dt.date
    merged_df = pd.merge(wind_df, wave_df, left_on='date', right_on='date', how='inner')
    
    if merged_df.empty:
        print(f"Warning: No matching dates for sheet {sheet_name}. Skipping.")
        continue
    
    # Creating time series plot
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # X-axis: h-2 to h+5
    x_labels = ['h-2', 'h-1', 'h=0', 'h+1', 'h+2', 'h+3', 'h+4', 'h+5']
    x = range(len(x_labels))
    
    # Plotting wave heights on primary y-axis
    ax1.plot(x, merged_df['sampelA_hs'], marker='s', linestyle='-', label='Sampel A')
    ax1.plot(x, merged_df['sampelB_hs'], marker='^', linestyle='-', label='Sampel B')
    ax1.plot(x, merged_df['sampelC_hs'], marker='d', linestyle='-', label='Sampel C')
    ax1.plot(x, merged_df['sampelD_hs'], marker='*', linestyle='-', label='Sampel D')
    ax1.set_xlabel('Waktu')
    ax1.set_ylabel('Tinggi Gelombang (m)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels)
    
    # Creating secondary y-axis for wind speed
    ax2 = ax1.twinx()
    ax2.plot(x, merged_df['v'], color='black', marker='o', linestyle='--', label='Kecepatan Angin (v)')
    ax2.set_ylabel('Kecepatan Angin (m/s)', color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # Highlighting h=0
    ax1.axvline(x=2, color='red', linestyle=':', label='Kejadian SS (h=0)')
    
    # Adding title and legend
    kejadian_date = kejadian_dates.get(sheet_name, sheet_name)
    plt.title(f'Tinggi Gelombang Signifikan dan Kecepatan Angin saat SS {kejadian_date} (Kategori: {merged_df["category"].iloc[0]})')

   # plt.title(f'Tinggi Gelombang Signifikan dan Kecepatan Angin saat SS {sheet_name} (Kategori: {merged_df["category"].iloc[0]})')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    ax1.grid(True)
    
    # Saving plot
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, f'time_series_{sheet_name}.png'))
    plt.close()

print(f"Plots saved in {plot_dir}/ directory")


