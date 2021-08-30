from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import Function as func
from sqlalchemy.exc import ProgrammingError
from functools import wraps
from contextlib import contextmanager
import logging

import pandas as pd 

from .hydro_db import HydroDailyPlantReadingsImportedFile, Plant, HydroDailyPlantReading

logger = logging.getLogger(__name__)

@contextmanager
def session_scope(con_string): 
    engine = create_engine(con_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

class DbClient(object): 
    def __init__(self, session):
        self.session = session

    def bulk_save_update_hdyro_daily_readings(self, data): 
        records = []
        for row in data: 
            record = HydroDailyPlantReading(**row)
            existing_record = self.retrieve_hdyro_daily_reading(record)
            if existing_record: 
                existing_record.value = record.value
                records.append(existing_record)
            else: 
                records.append(record)
        self.session.bulk_save_objects(records, update_changed_only=True)
        self.session.flush()

    def retrieve_hdyro_daily_reading(self, new_record): 
        record = self.session.query(HydroDailyPlantReading).filter_by(
            record_start=new_record.record_start,
            record_end=new_record.record_end,
            plant_id=new_record.plant_id,
            data_name=new_record.data_name).one_or_none()
        return record
    
    def retrieve_hdyro_daily_readings_file(self, file_name):
        data = (self.session.query(HydroDailyPlantReadingsImportedFile).
                filter(HydroDailyPlantReadingsImportedFile.file_name == file_name).first())
        return data

    def insert_to_hdyro_daily_readings_file(self, file_name, processed):
        file_instance = HydroDailyPlantReadingsImportedFile(file_name=file_name, processed=processed)
        self.session.add(file_instance)

    def update_hdyro_daily_readings_file(self, session, file):
        self.session.update(file)

    def retrieve_plant_id_by_transmission_id(self, id_list): 
        statement = self.session.query(Plant).filter(Plant.transmission_id.in_(id_list)).statement
        data = pd.read_sql(statement, con=self.session.bind)
        return data

    def retrieve_hydro_daily_readings(self, plant_id, record_start, record_end, data_name):
        data = self.session.query(Plant).filter(
            Plant.id==plant_id, 
            Plant.record_start==record_start,
            Plant.record_end==record_end,
            Plant.data_name==data_name
            ).first()
        return data

    def insert_into_plant(self, data):
        plants = [Plant(**row) for row in data.to_dict(orient='records')]
        self.session.bulk_save_objects(plants)
        logger.info('{} records inserted.'.format(data.shape[0]))


