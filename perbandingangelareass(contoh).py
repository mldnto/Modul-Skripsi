# %%
import pandas as pd
import matplotlib.pyplot as plt

# Path ke file Excel
excel_path = r'D:\anto\gelombang\bmkg_temp_download\dataregional\gabungan_perbandingan_hs_reg_all.xlsx'

# Tentukan dua sheet yang ingin dibandingkan
selected_sheets = ['20200102', '20201101', '20210620', '20220512', '20221029', '20230413', '20230820']  # Ganti dengan nama sheet yang kamu inginkan

# Label waktu standar
time_labels = ['h-2', 'h-1', 'h-0', 'h+1', 'h+2', 'h+3', 'h+4', 'h+5']

# Baca file Excel
xls = pd.ExcelFile(excel_path)
kejadian_data = {}

# Ambil hanya kolom 'areaSS_hs' dari 2 sheet
for sheet in selected_sheets:
    if sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        if 'areaSS_hs' in df.columns:
            data = df['areaSS_hs'].values[:8]
            kejadian_data[sheet] = pd.Series(data, index=time_labels)

# Plot
plt.figure(figsize=(12, 6))
for kejadian, series in kejadian_data.items():
    plt.plot(series.index, series.values, marker='o', label=kejadian)

plt.title('Perbandingan Tinggi Gelombang Area SS Kejadian Periode MAM')
plt.xlabel('Waktu Relatif')
plt.ylabel('Tinggi Gelombang (m)')
plt.grid(True)
plt.legend(title='Kejadian', loc='upper right', fontsize=9)
plt.tight_layout()
plt.show()



