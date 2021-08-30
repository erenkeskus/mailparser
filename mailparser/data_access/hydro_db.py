# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, NCHAR, String, Unicode, text
from sqlalchemy.dialects.mssql import BIT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Boolean
from sqlalchemy.sql import func


Base = declarative_base()
metadata = Base.metadata


class HydroDailyPlantReadingsImportedFile(Base):
    __tablename__ = 'hydro_daily_plant_readings_imported_file'

    id = Column(Integer, primary_key=True)
    file_name = Column(Unicode(255), nullable=False)
    processed = Column(Boolean, nullable=False)
    insert_datetime = Column(DateTime, server_default=func.now())


class HydroDataName(Base):
    __tablename__ = 'hydro_data_name'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)


class Plant(Base):
    __tablename__ = 'plant'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    transmission_id = Column(Integer)
    transmission_facility_name = Column(Unicode)
    #todo 
    insert_datetime = Column(DateTime, server_default=func.now())
    update_datetime = Column(DateTime, onupdate=func.now())


class HydroDailyPlantReading(Base):
    __tablename__ = 'hydro_daily_plant_readings'

    id = Column(Integer, primary_key=True)
    plant_id = Column(ForeignKey('plant.id'),  nullable=False)
    record_start = Column(DateTime, nullable=False)
    record_end = Column(DateTime, nullable=False)
    data_name = Column(Unicode(100), nullable=False)
    value = Column(Float(53), nullable=False)
    unit = Column(Unicode(50))
    insert_datetime = Column(DateTime, server_default=func.now())
    update_datetime = Column(DateTime, onupdate=func.now())

    plant = relationship('Plant')
