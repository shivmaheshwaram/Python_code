import pymysql
import pyodbc as db
from datetime import datetime
from commons.Utility import Utilities
from acquisition.CommonUtil.LoggerUtility import get_logger, decode_encrypted_psw
# from acquisition.CommonUtil.Common_Util import decode_encrypted_psw

log = get_logger('Database')


class Database(object):

    def __init__(self, app_config_prop, conn_type, server, db_name, user_name, password, port_num=3703):

        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_description = app_config_prop.get("QUERIES", 'update_description')
        self.update_folders = app_config_prop.get("QUERIES", 'update_folders')
        self.get_file_name = app_config_prop.get("QUERIES", 'get_file_name')
        self.get_icp_count = app_config_prop.get("QUERIES", 'get_icp_count')

        self.update_icp_status = app_config_prop.get("QUERIES", 'update_icp_status')
        self.sf_inquiry_update = app_config_prop.get("QUERIES", "sf_inquiry_update")
        self.sf_status_change = app_config_prop.get("QUERIES", "non_reoder_query")

        self.dp_query = app_config_prop.get("QUERIES", "dp_query")
        self.qda_query = app_config_prop.get("QUERIES", "qda_query")

        self.dp_query_prod_type = app_config_prop.get("QUERIES", "dp_query_prod_type")
        self.qda_query_prod_type = app_config_prop.get("QUERIES", "qda_query_prod_type")

        self.tax_roll_db_query = app_config_prop.get("QUERIES", 'tax_roll_db_query')

        self.sf_db_query = app_config_prop.get("QUERIES", 'sf_db_query')  # Used
        self.sql_icp_list_query = app_config_prop.get("QUERIES", "sqlgeticplist")
        self.spl_inst_query = app_config_prop.get("QUERIES", "spec_inst")
        self.get_fips_body = app_config_prop.get("QUERIES", 'get_fips_body')  # Used
        # self.sql_icp_user = app_config_prop.get("QUERIES", 'icp_user')
        self.sate_wide_query = app_config_prop.get("QUERIES", "statewideicplist")
        self.get_prod_type = app_config_prop.get("QUERIES", "get_prod_type")
        self.reorder_problem_filenames_query = app_config_prop.get("QUERIES", "reorder_problem_filenames")
        self.sate_wide_query_in = app_config_prop.get("QUERIES", "statewide_IN_icp_list")

        # File sharing queries
        self.sf_icp_shared_with = app_config_prop.get("QUERIES", "sf_icp_shared_with")
        self.sf_county_restrictions = app_config_prop.get("QUERIES", "sf_county_restr")
        self.shared_sf_db_query = app_config_prop.get("QUERIES", "shared_sf_db_query")
        self.shared_date_update = app_config_prop.get("QUERIES", "update_shared_date")
        self.shared_rlo_check = app_config_prop.get("QUERIES", "shared_rlo_query")
        self.pattern_list_all = app_config_prop.get("QUERIES", "pattern_list_all")
        self.taxroll_insert_query = app_config_prop.get("QUERIES", "taxroll_insert_query")
        self.fileinventory_insert_query = app_config_prop.get("QUERIES", "fileinventory_insert_query")
        self.stopped_county_update_query = app_config_prop.get("QUERIES", "stopped_county_update_query")
        self.sf_county_restrictions = app_config_prop.get("QUERIES", "sf_county_restr")
        self.util_Obj = Utilities()
        self.error_msg = self.util_Obj.get_json_data('\JsonData\error_codes.json')
        self.record_county_icp = app_config_prop.get("QUERIES", "record_count_icp")

        # Force match query
        self.sf_force_match_query = app_config_prop.get("QUERIES", "sf_force_match_query")
        #Data_prep
        self.get_automated_counties = app_config_prop.get("QUERIES", "get_automated_counties")
        self.dataprep_insert_query = app_config_prop.get("QUERIES", "dataprep_insert_query")

        try:
            con = None
            log.info(">> Connecting to database : {}".format(db_name))
            if conn_type.lower() == 'sqlserver':
                if user_name == 'None' or password == 'None':
                    con = db.connect(
                        'DRIVER={ODBC Driver 17 for SQL Server};Server=' + server + ';Database=' + db_name + ';Trusted_connection=yes')
                else:
                    con = db.connect(
                        'DRIVER={ODBC Driver 17 for SQL Server};Server=' + server + ';Database=' + db_name + ';UID=' + user_name + ';PWD=' + password + ';')

            if conn_type.lower() == 'mssql':
                con = pymysql.connect(host=server, user=user_name, passwd=password, db=db_name, port=int(port_num))
            cur = con.cursor()
            self.cur = cur
            log.info(">> Connection to {0} database Successful".format(db_name))
        except Exception as e:
            log.error(self.error_msg["Database Connection Failure"] + "\n{}".format(str(e)))
            self.sendemail.send_emails(self.emailid, self.distribution_list_dev, "TRO-DBF-PROD-000631: Error Alert!!",
                                       "<br>Immediate action needed :<br>"
                                       "<br>Dbname: {0}<br>"
                                       "<br>Error Details:  {1}<br>".format(db_name, self.error_msg["Database Connection Failure"]), 'smtp.corelogic.com')

    @classmethod
    def taxroll_db_initialize(cls, config_prop, app_config_prop):
        try:

            sql_connection_type = config_prop.get("DATABASE", "conn_type")
            sql_server_name = config_prop.get("DATABASE", "server")
            sql_icp_update_db = config_prop.get("DATABASE", 'icp_update_db')
            sql_icp_user = config_prop.get("DATABASE", 'icp_user')
            sql_icp_password = decode_encrypted_psw(config_prop.get("DATABASE", 'icp_password'))

            return cls(app_config_prop, sql_connection_type, sql_server_name, sql_icp_update_db, sql_icp_user, sql_icp_password)
        except Exception as e:
            log.error(e.args)

    @classmethod
    def sf_db_initialize(cls, config_prop, app_config_prop):
        try:

            sql_connection_type = config_prop.get("DATABASE", "conn_type")
            sql_server_name = config_prop.get("DATABASE", "server")
            sf_db_name = config_prop.get("DATABASE", 'sf_dev_db')
            sf_user = config_prop.get("DATABASE", 'sf_user')
            sf_pwd = config_prop.get("DATABASE", 'sf_pwd')

            return cls(app_config_prop, sql_connection_type, sql_server_name, sf_db_name, sf_user, sf_pwd)
        except Exception as e:
            log.error(e.args)

    @classmethod
    def diablo_db_initialize(cls, config_prop, app_config_prop):
        try:

            sql_connection_type = config_prop.get("DATABASE", "conn_type")
            sql_server_name = config_prop.get("DATABASE", "diablo_server")
            sql_icp_update_db = config_prop.get("DATABASE", 'diablo_db')
            sql_icp_user = config_prop.get("DATABASE", 'diablo_user')
            sql_icp_password = config_prop.get("DATABASE", 'diablo_password')

            return cls(app_config_prop, sql_connection_type, sql_server_name, sql_icp_update_db, sql_icp_user, sql_icp_password)
        except Exception as e:
            log.error(e.args)

    @classmethod
    def mssql_dp_db_initialize(cls, config_prop, app_config_prop):
        try:

            sql_connection_type = config_prop.get("DATABASE", "mysql_conn_type")
            sql_dp_server_name = config_prop.get("DATABASE", "mysql_dp_server")
            sql_dp_db = config_prop.get("DATABASE", 'mysql_dp_db')
            sql_dp_user = config_prop.get("DATABASE", 'mysql_dp_user')
            sql_dp_password = config_prop.get("DATABASE", 'mysql_dp_password')
            sql_dp_port = int(config_prop.get("DATABASE", 'mysql_dp_port'))
            return cls(app_config_prop, sql_connection_type, sql_dp_server_name, sql_dp_db, sql_dp_user, sql_dp_password, sql_dp_port)
        except Exception as e:
            log.error(e.args)

    @classmethod
    def mssql_qda_db_initialize(cls, config_prop, app_config_prop):
        try:

            sql_connection_type = config_prop.get("DATABASE", "mysql_conn_type")
            sql_qda_server_name = config_prop.get("DATABASE", "mysql_qda_server")
            sql_qda_db = config_prop.get("DATABASE", 'mysql_qda_db')
            sql_qda_user = config_prop.get("DATABASE", 'mysql_qda_user')
            sql_qda_password = config_prop.get("DATABASE", 'mysql_qda_password')
            sql_qda_port = int(config_prop.get("DATABASE", 'mysql_qda_port'))
            return cls(app_config_prop, sql_connection_type, sql_qda_server_name, sql_qda_db, sql_qda_user, sql_qda_password, sql_qda_port)
        except Exception as e:
            log.error(e.args)

    @classmethod
    def dataprep_db_initialize(cls, config_prop, app_config_prop):
        try:

            sql_connection_type = config_prop.get("DATABASE", "conn_type")
            sql_server_name = config_prop.get("DATABASE", "server")
            sql_dp_icp_update_db = config_prop.get("DATABASE", 'dp_icp_update_db')
            sql_icp_user = config_prop.get("DATABASE", 'sf_user')
            sql_icp_password = config_prop.get("DATABASE", 'sf_pwd')

            return cls(app_config_prop, sql_connection_type, sql_server_name, sql_dp_icp_update_db, sql_icp_user,
                       sql_icp_password)
        except Exception as e:
            log.error(e.args)

    def insert_update_data(self, query):
        try:
            log.info(">> Executing SQL Query={0}".format(query))
            self.cur.execute(query)
            self.cur.commit()
            result = self.cur
            log.info(">> QueryResult={0}".format(result))
            return result
        except Exception as e:
            log.error(self.error_msg["DB Query Execution and Response"] + "\n {}".format(str(e)))

    def fetch_data(self, query):
        try:
            log.info(">> Executing SQL Query={0}".format(query))
            self.cur.execute(query)
            result = self.cur.fetchall()
            log.info(">> QueryResult={0}".format(result))
            return result
        except Exception as e:
            log.error(self.error_msg["DB Query Execution and Response"]+":"+"{}".format(query))

    def update_ICP_table(self, icp_details_obj, sub_status, zip_file_count, icp_file_name, dasi_id):
        try:
            # bd = ''
            body = icp_file_name.replace("'", '"')
            CountyName = icp_details_obj.get('county')
            FipsCode = icp_details_obj.get('fips')
            StateName = icp_details_obj.get('state')
            Edition = icp_details_obj.get('edition')
            Version = icp_details_obj.get('version')
            ProductionType = icp_details_obj.get('productiontype')
            IcpNumber = icp_details_obj.get('icpnumber')
            SubmissionStatus = icp_details_obj.get('SubmissionStatus')

            query = 'INSERT INTO Taxroll_QA.dbo.ICP_processed(CountyName, FipsCode, StateName, Edition, Version, ProductionType, Status, IcpNumber, Date, [User], FileCount, SubmissionStatus, Body, DASIID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            args = (CountyName, FipsCode, StateName, Edition, Version, ProductionType, sub_status, IcpNumber, self.date,
                    self.sql_icp_user, zip_file_count, SubmissionStatus, body, dasi_id)
            log.info(">> Executing SQL Query={0}".format(query))

            self.cur.execute(query, args)
            self.cur.commit()
            log.info('Completed database update successful')
        except Exception as e:
            log.error(self.error_msg["DB Query Execution and Response"] +"\n {}".format(str(e)))

    def update_file_inventory_table(self, icp_details_obj, folder_type, file_path, file_name):
        try:
            # bd = ''
            icp_number = icp_details_obj.get('icpnumber')
            dasi_file_path = icp_details_obj.get('dasi_file_path')
            dasi_file_name = icp_details_obj.get('dasi_file_name')
            dasi_date = icp_details_obj.get('dasi_date_stamp')
            act_file_path = str(file_path).split("TAX_ROLL")[1].split(file_name)[0]

            query = 'insert into file_inventory (ICP,folder_type, dasi_path, dasi_name, file_path, file_name,dasi_date) values (?, ?, ?, ?, ?, ?, ?)'
            args = (icp_number, folder_type, dasi_file_path, dasi_file_name, act_file_path, file_name, dasi_date)
            log.info(">> Executing SQL Query={0}".format(query))
            log.info(">> SQL Args = {0}".format(args))

            self.cur.execute(query, args)
            self.cur.commit()
            log.info('Completed database update successful')
        except Exception as e:
            log.error(["DB Query Execution and Response"] + ":" + "{}".format(e))
