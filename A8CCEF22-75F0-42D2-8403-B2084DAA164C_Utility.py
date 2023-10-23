import os
import shutil
from os import walk
import logging
# import usaddress
import re
import json
from datetime import datetime
from mailer import Mailer
from mailer import Message
dict1 = {}


class Utilities:

    def __init__(self):
        self.vesting_codes_val = []
        self.owner_info = {}
        self.address_info = {}
        self.market_value_info = {}
        self.residence_info = {}
        self.tax_info = {}
        self.legal_info = {}
        self.county_info = {}
        self.tax_info = {}
        self.pcl_id_change_info = {}
        self.land_info = {}
        self.json_data = self.fi_field_info = {}

    # This method will search file in given pathself.county_info['FiUnvCondCd'] = ""
    def serach_file_in_path(self, drive, lctrl):
        try:
            filename = ""
            for root, dir, files in os.walk(drive, topdown=True):
                for file in files:
                    file = file.lower()
                    if file.find(lctrl) > 0:
                        filename = file
                        return filename
        except Exception as e:
            print(e.args)

    # This method will copy file from source to destination
    def copy_file(self, source, destination):
        try:
            shutil.copy(source, destination)
        except Exception as e:
            print(e.args)

    def get_logger(self, modname, logfile, root_dir):
        log = logging.getLogger(modname)
        c_handler = logging.StreamHandler()
        log_file = root_dir + "\\" + logfile + "_{:%m-%d-%Y}.log".format(datetime.now())
        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(name)s %(threadName)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        c_handler.setFormatter(formatter)
        log.addHandler(hdlr)
        log.addHandler(c_handler)
        log.setLevel(logging.INFO)
        return log

    def get_VV_log_file(self, modname, loc, root_di):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log = self.get_logger(modname, loc, root_di)
        return log

    def get_qc_log_file(self, modname, loc):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log = self.get_logger(modname, loc, root_dir)
        return log

    # This method will return all files with extensions from give path
    def file_names_with_extensions(self, path):
        try:
            file_name = []
            for (dirpath, dirnames, filenames) in walk(path):
                file_name.extend(filenames)
                break
            return file_name
        except Exception as e:
            print(e.args)

    # This method will return all files from give path
    def file_names_without_extensions(self, path, extension =''):
        try:
            file_name = self.file_names_with_extensions(path)
            file_names = []
            for fname in file_name:
                filename, file_extension = os.path.splitext(fname)
                if extension == '':
                    file_names.append(os.path.basename(filename))
                elif extension.lower() == file_extension:
                    file_names.append(os.path.basename(filename))
            return file_names
        except Exception as e:
            print(e.args)

    def return_string_list(self, val):
        try:
            return list(filter(None, re.findall(r'([a-zA-Z]+)', val)))
        except Exception as e:
            print(e.args)

    def return_numbers_list(self, val):
        try:
            return list(filter(None, re.findall(r'(\d+)', val)))
        except Exception as e:
            print(e.args)

    def return_string_numbers_list(self, val):
        try:
            return list(filter(None, re.split(r'(\d+)', val)))
        except Exception as e:
            print(e.args)

    def list_to_dict(self, list_value, split_val):
        try:
            result = {}
            for item in list_value:
                text = item.text.split(split_val)
                for key, value in zip(text[::2], text[1::2]):
                    result[key] = value.strip()
            return result
        except Exception as e:
            print(e.args)

    def tuple_to_dict(self, tuple_value):
        try:
            result = {}
            for key, value in tuple_value:
                result[key] = value.strip()
            return result
        except Exception as e:
            print(e.args)

    def address_standardization(self, address):
        try:
            formatted_address = usaddress.tag(address)
            res = self.tuple_to_dict(formatted_address[0].items())
            return res
        except Exception as e:
            print(e.args)

    def string_without_specialchars(self, string):
        try:
            return ''.join(e for e in string if e.isalnum())
        except Exception as e:
            print(e.args)

    def add_leading_number(self, actual_number, leading_val, number_of_leading):
        try:
            res = str(actual_number).rjust(number_of_leading, str(leading_val))
            print("The string after adding leading zeros : " + str(res))
            return res
        except Exception as e:
            print(e.args)

    def owner_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'owner_information')['column_names'][0]
            for fields in fields_data:
                self.owner_info[fields] = ''
            return self.owner_info
        except Exception as e:
            print(e.args)

    def address_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'owner_address')['column_names'][0]
            for fields in fields_data:
                self.address_info[fields] = ''

            return self.address_info
        except Exception as e:
            print(e.args)

    def market_valuation_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'market_information')['column_names'][0]
            for fields in fields_data:
                self.market_value_info[fields] = ''

            return self.market_value_info
        except Exception as e:
            print(e.args)

    def legal_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'legal_information')['column_names'][0]
            for fields in fields_data:
                self.legal_info[fields] = ''

            return self.legal_info
        except Exception as e:
            print(e.args)

    def residence_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'residence_information')['column_names'][0]
            for fields in fields_data:
                self.residence_info[fields] = ''
            return self.residence_info
        except Exception as e:
            print(e.args)

    def tax_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'tax_information')['column_names'][0]
            for fields in fields_data:
                self.tax_info[fields] = ''
            return self.tax_info
        except Exception as e:
            print(e.args)

    def land_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'land_information')['column_names'][0]
            for fields in fields_data:
                self.land_info[fields] = ''

            return self.land_info
        except Exception as e:
            print(e.args)

    def not_required_info_list(self):
        try:
            fields_data = self.get_json_data('\JsonData\dbcolumns.json', 'not_required_fields')['column_names']
            return fields_data
        except Exception as e:
            print(e.args)

    def pcl_id_change_info_list(self):
        try:
            fields_data = ['CompPclId', 'CompPclSeqNbr', 'PclIDIrisFrmtd', 'PclSeqNbr', 'PrevPclId', 'PrevPclIdFrmtd', 'PrevPclSeqNbr', 'IrisSecKey']
            for fields in fields_data:
                self.pcl_id_change_info[fields] = ''

            return self.pcl_id_change_info
        except Exception as e:
            print(e.args)

    def vesting_codes(self):
        try:
            self.vesting_codes_val = ['99', 'AS', 'CE', 'CF', 'CO', 'CP', 'CT', 'ES', 'EX', 'GD', 'GF', 'GM', 'IT', 'JT', 'JV', 'LB', 'LE', 'LF', 'LP', 'LT', 'NT', 'PR', 'PS', 'PT', 'RM', 'RS', 'RT', 'SE', 'SO', 'SP', 'SU', 'TC', 'TE', 'TR', 'TS', 'TY', 'UI', 'XX']
            return self.vesting_codes_val
        except Exception as e:
            print(e.args)

    def compare_data(self, exp_val, act_val):
        try:
            flag = False
            if self.string_without_specialchars(str(exp_val).lower()) in self.string_without_specialchars(str(act_val).lower()) or (
                    self.string_without_specialchars(str(exp_val).lower()) == 'none' and self.string_without_specialchars(str(act_val).lower()) == '')or \
                    (self.string_without_specialchars(str(exp_val).lower()) == 'none'):
                flag = True
            return flag
        except Exception as e:
            print(e.args)

    def inc_compare_data(self, exp_val, act_val, col_name, pass_col, fail_col, log):
        try:
            if self.compare_data(exp_val, act_val) is True:
                if col_name in pass_col.keys():
                    pass_col[col_name] = pass_col[col_name] + 1
                else:
                    pass_col[col_name] = 1
            else:
                print('Failed Column Name: ' + str(col_name) + '  Expected Data: ' + str(exp_val))
                log.info('Failed Column Name: ' + str(col_name) + '  Expected Data: ' + str(exp_val))
                # print('Column Name: ' + str(col_name) + '  Expected Data: ' + str(exp_val) + ' -- Actual Data: ' + str(act_val))
                if col_name in fail_col.keys():
                    fail_col[col_name] = fail_col[col_name] + 1
                else:
                    fail_col[col_name] = 1
        except Exception as e:
            print(e.args)

    def get_json_data(self, json_path, var_val=''):
        try:
            loc_json = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + json_path
            with open(loc_json) as json_file:
                self.json_data = json.load(json_file)
            if var_val == '':
                return self.json_data
            else:
                return self.json_data[var_val]
        except Exception as e:
            print(e.args)

    def change_address_text_to_number(self, address):
        try:
            address_text = {'ZERO': '0TH', 'FIRST': '1ST', 'SECOND': '2ND', 'THIRD': '3RD', 'FOURTH': '4TH', 'FIFTH': '5TH', 'SIXTH': '6TH', 'SEVENTH': '7TH', 'EIGHTH': '8TH', 'NINTH': '9TH', 'TENTH': '10TH', 'ELEVENTH': '11TH', 'TWELFTH': '12TH', 'THIRTEENTH': '13TH',
                            'FOURTEENTH': '14TH', 'FIFTEENTH': '15TH', 'SIXTEENTH': '16TH', 'SEVENTEENTH': '17TH', 'EIGHTEENTH': '18TH', 'NINETEENTH': '19TH', 'TWENTY': '20TH', 'THIRTY': '30TH', 'FORTY': '40TH', 'FIFTY': '50TH', 'SIXTY': '60TH',
                            'SEVENTY': '70TH', 'EIGHTY': '80TH', 'NINETY': '90TH'}
            for address_numbers in address_text.keys():
                if address_numbers in address:
                    address = address.replace(address_numbers, address_text[address_numbers])
            return address
        except Exception as e:
            print(e.args)

    def get_values_from_list(self, table):
        new = table.replace('$', '').replace(',', '').replace('+', '').replace('=', '').replace('.', '').split()
        digit = [s for s in new if s.isdigit()]
        return digit

    def send_emails(self, mail_id, tolist, email_sub, email_body, smtp):
        try:
            message = Message(From=mail_id, To=tolist)
            message.Subject = email_sub
            message.Html = email_body
            sender = Mailer(smtp)
            sender.send(message)
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    obj = Utilities()
    print(obj.address_standardization('107 FIRST ST ALLENPORT ST'))

