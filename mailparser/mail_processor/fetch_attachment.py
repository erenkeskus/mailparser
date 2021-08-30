# -*- coding: utf-8 -*-
import email
import imaplib
import os
from pathlib import Path
import logging
import ntpath
from munch import munchify
from email.header import decode_header, make_header
import base64
import binascii

class MailReader(object):

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.connection = imaplib.IMAP4_SSL(config.mail_server)
        self.connection.login(config.mail_address, config.mail_password)
        self.connection.select(mailbox='INBOX', readonly=False)
    
    def close_connection(self):
        """
        Close the connection to the IMAP server
        """
        self.connection.close()

    def save_attachment(self, mails, wanted_keywords, file_ending):
        """
        Walks in mails, saves their attachments 
        Returns: 
            att_path_result: path info of fetched attachments 
        """
        att_path_result = []

        for mail in mails:
            att_path_result = self._save_attachment_of_mail(mail, wanted_keywords, att_path_result, att_path_result)
        if len(att_path_result) == 0: 
            self.logger.info('No new attachment.')
        return att_path_result

    def _save_attachment_of_mail(self, mail, wanted_keywords, file_ending, att_path_result): 
        """
        Given a message, save its attachments to the given
        download folder

        Returns: 
            att_path_result: path info of fetched attachments 
        """
        for wanted_keyword, file_dir in wanted_keywords: 
            if mail.get_content_maintype() != 'multipart':
                continue
            for part in mail.walk():  
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_content_maintype() == 'image':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                try: 
                    file_name = part.get('Content-Description')
                    file_name = base64.b64decode(file_name.split('?')[-2]).decode(file_name.split('?')[1])
                except IndexError as e: 
                    pass 
                except binascii.Error as e: 
                    self.logger.error(f'{e} in: {file_name}')
                    continue 
                if not file_name: 
                    continue
                if  wanted_keyword not in file_name: 
                    continue
                if file_ending: 
                    if file_ending not in file_name: 
                        continue
                    att_path = file_dir / file_name
    
                    with open(att_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    att_path_result.append(str(att_path))
                    self.logger.info('Saving file {}'.format(file_name))

        return att_path_result
    
    def fetch_mail(self, mail_query='ALL'):
        """
        Retrieve unread messages
        """
        emails = []
        try: 
            result, message_ids = self.connection.search(None, '({})'.format(mail_query))
            
            if result != "OK":
                return emails, None

            for message_id in message_ids[0].split():
                try: 
                    ret, data = self.connection.fetch(message_id, "(BODY.PEEK[])")
                
                except Exception as e:
                    print (e)
                    self.close_connection()
                    exit()

                msg = email.message_from_bytes(data[0][1])
                
                if not isinstance(msg, str):
                    emails.append(msg)
                    title = make_header(decode_header(msg['Subject']))
                    mail_sender = make_header(decode_header(msg['From']))
                    self.logger.info('Mail from {} with subject {} fetched. '.\
                        format(mail_sender, title))

            return emails, message_ids

        except Exception as e: 
            self.logger.exception(e)
            raise e

        return emails, None

    def mark_as_read(self, message_ids):
        for message_id in message_ids[0].split():
            response, data = self.connection.store(message_id, '+FLAGS','\\Seen')




