import logging
import os
import ntpath

from mailparser.file_parser.parse_water_report_file import WaterReportParser, WaterReportParser_v2

logger = logging.getLogger(__name__)

def parse_file(file_path): 
    
    if os.path.isfile(file_path) != True: 
        raise ValueError(file_path)
        
    parser = _get_parser(file_path)
    logger.info('Parsing with: {}'.format(str(parser)))
    
    data = parser(file_path)
    return data

def _get_parser(file_path): 
    
    if 'GUNLUK_SU_RAPORU' in file_path: 
        return WaterReportParser()
    
    elif 'daily_incoming_water' in file_path and file_path.split('.')[-1]=='csv': 
        return WaterReportParser_v2()
    else: 
        raise Exception('File unkown {}, parser not implemented.'.format(file_path))
