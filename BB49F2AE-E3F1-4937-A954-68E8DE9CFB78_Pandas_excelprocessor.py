import os
from openpyxl import load_workbook, Workbook
from dataprep.Utility.Utility import Utility
import csv
from acquisition.CommonUtil.Common_Util import get_logger
import pandas as pd
from io import StringIO
# import datetime
log = get_logger('Pandas_Excelprocessor')

class Excelprocessor:

    def __init__(self, input_file_path: str, input_file_nam: str):
        self.Utility_process = Utility
        self.input_file_path = input_file_path
        self.input_file_nam = input_file_nam
        self.edition = 10
        self.version = 1
        self.tab_dir_path = ''
        self.na_values = ["", "#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", "-NaN", "-nan", "1.#IND", "1.#QNAN", "<NA>", "N/A", "NA",  "NULL", "NaN", "n/a", "nan", "null"]

    def excel_processer(self):
        try:
            log.info("Started Excel {0} - file processing to TAB".format(str(self.input_file_nam)))
            if not os.path.exists(os.path.join(self.input_file_path, 'PROCESSEDCOUNTIES_PY')):
                os.makedirs(os.path.join(self.input_file_path, 'PROCESSEDCOUNTIES_PY'))
                self.tab_dir_path = os.path.join(self.input_file_path, 'PROCESSEDCOUNTIES_PY')
            else:
                self.tab_dir_path = os.path.join(self.input_file_path, 'PROCESSEDCOUNTIES_PY')
            base, extension = os.path.splitext(str(self.input_file_nam))
            out_file_nam = base + '_E{0}V{1}.tab'.format(self.edition, self.version)
            execl_file = os.path.join(self.input_file_path, self.input_file_nam)
            df = pd.read_excel(execl_file, header=None, dtype=str, keep_default_na=False)
            df = df.fillna('')
            write = open('{0}/{1}'.format(self.tab_dir_path, out_file_nam), 'w', newline='')
            tab_write = csv.writer(write, delimiter="\t", quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            row_count = 0
            for index, row in df.iterrows():
                # print(row.tolist())
                # print([Utility.formated_row_cleanup(str(cell)) for cell in row.tolist()])
                tab_write.writerow([Utility.formated_row_cleanup(str(cell)) for cell in row.tolist()])
                row_count += 1
            log.info("{0} - Row count  - {1}".format(out_file_nam, row_count))
            log.info("{0} - File Converted to TAb - {1}".format(self.input_file_nam, out_file_nam))
            return str(self.tab_dir_path)
        except Exception as e:
            log.error(str(e))


if __name__ == '__main__':
    file_path = 'C:/Users/ISC-SA-EDG-SLA/Documents/Dataprep_PY/Xls'
    filename = 'Lake_County_2.xlsx'
    obj = Excelprocessor(file_path, filename)
    obj.excel_processer()
