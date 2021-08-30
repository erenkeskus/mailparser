import datetime as date
import os
import pandas as pd
from datetime import timedelta
from datetime import datetime 
import logging
import ntpath

from mailparser.file_parser.base import AbstractParser

logger = logging.getLogger(__name__)

DATANAME_UNIT_MAP = {
    'incoming_water':'t M3', 
    'consumed_water':'t M3', 
    'thrown_water':'t M3', 
    'evaporated_water':'t M3', 
    'level0':'meter', 
    'level1':'meter', 
    'level2':'meter', 
    'level3':'meter', 
    'level4':'meter',
    'level5':'meter'}




class WaterReportParser(AbstractParser): 

    def __str__(self): 
        return super().__str__()

    def __call__(self, file_path): 
        file_name = os.path.split(file_path)[1]
        dest_column_names = ['facility_id', 'record_start', 'record_end', 'data_name', 'value', 'unit']
        number_of_columns = 17
        
        org_column_names = ['SANTRAL ID','SANTRAL ADI','KURULU GÜÇ','ÜRETİM','MAKSİMUM SU SEVİYESİ',
        'MİNİMUM SU SEVİYESİ', '04:00 SU SEVİYESİ',  '08:00 SU SEVİYESİ',  '12:00 SU SEVİYESİ' , '16:00 SU SEVİYESİ', 
          '20:00 SU SEVİYESİ'  ,'24:00 SU SEVİYESİ','GELEN SU','GELEN SU HIZ',  
          'ENERJİYE KULLANILAN SU',  'BUHARLAŞAN VE SIZAN SU' , 'KULLANILMADAN ATILAN SU',  'DEPO EDİLEN SU']
        
        columns_to_be_saved = ['SANTRAL ID','KURULU GÜÇ','ÜRETİM','MAKSİMUM SU SEVİYESİ','MİNİMUM SU SEVİYESİ',
          '04:00 SU SEVİYESİ',  '08:00 SU SEVİYESİ',  '12:00 SU SEVİYESİ' , '16:00 SU SEVİYESİ', 
          '20:00 SU SEVİYESİ'  ,'24:00 SU SEVİYESİ', 'GELEN SU','GELEN SU HIZ',  
          'ENERJİYE KULLANILAN SU', 'BUHARLAŞAN VE SIZAN SU' , 'KULLANILMADAN ATILAN SU', 'DEPO EDİLEN SU']

        with open(file_path, 'rb') as file: 
            xl =  pd.ExcelFile(file)
            for name in xl.sheet_names:
                df = pd.read_excel(xl, name).iloc[:,:number_of_columns+1]
                date_str = df.loc[1].iloc[1]
                if isinstance(date_str, str):
                    date = datetime.strptime(date_str, "%d-%m-%Y")
                elif isinstance(date_str, datetime):
                    date = date_str
                else: 
                    date_str = df.loc[2].iloc[0]
                    if isinstance(date_str, str): 
                        date = datetime.strptime(date_str, "%d-%m-%Y")
                    elif isinstance(date_str, datetime):
                        date = date_str
                    else: 
                        exit()

                first_row = df.loc[df.iloc[:,2]=='MW'].index.values
                start_index = first_row[0]
                raw_data = df.iloc[start_index+1:].copy()
                new_columns = dict(zip(raw_data.columns, org_column_names ))
                raw_data.rename(columns = new_columns,  inplace = True)
                data = raw_data.loc[:,columns_to_be_saved]
                data['record_start'] = date
                data.reset_index(inplace=True, drop=True)
                data['record_end'] = date + timedelta(hours= 23, minutes= 59)
                units = pd.DataFrame.from_dict(
                    dict(zip(org_column_names, df.iloc[start_index].dropna())), orient='index')
                data.set_index(['SANTRAL ID', 'record_start', 'record_end'],  drop=True, inplace=True)
                data = data.dropna().stack(dropna = False)
                stacked_data = data.reset_index()
                stacked_data['unit'] = units.loc[stacked_data.iloc[:,3]].iloc[:,0].values
                stacked_data.rename(columns = dict(zip(stacked_data.columns, dest_column_names)), inplace = True)
                stacked_data.set_index(['facility_id', 'record_start', 'record_end', 'data_name']).drop_duplicates(inplace=True)
                stacked_data.value = round(stacked_data.value.astype(float), 5)
            logger.info('Parsed number of lines: {} of file: {}'.format(stacked_data.shape[0], file_path))
            return stacked_data

class WaterReportParser_v2(AbstractParser):

    def __str__(self): 
        return super().__str__()

    def __call__(self, file_path): 

        dest_column_names = ['facility_id', 'record_start', 'record_end', 'data_name', 'value']
        org_column_names = [
           'transmission_id',
           'incoming',
           'consumed',
           'thrown',
           'evaporated',
           'level0',
           'level1',
           'level2',
           'level3',
           'level4',
           'level5',
           'date'
           ]    

        new_column_names = [
            'transmission_id',
            'incoming',
            'consumed',
            'thrown',
            'evaporated',
            'level0',
            'level1',
            'level2',
            'level3',
            'level4',
            'level5',
            'record_start'
            ]    

        column_names_map = dict(zip(org_column_names, new_column_names))
        try:
            data = pd.read_csv(
                file_path,
                usecols=org_column_names, 
                parse_dates=True
                )
            data = data.rename(columns=column_names_map)
            data.record_start = pd.to_datetime(data.record_start)
            assert data.record_start.dtype == 'datetime64[ns]', \
                'Date column of sheet:{} is not cast. Data type: {}'.format(
                 sheet_name, data.record_start.dtype)
            data['record_end'] = data.record_start + timedelta(hours=23, minutes=59)
            data.set_index(
                ['transmission_id', 'record_start', 'record_end'], 
                drop=True, inplace=True)
            data = data.stack(dropna=False)
            data = data.reset_index()
            data.rename(
                columns=dict(zip(data.columns, dest_column_names)), 
                inplace=True
                )
            
            data.dropna(subset=['value'], inplace=True)
            data['value'] = round(data.value.astype(float), 5)
            
            if data is None: 
                raise 'File empty: '.format(file_path)
            
            data['unit'] = data['data_name'].map(DATANAME_UNIT_MAP)
            logger.info('Parsed number of lines: {}'.format(data.shape[0]))
            data  = data[~data.index.duplicated(keep='last')]
            logger.info('Number of lines to be inserted after dropping dublicates: {}'.format(data.shape[0]))

            return data

        except ValueError as e: 
            logger.error(f'Error in file: {file_path}, {e}')
        
        

        


