import os
import logging
from datetime import datetime

import pandas as pd

from mailparser.importer.base_import_file import BaseImportFile
from mailparser.data_access.db_client import DbClient
from mailparser.data_access.db_client import session_scope

logger = logging.getLogger(__name__)
con_string = os.environ['DB_URI']

class HydroDataImporter(BaseImportFile): 

    def _insert_file_processed(self, db_client, file_name): 
        with session_scope(con_string) as session: 
            db_client = DbClient(session)
            file = db_client.retrieve_hdyro_daily_readings_file(file_name)
            processed = True
            db_client.insert_to_hdyro_daily_readings_file(file_name, processed)
    
    def import_data(self, data, file_name):
        '''
            Executes bulk save and update on hydro daily recording data
            Arguments: 
                data-> (pandas.DataFrame) 
                file_name -> str of file_name
        '''
        super().import_data(data, file_name)

        if data is None:
            logger.info('File {} does not contain any data'.format(file_name)) 
            return
        if isinstance(data, pd.DataFrame) == False: 
            raise TypeError("Expecting a pandas dataframe")
        
        dest_column_names = [
            'plant_id', 
            'record_start', 
            'record_end', 
            'data_name', 
            'value', 
            'unit'
            ]
        
        with session_scope(con_string) as session: 
            db_client = DbClient(session)

            file_desc = db_client.retrieve_hdyro_daily_readings_file(file_name)
            plant_desc = db_client.retrieve_plant_id_by_transmission_id(
                data.facility_id.unique().tolist())

            data = data.merge(
                plant_desc[['id', 'transmission_id']], how='left', left_on=['facility_id'], right_on=['transmission_id'])
            data.rename(columns={'id':'plant_id'}, inplace=True)
            
            if any(data.plant_id.isna()):  
                logger.warning('Plant/ s with transmissionId/ s not found:  {}'.format(
                    data.loc[data.plant_id.isna()]['facility_id'].unique()))

            data = data.reindex(columns=dest_column_names)
            data.dropna(inplace=True)
            logger.debug('Number of lines: {}'.format(data.shape[0]))

            records = data.to_dict(orient='records')
            db_client.bulk_save_update_hdyro_daily_readings(records)
            self._insert_file_processed(db_client, file_name)
