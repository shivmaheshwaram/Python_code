import os
from mailer import Mailer
from mailer import Message as messag
from datetime import datetime
from exchangelib.properties import Mailbox
from jinja2 import Environment, FileSystemLoader
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from exchangelib import DELEGATE, Account, Credentials, Configuration, FileAttachment, Message, HTMLBody

BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter


class utilities:
    try:

        global root_dir, email_json

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        email_json = root_dir + "\\CommonUtil\\email_new.json"

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
    except Exception as e:
        print(e.args)

    def send_emails_attach(self, tolist, emailsub, emailBdy, file_path = None):
        """Commenting below lines. TODO: Intergrate as one code block
        If using below code then add these as args "bcclist=None, cclist = None, attch = None"
        """
        file_list = os.listdir(file_path)
        attachments = []
        for file in file_list:
            with open(file_path + file, 'rb') as f:
                content = f.read()
            attachments.append((file, content))

        try:
            email = Message(account=self.account,
                            subject=emailsub,
                            body=HTMLBody(emailBdy),
                            to_recipients=[Mailbox(email_address=i) for i in tolist],
                            )

            for attachment_name, attachment_content in attachments or []:
                file = FileAttachment(name=attachment_name, content=attachment_content)
                email.attach(file)
            email.send_and_save()

            # email.send()
        except Exception as e:
            print(str(e))


class SendEmail:

    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = self.root_dir + "\\templates"

    def send_emails(self, mail_id, tolist, email_sub, email_body, smtp):
        try:
            message = messag(From=mail_id, To=tolist)
            message.Subject = email_sub
            message.Html = email_body
            sender = Mailer(smtp)
            sender.send(message)
        except Exception as e:
            print(str(e))

    def email_notification(self, icp_details_obj, description, mail_id, tolist, submission_error=None):
        try:
            state = icp_details_obj.get('state')
            county = icp_details_obj.get('county')
            icpnumber = icp_details_obj.get('icpnumber')
            edition = icp_details_obj.get('edition')
            version = icp_details_obj.get('version')
            fips = icp_details_obj.get('fips')
            prodtype = icp_details_obj.get('productiontype')

            headers_dict = [{
                            'date': datetime.now().date(),
                            'group': 'TaxRoll Submission',
                            'state': state,
                            'county': county,
                            'icp': icpnumber,
                            'edition': edition,
                            'version': version,
                            'fips': fips,
                            'prodtype': prodtype}]

            if len(description) > 0:
                for i, j in enumerate(description):
                    description[i].update({'number': i + 1, 'status': 'Failed'})
                    if 'DASI' in description[i].keys():
                        del description[i]['DASI']

                emails = [{'headers': headers_dict, 'details': description}]

                env = Environment(loader=FileSystemLoader(self.template_dir))
                template = env.get_template('child.html')
                output = template.render(email=emails[0])
                self.send_emails(mail_id, tolist, 'Failed - FIPS: {} - ICP: {}'.format(fips, icpnumber), output, 'smtp.corelogic.com')

            if len(submission_error) > 0:
                for i, j in enumerate(submission_error):
                    submission_error[i].update({'number': i + 1, 'status': 'Failed'})
                    if 'RLO' in submission_error[i].keys():
                        del submission_error[i]['RLO']

                emails = [{'headers': headers_dict,  'details': submission_error}]

                env = Environment(loader=FileSystemLoader(self.template_dir))
                template = env.get_template('child.html')
                output = template.render(email=emails[0])
                self.send_emails(mail_id, tolist, 'Submission Team: ICP Failure: FIPS: {} - ICP: {} Processing Failed'.format(fips, icpnumber), output, 'smtp.corelogic.com')

        except Exception as e:
            print(str(e))
