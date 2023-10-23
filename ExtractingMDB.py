import os
import csv
import pyodbc
import configparser
from acquisition.CommonUtil.Patterns import PatternMining
from commons.Utility import Utilities
from datetime import datetime
from acquisition.CommonUtil.utilityEmail import utilities, SendEmail
from acquisition.CommonUtil.FTP_Util import FTP_Util
from acquisition.CommonUtil.Common_Util import get_logger, decode_encrypted_psw

log = get_logger('Convert DB files to CSV/TAB')


class ExtractDBFiles_CSV:

    def __init__(self):
        self.state = ''
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        property_file_location = os.path.join(root_dir, "environmentconfig.properties")
        self.config_prop = configparser.RawConfigParser()
        self.config_prop.read(property_file_location)
        self.util_Obj = Utilities()
        self.sendemail = SendEmail()
        self.error_mesg = self.util_Obj.get_json_data('\JsonData\Error_codes.json')
        self.distribution_list_dev = self.config_prop.get("Email", "emaildistributionlistdev").split(",")
        self.emailid = self.config_prop.get("Email", "sender_email")
        self.email_pw = decode_encrypted_psw(self.config_prop.get("Email", "sender_password"))
        self.email = utilities(self.emailid, self.email_pw)
        self.ftp_util_obj = FTP_Util()

    def convert_db_csv(self, filename, file_path, icp_det_obj, pattern_list, file_destination_path, submission_error):

        file_name = folder_path = ''
        try:
            self.state = str(icp_det_obj.get('state')).lower()
            if not os.path.exists(os.path.join(file_path, os.path.splitext(filename)[0])):
                os.mkdir(os.path.join(file_path, os.path.splitext(filename)[0]))
                folder_path = os.path.join(file_path, os.path.splitext(filename)[0])
            else:
                folder_path = os.path.join(file_path, os.path.splitext(filename)[0])

            file = os.path.join(file_path, filename)
            # DRV = '{Driver do Microsoft Access (*.mdb)}'
            DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
            new_con = pyodbc.connect('DRIVER={};DBQ={};'.format(DRV, file))
            new_cur = new_con.cursor()
            main_tables = set([i.table_name for i in new_cur.tables() if i.table_type == "TABLE"])
            log.info('Checking the file name {}'.format(filename))
            log.info('DB Table list {}'.format(main_tables))

            for table_data in list(main_tables):
                final_final_name = ''.join(e for e in table_data if e.isalnum())
                file_name = folder_path + "\\" + str(final_final_name)
                try:
                    new_cur.execute("SELECT * FROM [" + table_data + "]")
                    with open(file_name + '.csv', 'w', newline='') as f:
                        writer = csv.writer(f)
                        headers = [header_data[0] for header_data in new_cur.description]
                        writer.writerow(headers)
                        for row in new_cur.fetchall():
                            try:
                                row_to_list = [self.clean_up_non_printable(elem) for elem in row]
                                writer.writerow(row_to_list)
                            except Exception as e:
                                continue
                except Exception as e:
                    self.exception_csv_file(new_cur, table_data, file_name)
                    log.info('Calling exception_csv_file Method')
                    log.info('>> Error message:{0}'.format(e.args))
            new_cur.close()
            new_con.close()
            pattern = PatternMining(file_destination_path, submission_error)
            folder_path = folder_path + '\\'
            log.info('Process completed')

            return folder_path
        except Exception as e:
            log.error(self.error_mesg["Convert DB To CSV Failure"]+":{}".format(e))
            self.sendemail.send_emails(self.emailid, self.distribution_list_dev, "TRO-CDCSV-000509: Error Alert!!",
                                       "<br>Immediate action needed :<br>"
                                       "<br>DRV: {0}<br>"
                                       "<br>Error Details:  {1}<br>".format("PYODBC", self.error_mesg["Convert DB To CSV Failure"]), 'smtp.corelogic.com')

    def exception_csv_file(self, new_cur, table_data, file_name):
        try:
            new_cur.execute("SELECT * FROM [" + table_data + "]")
            with open(file_name + '.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                headers = [header_data[0] for header_data in new_cur.description]
                writer.writerow(headers)
                row = new_cur.fetchone()
                while row is not None:
                    try:
                        row_to_list = [self.clean_up_non_printable(elem) for elem in row]
                        writer.writerow(row_to_list)
                        row = new_cur.fetchone()
                    except Exception as e:
                        continue
        except Exception as e:
            log.error(e.args)

    def clean_up_non_printable(self, input_to_clean):
        regex_expression = "[\x20-\x7E]"
        input_to_clean = str(input_to_clean).replace('\r\n', " ") if self.state != 'ks' else str(input_to_clean).replace('\r\n', "@")
        input_to_clean = str(input_to_clean).replace('\n\r', " ") if self.state != 'ks' else str(input_to_clean).replace('\n\r', "@")
        input_to_clean = str(input_to_clean).replace('\r', " ") if self.state != 'ks' else str(input_to_clean).replace('\r', "@")
        input_to_clean = str(input_to_clean).replace('\n', " ") if self.state != 'ks' else str(input_to_clean).replace('\n', "@")
        input_to_clean = str(input_to_clean).replace('None', "")
        input_to_clean = str(input_to_clean).replace('\t', " ")
        input_to_clean = str(input_to_clean).replace('\x00', " ")
        input_to_clean = str(input_to_clean).replace("\xB0", "(DEGREES)").replace("\xBA", "(DEGREES)").replace("\xBE", "3/4").replace("\xBD", "1/2").replace("\xBC", "1/4").replace("\x92", "'").replace("\x91", "'")
        input_to_clean = str(input_to_clean).replace("’", "'").replace("\xAD", "-").replace("\x90", " ").replace("\xAC", " ").replace("“", "\\").replace("”", "\\").replace("\x19", "'").replace("\x1A", "")
        input_to_clean = str(input_to_clean).replace(regex_expression, " ")
        return input_to_clean


if __name__ == '__main__':
    icpDetObj = {'icpnumber': '102724', 'fips': ' 20059', 'state': 'KS', 'county': 'FRANKLIN', 'edition': '13', 'version': '1', 'productiontype': 'Full Production Lite', 'businessliaison': 'Irene Eaton', 'noofinputfilesexpcted': '23', 'processedFiles': '', 'SubmissionStatus': 'New -- Complete',
                 'spec_inst_arr': [{'filepassword': '', 'filePath': '/DACQ/WALTER/KANSAS/2019 STATE WIDE', 'dateStamp': datetime(2019, 8, 9, 0, 0), 'fileNameArr': ['Central 2.zip'], 'dasiid': '0020t000000za9fAAA'}],
                 'spec_inst_obj': {'filepassword': '', 'filePath': '/DACQ/WALTER/KANSAS/2019 STATE WIDE', 'dateStamp': datetime(2019, 8, 9, 0, 0), 'fileNameArr': ['Central 2.zip'], 'dasiid': '0020t000000za9fAAA'}}
    filename = "dbo_Bldg.accdb"
    filepath = r"Y:\QA Projects\Prod_Taxrol\EDG_Taxroll\acquisition"
    pattern_list = [()]
    inquiry_error = []
    fileDestinationPath = "Y:\\QA Projects\\Prod_Taxrol\\EDG_Taxroll\\acquisition\\..\\..\\Data Prep\\"
    folder_path = "Y:\\QA Projects\\Prod_Taxrol\\EDG_Taxroll\\acquisition"
    obj = ExtractDBFiles_CSV()
    folder_path1 = obj.convert_db_csv(filename, filepath, icpDetObj, pattern_list, fileDestinationPath, inquiry_error)
    print(folder_path1)