import configparser
import base64
import shutil
import re
import os
import tempfile
import gc
import csv
import logging
import time
import datetime
import traceback
from fuzzywuzzy import fuzz
from os import listdir
from os.path import isfile, join
from operator import itemgetter
from commons.Utility import Utilities
from pathlib import Path
from datetime import datetime
from dateutil import parser
from acquisition.CommonUtil import RestApi
from acquisition.CommonUtil.database import Database
# from acquisition.ApiUtil.salesforceApi import SalesforceApi
from acquisition.CommonUtil.USA_State_Codes import state_code_name_mapping
# from acquisition.CommonUtil.LoggerUtility import get_logger


stm = datetime.now().strftime('%H:%M:%S.%f')[:-3]


class TimeFilter(logging.Filter):
    def filter(self, record):
        global stm
        record.relative = stm
        stm = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        return True


def get_logger(modname, dp_log=False):
    try:
        utilObj = Utilities
        qc_config_jsonData = utilObj.get_json_data(utilObj, '\JsonData\qcconfig.json')
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log = logging.getLogger(modname)
        c_handler = logging.StreamHandler()
        if dp_log:
            log_loc = root_dir + "\\" + qc_config_jsonData['Dataprep_log_loc']
        else:
            log_loc = root_dir + "\\" + qc_config_jsonData['submission_log_loc']
        # if os.path.exists(log_loc):
        #     log_file = log_loc + qc_config_jsonData['submission_file'] + "_{:%m-%d-%Y}.log".format(datetime.now())
        # else:
        path = Path(log_loc)
        path.mkdir(parents=True, exist_ok=True)
        if dp_log:
            log_file = log_loc + qc_config_jsonData['dataprep_file'] + "_{:%m-%d-%Y}.log".format(datetime.now())
        else:
            log_file = log_loc + qc_config_jsonData['submission_file'] + "_{:%m-%d-%Y}.log".format(datetime.now())
        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '[%(levelname)s] [%(relative)s] [%(asctime)s.%(msecs)03d] [%(name)s %(threadName)s]: %(message)s',
            datefmt='%H:%M:%S')
        hdlr.setFormatter(formatter)
        c_handler.setFormatter(formatter)
        log.addHandler(hdlr)
        log.addHandler(c_handler)
        log.setLevel(logging.INFO)
        for hndl in log.handlers:
            hndl.addFilter(TimeFilter())
        # log = logging.LoggerAdapter(log, extra)
        return log
    except Exception as e:
        print(e.args)


def validate_special_inst_format(icp_details_obj, sp_inst_details, inquiry_error):
    """Get Date Stamp, file location, DASI Special instructions Notes """
    file_path_pattern = "FOLDER/FILE:"
    file_path_pattern2 = "FOLDER:"
    date_stamp_pattern = "DATE STAMP:"
    filename = "FILE NAME:"
    password_pattern = "PASSWORD:"
    spec_inst_arr = []
    spec_inst_obj = None
    if len(sp_inst_details) > 0:
        for spec_inst in sp_inst_details:
            try:
                text_value = spec_inst[0]
                if text_value is None:
                    inquiry_error.extend(
                        [{"filename": '', "reason": 'DASI notes missing', "filetype": '', 'DASI': 'yes'}])
                else:
                    db_dasi_date = str(spec_inst[1]).split(' ')[0]
                    format_date = time.strptime(db_dasi_date, '%Y-%m-%d')
                    dasi_created_date = time.strftime('%m/%d/%Y', format_date)
                    status = spec_inst[2]
                    dasi_id = spec_inst[3]
                    spec_inst_obj = {"filepassword": ""}
                    for x in text_value.split("\n"):
                        x = x.strip()
                        if len(x) > 0:
                            if str(x).upper().find(file_path_pattern) != -1:
                                x = ': /DACQ'.join(x.split(": ")) if ('dacq' not in x.lower()) else x
                                spec_inst_obj["filePath"] = x[str(x).upper().find(file_path_pattern) + len(
                                    file_path_pattern):].strip()
                            elif str(x).upper().find(file_path_pattern2) != -1:
                                x = ': /DACQ'.join(x.split(": ")) if ('dacq' not in x.lower()) else x
                                x = ': /'.join(x.split(": ")) if ('/dacq' not in x.lower()) else x
                                spec_inst_obj["filePath"] = x[str(x).upper().find(file_path_pattern2) + len(
                                    file_path_pattern2):].strip()
                            elif str(x).upper().find(password_pattern) != -1:
                                spec_inst_obj["filepassword"] = x[str(x).upper().find(password_pattern) + len(
                                    password_pattern):].strip()
                            elif str(x).upper().find(date_stamp_pattern) != -1:
                                date_stamp = x[str(x).upper().find(date_stamp_pattern) + len(date_stamp_pattern):]
                                if date_stamp != '':
                                    spec_inst_obj["dateStamp"] = parser.parse(date_stamp)
                                else:
                                    spec_inst_obj["dateStamp"] = 0
                            elif str(x).upper().find(filename) != -1:
                                file = x[str(x).upper().find(filename) + len(filename):].strip()
                                if file != '':
                                    file_name = [file]
                                    spec_inst_obj["fileNameArr"] = file_name
                                else:
                                    spec_inst_obj["fileNameArr"] = ''
                            elif str(x).upper().find('FIIE NAME:') != -1:
                                file = x[str(x).upper().find('FIIE NAME:') + len('FIIE NAME:'):].strip()
                                if file != '':
                                    file_name = [file]
                                    spec_inst_obj["fileNameArr"] = file_name
                                else:
                                    spec_inst_obj["fileNameArr"] = ''
                    spec_inst_obj["dasiid"] = dasi_id
                    spec_inst_obj["invdatestamp"] = dasi_created_date
                    if len(spec_inst_obj["fileNameArr"]) > 0 and spec_inst_obj["dateStamp"] and spec_inst_obj[
                        "filePath"]:
                        spec_inst_arr.append(spec_inst_obj)
                    else:
                        if len(spec_inst_obj["fileNameArr"]) == 0:
                            inquiry_error.extend([{"filename": '', "reason": 'File is missing in DASI notes',
                                                   "filetype": '', 'DASI': 'yes'}])
                        if spec_inst_obj["dateStamp"] == 0:
                            inquiry_error.extend([{"filename": '', "reason": 'Date Stamp missing in DASI notes',
                                                   "filetype": '', 'DASI': 'yes'}])
                        if len(spec_inst_obj["filePath"]) == 0:
                            inquiry_error.extend([{"filename": '', "reason": 'File path is missing in DASI notes',
                                                   "filetype": '', 'DASI': 'yes'}])
            except Exception as e:
                inquiry_error.extend([{"filename": spec_inst[0].replace("\r\n", ""),
                                       "reason": 'DASI notes are not in correct format', "filetype": '',
                                       'DASI': 'yes'}])
    else:
        inquiry_error.extend([{"filename": '', "reason": 'DASI notes missing', "filetype": '', 'DASI': 'yes'}])

    """ Data Validations """
    icp_details_obj["spec_inst_arr"] = spec_inst_arr


def decode_encrypted_psw(encrypsw):
    try:
        value = base64.b64decode(encrypsw).decode('ascii')
        return value
    except Exception as e:
        log.error(e.args)


def fuzzy_similarity(data, Str1):
    """
    :param data: List of previous edition files
    :param Str1: Current edition file
    :return: Percentage matched current edition with prev edition files
    """
    try:
        scores = []
        for i in data:
            Ratio = fuzz.ratio(Str1.lower(), i.lower())
            Partial_Ratio = fuzz.partial_ratio(Str1.lower(), i.lower())
            scores.append(Partial_Ratio)
        return scores
    except Exception as e:
        log.error(e.args)


def fuzzy_similarity_ratio(data, Str1):
    """
    :param data: previous edition file
    :param Str1: Current edition file
    :return: Percentage matched current edition with prev edition files
    """
    try:
        Ratio = fuzz.ratio(data.lower(), Str1.lower())
        return Ratio
    except Exception as e:
        log.error(e.args)


def extract_numbers(filename):
    try:
        out_file = ''.join([i for i in filename if not i.isdigit()])
        return out_file
    except Exception as e:
        log.error(e.args)


def matched_file(prev_edition, current_edition):
    try:
        output = [extract_numbers(prev_edition), extract_numbers(current_edition)]
        score = fuzzy_similarity_ratio(output[0], output[1])
        if score == 100 or output[0] == output[1]:
            return prev_edition
        else:
            return False
    except Exception as e:
        log.error(e.args)


log = get_logger('Move file')


class FileHandling:

    def __init__(self, file_destination_path):
        self.file_destination_path = file_destination_path
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.property_file_location = os.path.join(self.root_dir, "environmentconfig.properties")
        self.config_prop = configparser.RawConfigParser()
        self.config_prop.read(self.property_file_location)

        self.property_file_location = os.path.join(self.root_dir, "appconfig.properties")
        self.app_config_prop = configparser.RawConfigParser()
        self.app_config_prop.read(self.property_file_location)

        self.sql_connection_type = self.config_prop.get("DATABASE", "conn_type")
        self.sql_server_name = self.config_prop.get("DATABASE", "server")
        self.sql_icp_update_db = self.config_prop.get("DATABASE", 'icp_update_db')
        self.sql_icp_user = self.config_prop.get("DATABASE", 'icp_user')
        self.sql_icp_password = decode_encrypted_psw(self.config_prop.get("DATABASE", 'icp_password'))
        self.db_util = Database.taxroll_db_initialize(self.config_prop, self.app_config_prop)
        self.util_Obj = Utilities()
        self.error_msg = self.util_Obj.get_json_data('\JsonData\Error_codes.json')
        self.bothreorder_status = self.app_config_prop.get("value_list", "newreorder_status")

    def move_file(self, folder_path, file_name, icp_details_obj, is_other, RLO=False):
        try:
            file_path = os.path.join(folder_path, file_name)
            dest_path = self.prepare_file_dest_dir(icp_details_obj, is_other, False, is_rec_layout=RLO)
            log.info(">> Source File: {}, Destination File: {}".format(file_path, dest_path))
            name = os.path.basename(file_path)
            sub_status = icp_details_obj.get("SubmissionStatus")
            reorder_location = ''
            if is_other:
                location = 'Other'
            elif RLO:
                location = 'Record Layouts'
            else:
                location = 'Current Edition'

            if sub_status in self.bothreorder_status:
                if is_other:
                    reorder_location = 'OTHER-REORDER'
                elif RLO:
                    reorder_location = 'Record Layouts'
                else:
                    reorder_location = 'FILES-REORDER'

            icp_number = icp_details_obj.get('icpnumber')
            dasi_file_path = icp_details_obj.get('dasi_file_path')
            dasi_file_name = icp_details_obj.get('dasi_file_name')
            dasi_date = icp_details_obj.get('dasi_date_stamp')
            act_file_path = str(file_path).split("TAX_ROLL")[1].split(file_name)[0]

            if not os.path.exists(os.path.join(dest_path, name)):
                shutil.move(file_path, os.path.join(dest_path, name))
                # Update File inventory table
                if sub_status in self.bothreorder_status:
                    self.db_util.insert_update_data(self.db_util.fileinventory_insert_query.format(icp_number, reorder_location, dasi_file_path, dasi_file_name, act_file_path, file_name, dasi_date))
                else:
                    self.db_util.insert_update_data(self.db_util.fileinventory_insert_query.format(icp_number, location, dasi_file_path, dasi_file_name, act_file_path, file_name, dasi_date))

            else:
                base, extension = os.path.splitext(name)
                i = 1
                while os.path.exists(os.path.join(dest_path, '{}({}){}'.format(base, i, extension))):
                    i += 1
                shutil.move(file_path, os.path.join(dest_path, '{}({}){}'.format(base, i, extension)))
                # Update File inventory table
                if sub_status in self.bothreorder_status:
                    self.db_util.insert_update_data(self.db_util.fileinventory_insert_query.format(icp_number, reorder_location, dasi_file_path, dasi_file_name, act_file_path, file_name, dasi_date))
                else:
                    self.db_util.insert_update_data(self.db_util.fileinventory_insert_query.format(icp_number, location, dasi_file_path, dasi_file_name, act_file_path, file_name, dasi_date))

            log.info(">> File Moved to: " + dest_path)
        except Exception as e:
            log.error(self.error_msg["Move File Method Failure"])
            log.error(e.args)

    def copy_file(self, folder_path, file_name, icp_details_obj, RLO=False):
        try:
            file_path = os.path.join(folder_path, file_name)
            dest_path = self.prepare_file_dest_dir(icp_details_obj, False, False, is_rec_layout=RLO)
            log.info(">> Source File: {}, Destination File: {}".format(file_path, dest_path))
            name = os.path.basename(file_path)

            if not os.path.exists(os.path.join(dest_path, name)):
                shutil.copy(file_path, os.path.join(dest_path, name))
            else:
                base, extension = os.path.splitext(name)
                i = 1
                while os.path.exists(os.path.join(dest_path, '{}({}){}'.format(base, i, extension))):
                    i += 1
                shutil.copy(file_path, os.path.join(dest_path, '{}({}){}'.format(base, i, extension)))
            log.info(">> File Copied to: " + dest_path)
        except Exception as e:
            log.error(e.args)

    def prepare_file_dest_dir(self, icp_details_obj, is_other, is_prev, is_rec_layout=False):
        """ Prepares Destionation path for processed files """
        try:
            county = icp_details_obj.get("county")
            state_code = icp_details_obj.get("state")
            state = state_code_name_mapping.get(state_code)
            des_path = ""
            if is_prev:
                des_path = self.file_destination_path + "{0}\\{1}\\Prior Edition\\".format(state.upper(),
                                                                                           county.upper())
            elif is_rec_layout:
                des_path = self.file_destination_path + "{0}\\{1}\\Record Layouts\\".format(state.upper(),
                                                                                            county.upper())
            elif is_other:
                des_path = self.file_destination_path + "{0}\\{1}\\Other\\{2}\\".format(state.upper(), county.upper(),
                                                                                        icp_details_obj.get(
                                                                                            'icpnumber'))
            else:
                des_path = self.file_destination_path + "{0}\\{1}\\Current Edition\\{2}\\".format(state.upper(),
                                                                                                  county.upper(),
                                                                                                  icp_details_obj.get(
                                                                                                      'icpnumber'))

            prior_path = self.file_destination_path + "{0}\\{1}\\Prior Edition\\".format(state.upper(), county.upper())
            rlo_path = self.file_destination_path + "{0}\\{1}\\Record Layouts\\".format(state.upper(), county.upper())
            other_path = self.file_destination_path + "{0}\\{1}\\Other\\{2}\\".format(state.upper(), county.upper(),
                                                                                      icp_details_obj.get('icpnumber'))
            current_path = self.file_destination_path + "{0}\\{1}\\Current Edition\\{2}\\".format(state.upper(),
                                                                                                  county.upper(),
                                                                                                  icp_details_obj.get(
                                                                                                      'icpnumber'))

            if not os.path.exists(prior_path):
                os.makedirs(prior_path)
            if not os.path.exists(rlo_path):
                os.makedirs(rlo_path)
            if not os.path.exists(other_path):
                os.makedirs(other_path)
            if not os.path.exists(current_path):
                os.makedirs(current_path)
            return des_path
        except Exception as e:
            log.error(self.error_msg["Create Dir's Failure"])
            log.error(e.args)

    def get_file_dest_dir(self, icp_number, county, state_code, is_other, is_prev, is_rec_layout=False):
        try:
            """ Prepares Destionation path for processed files """
            county = county
            state_code = state_code
            state = state_code_name_mapping.get(state_code)

            if is_prev:
                des_path = self.file_destination_path + "{0}\\{1}\\Prior Edition\\{2}\\".format(state.upper(),
                                                                                                county.upper(),
                                                                                                icp_number)
            elif is_rec_layout:
                des_path = self.file_destination_path + "{0}\\{1}\\Record Layouts\\".format(state.upper(),
                                                                                            county.upper())
            elif is_other:
                des_path = self.file_destination_path + "{0}\\{1}\\Other\\{2}\\".format(state.upper(), county.upper(),
                                                                                        icp_number)
            else:
                des_path = self.file_destination_path + "{0}\\{1}\\Current Edition\\{2}\\".format(state.upper(),
                                                                                                  county.upper(),
                                                                                                  icp_number)

            return des_path
        except Exception as e:
            log.error(e.args)

    def prepare_file_destination_dir_reorder(self, icp_details_obj, full_reorder=False):
        """ Prepares Destionation path for reorder """
        try:
            county = icp_details_obj.get("county")
            state_code = icp_details_obj.get("state")
            state = state_code_name_mapping.get(state_code)
            date_stamp = datetime.today().strftime('%Y-%m-%d %H-%M-%S')
            prev_path = self.file_destination_path + "{0}\\{1}\\Prior Edition\\{2}\\".format(state.upper(),
                                                                                             county.upper(),
                                                                                             icp_details_obj.get(
                                                                                                 'icpnumber'))
            prev_rename_path = self.file_destination_path + "{0}\\{1}\\Prior Edition\\{2}_reorder_{3}\\".format(
                state.upper(), county.upper(), icp_details_obj.get('icpnumber'), date_stamp)
            current_edition_path = self.file_destination_path + "{0}\\{1}\\Current Edition\\{2}\\".format(state.upper(),
                                                                                                          county.upper(),
                                                                                                          icp_details_obj.get(
                                                                                                              'icpnumber'))
            if full_reorder:
                other_path = self.file_destination_path + "{0}\\{1}\\Other\\{2}\\".format(state.upper(), county.upper(),
                                                                                          icp_details_obj.get(
                                                                                              'icpnumber'))
                other_rename_path = self.file_destination_path + "{0}\\{1}\\Other\\{2}_reorder_{3}\\".format(
                    state.upper(), county.upper(), icp_details_obj.get('icpnumber'), date_stamp)
                if os.path.exists(other_path):
                    os.rename(other_path, other_rename_path)
            if os.path.exists(prev_path):
                os.rename(prev_path, prev_rename_path)
            if not os.path.exists(current_edition_path):
                os.makedirs(current_edition_path)

            return prev_rename_path, current_edition_path

        except Exception as ex:
            log.error(f'>> Error: Re-order prepare_file_destination_dir_reorder{ex.args}')
            log.error(self.error_msg["Create Dir's Failure"])
            traceback.print_exc()

    def reorder_files(self, reorder_problem_files, dp_results, prev_rename_path, current_edition_path, icp_details_obj):
        try:
            raw_file_names = []
            if dp_results is None: dp_results = []
            if os.path.exists(prev_rename_path) and len(reorder_problem_files) > 0:
                if not icp_details_obj.get("state") == "MI":
                    problem_files_all = max(reorder_problem_files, key=itemgetter(1))[0]
                    problem_files_list = problem_files_all.split('\r\n')
                    for problem_files in problem_files_list:
                        for tuple in dp_results:
                            if problem_files == tuple[1]:
                                file_name = tuple[0]
                                raw_file_names.append(file_name)

                log.info(f'>> Re-order RAW File names: {raw_file_names}')

                if icp_details_obj.get("state") == "MI":
                    problem_files_all = max(reorder_problem_files, key=itemgetter(1))[0]
                    problem_files_list = problem_files_all.split('\r\n')
                    raw_file_names = problem_files_list

                prev_edition_files = [files for files in listdir(prev_rename_path) if
                                      isfile(join(prev_rename_path, files))]
                log.info(f'>> Re-order Previous Edition files list: {prev_edition_files}')

                for file in raw_file_names:
                    if file in prev_edition_files:
                        prev_edition_files.remove(file)

                log.info(f'>> Re-order Previous Edition good files: {prev_edition_files}')

                for prev_file in prev_edition_files:
                    base, extension = os.path.splitext(prev_file)
                    i = 1
                    while os.path.exists(os.path.join(current_edition_path, '{}({}){}'.format(base, i, extension))):
                        i += 1
                    shutil.move(os.path.join(prev_rename_path, prev_file),
                                os.path.join(current_edition_path, '{}{}'.format(base, extension)))
                    log.info(
                        f'>> Re-order Previous edition file: {prev_file} move to current edition folder {current_edition_path}')
                    # shutil.move(os.path.join(prev_rename_path, prev_file), current_edition_path)
            else:
                log.info(f'There are no reorder problem files {reorder_problem_files}')
        except Exception as ex:
            log.error(ex.args)
            traceback.print_exc()

    def check_files_others(self, icp_details_obj, current_filename):
        Others_files = []
        other_files_base = []
        try:
            other_path_icp = self.prepare_file_dest_dir(icp_details_obj, True, False)
            other_path = other_path_icp.rstrip('{}\\'.format(icp_details_obj.get('icpnumber')))
            others_files_list = [files for files in listdir(other_path) if isfile(join(other_path, files))]

            for file_name in others_files_list:
                base, extension = os.path.splitext(file_name)
                Others_files.append(re.sub(r"[^a-zA-Z]", "", base) + extension)
                other_files_base.append(re.sub(r"[^a-zA-Z]", "", base))

            base, extension = os.path.splitext(current_filename)
            file_search = (re.sub(r"[^a-zA-Z]", "", base) + extension)
            file_base = re.sub(r"[^a-zA-Z]", "", base)
            log.info(f'>> Checking File name {file_search} with extension in Others folder')
            log.info(f'>> Checking File name {file_base} without extension in Others folder')

            if next(filter(lambda x: x.lower() == str(file_search).lower().replace('"', ''), Others_files),
                    None) is not None:
                log.info('Moving the file to other location {}'.format(current_filename))
                gc.collect()
                return True
            else:
                gc.collect()
                return False
        except Exception as ex:
            log.error(">> Error in check files others: {0}".format(str(ex.args)))


    def check_files_used_by_qda(self, api_response_data, current_filename, file_path, icp_details_obj, inquiry_error,
                                sheet_name, num_rows):
        base, extension = os.path.splitext(current_filename)
        file_search = (re.sub(r"[^a-zA-Z]", "", base) + extension)
        formatted_base_name = re.sub(r"[^a-zA-Z]", "", base)
        flag = 'No File Found'
        header_row1 = []
        header_row2 = []
        delim = ','
        file_type = 'Delim'
        full_pah_file_name = os.path.join(file_path, current_filename)
        gc.collect()
        try:
            for json_data in api_response_data:
                if json_data.get('BLFileName') is not None:
                    bl_base, bl_extension = os.path.splitext(json_data.get('BLFileName'))
                    if extension.lower() == '.xls' or extension.lower() == '.xlsx':
                        sheet_valid = False
                        if bl_extension == extension and sheet_name in json_data['Formatted_API_File_Name'].lower():
                            sheet_valid = True

                        if json_data['Formatted_BL_FileName'].lower() == str(file_search).lower() or json_data['BL_FileName_Base'].lower() == formatted_base_name.lower() or sheet_valid:
                            if json_data['usedByQDA']:
                                self.check_records_threshold_xlsx(inquiry_error, json_data['IsDriver'],json_data['recordCount'], json_data['BLFileName'],current_filename, num_rows)
                                flag = False
                                break
                            else:
                                flag = True
                    elif json_data['Formatted_BL_FileName'].lower() == str(file_search).lower().replace('"', '') or \
                            json_data['BL_FileName_Base'].lower() == str(
                            re.sub(r"[^a-zA-Z]", "", base)).lower().replace('"', ''):
                        if json_data['usedByQDA']:

                            lines_data, delim1, delim2 = self.get_file_type(full_pah_file_name, 20, 20)
                            if delim1 == '^' and delim2 == ',': delim1 = ','
                            if delim1.upper() != 'FIXED':
                                column_names = []
                                formatted_columns_names = []
                                for cname in json_data['fields']:
                                    column_names.append(cname['fieldName'].lower())
                                    formatted_columns_names.append(re.sub(r"[^a-zA-Z]", "", cname['fieldName'].lower()))

                                delim1_header_check = self.header_check(file_path, current_filename, delim1)

                                if delim1_header_check:
                                    print('File has headers')
                                    log.info('File has headers')
                                else:
                                    header_row1 = lines_data[0].split(delim1)
                                    header_row2 = lines_data[0].split(delim1)
                                    delim = self.return_delim(header_row1, header_row2, column_names, delim1, delim2)

                                    log.info('Header row1: {0}'.format(header_row1))
                                    log.info('Header row2: {0}'.format(header_row2))
                                    log.info('Column Names: {0}'.format(column_names))
                                    tmpdir = tempfile.mkdtemp()
                                    predictable_filename = 'myfile'
                                    path = os.path.join(tmpdir, predictable_filename)
                                    try:
                                        with open(path, "w", encoding="ANSI") as tmp:
                                            tmp.write(delim.join(column_names) + '\n')
                                            with open(full_pah_file_name, 'r', encoding="ANSI") as dif:
                                                for line in dif:
                                                    tmp.write(line)
                                        tmp.close()
                                        shutil.move(path, full_pah_file_name)
                                    except IOError as e:
                                        log.error(">> IO Error File: {0}".format(str(e.args)))
                                    except Exception as ex:
                                        os.remove(path)
                                        log.error(">> Error in writing file: {0}".format(str(ex.args)))
                            else:
                                file_type = 'Fixed'

                            self.validate_record_count(icp_details_obj, inquiry_error, json_data['IsDriver'],
                                                       json_data['recordCount'], json_data['BLFileName'],
                                                       current_filename, file_path)
                            flag = False
                            break
                        else:
                            flag = True
        except Exception as ex:
            log.error(self.error_msg["Error In Check Files Used By QDA"] + ":{}".format(str(ex.args)))
        gc.collect()
        return flag, file_type

    def return_delim(self, header_row1, header_row2, column_names, delim1, delim2):
        try:
            delim = ','
            get_unknown_count = 0

            for cname in column_names:
                if 'unknown' in str(cname).lower() or 'filler' in str(cname).lower():
                    get_unknown_count = get_unknown_count + 1

            if (len(header_row1) + get_unknown_count == len(column_names) or len(header_row1) + 1 == len(
                    column_names) or len(header_row1) == len(column_names) + 1 or len(header_row1) == len(
                    column_names)) and delim1 != '[':
                delim = delim1
                if delim == '[': delim = delim2
            elif (len(header_row2) + get_unknown_count == len(column_names) or len(header_row2) + 1 == len(
                    column_names) or len(header_row2) == len(column_names) + 1 or len(header_row2) == len(
                    column_names)) and delim2 != '[':
                delim = delim2
                if delim == '[': delim = delim
            elif delim1 == ',' or delim2 == ',':
                delim = delim2
                if delim == '[': delim = delim1

            return delim
        except Exception as ex:
            log.error(">> Error in return_delim: {0}".format(str(ex.args)))

    def get_file_type(self, file_name, line_to_check, lines_to_get):
        try:
            string = 'FileName'
            inc = 0
            num_lines = 0
            delim1 = 'fixed'
            delim2 = None
            num_lines, lines_data = self.get_file_rows(file_name, line_to_check, lines_to_get)

            if string in str(lines_data[0]):
                log.info('Please Delete First row from File')
                inc = 1
                header = len(lines_data[1])
            else:
                header = len(lines_data[0])

            for lines in lines_data:
                inc = inc + 1
                if inc < num_lines:
                    if header != len(lines):
                        delim1, delim2 = self.find_delim(lines_data)
                        log.info(">> Delimiter1: {0}".format(delim1))
                        log.info(">> Delimiter2: {0}".format(delim2))
                        return lines_data, delim1, delim2
                else:
                    result, delim1, delim2 = self.find_fixed_file(lines_data)
                    if result:
                        log.info(">> Delimiter1: {0}".format(delim1))
                        log.info(">> Delimiter2: {0}".format(delim2))
                        return lines_data, delim1, delim2
                    else:
                        return lines_data, 'fixed', None
        except Exception as ex:
            log.error(">> Error in Deimter: {0}".format(str(ex.args)))

    def get_file_rows(self, file_name, line_to_check, lines_to_get):
        try:
            lines_data = []
            with open(file_name, 'rb') as file:
                num_lines = sum(1 for count, i in enumerate(file) if count < line_to_check)

            with open(file_name, 'r', encoding="ANSI") as my_file:
                lines_data = [next(my_file) for x in range(min(lines_to_get, num_lines))]

            log.info(">> Number of lines: {0}".format(num_lines))
            return num_lines, lines_data
        except Exception as ex:
            log.error(">> Error in get file rows: {0}".format(str(ex.args)))

    def find_delim(self, lines_data):
        try:
            data = "".join(lines_data)
            delim = {"[": 0, ";": 0, "|": 0, ",": 0, "\t": 0, "!": 0, "~": 0, "^": 0, "\\t": 0}
            sec_delim = None
            lines = data.splitlines()[:100]
            for line in lines:
                for i, d in enumerate(delim):
                    delim[d] += len(line.split(d))

            max1 = max(delim.values())
            max2 = 0
            for v in delim.keys():
                if (delim[v] > max2 and delim[v] < max1):
                    max2 = delim[v]
                    sec_delim = v
            log.info(">> Delimiter: {0}".format(delim))
            return max(delim, key=delim.get), sec_delim
        except Exception as ex:
            log.error(">> Error in find_delim: {0}".format(str(ex.args)))

    def find_fixed_file(self, lines_data):
        length_data = []
        result_length = False
        delimiter = self.find_delim(lines_data)
        if delimiter == '[' or delimiter == ',':
            return result_length
        try:
            for line in lines_data:
                # row = line.decode("ANSI")
                row_len = len(str(line).split(delimiter[0]))
                length_data.append(row_len)

            result_length = all(elem == length_data[0] for elem in length_data)
            result_check_one = all(elem == 1 for elem in length_data)

            if result_length and result_check_one is False:
                log.info('>> Verified data File is a delimeter file.')
                return True, delimiter[0], delimiter[1]
            else:
                log.info('>> Verified data File is a Fixed file')
                return False, 'Fixed', None

        except Exception as ex:
            log.error(">> Error in find_fixed_file: {0}".format(str(ex.args)))

    def validate_record_count(self, icpDetObj, inquiry_error, isdriver, expected_rec_count, previous_file_name,
                              current_file_name, file_path):
        flag = True
        if icpDetObj.get('county') == 'LOS ANGELES' and icpDetObj.get('state') == 'CA' and icpDetObj.get(
                'productiontype') == 'Automated Update':
            flag = False
        if 'permit' in current_file_name.lower() or 'sale' in current_file_name.lower() or 'deed' in current_file_name.lower() or 'transaction' in current_file_name.lower():
            flag = False

        try:
            if flag:
                full_pah_file_name = os.path.join(file_path, current_file_name)
                line_count = sum(1 for line in open(full_pah_file_name, 'rb'))

                flag = False
                if isdriver == 'Yes' and (
                        line_count > (expected_rec_count * 1.02) or line_count < (expected_rec_count * .98)):
                    flag = True
                if isdriver == 'No' and (
                        line_count < (expected_rec_count * .95) or line_count > (expected_rec_count * 1.05)):
                    flag = True

                if flag:
                    filename = "Current edition {} file record count is {}, previous edition {} file record count is {}".format(
                        current_file_name, line_count, previous_file_name, expected_rec_count)
                    inquiry_error.extend(
                        [{"filename": filename, "reason": 'RecordCount Not Matching.', "filetype": ''}])
        except Exception as ex:
            log.error(">> Error in validate_record_count: {0}".format(str(ex.args)))
            pass

    def validate_file_Other_used_by_qda(self, icp_details_obj, file_name, folder_path, inquiry_error, api_response_data, usedby_qda, extract_sheets='winsrex', num_rows=0):
        try:
            file_path = os.path.join(folder_path, file_name)
            icp_number = icp_details_obj.get('icpnumber')
            dasi_file_path = icp_details_obj.get('dasi_file_path')
            dasi_file_name = icp_details_obj.get('dasi_file_name')
            dasi_date = icp_details_obj.get('dasi_date_stamp')
            act_file_path = str(file_path).split("TAX_ROLL")[1].split(file_name)[0]
            other_dest_path = self.prepare_file_dest_dir(icp_details_obj, True, False)
            sub_status = icp_details_obj.get("SubmissionStatus")

            if sub_status in self.bothreorder_status:
                location = "FILES ARE NOT USED BY QDA-REORDER"
            else:
                location = "FILES ARE NOT USED BY QDA"

            output = self.check_files_others(icp_details_obj, file_name)
            if output:
                self.move_file(folder_path, file_name, icp_details_obj, True)
                return True, 0, 0, 'None'
            if True in usedby_qda:
                used_by_qda, file_type = self.check_files_used_by_qda(api_response_data, file_name, folder_path,icp_details_obj, inquiry_error, extract_sheets,num_rows)
                if used_by_qda == True:
                    shutil.move(os.path.join(folder_path, file_name), os.path.join(other_dest_path, file_name))
                    #self.move_file(folder_path, file_name, icp_details_obj, True)
                    ''''When files are not used by qda for sf_description field '''''
                    self.db_util.insert_update_data(self.db_util.fileinventory_insert_query.format(icp_number, location, dasi_file_path, dasi_file_name, act_file_path, file_name, dasi_date))
                    return True, 1, 0, 'None'
                elif used_by_qda == False:
                    if file_type.upper() != 'FIXED':
                        self.move_file(folder_path, file_name, icp_details_obj, False)
                        return True, 0, 1, 'Delim'
                    else:
                        return True, 0, 1, 'Fixed'
                else:
                    return False, 0, 0, 'None'
            else:
                return False, 0, 0, 'None'
        except Exception as ex:
            log.error(">> Error in validate_file_Other_used_by_qda: {0}".format(str(ex.args)))

    def check_records_threshold_xlsx(self, inquiry_error, isdriver, expected_rec_count, previous_file_name,
                                     current_file_name, line_count):

        try:
            flag = False
            if isdriver == 'Yes' and (
                    line_count > (expected_rec_count * 1.02) or line_count <= (expected_rec_count * .98)):
                flag = True
            if isdriver == 'No' and (
                    line_count < (expected_rec_count * .95) or line_count >= (expected_rec_count * 1.05)):
                flag = True
            if flag:
                if line_count > 1:
                    filename = "Current edition {} file record count is {}, previous edition {} file record count is {}".format(
                        current_file_name, line_count, previous_file_name, expected_rec_count)
                    inquiry_error.extend(
                        [{"filename": filename, "reason": 'RecordCount Not Matching.', "filetype": ''}])
        except Exception as ex:
            log.error(f'>> Error in check_records_threshold_xlsx: {ex.args}')

    @staticmethod
    def get_rec_count_api_response(icp_details_obj, dp_db_util, qda_db_util, sf_db_util, file_destination_path):

        api_response_data = []
        dp_obj = []
        qda_obj = []
        prod_data = []
        query = 'single'
        record_count_obj = {}
        previous_edition_lst = []
        singl_prod_resp = False
        qda_results = []
        dp_results = []
        prod_type = ''
        try:
            prev_edition = int(icp_details_obj.get("edition")) - 1
            state_name = icp_details_obj.get("fullstatename")
            county_name = icp_details_obj.get("county")
            version = icp_details_obj.get("version")
            orginl_prodtyp = icp_details_obj.get("prodtype")
            pre_prod_type = dp_db_util.fetch_data(
                dp_db_util.get_prod_type.format(state_name, county_name, prev_edition, version))
            log.info(f">> state_name {state_name}  - county_name {county_name} - pre_prod_type {pre_prod_type} - prev_edition {prev_edition} - version {version}")

            if orginl_prodtyp in [prod_name[0] for prod_name in pre_prod_type]:
                prod_data.append(orginl_prodtyp)
                prod_type = orginl_prodtyp
                dp_results = dp_db_util.fetch_data(dp_db_util.dp_query_prod_type.format(state_name, county_name, prev_edition, version, prod_type))
                qda_results = qda_db_util.fetch_data(qda_db_util.qda_query_prod_type.format(state_name, county_name, prev_edition, version, prod_type))
                if len(dp_results) > 0:
                    singl_prod_resp = True

            if not singl_prod_resp:
                if len(pre_prod_type) > 1:
                    prod_type = tuple([prod_name[0] for prod_name in pre_prod_type])
                    query = 'multi'
                    prod_data = prod_type
                elif len(pre_prod_type) == 1:
                    prod_type = pre_prod_type[0][0]
                    prod_data.append(prod_type)
                else:
                    prod_type = icp_details_obj.get("prodtype")
                    prod_data.append(prod_type)

            log.info(f">> query results: '{query}'")
            log.info(f">> prod_data results: '{prod_data}'")

            if not singl_prod_resp:
                if query == 'multi':
                    dp_results = dp_db_util.fetch_data(
                        dp_db_util.dp_query.format(state_name, county_name, prev_edition, version, prod_type))
                    qda_results = qda_db_util.fetch_data(
                        qda_db_util.qda_query.format(state_name, county_name, prev_edition, version, prod_type))
                else:
                    dp_results = dp_db_util.fetch_data(
                        dp_db_util.dp_query_prod_type.format(state_name, county_name, prev_edition, version, prod_type))
                    qda_results = qda_db_util.fetch_data(
                        qda_db_util.qda_query_prod_type.format(state_name, county_name, prev_edition, version, prod_type))

            if len(qda_results) > 0:
                qda_obj = [qda_val[0] for qda_val in qda_results]

            log.info(f">> qda_obj results: '{qda_obj}'")

            if len(dp_results) > 0:
                for f_name in dp_results:
                    if f_name[1] in qda_obj:
                        dp_obj.append([f_name[0], f_name[1], f_name[2], 'Yes'])
                        record_count_obj[f_name[0]] = f_name[2]
                        record_count_obj[f_name[1]] = f_name[0]
                        record_count_obj[f_name[0] + "_driver_status"] = 'Yes'
                    else:
                        dp_obj.append([f_name[0], f_name[1], f_name[2], 'No'])
                        record_count_obj[f_name[0]] = f_name[2]
                        record_count_obj[f_name[1]] = f_name[0]
                        record_count_obj[f_name[0] + "_driver_status"] = 'No'

            log.info(f">> record_count_obj results: '{record_count_obj}'")

            for prod_name in prod_data:
                obj = RestApi.GetQDADetails(str(icp_details_obj.get('fips')).strip(), icp_details_obj.get('state'), '', prev_edition, version, prod_name)
                response_prior_edition = obj.get_last_files_used(icp_details_obj)
                for json_data in response_prior_edition['sourceFileInfoList']:
                    api_response_data.append(json_data)

            log.info(f">> api_response_data Before format: '{api_response_data}'")

            # Get all files from previous edition folder
            prev_edition_icp = sf_db_util.fetch_data(sf_db_util.record_county_icp.format(str(prev_edition), version, icp_details_obj.get("productiontype"), icp_details_obj.get('fips')))
            if len(prev_edition_icp) > 0:
                filehandling = FileHandling(file_destination_path)
                prev_edition_path = filehandling.get_file_dest_dir(prev_edition_icp[0][0], county_name, icp_details_obj.get("state"), False, True, False)

                if not os.path.exists(prev_edition_path):
                    previous_edition_lst = []
                else:
                    previous_edition_lst = [files for files in listdir(prev_edition_path) if isfile(join(prev_edition_path, files))]

            for josn_data in api_response_data:
                for f_name in dp_obj:
                    dp_base, dp_ext = os.path.splitext(str(f_name[1]).lower())
                    api_base, api_ext = os.path.splitext(str(josn_data['fileName']).lower())
                    if api_base == dp_base:
                        josn_data['BLFileName'] = f_name[0]
                        josn_data['IsDriver'] = f_name[3]
                        base, extension = os.path.splitext(f_name[0])
                        josn_data['Formatted_BL_FileName'] = (re.sub(r"[^a-zA-Z]", "", base) + extension)
                        josn_data['BL_FileName_Base'] = re.sub(r"[^a-zA-Z]", "", base)
                        josn_data['Formatted_API_File_Name'] = re.sub(r"[^a-zA-Z]", "", str(josn_data['fileName'])).lower().replace('evtab', '')

                    if len(previous_edition_lst) > 0:
                        for prev_file in previous_edition_lst:
                            if api_base == dp_base and f_name[0] == prev_file:
                                josn_data['recordCount'] = filehandling.record_count(prev_file, prev_edition_path)
                            break
                    else:
                        if api_base == dp_base:
                            josn_data['recordCount'] = f_name[2]

            # for josn_data in api_response_data:
            #     for f_name in dp_obj:
            #         for prev_file in previous_edition_lst:
            #             dp_base, dp_ext = os.path.splitext(str(f_name[1]).lower())
            #             api_base, api_ext = os.path.splitext(str(josn_data['fileName']).lower())
            #             if api_base == dp_base and f_name[0] == prev_file:
            #                 josn_data['BLFileName'] = f_name[0]
            #                 josn_data['recordCount'] = filehandling.record_count(prev_file, prev_edition_path)
            #                 josn_data['IsDriver'] = f_name[3]
            #                 base, extension = os.path.splitext(f_name[0])
            #                 josn_data['Formatted_BL_FileName'] = (re.sub(r"[^a-zA-Z]", "", base) + extension)
            #                 josn_data['BL_FileName_Base'] = re.sub(r"[^a-zA-Z]", "", base)
            #                 josn_data['Formatted_API_File_Name'] = re.sub(r"[^a-zA-Z]", "", str(josn_data['fileName'])).lower().replace('evtab', '')
            #                 break
            log.info(f">> api_response_data After format: '{api_response_data}'")

        except Exception as ex:
            log.error(ex.args)
        return record_count_obj, api_response_data

    def header_check(self, folder, filename, delim):
        try:
            with open(os.path.join(folder, filename), 'r') as csvfile:
                head = [next(csvfile) for x in range(10)]
                sample_data = "".join(line for line in head)

                csvfile.seek(0)
                if csv.Sniffer().has_header(sample_data, delim):
                    print(filename, ' - has a header')
                    log.info("Header is present in the file {}".format(filename))
                    return True
                else:
                    print(filename, ' - does not have a header')
                    log.info("No Header found in the file {}".format(filename))
                    return False

        except Exception as ex:
            log.error(ex.args)

    @staticmethod
    def date_match_validation(icp_num_list: list, sf_db_util) -> list:
        # Salesforce API connection
        sf_obj = SalesforceApi()
        new_icp_num_list = []
        try:

            if len(icp_num_list) <= 0:
                return new_icp_num_list

            for icp_details in icp_num_list:
                full_time_stamp = str(icp_details[13]).split(':', 2)[:2]
                last_modified_date = full_time_stamp[0] + ':' + full_time_stamp[1]
                sf_json_icp_data = sf_obj.get_icp_data(str(icp_details[0]))

                if last_modified_date == sf_obj.get_icp_last_modified_date(sf_json_icp_data):
                    try:
                        # returns a list of tuples containing dasi information for queried icp
                        db_dasi_notes = sf_db_util.fetch_data(sf_db_util.spl_inst_query.format(icp_details[0], icp_details[1], icp_details[4], icp_details[5]))
                    except Exception as ex:
                        log.info(ex.args)
                    else:
                        if len(db_dasi_notes) == 0:
                            new_icp_num_list.append(icp_details)

                        # create icp Object
                        icp_data_obj = sf_obj.create_icp_obj(sf_json_icp_data)
                        # get ICP notes in JSON format
                        json_icp_notes = sf_obj.get_icp_notes(icp_data_obj)
                        # get ICP notes dict list
                        sf_dasi_notes = sf_obj.create_dasi_obj(json_icp_notes)

                        flag = False
                        for db_notes in db_dasi_notes:
                            query_note_id = db_notes[3]
                            dasi_last_modified_date = str(db_notes[4])[:16]

                            flag = True if query_note_id in sf_dasi_notes.keys() else False
                            flag = True if dasi_last_modified_date == sf_dasi_notes[query_note_id][0] and flag else False
                        if flag:
                            new_icp_num_list.append(icp_details)

            log.info('-> new_icp_num_list: {}'.format(new_icp_num_list))
        except Exception as ex:
            log.error(ex.args)
        return new_icp_num_list

    def record_count(self, filename, folderpath):
        try:
            full_path_file_name = os.path.join(folderpath, filename)
            line_count = sum(1 for line in open(full_path_file_name, 'rb'))
            return line_count
        except Exception as ex:
            log.error(ex.args)
