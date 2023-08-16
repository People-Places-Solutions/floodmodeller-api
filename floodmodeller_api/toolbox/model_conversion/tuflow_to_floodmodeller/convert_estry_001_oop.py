#   Import necessary packages

import sys
import geopandas as gpd 
import pandas as pd
from shapely.geometry import Point
from floodmodeller_api import DAT 
from floodmodeller_api.units.sections import RIVER
from floodmodeller_api.units.comment import COMMENT 
from typing import List

class TuflowToDat:

    def _process_shapefile(self, paths):
        attributes = ""
        if type(paths) == str:
            #the paths is just a single path and also a single string
            attributes = gpd.read_file(paths)
            attributes.dropna(how='all', axis=1, inplace=True)
        else:
            attributes_list = []
            for path in paths:
                temp = gpd.read_file(path)
                temp.dropna(how='all', axis=1, inplace=True)
                attributes_list.append(temp)

            attributes = gpd.GeoDataFrame(pd.concat(attributes_list, ignore_index=True))
        return attributes
    

    def _read_in(self, model_path, nwk_paths, xs_path):
        #   File paths for model, xs and nwk, read in 

        self._model_path = model_path
        self._nwk_paths = nwk_paths
        self._xs_path = xs_path
        #self._model_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model"
        #self._nwk_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_nwk_EG14_channels_001_L.shp"
        #self._xs_path = r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_xs_EG14_001_L.shp"

        self._nwk_attributes = self._process_shapefile(self._nwk_paths)
        self._xs_attributes = self._process_shapefile(self._xs_path)


    def _clean_df_1(self):
        #   Clean up dataframes
        self._nwk_attributes = self._nwk_attributes.query("Type.str.lower() == 's' | Type.str.lower() == 'r'") 
        if "Len_or_ANA" in self._nwk_attributes:
            self._nwk_attributes = self._nwk_attributes.drop(columns=['Len_or_ANA'])
        if "Form_Loss" in self._nwk_attributes:
            self._nwk_attributes = self._nwk_attributes.drop(columns=['Form_Loss'])
        if "pBlockage" in self._nwk_attributes:
            self._nwk_attributes = self._nwk_attributes.drop(columns=['pBlockage'])
        if "Conn_No" in self._nwk_attributes:
            self._nwk_attributes = self._nwk_attributes.drop(columns=['Conn_No'])
        if "Width_or_D" in self._nwk_attributes:
            self._nwk_attributes = self._nwk_attributes.drop(columns=['Width_or_D'])
        if "Height_or_" in self._nwk_attributes:
            self._nwk_attributes = self._nwk_attributes.drop(columns=['Height_or_'])
        if "Number_of" in self._nwk_attributes:
            self._nwk_attributes = self._nwk_attributes.drop(columns=['Number_of'])
        self._nwk_attributes = self._nwk_attributes.dropna(subset=['geometry']) 
        self._xs_attributes = self._xs_attributes.dropna(subset=['geometry']) 
        if not (self._nwk_attributes.unary_union == None):
            self._xs_attributes = self._xs_attributes[self._xs_attributes.intersects(self._nwk_attributes.unary_union)] 


    def _extract_geometry_data(self):
        #   Extract geometry data
        self._nwk_attributes['length'] = self._nwk_attributes.length
        self._nwk_attributes['start'] = self._nwk_attributes["geometry"].apply(lambda g: Point(g.coords[0])) 
        self._nwk_attributes['end'] = self._nwk_attributes["geometry"].apply(lambda g: Point(g.coords[-1]))


    def _find_xs_intersect(self):
        #   Find which network line the xs intersects and where
        self._xs_attributes['intersect'] = [
            next((row['ID'] for _, row in self._nwk_attributes.iterrows()
                  if row['start'].intersects(xs_geometry)),
                 None) for xs_geometry in self._xs_attributes['geometry']]
        self._xs_attributes['mid_intersect'] = [
            next((river_row['ID'] for river_index, river_row in self._nwk_attributes.iterrows()
                  if xs_geometry.intersects(river_row['geometry']) and not xs_geometry.touches(river_row['geometry'])),
                 None) for xs_geometry in self._xs_attributes['geometry']]
        self._xs_attributes['end_intersect'] = [
            next((row['ID'] for _, row in self._nwk_attributes.iterrows()
                  if row['end'].intersects(xs_geometry)),
                 None) for xs_geometry in self._xs_attributes['geometry']]

        #   Put mid intersect in intersect column if nothing there
        for index, row in self._xs_attributes.iterrows(): 
            if row['mid_intersect'] is not None:
                self._xs_attributes.at[index, "intersect"] = row["mid_intersect"]


    def _find_ds_intersect(self):
        #   nwk find connected network line ds
        self._nwk_attributes['end'] = self._nwk_attributes['end'].apply(lambda x: Point(x))
        self._nwk_attributes['connected'] = [[]] * len(self._nwk_attributes)
        self._nwk_attributes['Flag'] = ''

        for i, row in self._nwk_attributes.iterrows():
            end_point = row['end']
            intersected_rows = self._nwk_attributes[~self._nwk_attributes.index.isin([i]) & self._nwk_attributes.geometry.intersects(end_point)]
            next_ids = intersected_rows['ID'].tolist()
            self._nwk_attributes.at[i, 'connected'] = next_ids
            if not (row['Type'] == "s"):
                self._nwk_attributes['Flag'][i] = "culvert"


    def _find_us_intersect(self):
        #   Find the us connection
        self._nwk_attributes['before'] = [[]] * len(self._nwk_attributes) 

        for i, row in self._nwk_attributes.iterrows():
            start_point = row['start']
            intersected_rows = self._nwk_attributes[~self._nwk_attributes.index.isin([i]) & self._nwk_attributes.geometry.intersects(start_point)]
            previous_ids = intersected_rows['ID'].tolist()
            self._nwk_attributes.at[i, 'before'] = previous_ids


    def _highlight_flag(self):
        #   Highlight flag from nwk and map length/ maning/gxy stuff to xs
        filtered_df = self._nwk_attributes[self._nwk_attributes['connected'].apply(lambda x: len(x) > 1)] 
        lists = filtered_df['connected'].tolist() 
        master_list = [item for sublist in lists for item in sublist] 
        master_list = list(set(master_list)) 
        filtered_df = self._nwk_attributes[self._nwk_attributes['ID'].isin(master_list)] 

        self._nwk_attributes.loc[self._nwk_attributes['ID'].isin(filtered_df['ID'][filtered_df['connected'].apply(lambda x: len(x) == 1)]), 'Flag'] = 'join_start'
        self._nwk_attributes.loc[self._nwk_attributes['ID'].isin(filtered_df['ID'][filtered_df['connected'].apply(lambda x: len(x) != 1)]), 'Flag'] = 'join_end'
        self._nwk_attributes.loc[self._nwk_attributes['connected'].apply(lambda x: len(x) == 0), 'Flag'] = 'end'
        self._nwk_attributes.loc[self._nwk_attributes['before'].apply(lambda x: len(x) == 0), 'Flag'] = 'start'

        non_empty_rows = self._nwk_attributes[self._nwk_attributes['Flag'].notna()]
        id_flag_dict = non_empty_rows.set_index('ID')[['Flag', 'n_nF_Cd', 'length',  'end']].to_dict(orient='index')
        self._full_flag_dict = self._nwk_attributes.set_index('ID')[['Flag', 'n_nF_Cd', 'length', 'start']].to_dict(orient='index')

        self._end_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'end'}
        self._start_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'start'}
        self._join_start_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'join_start'}
        self._join_end_dict = {key: value for key, value in id_flag_dict.items() if value['Flag'] == 'join_end'}


    def _add_to_xs_data(self):
        #   add to the xs data
        self._xs_attributes['Flag'] = ''
        self._xs_attributes.loc[self._xs_attributes['end_intersect'].isin(self._end_dict.keys()), 'Flag'] = 'end'
        self._xs_attributes.loc[self._xs_attributes['intersect'].isin(self._start_dict.keys()), 'Flag'] = 'start'
        self._xs_attributes.loc[self._xs_attributes['intersect'].isin(self._join_end_dict.keys()), 'Flag'] = 'join_end'
        self._xs_attributes.loc[self._xs_attributes['intersect'].isin(self._join_start_dict.keys()), 'Flag'] = 'join_start'

        self._xs_attributes['dist_to_next'] = ''
        for key, values in self._full_flag_dict.items():
            mask = self._xs_attributes['intersect'] == key
            self._xs_attributes.loc[mask, 'dist_to_next'] = values['length']
        self._xs_attributes.dist_to_next.replace('',0,regex = True, inplace=True)

        self._xs_attributes['mannings'] = ''
        for key, values in self._full_flag_dict.items():
            mask = self._xs_attributes['intersect'] == key
            self._xs_attributes.loc[mask, 'mannings'] = values['n_nF_Cd']
        for key, values in self._end_dict.items():
            mask = self._xs_attributes['end_intersect'] == key
            self._xs_attributes.loc[mask, 'mannings'] = values['n_nF_Cd']

        self._xs_attributes['location'] = ''#self._xs_attributes['start']
        for key, values in self._full_flag_dict.items():
            mask = self._xs_attributes['intersect'] == key
            self._xs_attributes.loc[mask, 'location'] = values['start']
        for key, values in self._end_dict.items():
            mask = self._xs_attributes['end_intersect'] == key
            self._xs_attributes.loc[mask, 'location'] = values['end']
        #for index, row in self._xs_attributes.iterrows():
        #    if row['location'] == '':
        #        self._xs_attributes = self._xs_attributes.drop(index)


    def _get_coordinates(self, point):
        #   take xs intersect, map to start point from nwk, set x as east, y as north
        return point.x, point.y


    def _set_eastings_northings(self):
        geoseries = gpd.GeoSeries(self._xs_attributes['location'])
        coords = geoseries.apply(self._get_coordinates).str #type: ignore 
        easting = coords[0]
        northing = coords[1]
        self._xs_attributes['easting'] = easting
        self._xs_attributes['northing'] = northing


    # this method needs fixing apparently
    def _organise_df(self):
        ###### Currently works but misses out last XS in series 
        #   organise df 
        self._xs_attributes['order'] = 0
        order_counter = 1
        isCulvertDict = (self._nwk_attributes['Flag'] == "culvert").to_dict()
        culvertsIndex = [key for key, value in isCulvertDict.items() if value == True]
        culvertsID = []
        for index in culvertsIndex:
            culvertsID.append(self._nwk_attributes['ID'][index])
        for i, row in self._xs_attributes.iterrows():
            if row['intersect'] in culvertsID:
                    continue
            # Check if the row is a start or join_start
            if not ('start' in row['Flag'] or 'join_start' in row['Flag']):
                continue
            self._xs_attributes.at[i, 'order'] = order_counter
            order_counter += 1
            intersect_value = row['intersect']
            next_row_index = self._xs_attributes[(self._xs_attributes['end_intersect'] == intersect_value) & (self._xs_attributes['Flag'] == '')].index
            while not next_row_index.empty: 
                if row['intersect'] in culvertsID:
                    continue
                next_row_index = next_row_index[0]
                self._xs_attributes.at[next_row_index, 'order'] = order_counter
                order_counter += 1

                intersect_value = self._xs_attributes.at[next_row_index, 'intersect']
                end_intersect_value = self._xs_attributes.at[next_row_index, 'end_intersect']
                next_row_index = self._xs_attributes[(self._xs_attributes['end_intersect'] == intersect_value) & (self._xs_attributes['Flag'] == '')].index

            if next_row_index.empty:
                next_row_index = self._xs_attributes[self._xs_attributes['end_intersect'] == intersect_value].index
                next_row_index = next_row_index[0]
                self._xs_attributes.at[next_row_index, 'order'] = order_counter
                order_counter += 1

        print("")

        # Sort the dataframe based on the order column
        self._xs_attributes = self._xs_attributes.sort_values('order')
        print("")


    def _clean_df_2(self):
        #clean up df 
        col_to_drop = ["Type", "Z_Incremen", "Z_Maximum", "mid_intersect", "geometry", "intersect", "end_intersect", "location", "order"]
        self._cross_sections = self._xs_attributes.drop(col_to_drop, axis = 1)
        self._cross_sections['Name'] = ['RIV' + str(i).zfill(3) for i in range(1, len(self._cross_sections) + 1)]


    def _make_dat(self, empty_dat):
        self._dat = empty_dat
        self._comment = COMMENT(text = "End of Reach")
        self._headings = ['X', 'Y', 'Mannings n', 'Panel', 'RPL', 'Marker', 'Easting',
               'Northing', 'Deactivation', 'SP. Marker']
        self._dat._gxy_data = None


    def _add_xss(self):
        #iterate through adding xs 
        for index, row in self._cross_sections.iterrows():
            unit_csv_name = str(row['Source']) #'..\\csv\\1d_xs_M14_C99.csv' pulled out     
            unit_csv = pd.read_csv(self._model_path + unit_csv_name.lstrip(".."),skiprows=[0])
            unit_csv.columns = ['X', 'Z']
            unit_data = pd.DataFrame(columns = self._headings)
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
            self._dat.insert_unit(unit, add_at=-1)
            if row['Flag']=='end' or row['Flag']=='join_end':
                    self._dat.insert_unit(self._comment, add_at= -1)


    def _add_gxy_data(self):
        #   Write out .gxy 
        file_contents = ""
        for index, row in self._cross_sections.iterrows():
            file_contents += "[RIVER_SECTION_{}]\n".format(row['Name'])
            file_contents += "x={:.2f}\n".format(row['easting'])
            file_contents += "y={:.2f}\n\n".format(row['northing'])

        self._dat._gxy_data = file_contents


    def convert(self, model_path: str, nwk_paths: List[str], xs_path: str, empty_dat: DAT):

        self._read_in(model_path, nwk_paths, xs_path)

        self._clean_df_1()

        self._extract_geometry_data()
        
        self._find_xs_intersect()

        self._find_ds_intersect()
        
        self._find_us_intersect()

        self._highlight_flag()

        self._add_to_xs_data()

        self._set_eastings_northings()

        self._organise_df()

        self._clean_df_2()

        self._make_dat(empty_dat)

        self._add_xss()

        self._add_gxy_data()

        #self._dat.save(output_path)

        #return self._dat

