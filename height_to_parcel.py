# Melt height value into parcel
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
from PIL import Image
import gc
import pdb

ColorCode = {'UQA110': [245,245,7, '#F5F507'],
             'UQA111': [237, 248, 91, '#EDF85B'],
             'UQA112': [222, 237, 36, '#DEED24'],
             'UQA120': [248, 255, 105, '#F8FF69'],
             'UQA121': [247, 238, 48, '#F7EE30'],
             'UQA122': [252, 221, 43, '#FCDD2B'],
             'UQA123': [245, 203, 31, '#F5CB1F'],
             'UQA124': [245, 203, 31, '#F5CB1F'],
             'UQA130': [220, 168, 7, '#DCA807'],
             'UQA210': [211, 107, 66, '#D36B42'],
             'UQA220': [231, 153, 107, '#E7996B'],
             'UQA230': [241, 182, 140, '#F1B68C'],
             'UQA240': [253, 213, 172, '#FDD5AC'],
             'UQA330': [169, 169, 255, '#A9A9FF'],
             'UQA410': [157, 147, 79, '#9D934F'],
             'UQA420': [116, 215, 83, '#74D753'],
             'UQA430': [96, 202, 96, '#60CA60'],
             'UQA999': [169, 169, 169, '#A9A9A9']}
ColorCode_RGB = {k: v[:3] for k, v in ColorCode.items()}
ColorCode_16 = {k: v[-1] for k, v in ColorCode.items()}

class gpd_to_img:        
    def read_file(self, target):
        '''
        Read shp file to geopandas
        Input: str / Output: geodataframe
        '''
        path = './Rawdata/Total/Seoul_{}.shp'
        target_path = path.format(target)
        target_gdf = gpd.read_file(target_path)
        return target_gdf.to_crs(epsg = 5179)
    
    def trim_layer(self, boundary, target):
        '''
        Trim given target layer according to the boundary layer
        Input: GeoDataFrame, GeoDataFrame / Output: GeoDataFrame
        '''
        trimmed_layer = gpd.overlay(boundary, target, keep_geom_type = False)
        return trimmed_layer
    
    def get_districts(self, boundary, target):
        '''
        Trim every layers by boundary
        Input: GeoDataFrame, GeoDataFrame / Output: List of GeoDataFrame
        '''
        total = len(boundary)
        trimmed_layers = []
        for k, v in boundary.iterrows():
            p1 = v.geometry
            g = gpd.GeoSeries([p1])
            gdf = gpd.GeoDataFrame(crs = 'EPSG:5179', geometry = g)
            temp = self.trim_layer(gdf, target)
            trimmed_layers.append(temp)
            if k % 100 == 0 and k >= 100:
                print('{}/{}'.format(k, total))
        return trimmed_layers
    
    def flatten(self, t):
        return [item for sublist in t for item in sublist]
    
    def useColorcode(self, listLU, listRW, listPCL, index):
        '''
        Apply color code on land use gdf to export img
        Input: List of GeoDataFrame * 3, int / Output: png
        '''
        n = len(listLU)
        my_dpi = 96
        for i in range(n):
            fig, ax = plt.subplots(figsize = (512/my_dpi, 512/my_dpi), dpi = my_dpi)
            ax.set_axis_off()
            ax.set_aspect('equal')
            listLU[i].plot(ax = ax, color = listLU[i]['color'])
            listPCL[i].plot(ax = ax, facecolor = 'none', edgecolor = 'black', lw = 0.1)
            listRW[i].plot(ax = ax, color = 'gray')
            
            fig_name = './blk{}/sample_{}'.format(str(index). str(i))
            fig.savefig(fig_name)
        return 0
    
    def parcel_height(self, parcels, buildings):
        '''
        Join average building height (floor) by matching parcel
        Input: List of GeoDataFrame, List of GeoDataFrame / Output: List of GeoDataFrame
        '''
        parcel_Hs = []
        for i in range(len(parcels)):
            parcel = parcels[i]
            building = buildings[i]
            building_h = building[['TOTAL_AREA', 'geometry']]
            parcel_h = gpd.sjoin(parcel, building_h, how = 'left')
            parcel_sumH = parcel_h.groupby('PNU').sum()
            parcel_H = parcel.merge(parcel_sumH, on = 'PNU')
            try:
                parcel_H['TOTAL_AREA'].fillna(0, inplace = True)
                parcel_H['block_FAR'] = parcel_H['TOTAL_AREA'] / parcel_H['area_x']
            except:
                parcel_H['block_FAR'] = 0
            parcel_Hs.append(parcel_H)
        return parcel_Hs
    
    def parcel_Hcolor(self, parcels, index):
        '''
        Give R gradation according to the parcel's height
        Input: List of GeoDataFrame, int / Output: List of imgs
        '''
        for i in range(len(parcels)):
            parcel = parcels[i]
            def h_to_rgb(h):
                return (h, 0, 0)
            parcel['color'] = parcel['block_FAR'].map(lambda x: h_to_rgb(x))
            my_dpi = 96
            fig, ax = plt.subplots(figsize = (512/my_dpi, 512/my_dpi),dpi = my_dpi)
            ax.set_axis_off()
            try: parcel.plot(ax = ax, color = parcel['color'], edgecolor = 'None')
            except: parcel.plot(ax = ax, color = '#FFFFFF', edgecolor = 'None')
            fig_name = './Code/blockFAR_{}/building_{}'.format(str(index), str(i))
            fig.savefig(fig_name)
        return 0
    
gen_img = gpd_to_img()
gdf_emd = gen_img.read_file('EMD')
gdf_parcel = gen_img.read_file('Parcel')
gdf_building = gen_img.read_file('BULD')
gdf_block = gen_img.read_file('Block')

EMD1, EMD2, EMD3, EMD4 = gdf_emd[:100], gdf_emd[100:200], gdf_emd[200:300], gdf_emd[300:]
EMDs = [EMD1, EMD2]

for _, emd in enumerate(EMDs):
    emd_blk = gen_img.get_districts(emd, gdf_block)
    emd_pcl = gen_img.get_districts(emd, gdf_parcel)
    emd_buld = gen_img.get_districts(emd, gdf_building)
    
    blk_pcl, blk_buld = [], []
    for k, blk in enumerate(emd_blk):
        blk_pcl.append(gen_img.get_districts(blk, emd_pcl[k]))
        blk_buld.append(gen_img.get_districts(blk, emd_buld[k]))
        if k % 20 == 0:
            print('Block Count: {}/{}'.format(k, len(emd_blk)))
    blk_pcl = gen_img.flatten(blk_pcl)
    blk_buld = gen_img.flatten(blk_buld)
    pcl_withH = gen_img.parcel_height(blk_pcl, blk_buld)
    img_pcl_withH = gen_img.parcel_Hcolor(pcl_withH, _)
    print('IterCounts: {}/{}'.format(str(_), str(len(EMDs))))
    del emd, emd_blk, emd_pcl, emd_buld, blk_pcl, blk_buld, pcl_withH, img_pcl_withH
    gc.collect()
    
    