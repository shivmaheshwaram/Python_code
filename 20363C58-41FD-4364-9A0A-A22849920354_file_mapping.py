import os
import xlrd
import traceback
from acquisition.CommonUtil.Common_Util import FileHandling


class FileMapping:

    def __init__(self):
        print('happy')

    def intersecting_file(self, sub_path: str, current_fname: str) -> list:
        try:
            previous_files = []
            file_handling = FileHandling(current_fname)
            print('Current filename: {}'.format(current_fname))

            current_lines_data, current_delim1, current_delim2 = file_handling.get_file_type(current_fname, 20, 20)
            if current_delim1 == '^' and current_delim2 == ',': current_delim1 = ','
            current_file_line_len = len(current_lines_data[0])

            for (dirpath, dirnames, filenames) in os.walk(os.path.join(sub_path, 'previous_edition')):
                previous_files += [os.path.join(dirpath, file) for file in filenames]

            for prev_file in previous_files:
                print('Previous filename: {}'.format(prev_file))
                prev_lines_data, prev_delim1, prev_delim2 = file_handling.get_file_type((prev_file), 20, 20)
                if prev_delim1 == '^' and prev_delim2 == ',': prev_delim1 = ','
                prev_file_line_len = len(prev_lines_data[0])
                if current_delim1.upper() == 'FIXED':
                    if current_file_line_len == prev_file_line_len:
                        return prev_file
                    break
                else:
                    output = self.compare_columns(current_lines_data, prev_lines_data, current_delim1, prev_delim1)
                    if output:
                        return prev_file
        except Exception as e:
            traceback.print_exc()

    def excel_file_match(self, filename: str, sub_path: str):
        previous_files = []
        try:
            for (dirpath, dirnames, filenames) in os.walk(os.path.join(sub_path, 'previous_edition')):
                previous_files += [os.path.join(dirpath, file) for file in filenames]

            excel_sheet = xlrd.open_workbook(filename)
            sheet = excel_sheet.sheet_by_index(0)
            current_header = sheet.row_values(0)

            for prev_file in previous_files:
                if prev_file.lower().endswith(".xlsx") or prev_file.lower().endswith(".xls") or prev_file.lower().endswith(".xlsb"):
                    excel_sheet = xlrd.open_workbook(prev_file)
                    sheet = excel_sheet.sheet_by_index(0)
                    prev_header = sheet.row_values(0)
                    if current_header == prev_header:
                        return prev_file
        except Exception as e:
            traceback.print_exc()

    def compare_columns(self, current_lines_data, prev_lines_data, current_delim1, prev_delim1):
        try:
            current_column_len = current_lines_data[0].split(current_delim1)
            prev_column_len = prev_lines_data[0].split(prev_delim1)
            if current_column_len == prev_column_len:
                return True
            else:
                return False
        except Exception as e:
            traceback.print_exc()


def main():
    # root_path = 'C://Users//gbasiri//Documents//testing_joanna//OH NOBLE'
    try:
        root_path = 'C://Users//gbasiri//Documents//testing_joanna//Carver_County_Tax_Data'
        # current_file_path = 'C://Users//gbasiri//Documents//testing_joanna//OH NOBLE//OH//NOBLE//new_edition//'
        current_file_path = 'C://Users//gbasiri//Documents//testing_joanna//Carver_County_Tax_Data//new_edition//'
        # state = 'OH'
        state = 'MN'
        # county = 'NOBLE'
        county = 'CARVER'
        sub_path = os.path.join(root_path, state, county)

        # current_fname = 'Noble rex1280 31621.txt'
        current_fname = 'Assessor_Certified_P2021.xlsx'

        base, extension = os.path.splitext(current_fname)

        if extension.lower().endswith(".xlsx") or extension.lower().endswith(".xls"):
            excel_file_match(current_file_path+current_fname, sub_path)
        else:
            closest_match = intersecting_file(sub_path, current_file_path + current_fname)
            print(closest_match)
    except Exception as e:
        traceback.print_exc()
