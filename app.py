import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

credentials  = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
st.set_page_config(layout="wide")
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")

ee.Initialize(credentials=credentials) 

point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])


my_image = (ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
    .filterBounds(point)
    .filterDate('2021-01-01', '2022-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
    .sort('CLOUDY_PIXEL_PERCENTAGE') 
    .first()
    .select('B[1-9]')
)


training001 = my_image.sample(
    region=my_image.geometry(), 
    scale=30,
    numPixels=10000,
    seed=0,
    geometries=True
)

vis_params = {
    'min': 0.0,
    'max': 3000,
    'bands': ['B4', 'B3', 'B2']
}

# 訓練樣本
training001 = my_image.sample(
    region=my_image.geometry(),
    scale=30,
    numPixels=10000,
    seed=0,
    geometries=True
)

n_clusters = 10
clusterer_KMeans = ee.Clusterer.wekaKMeans(nClusters=n_clusters).train(training001)
result001 = my_image.cluster(clusterer_KMeans)

legend_dict = { 
    'xero':   '#4b0082',
    'one':    '#ffff4c',
    'two':    '#f096ff',
    'three':  '#00ff7d',
    'four':   '#79ff00',
    'five':   '#0064c8',
    'six':    '#fae6a0',
    'seven':  '#00cf75',
    'eight':  '#006400',
    'nine':   '#7d00ff',
    'ten':    '#0000ff',
}

palette = list(legend_dict.values())
vis_params_001 = {'min': 0, 'max': 10, 'palette': palette}

my_Map = geemap.Map()
my_Map.centerObject(result001, 8)
my_Map.addLayer(result001, vis_params_001, 'Labelled clusters')
my_Map.add_legend(title='Land Cover Type', legend_dict=legend_dict, position='bottomright')

# 左右分割地圖
left_layer = geemap.ee_tile_layer(result001.randomVisualizer(), {}, 'K-Means clusters')
right_layer = geemap.ee_tile_layer(my_image.visualize(**vis_params), {}, 'S2 false color')
my_Map.split_map(left_layer, right_layer)

# 顯示地圖
my_Map.to_streamlit(height=600)
