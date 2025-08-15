# %%
import numpy as np
import pandas as pd
import xarray as xr
import os
import matplotlib
from mpl_toolkits.basemap import Basemap
from matplotlib import pyplot as plt
import datetime as datetime

# %%

# Path lengkap ke file NetCDF yang baru
tahunbulantanggal = '20201101'
#tanggal= '02'
file_path = fr'D:\anto\proposal\modulskripsi\gelombang\reg\{tahunbulantanggal}\hasil_rata_rata_harian_{tahunbulantanggal}.nc'

# Buka dataset menggunakan xarray
ds = xr.open_dataset(file_path)

# Tampilkan informasi dataset (opsional)
ds

# %%
ds.hs.isel(time=0).plot()

# %%
lat1=-30
lat2=0
lon1=90
lon2=130

# %%
# Loop langsung pada waktu asli (datetime64)
for t in pd.to_datetime(ds.time.values):
    print(f"Memproses waktu: {t.strftime('%Y%m%d')}")

# %%
for t in pd.to_datetime(ds.time.values):
    print(f"Memproses waktu: {t.strftime('%Y%m%d')}")

    # Slice data
    slice_lat = slice(lat1,lat2)
    slice_lon = slice(lon1,lon2)
    selected_data = ds.hs.sel(time=t, lat=slice_lat, lon=slice_lon)
    selected_dir = ds.dir.sel(time=t, lat=slice_lat, lon=slice_lon)
    selected_u = np.cos(np.deg2rad(selected_dir))
    selected_v = np.sin(np.deg2rad(selected_dir))

    # --- Semua kode visualisasi di bawah ini HARUS DI DALAM LOOP ---
    """
    Setup map properties
    """
    lat = selected_data.lat.data # get latitude array
    lon = selected_data.lon.data # get longitude array
    lons, lats = np.meshgrid(lon,lat) # Create meshgrid to place the value of selected data
    llcrnrlon = lon[0] # most east longitude
    urcrnrlon = lon[-1] # most west longitude
    llcrnrlat = lat[0] # southest longitude
    urcrnrlat = lat[-1] # northest longitude
    latlon_line = 5 # variable for density of paralel and meridian
    arrow_density = 10 # Select to modify arrow density. The lower the value, the denser.
    arrow_scale = 200 # Select to modify arrow scale. The lower the value, the llonger the arrow
    arrow_width = 0.001 # Select to modify arrow width


# %%
import matplotlib.pyplot as plt
import matplotlib
import geopandas as gpd
import fiona
from shapely.geometry import box

# === 1. Load Geodatabase ===
gdb_path = r"C:/Users/anto/Documents/petawilayanselatanjawa.gdb"
gdf_layers = fiona.listlayers(gdb_path)
print("Layer tersedia:", gdf_layers)

# Gunakan layer pertama atau ganti sesuai kebutuhan

gdf = gpd.read_file(gdb_path, layer='db_mksdemarine_weather_forecast_area_d0')
gdf = gdf.to_crs(epsg=4326)  # Konversi ke koordinat lat/lon (jika belum)

# === 2. Fungsi Visualisasi ===
def plot_map(lat_data, lon_data, latlon_interval, color_map, level, magnitude,
             u_comp, v_comp, skip, scale, map_title, legend_title, file_name,
             gdf_overlay=None):
    fig, ax = plt.subplots(figsize=(15, 7.5))
    fig.patch.set_facecolor('white')
    print(f'\tMembuat peta {map_title}')
    lons, lats = np.meshgrid(lon_data, lat_data)

    bsmap = Basemap(projection='merc',
                    llcrnrlon=lon_data[0],
                    urcrnrlon=lon_data[-1],
                    llcrnrlat=lat_data[0],
                    urcrnrlat=lat_data[-1],
                    resolution='l')

    bsmap.drawcoastlines(linewidth=1)
    bsmap.drawcountries(linewidth=1)
    bsmap.drawlsmask(land_color='Linen')
    bsmap.fillcontinents(lake_color='royalblue')

    bsmap.drawparallels(np.arange(lat_data[0], lat_data[-1], latlon_interval),
                        labels=[1, 0, 0, 0], dashes=[1, 0], linewidth=0.2,
                        color='w', fontsize=10)
    bsmap.drawmeridians(np.arange(lon_data[0], lon_data[-1], latlon_interval),
                        labels=[0, 0, 0, 1], dashes=[1, 0], linewidth=0.2,
                        color='w', fontsize=10)

    # Setup colormap
    cmap = color_map
    cmap.set_over('indigo')
    bounds = level
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    x, y = bsmap(lons, lats)
    wv_map = bsmap.contourf(x, y, magnitude, cmap=cmap, norm=norm,
                            levels=bounds, extend='max')

    bsmap.quiver(x[::skip, ::skip], y[::skip, ::skip],
                 u_comp[::skip, ::skip], v_comp[::skip, ::skip],
                 units='inches', scale=scale, pivot='mid', width=0.015)

    col_bar = bsmap.colorbar(wv_map, 'bottom', ticks=bounds, spacing='uniform',
                             extendfrac='auto', pad=0.5)
    bounds_str = [str(i) for i in bounds]
    col_bar.set_ticklabels(bounds_str)
    col_bar.ax.tick_params(labelsize=10)
    col_bar.set_label(legend_title, fontsize=7)

    # Re-overlay batas lagi agar tidak tertutup colorbar
    bsmap.drawcoastlines(linewidth=1)
    bsmap.drawcountries(linewidth=1)
    bsmap.drawlsmask(land_color='Linen')
    bsmap.fillcontinents(lake_color='royalblue')

    # === Tambahkan overlay shapefile ===
    if gdf_overlay is not None:
        for geom in gdf_overlay.geometry:
            if geom.is_empty or geom is None:
                continue
            if geom.geom_type == 'Polygon':
                xg, yg = bsmap(*geom.exterior.coords.xy)
                ax.plot(xg, yg, color='black', linewidth=1)
            elif geom.geom_type == 'MultiPolygon':
                for part in geom.geoms:
                    if not part.is_empty:
                        xg, yg = bsmap(*part.exterior.coords.xy)
                        ax.plot(xg, yg, color='black', linewidth=1)


    # === Tambahkan kotak hitam ===
    min_lat, max_lat = -30, -25
    min_lon, max_lon = 105, 110
    kotak = box(min_lon, min_lat, max_lon, max_lat)
    x_box, y_box = bsmap(*kotak.exterior.xy)
    ax.plot(x_box, y_box, color='black', linewidth=2)

    plt.title(map_title, y=1.0, pad=20)
    plt.savefig(file_name, bbox_inches='tight', dpi=300)
    plt.show()

# === 3. Setup Warna, Level, dan Parameter Visualisasi ===
cmap_wave = matplotlib.colors.ListedColormap(
    ["#0859E7", "#3075BD", "#63C3E7", "#55FBBD", "#48D342", "#FFFB52", "#F9AD39",
     "#F7792A", "#A54518", "#E74941", "#CE2C38", "#EF37CE", "#B5349C"])

cmap_wind = matplotlib.colors.ListedColormap(
    ["#C6EBFF", "#A5D7E7", "#63C7F7", "#B5FFBD", "#4EE36B", "#B5DF73", "#EFDB6B",
     "#F7BA73", "#F65D21", "#CE2010", "#F51F2B", "#E737C6"])

wave_lvl = [0, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7]
wave_lgnd = 'meter'
wind_lvl = [0, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 50]
wind_lgnd = 'knot'

arw_intv = 2
arw_scle = 15
latlon_intv = 5

# === 4. Looping Visualisasi ===
ds_w = ds
out_dir = f'output_maps_reg/{tahunbulantanggal}'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

for t in pd.to_datetime(ds.time.values):
    t_str = t.strftime('%Y-%m-%d')

    hs = ds_w.hs.sel(time=t, lat=slice_lat, lon=slice_lon)
    hs_dir = ds_w.dir.sel(time=t, lat=slice_lat, lon=slice_lon)
    hs_u = np.cos(np.deg2rad(hs_dir))
    hs_v = np.sin(np.deg2rad(hs_dir))
    hs_uv = np.arctan2(hs_v, hs_u)
    hs_u, hs_v = 2. * np.cos(hs_uv), 2. * np.sin(hs_uv)

    lat = hs.lat.values
    lon = hs.lon.values
    wv_avg_title = f'Tinggi Gelombang Signifikan Rata-Rata pada {t_str}'
    fl_out_wvavg = f"{out_dir}/Tinggi Gelombang Signifikan Rata-Rata pada {t_str}.png"

    plot_map(lat, lon, latlon_intv, cmap_wave, wave_lvl, hs,
             hs_u, hs_v, arw_intv, arw_scle, wv_avg_title,
             wave_lgnd, fl_out_wvavg, gdf_overlay=gdf)

    print("Done")


# %%
out_dir = f"output_maps_reg/{tahunbulantanggal}"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

for t in pd.to_datetime(ds.time.values):
    t_str = t.strftime('%Y-%m-%d')

    print(f"Memproses: {t_str}")

    uwnd = ds_w.uwnd.sel(time=t, lat=slice_lat, lon=slice_lon)
    vwnd = ds_w.vwnd.sel(time=t, lat=slice_lat, lon=slice_lon)

    wind_mag = np.sqrt(np.square(uwnd) + np.square(vwnd))
    wind_u = 2. * uwnd / wind_mag
    wind_v = 2. * vwnd / wind_mag

    lat = uwnd.lat.values
    lon = uwnd.lon.values
    wsd_avg_title = f'Kecepatan Angin pada {t_str}'

    fl_out_wsdavg = f"{out_dir}/Kecepatan Angin pada {t_str}_4.png"

    plot_map(lat, lon, latlon_intv, cmap_wind, wind_lvl, wind_mag,
             wind_u, wind_v, arw_intv, arw_scle, wsd_avg_title,
             wind_lgnd, fl_out_wsdavg, gdf_overlay=gdf)

    print("Done")
    plt.show()



