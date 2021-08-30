import logging
import logging.config
import yaml
from datetime import datetime
import os
import sys

from mailparser import settings

DEFAULT_LOG_CONFIG_FILENAME = 'logconfig.yaml'
	
def construct_logger(file_name=DEFAULT_LOG_CONFIG_FILENAME, name='mailparser', testing=True): 
	'''
		Constructs a logger from a logging config file
		Arguments: 
		file_name -- name of the logging config file, which sits at the root of the app 
		testing -- boolean for logging testing or production configuration
	'''
	app_root = os.environ['APP_ROOT']
	config_path = os.path.join(app_root, file_name)
	logging_config = settings.from_file(config_path)
	current_date = datetime.now().date()
	file_name = logging_config.handlers.file.filename.format(current_date)
	log_file_path = os.path.join(
		app_root, 'bin', 'log', file_name)

	if not os.path.exists(os.path.dirname(log_file_path)):
		os.makedirs(os.path.dirname(log_file_path))
	if not os.path.exists(log_file_path): 
		with open(log_file_path, 'a'):
			os.utime(log_file_path, None)

	logging_config.handlers.file.filename = log_file_path
	logging.config.dictConfig(logging_config)
	logging.basicConfig(level=logging.NOTSET)
	logging.getLogger(name)

def get_child_with_filename(self, parent_name, file_name): 
	return logging.getLogger(self.logging_config.loggers + '.' +  os.path.splitext(os.path.split(file_name)[1])[0])