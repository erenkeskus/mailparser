import os
import logging
import string
from munch import munchify
import sys, io
from pathlib import Path
from os import walk, listdir, environ
from os.path import isfile, join
import argparse

from mailparser.file_parser.file_parser import parse_file
from mailparser.importer.importer_creator import ImporterCreator
from mailparser.mail_processor.fetch_attachment import MailReader
import mailparser.logging_setup as logging_setup
from mailparser.settings import from_file

logger = logging.getLogger('mailparser.run')

def make_dir_recursive(dir_name):    
    '''
    Creates a directories in a path recursively
    Arguments: 
       dir_name: a nested directory
       '''
    if dir_name=='': 
        return
    parent_dir = os.path.dirname(dir_name)
    if not os.path.isdir(parent_dir):         
        make_dir_recursive(parent_dir)
    if not os.path.isdir(dir_name): 
        os.mkdir(dir_name)
        logger.debug('Directory created: {}'.format(dir_name))


class Runner(object): 

    def __init__(self, testing=False):
        self.testing = testing
        self.config = from_file(testing=testing)

    def _get_download_dir(self, file_name): 
        '''
        Provides a directory name on the local machine to save files to
        '''
        download_dir = self.config.download_folder
        download_dir = Path(os.environ[self.config.app_root_key]) / Path(download_dir)
        file_dir = download_dir / str.replace(file_name.strip().lower(), ' ', '_')
        logger.info('File dir: {}'.format(file_dir))

        make_dir_recursive(file_dir)
        return file_dir

    def _fetch_new_attachment(self, file_name_n_dir, mail_filter): 
        try:
            fetcher = MailReader(self.config)
            emails, mail_ids = fetcher.fetch_mail(mail_filter)
            if emails: 
                fetcher.save_attachment(emails, file_name_n_dir, file_ending='csv')
                if not self.testing: 
                    fetcher.mark_as_read(mail_ids)
            else:
                logger.info('No new mail.')
        except Exception as e: 
            logger.exception(e)
            pass
        finally: 
            fetcher.close_connection()

    def run(self, asked_filenames, mail_filter): 
        file_name_n_dir = [(file_name, self._get_download_dir(file_name)) 
                           for file_name in asked_filenames]
        self._fetch_new_attachment(file_name_n_dir, mail_filter)
        # iterating through the list of tuples of requested file names and download directories
        for requested_filename, download_dir in file_name_n_dir: 
            files_in_dir = [f for f in listdir(download_dir) if isfile(join(download_dir, f))]
            attachment_file_path = ((os.path.join(download_dir, file_name), file_name) 
                                     for file_name in files_in_dir)

            for att_path, file_name in attachment_file_path: 
                
                try:
                    logger.info('Processing file: {}'.format(file_name))
                    importer_factory = ImporterCreator()
                    importer = importer_factory.create_importer(requested_filename)
                    transformed_data = importer.transform_data(parse_file, att_path)
                    importer.import_data(transformed_data, file_name)
                    logger.info(f'Imported file: {att_path}')
                    self._move_file_to_processed(att_path, file_name)
                
                except Exception as e: 
                    logger.exception(e)
              
    def _move_file_to_processed(self, att_path, file_name): 
        if not self.testing: 
            processed_file_dir = os.path.join(os.path.dirname(att_path), self.config.processed_file_dir)
            # create processed dir if it doesn't already exist
            make_dir_recursive(processed_file_dir)
            file_path = os.path.join(processed_file_dir, file_name)
            # see if there is a processed file with a bigger size. if that's the case leave it be 
            # and just remove the more recent file from download dir, as some files' data is accumulating through time. 
            if os.path.isfile(file_path): 
                if os.path.getsize(file_path) < os.path.getsize(att_path): 
                    os.replace(att_path, file_path)
                else:
                    logger.info(f'File removed from {att_path}')
                    os.remove(att_path)
            else: 
                os.replace(att_path, file_path)
                logger.info(f'File moved from {att_path} to: {file_path}')

def execute(attachments=[], testing=False, mail_filters=''): 
    logging_setup.construct_logger(testing=testing)
    
    parser = argparse.ArgumentParser()
 
    parser.add_argument("-t", "--Testing", help = "Set testing true.", dest='Testing', action='store_true')
    required_arguments = parser.add_argument_group('Required args.')
    required_arguments.add_argument("-a", "--Attachment", help = "Name of the attachment/s. Multiple seperated with space.", 
        nargs='*', required=True)
    required_arguments.add_argument("-s", "--Sender_address", help = "Sender mail address.", required=True)
    parser.add_argument("-f", "--Filter", nargs='*', 
        help = "Search through mail box with filter/s. Multiple seperated with space.")
    args = parser.parse_args()

    if args.Testing: 
        testing = True
    if args.Attachment: 
        attachments = list(args.Attachment)
    if args.Filter: 
        mail_filters +=' '.join(args.Filter)
    if args.Sender_address: 
        mail_filters = ' '.join(['FROM', args.Sender_address, mail_filters])

    logger.info(f'Args-> testing: {testing}, attachment: {attachments}, filters: {mail_filters}')

    client = Runner(testing=testing)
    client.run(attachments, mail_filters)
