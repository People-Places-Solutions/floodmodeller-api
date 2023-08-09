#   Import necessary packages

import sys
import geopandas as gpd 
import pandas as pd
from shapely.geometry import Point
from floodmodeller_api import DAT 
from floodmodeller_api.units.sections import RIVER
from floodmodeller_api.units.comment import COMMENT 



#   File paths for model, xs and nwk, read in 
model_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model"
nwk_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_nwk_EG14_channels_001_L.shp"
xs_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_xs_EG14_001_L.shp"

def process_shapefile(path):
    attributes = gpd.read_file(path)
    attributes.dropna(how='all', axis=1, inplace=True)
    return attributes

nwk_attributes = process_shapefile(nwk_path)
xs_attributes = process_shapefile(xs_path)


#   Clean up dataframes
nwk_attributes = nwk_attributes.query("Type.str.lower() == 's'") 
nwk_attributes = nwk_attributes.dropna(subset=['geometry']) 
xs_attributes = xs_attributes.dropna(subset=['geometry']) 
xs_attributes = xs_attributes[xs_attributes.intersects(nwk_attributes.unary_union)] 


#   Extract geometry data
nwk_attributes['length'] = nwk_attributes.length
nwk_attributes['start'] = nwk_attributes["geometry"].apply(lambda g: Point(g.coords[0])) 
nwk_attributes['end'] = nwk_attributes["geometry"].apply(lambda g: Point(g.coords[-1]))


#   Find which network line the xs intersects and where
xs_attributes['intersect'] = [
    next((row['ID'] for _, row in nwk_attributes.iterrows()
          if row['start'].intersects(xs_geometry)),
         None) for xs_geometry in xs_attributes['geometry']]
xs_attributes['mid_intersect'] = [
    next((river_row['ID'] for river_index, river_row in nwk_attributes.iterrows()
          if xs_geometry.intersects(river_row['geometry']) and not xs_geometry.touches(river_row['geometry'])),
         None) for xs_geometry in xs_attributes['geometry']]
xs_attributes['end_intersect'] = [
    next((row['ID'] for _, row in nwk_attributes.iterrows()
          if row['end'].intersects(xs_geometry)),
         None) for xs_geometry in xs_attributes['geometry']]

#   Put mid intersect in intersect column if nothing there
for index, row in xs_attributes.iterrows(): 
    if row['mid_intersect'] is not None:
        xs_attributes.at[index, "intersect"] = row["mid_intersect"]


#   nwk find connected network line ds
nwk_attributes['end'] = nwk_attributes['end'].apply(lambda x: Point(x))
nwk_attributes['connected'] = [[]] * len(nwk_attributes)
nwk_attributes['Flag'] = ''

for i, row in nwk_attributes.iterrows():
    end_point = row['end']
    intersected_rows = nwk_attributes[~nwk_attributes.index.isin([i]) & nwk_attributes.geometry.intersects(end_point)]
    next_ids = intersected_rows['ID'].tolist()
    nwk_attributes.at[i, 'connected'] = next_ids
    
    
#   Find the us connection
nwk_attributes['before'] = [[]] * len(nwk_attributes) 

for i, row in nwk_attributes.iterrows():
    start_point = row['start']
    intersected_rows = nwk_attributes[~nwk_attributes.index.isin([i]) & nwk_attributes.geometry.intersects(start_point)]
    previous_ids = intersected_rows['ID'].tolist()
    nwk_attributes.at[i, 'before'] = previous_ids
    
    
#   Highlight flag from nwk and map length/ maning/gxy stuff to xs
filtered_df = nwk_attributes[nwk_attributes['connected'].apply(lambda x: len(x) > 1)] 
lists = filtered_df['connected'].tolist() 
master_list = [item for sublist in lists for item in sublist] 
master_list = list(set(master_list)) 
filtered_df = nwk_attributes[nwk_attributes['ID'].isin(master_list)] 

nwk_attributes.loc[nwk_attributes['ID'].isin(filtered_df['ID'][filtered_df['connected'].apply(lambda x: len(x) == 1)]), 'Flag'] = 'join_start'
nwk_attributes.loc[nwk_attributes['ID'].isin(filtered_df['ID'][filtered_df['connected'].apply(lambda x: len(x) != 1)]), 'Flag'] = 'join_end'
nwk_attributes.loc[nwk_attributes['connected'].apply(lambda x: len(x) == 0), 'Flag'] = 'end'
nwk_attributes.loc[nwk_attributes['before'].apply(lambda x: len(x) == 0), 'Flag'] = 'start'

non_empty_rows = nwk_attributes[nwk_attributes['Flag'].notna()]
id_flag_dict = non_empty_rows.set_index('ID')[['Flag', 'n_nF_Cd', 'length',  'end']].to_dict(orient='index')
full_flag_dict = nwk_attributes.set_index('ID')[['Flag', 'n_nF_Cd', 'length', 'start']].to_dict(orient='index')

end_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'end'}
start_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'start'}
join_start_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'join_start'}
join_end_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'join_end'}


#   add to the xs data
xs_attributes['Flag'] = ''
xs_attributes.loc[xs_attributes['end_intersect'].isin(end_dict.keys()), 'Flag'] = 'end'
xs_attributes.loc[xs_attributes['intersect'].isin(start_dict.keys()), 'Flag'] = 'start'
xs_attributes.loc[xs_attributes['intersect'].isin(join_end_dict.keys()), 'Flag'] = 'join_end'
xs_attributes.loc[xs_attributes['intersect'].isin(join_start_dict.keys()), 'Flag'] = 'join_start'

xs_attributes['dist_to_next'] = ''
for key, values in full_flag_dict.items():
    mask = xs_attributes['intersect'] == key
    xs_attributes.loc[mask, 'dist_to_next'] = values['length']
xs_attributes.dist_to_next.replace('',0,regex = True, inplace=True)

xs_attributes['mannings'] = ''
for key, values in full_flag_dict.items():
    mask = xs_attributes['intersect'] == key
    xs_attributes.loc[mask, 'mannings'] = values['n_nF_Cd']
for key, values in end_dict.items():
    mask = xs_attributes['end_intersect'] == key
    xs_attributes.loc[mask, 'mannings'] = values['n_nF_Cd']
    
xs_attributes['location'] = ''
for key, values in full_flag_dict.items():
    mask = xs_attributes['intersect'] == key
    xs_attributes.loc[mask, 'location'] = values['start']
for key, values in end_dict.items():
    mask = xs_attributes['end_intersect'] == key
    xs_attributes.loc[mask, 'location'] = values['end']


#   take xs intersect, map to start point from nwk, set x as east, y as north
def get_coordinates(point):
    return point.x, point.y

geoseries = gpd.GeoSeries(xs_attributes['location'])
coords = geoseries.apply(get_coordinates).str #type: ignore 
easting = coords[0]
northing = coords[1]
xs_attributes['easting'] = easting
xs_attributes['northing'] = northing

###### Currently works but misses out last XS in series 
#   organise df 
xs_attributes['order'] = 0
order_counter = 1
for i, row in xs_attributes.iterrows():
    # Check if the row is a start or join_start
    if 'start' in row['Flag'] or 'join_start' in row['Flag']:
        xs_attributes.at[i, 'order'] = order_counter
        order_counter += 1
        intersect_value = row['intersect']
        next_row_index = xs_attributes[(xs_attributes['end_intersect'] == intersect_value) & (xs_attributes['Flag'] == '')].index
        while not next_row_index.empty: 
            next_row_index = next_row_index[0]
            xs_attributes.at[next_row_index, 'order'] = order_counter
            order_counter += 1

            intersect_value = xs_attributes.at[next_row_index, 'intersect']
            end_intersect_value = xs_attributes.at[next_row_index, 'end_intersect']
            next_row_index = xs_attributes[(xs_attributes['end_intersect'] == intersect_value) & (xs_attributes['Flag'] == '')].index
        
        if next_row_index.empty:
            next_row_index = xs_attributes[xs_attributes['end_intersect'] == intersect_value].index
            next_row_index = next_row_index[0]
            xs_attributes.at[next_row_index, 'order'] = order_counter
            order_counter += 1
            
# Sort the dataframe based on the order column
xs_attributes = xs_attributes.sort_values('order')

#clean up df 
col_to_drop = ["Type", "Z_Incremen", "Z_Maximum", "mid_intersect", "geometry", "intersect", "end_intersect", "location", "order"]
cross_sections = xs_attributes.drop(col_to_drop, axis = 1)
cross_sections['Name'] = ['RIV' + str(i).zfill(3) for i in range(1, len(cross_sections) + 1)]       ###CHECK this



dat = DAT()
comment = COMMENT(text = "End of Reach")
headings = ['X', 'Y', 'Mannings n', 'Panel', 'RPL', 'Marker', 'Easting',
       'Northing', 'Deactivation', 'SP. Marker']
dat._gxy_data = None
#iterate through adding xs 
for index, row in cross_sections.iterrows():
        unit_csv_name = str(row['Source']) #'..\\csv\\1d_xs_M14_C99.csv' pulled out     
        unit_csv = pd.read_csv(model_path + unit_csv_name.lstrip(".."),skiprows=[0])
        unit_csv.columns = ['X', 'Z']
        unit_data = pd.DataFrame(columns = headings)
        unit_data['X'] = unit_csv['X']
        unit_data['Y'] = unit_csv['Z']
        unit_data['Mannings n'] = row['mannings']
        unit_data['Panel'].fillna(False, inplace=True)
        unit_data['RPL'].fillna(1.0, inplace=True)
        unit_data['Marker'].fillna(False, inplace = True)
        unit_data['SP. Marker'].fillna(0, inplace=True)
    
        unit = RIVER(name = row['Name'], 
                     data = unit_data, 
                     density= 1000.0, 
                     dist_to_next=row['dist_to_next'], 
                     slope = 0.0001) 
        dat.insert_unit(unit, add_at=-1)
        if row['Flag']=='end' or row['Flag']=='join_end':
            dat.insert_unit(comment, add_at= -1)


#   Write out .gxy 
file_contents = ""
for index, row in cross_sections.iterrows():
    file_contents += "[RIVER_SECTION_{}]\n".format(row['Name'])
    file_contents += "x={:.2f}\n".format(row['easting'])
    file_contents += "y={:.2f}\n\n".format(row['northing'])

dat._gxy_data = file_contents
dat.save(r"new2.dat")