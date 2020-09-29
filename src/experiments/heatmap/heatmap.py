#  Project: Evo-Sim
#  Developed by: Irina Danes

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap

font = {'family' : 'normal', 'size'   : 15}
plt.rc('font', **font)

street_map = gpd.read_file('London_Ward.shp')
street_map.crs = "EPSG:27700"

df = pd.read_csv('geolocations.csv')
crs = {'init': 'epsg:4326'}

geometry = [Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
geo_df = gpd.GeoDataFrame(df, crs = crs, geometry = geometry)
geo_df.crs = "EPSG:4326"

fig,ax = plt.subplots(figsize=(20,20))
street_map.plot(ax=ax, alpha=0.7, color="grey")
geo_df.to_crs(epsg=27700).plot(ax=ax,markersize=20, color="red", marker="o")
ax.set_xticks([])
ax.set_yticks([])

max_amount = 10
map = folium.Map(location=[51.54, -0.112], zoom_start=11)


for lat, lon in zip(df['Latitude'], df['Longitude']):
    folium.CircleMarker(location=[lat,lon], radius=0.5,fill=True,color='red',fill_color='red',fill_opacity=0.7).add_to(map)

heatmap = HeatMap(list(zip(df.Latitude.values, df.Longitude.values)),
                  min_opacity=0.2,
                  max_val=max_amount,
                  radius=9, blur=11,
                  max_zoom=1)

map.add_child(heatmap)
map.save('heatmap.html')