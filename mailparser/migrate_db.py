import logging

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from mailparser.data_access.hydro_db import metadata
from mailparser.settings import from_env
from mailparser.data_access.db_client import session_scope, DbClient
from mailparser import logging_setup

config = from_env()
logging_setup.construct_logger(name=__name__)
logger = logging.getLogger(__name__)

def create_db(): 
    engine = create_engine(config.con_string)
    metadata.create_all(engine)

def drop_db(): 
    engine = create_engine(config.con_string)
    metadata.drop_all(engine)

def populate_plant(db_client): 
    data = pd.read_csv('mailparser/power_plants.csv')
    db_client.insert_into_plant(data)

if __name__=='__main__':

    create_db()
    with session_scope(config.con_string) as session:
        db_client = DbClient(session)
        populate_plant(db_client)
