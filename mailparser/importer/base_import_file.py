from abc import ABCMeta, abstractmethod

import pandas as pd

class BaseImportFile(object): 

    __metaclass__ = ABCMeta

    @abstractmethod
    def exists(self, file_path):
        pass

    def transform_data(self, parser, file_path):
        try: 
            transformed_data = parser(file_path)
        except: 
            raise 
        return transformed_data

    def import_data(self, data, file_name): 
        if data is None: 
            exit()