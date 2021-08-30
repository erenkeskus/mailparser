from mailparser.importer.hydro_data_importer import HydroDataImporter


class ImporterCreator(object):

    def create_importer(self, requested_filename): 
        if any(requested_filename in file_type for file_type in ['DAILY_INCOMING_WATER']):
            importer = HydroDataImporter()
        else: 
            raise Exception('Importer not implemented for file: {}'.format(requested_filename))
        return importer
