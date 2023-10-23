import win32com.client as win32
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.command import Command
from exchangelib import DELEGATE, Account, Credentials, Configuration, FileAttachment, Message, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from exchangelib.items import ID_ONLY
from exchangelib.fields import FieldPath
from exchangelib.folders import Inbox, DistinguishedFolderId, FolderCollection, Folder
from exchangelib.properties import Mailbox
from exchangelib.services import GetFolder

from bs4 import BeautifulSoup
import os
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
class utilities:
    def __init__(self, mailid , paswd):
        credentials = Credentials(
            username=mailid,  # Or myusername@example.com for O365
            password=paswd
        )
        config = Configuration(server='outlook.office365.com', credentials=credentials)
        # dcdata.edg@corelogic.com
        self.account = Account(
            primary_smtp_address=mailid,
            credentials=credentials,
            autodiscover=False,
            config=config,
            access_type=DELEGATE
        )

    def read_emails(self, folder, downloc=None):
        try:
            outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6).Folders.Item(folder) #6 = Inbox (without mails from the subfolder)
            messages = inbox.Items
            emailcon = {}
            for message in messages:
                if message.UnRead == True:
                    body_content = message.body
                    sub_content = message.Subject
                    emailcon[sub_content] = body_content
                    # print(body_content) #Sometimes has parsing error due to different encoding format
                    # print(sub_content)
                    message.Unread = False
                    if downloc != None:
                        attachments = message.attachments
                        for attachment in attachments:
                            attachment.SaveAsFile(downloc)
        except Exception as e:
            print(str(e))

        return emailcon

    def send_emails(self, tolist, emailsub, emailBdy):
        """Commenting below lines. TODO: Intergrate as one code block
        If using below code then add these as args "bcclist=None, cclist = None, attch = None"
        """
        # try:
        #     outlook = win32.Dispatch('outlook.application')
        #     mail = outlook.CreateItem(0)
        #     tolist_new = ''.join(tolist)
        #     mail.To = tolist_new
        #     if bcclist != None:
        #         mail.Bcc = bcclist
        #     if cclist != None:
        #         mail.Cc = cclist
        #     mail.Subject = emailsub
        #     mail.HTMLBody = emailBdy
        #     if attch != None:
        #         mail.Attachments.Add(attch)
        #     mail.Send()
        # except Exception as e:
        #     print(str(e))
        try:
            email = Message(account=self.account,
                            subject=emailsub,
                            body=HTMLBody(emailBdy),
                            to_recipients=[Mailbox(email_address=i) for i in tolist],
                            )
            email.send()
        except Exception as e:
            print(str(e))

    def isElementPresent(self, driver, element):
        try:
            element = WebDriverWait(driver, 1000).until(EC.visibility_of(element))
            msg = True
        except Exception as e:
            print(str(e))
            msg = False
        return msg

    def isElementClickable(self, driver, element):
        try:
            element = WebDriverWait(driver, 1000).until(EC.element_to_be_clickable(element))
            msg = True
        except Exception as e:
            print(str(e))
            msg = False
        return msg

    def get_status(self, driver):
        try:
            driver.execute(Command.STATUS)
            return "Alive"
        except Exception as e:
            print(str(e))
            return "Dead"

    def get_unread_shared_mails(self,shared_mailid='dcdata.edg@corelogic.com'):
        additional_fields = {
        FieldPath(field=f) for f in self.account.inbox.supported_fields(version=self.account.version)
        }
        shared_folder = list(GetFolder(account=self.account).call(
        folders=[DistinguishedFolderId(
        id=Inbox.DISTINGUISHED_FOLDER_ID,
        mailbox=Mailbox(email_address=shared_mailid))
        ],
        # folder =account.inbox / 'Imp',
        additional_fields=additional_fields,
        shape=ID_ONLY
        ))[0]
        emailcon = {}
        print(shared_folder.unread_count)
        for mail in shared_folder.filter(is_read=False):
            mail.is_read = True
            mail.save()
            sub_content = mail.subject
            body_content = mail.body
            soup = BeautifulSoup(mail.body)
            body_content = soup.get_text()
            emailcon[sub_content] = body_content
            # print(body_content)
            # print(sub_content)

            for attachment in mail.attachments:
                if isinstance(attachment, FileAttachment):
                    local_path = os.path.join('/opt/email', attachment.name)
                with open(local_path, 'wb') as f:
                    f.write(attachment.content)
        return emailcon

    def get_unread_mails_from_folder_under_inbox(self, folder):
        child_folder = self.account.inbox / folder
        emailcon = {}
        for mail in child_folder.filter(is_read=False):
            mail.is_read = True
            mail.save()
            # print('Received Date: ' + str(mail.datetime_received))
            sub_content = mail.subject
            body_content = mail.body
            soup = BeautifulSoup(mail.body)
            body_content = soup.get_text()
            emailcon[sub_content] = body_content + 'Received Date: ' + str(mail.datetime_received)
            # print(body_content)
            # print(sub_content)

            for attachment in mail.attachments:
                if isinstance(attachment, FileAttachment):
                    local_path = os.path.join('/opt/email', attachment.name)
                with open(local_path, 'wb') as f:
                    f.write(attachment.content)
        return emailcon

    def get_unread_mails_from_inbox(self):
        emailcon = {}
        for mail in self.account.inbox.filter(is_read=False):
            mail.is_read = True
            mail.save()
            sub_content = mail.subject
            body_content = mail.body
            soup = BeautifulSoup(mail.body)
            body_content = soup.get_text()
            emailcon[sub_content] = body_content
            # print(body_content)
            # print(sub_content)

        for attachment in mail.attachments:
            if isinstance(attachment, FileAttachment):
                local_path = os.path.join('/opt/email', attachment.name)
        with open(local_path, 'wb') as f:
            f.write(attachment.content)
        return emailcon
