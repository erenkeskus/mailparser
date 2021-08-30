import os
from os import path
import time
import warnings
import yaml
import logging

from munch import munchify, unmunchify

cur_dir = os.environ['APP_ROOT']

DEFAULT_CONFIG_FILENAME = 'config.yaml'
config_file_path =  path.join(cur_dir, DEFAULT_CONFIG_FILENAME)
logger = logging.getLogger(__name__)

PRODUCTION = munchify({
    "app_root_key" : 'APP_ROOT', 
    "download_folder" :  "/bin/test/download_folder",
    "processed_file_dir" : "processed",
    "mail_server" : '',
    "mail_address" :  '',
    "mail_password" : '',
    "con_string": '',
    })

TEST = munchify({
    "app_root_key" : 'APP_ROOT', 
    "download_folder" :  "/bin/test/download_folder",
    "processed_file_dir" : "processed",
    "mail_server" : '',
    "mail_address" :  '',
    "mail_password" : '',
    "con_string": '',
    })

def from_file(config_file_path=config_file_path, testing=False):
    try: 
        with open(config_file_path) as fd:
            conf = yaml.load(fd, Loader=yaml.FullLoader)
        conf = munchify(conf)
        if testing:
            return conf['TEST']
        if not testing: 
            return conf['PRODUCTION']
    except IOError:
        logger.info("A configuration file named {} is missing" .format(config_file_path))
        s_conf = yaml.dump(unmunchify(TEST), explicit_start=True, indent=True, default_flow_style=False)
  
        time.sleep(3)
        try:
            with open(os.path.expanduser(config_file_path), "w") as fd:
                fd.write(s_conf)
        except IOError:
            logger.info("Find and edit at: ".format(config_file_path))

    return TEST

def from_env(): 
    config = munchify({
    "app_root_key" : 'APP_ROOT', 
    "download_folder" :  "/bin/test/download_folder",
    "processed_file_dir" : "processed",
    "mail_server" :'',
    "mail_address" : '',
    "mail_password" :'',
    "con_string": os.environ['DB_URI'],
    })

    return config 
