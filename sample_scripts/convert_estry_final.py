import sys
import os
from glob import glob
from pathlib import Path
import pandas as pd
import geopandas as gpd 
import fiona 
from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry
try:
    from floodmodeller_api import DAT 
    from floodmodeller_api.units import RIVER
except ImportError:
    print('Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment')
    sys.exit()

#read in nwk shapefile containing the nwk and xs data. 
model_path = r"C:\Users\LAMBERD3\Documents\Python\Data\Tuflow_data\TUFLOW\model"
nwk_path = r"C:\Users\LAMBERD3\Documents\Python\Data\Tuflow_data\TUFLOW\model\gis\1d_nwk_EG14_channels_001_L.shp"
xs_path = r"C:\Users\LAMBERD3\Documents\Python\Data\Tuflow_data\TUFLOW\model\gis\1d_xs_EG14_001_L.shp"

#Function for read file
def process_shapefile(path):
    attributes = gpd.read_file(path)
    attributes.dropna(how='all', axis=1, inplace=True)
    return attributes

network_attributes = process_shapefile(nwk_path)
xs_attributes = process_shapefile(xs_path)
river_df = network_attributes.query("Type.str.lower() == 's' and not geometry.is_empty") #get rid of anything but river 'S'
river_df['start'] = river_df["geometry"].apply(lambda g: Point(g.coords[0])) #start point
river_df['end'] = river_df["geometry"].apply(lambda g: Point(g.coords[-1])) #end point 
river_df['length'] = river_df.length
xs_df = xs_attributes[xs_attributes.intersects(river_df.unary_union)] #only keep xs when it intersects the river line 

# Find when lines intersect not at start or end 
xs_df['mid_intersect'] = [
    next((river_row['ID'] for river_index, river_row in river_df.iterrows()
          if xs_geometry.intersects(river_row['geometry']) and not xs_geometry.touches(river_row['geometry'])),
         None) for xs_geometry in xs_df['geometry']]

xs_df['start_intersect'] = [
    next((row['ID'] for _, row in river_df.iterrows()
          if row['start'].intersects(xs_geometry)),
         None) for xs_geometry in xs_df['geometry']]

#spatial join for start end or full geometry function - only needed for end in the end 
def find_intersects(df1, df2, column_name):
    df2 = df2.set_geometry(column_name)
    join_df = gpd.sjoin(df1, df2[['ID', column_name]], op='intersects')
    intersect_dict = {}
    for _, row in join_df.iterrows():
        index = row.name
        value = row['ID']
        if index not in intersect_dict:
            intersect_dict[index] = []
        intersect_dict[index].append(value)
    return intersect_dict

xs_df['end_intersect'] = [
    find_intersects(xs_df.loc[[index]], river_df, 'end').get(index, []) for index in xs_df.index]
#unit name
xs_df['Name'] = xs_df['Source'].str.extract(r'([^\\/.]+)\.csv', expand=False)

#joining 
xs_df['link'] = ''
# Iterate over each row in the DataFrame
for index, row in xs_df.iterrows():
    # Check if 'start_intersect' is not empty
    if not pd.isnull(row['start_intersect']):
        xs_df.at[index, 'link'] = row['start_intersect']
    # Check if 'mid_intersect' is not empty
    elif not pd.isnull(row['mid_intersect']):
        xs_df.at[index, 'link'] = row['mid_intersect']
    # Check if 'end_intersect' is not empty
    elif not pd.isnull(row['end_intersect']):
        xs_df.at[index, 'link'] = row['end_intersect']

#link together - horrible workaround to get rid of the brackets for the link column 
xs_df_copy = xs_df.copy()  # Create a copy of the DataFrame
xs_df_copy['link'] = xs_df_copy['link'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
xs_df.loc[:, 'link'] = xs_df_copy['link']
Final_df = pd.merge(xs_df, river_df, left_on='link', right_on='ID', how='inner')

Final_df['dist_to_next'] = Final_df['length']
Final_df['intersection_point'] = Final_df['start']

rows_with_empty_start_intersect = Final_df[Final_df['start_intersect'].isnull() | (Final_df['start_intersect'] == '')]
Final_df.loc[rows_with_empty_start_intersect.index, 'dist_to_next'] = 0
Final_df.loc[rows_with_empty_start_intersect.index, 'intersection_point'] = Final_df['end']
geoseries = gpd.GeoSeries(Final_df['intersection_point'])

def get_coordinates(point):
    return point.x, point.y

easting, northing = geoseries.apply(get_coordinates).str
Final_df['easting'] = easting
Final_df['northing'] = northing

Final_df.to_csv('check.csv')

#write .gxy
file_contents = ""

# Iterate over each row in the DataFrame
for index, row in Final_df.iterrows():
    # Append the section header to the file contents
    file_contents += "[RIVER_SECTION_{}]\n".format(row['Name'])
    # Append the 'x' and 'y' values to the file contents
    file_contents += "x={:.2f}\n".format(row['easting'])
    file_contents += "y={:.2f}\n\n".format(row['northing'])

with open('test.gxy', 'w') as file:
    file.write(file_contents)
    
    
    
#write out .dat file 
dat = DAT()
headings = ['X', 'Y', 'Mannings n', 'Panel', 'RPL', 'Marker', 'Easting',
       'Northing', 'Deactivation', 'SP. Marker']
#read all river types 
for index, row in Final_df.iterrows():
        unit_csv_name = str(row['Source']) #'..\\csv\\1d_xs_M14_C99.csv' pulled out     
        unit_csv = pd.read_csv(model_path + unit_csv_name.lstrip(".."),skiprows=[0])
        unit_csv.columns = ['X', 'Z']
        #unit_name = unit_csv_name.replace("..\\csv\\1d_xs_", "")[:-4] #named unit 'M14_C99'

        #for each csv file append data 
        unit_data = pd.DataFrame(columns = headings)
        unit_data['X'] = unit_csv['X']
        unit_data['Y'] = unit_csv['Z']
        unit_data['Mannings n'] = row['n_nF_Cd']
        #unit_data['Mannings n'].fillna(0.0, inplace=True)
        unit_data['Panel'].fillna(False, inplace=True)
        unit_data['RPL'].fillna(1.0, inplace=True)
        unit_data['Marker'].fillna(False, inplace = True)
        #unit_data['Easting'] = row['easting']
        #unit_data['Northing']= row['northing']
        unit_data['SP. Marker'].fillna(0, inplace=True)
    
        unit = RIVER(name = row['Name'],
                     data = unit_data, 
                     density= 1000.0, 
                     dist_to_next=row['dist_to_next'],
                     slope = 0.0001) 
        dat.insert_unit(unit, add_at=-1)
        
dat.save(r"test.dat")