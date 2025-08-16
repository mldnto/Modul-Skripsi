# %%
import xarray as xr
import pandas as pd
from pathlib import Path

#define tanggal
tanggal_proses = "20201101"

# File paths using f-strings for easy formatting
file_paths = {
    "areaSS": f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/areaSS_dayfldmean_{tanggal_proses}.nc",
    "sampelA": f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/sampelA_dayfldmean_{tanggal_proses}.nc",
    "sampelB": f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/sampelB_dayfldmean_{tanggal_proses}.nc",
    "sampelC": f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/sampelC_dayfldmean_{tanggal_proses}.nc",
    "sampelD": f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/sampelD_dayfldmean_{tanggal_proses}.nc",
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
    output_path_str = f"D:/anto/proposal/modulskripsi/gelombang/reg/{tanggal_proses}/perbandingan_hs_areaSS&sampelA-D_{tanggal_proses}.xlsx"
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
output_file = base_dir / "gabungan_perbandingan_hs_reg_all.xlsx"

# 3. Temukan semua file Excel yang cocok di semua subfolder
excel_files = list(base_dir.rglob("perbandingan_hs_areaSS&sampelA-D_*.xlsx"))

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
plot_dir = r"D:\anto\proposal\modulskripsi\gelombang\reg\plots"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# Loading wave data from Excel file
wave_data = pd.read_excel(r"D:\anto\proposal\modulskripsi\gelombang\reg\gabungan_perbandingan_hs_reg_all.xlsx", sheet_name=None)

# Processing each sheet (event) in the wave data
for sheet_name in wave_data.keys():
    # Loading wave data for the current sheet
    wave_df = wave_data[sheet_name]
    
    # Converting dates to datetime
    wave_df['time'] = wave_df['time'].apply(parse_date)
    
    # Dropping rows with invalid dates
    wave_df = wave_df.dropna(subset=['time'])
    
    # Converting wave heights to numeric
    for col in ['areaSS_hs', 'sampelA_hs', 'sampelB_hs', 'sampelC_hs', 'sampelD_hs']:
        wave_df[col] = pd.to_numeric(wave_df[col], errors='coerce')
    
    # Dropping rows with NaN values in wave height columns
    wave_df = wave_df.dropna(subset=['areaSS_hs', 'sampelA_hs', 'sampelB_hs', 'sampelC_hs', 'sampelD_hs'])
    
    # Ensuring we have at least 8 rows for plotting (h-2 to h+5)
    if len(wave_df) < 8:
        print(f"Warning: Sheet {sheet_name} has fewer than 8 rows after cleaning. Skipping.")
        continue
    
    # Creating time series plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # X-axis: h-2 to h+5
    x_labels = ['h-2', 'h-1', 'h=0', 'h+1', 'h+2', 'h+3', 'h+4', 'h+5']
    x = range(len(x_labels))
    
    # Plotting wave heights
    ax.plot(x, wave_df['areaSS_hs'].iloc[:8], marker='o', linestyle='-', color='black', label='Area SS')
    ax.plot(x, wave_df['sampelA_hs'].iloc[:8], marker='s', linestyle='-', color='blue', label='Sampel A')
    ax.plot(x, wave_df['sampelB_hs'].iloc[:8], marker='^', linestyle='-', color='green', label='Sampel B')
    ax.plot(x, wave_df['sampelC_hs'].iloc[:8], marker='d', linestyle='-', color='red', label='Sampel C')
    ax.plot(x, wave_df['sampelD_hs'].iloc[:8], marker='*', linestyle='-', color='purple', label='Sampel D')
    
    # Setting labels and title
    ax.set_xlabel('Waktu')
    ax.set_ylabel('Tinggi Gelombang (m)')
    ax.set_title(f'Tinggi Gelombang Signifikan Area SS dan Sampel saat Kejadian SS {sheet_name}')
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    
    # Highlighting h=0
    ax.axvline(x=2, color='red', linestyle=':', label='Kejadian SS (h=0)')
    
    # Adding legend and grid
    ax.legend(loc='upper right')
    ax.grid(True)
    
    # Saving plot
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, f'wave_comparison_{sheet_name}.png'))
    plt.close()

print(f"Plots saved in {plot_dir}/ directory")



