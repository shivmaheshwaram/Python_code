import pyodbc
import pandas as pd
import os
from acquisition.CommonUtil.Common_Util import get_logger
from acquisition.CommonUtil.FTP_Util import FTP_Util
from sqlalchemy import create_engine, inspect, MetaData
import shutil
import time
log = get_logger('Convert DB files to TAB')


class ConvertDBFiles_TAB:

    def __init__(self):
        self.ftp_util_obj = FTP_Util()
        self.db_restor_filsonly_cmd = "RESTORE FILELISTONLY FROM DISK = '{0}' WITH FILE = 1"
        self.db_restor_cmd = "USE [master] RESTORE DATABASE [{0}] FROM DISK = N'{1}' WITH FILE = 1, MOVE N'{0}' TO N'{2}', MOVE N'{3}'TO N'{4}', RECOVERY, NOUNLOAD, STATS = 5, REPLACE"
        self.restore ="USE [master] RESTORE DATABASE [{0}] FROM  DISK = N'{1}' WITH  FILE = 1,  MOVE N'{0}' TO N'{2}',  MOVE N'{3}' TO N'{4}',  NOUNLOAD,  STATS = 5"
        self.rol_back = "IF EXISTS (SELECT name FROM master.dbo.sysdatabases WHERE name = '{0}') DROP DATABASE {0} RESTORE DATABASE {0} FROM DISK = '{1}'  WITH MOVE '{0}' TO '{2}', MOVE '{3}' TO '{4}'"
        self.db_alter_multi_cmd = "ALTER DATABASE [{0}] SET MULTI_USER"
        self.db_fetch_schemas_cmd ="SELECT * FROM INFORMATION_SCHEMA.TABLES"
        self.db_alter_single_cmd = "alter database [{0}] set single_user with rollback immediate"
        self.db_drop_cmd = "DECLARE @sql AS NVARCHAR(MAX); SET @sql = 'DROP DATABASE ' + QUOTENAME(?); EXEC sp_executesql @sql"
        self.sqlserver = "ISCEQNC01VDI565\SQLEXPRESS"
        #self.sqlserver = "ISCEQNC01VDI565"

    def convert_sqlite_tab(self, filename, file_path):
        '''Function to convert Sqlite to Tab files'''
        try:
            if not os.path.exists(os.path.join(file_path, os.path.splitext(filename)[0])):
                os.mkdir(os.path.join(file_path, os.path.splitext(filename)[0]))
                folder_path = os.path.join(file_path, os.path.splitext(filename)[0])
            else:
                folder_path = os.path.join(file_path, os.path.splitext(filename)[0])
            file = os.path.join(file_path, filename)
            local_engine = create_engine("sqlite:///" + file)
            inspector = inspect(local_engine)
            schemas = inspector.get_schema_names()
            source_metadata = MetaData(bind=local_engine)
            source_metadata.reflect(local_engine)
            for schema in schemas:
                for table_name in inspector.get_table_names(schema=schema):
                    query = "select * from {0};".format(table_name)
                    df = pd.read_sql(query, local_engine)
                    df.to_csv(folder_path + '\\' + table_name + '.TAB', index=False, sep='\t')
            return folder_path
        except Exception as e:
            log.error(e)

    def convert_dbfiles_to_tab(self, file_name, root_filepath, db_temp_path):
        try:
            self.ftp_util_obj.delete_folder_contents(db_temp_path)
            shutil.copyfile(root_filepath + file_name, db_temp_path + file_name)
            log.info("{0} - File copied to temp path-{1}".format(file_name, db_temp_path))
            if not os.path.exists(os.path.join(root_filepath, os.path.splitext(file_name)[0])):
                os.mkdir(os.path.join(root_filepath, os.path.splitext(file_name)[0]))
                folder_path = os.path.join(root_filepath, os.path.splitext(file_name)[0])
            else:
                folder_path = os.path.join(root_filepath, os.path.splitext(file_name)[0])
            db_file = os.listdir(db_temp_path)[0]
            file_fullpath = os.path.join(db_temp_path, db_file)

            if file_name.lower().endswith(".mdf"):
                '''Convert Mdf to Tab files'''
                cnxn = self.sql_get_conx_str(file_fullpath, db_file, self.sqlserver)
                cnxn.autocommit = True
                new_cur = cnxn.cursor()
                if cnxn != None:
                    tab_file_path = self.fetch_tables_convert_tab(cnxn, db_file, folder_path, db_temp_path, new_cur)
                    if tab_file_path != None:
                        return tab_file_path

            elif file_name.lower().endswith(".bak"):
                '''Convert Bak to Tab files'''
                cnxn = self.sql_get_conx_str('', 'master', self.sqlserver)
                if cnxn != None:
                    cnxn.autocommit = True
                    new_cur = cnxn.cursor()
                    sql1_restor_filsonly_cmd = self.db_restor_filsonly_cmd.format(file_fullpath)
                    new_cur.execute(sql1_restor_filsonly_cmd)
                    db_nam_list = new_cur.fetchall()
                    if len(db_nam_list) > 0:
                        db_mdf_name = db_nam_list[0][0]
                        cpth = "C:/Program Files/Microsoft SQL Server/MSSQL14.SQLEXPRESS/MSSQL/DATA"
                        #db_name = db_mdf_name + '.mdf'
                        db_mdf_path = db_temp_path + '\\' + db_mdf_name + '.mdf'
                        db_ldf_name = db_nam_list[1][0]
                        db_ldf_path = db_temp_path + '\\' + db_ldf_name + '.ldf'
                        restor_sql_cmd = self.db_restor_cmd.format(db_mdf_name, file_fullpath, db_mdf_path, db_ldf_name, db_ldf_path)
                        log.info("{0} - Database Restore process in progress...".format(db_mdf_name))
                        new_cur.execute(restor_sql_cmd)
                        # set_offline = "ALTER DATABASE [{0}] SET OFFLINE WITH ROLLBACK IMMEDIATE; DROP DATABASE [{0}]"
                        # time.sleep(10)
                        # drop = "DROP DATABASE [{0}]"
                        # new_cur.execute(set_offline.format(db_mdf_name))
                        # #new_cur.execute(drop.format(db_mdf_name))
                        # #new_cur.execute((self.db_drop_cmd), db_mdf_name)
                        # cnxn = self.sql_get_conx_str(db_mdf_path, db_name, self.sqlserver)
                        # new_cur = cnxn.cursor()
                        # if cnxn != None:
                        #     tab_file_path = self.fetch_tables_convert_tab(cnxn, db_file, folder_path, db_temp_path, new_cur)
                        #     if tab_file_path != None:
                        #         return tab_file_path
                        time.sleep(100)
                        log.info("{0} - Database Restored db process completed.".format(db_mdf_name))
                        #new_cur.execute(self.db_alter_multi_cmd.format(db_mdf_name))
                        new_cur.execute("USE [{0}]".format(db_mdf_name))
                        tab_file_path = self.fetch_tables_convert_tab(cnxn, db_mdf_name, folder_path, db_temp_path, new_cur)
                        if tab_file_path != None:
                            return tab_file_path
        except Exception as e:
            log.error(str(e))

    def fetch_tables_convert_tab(self, cnxn, db_file, folder_path, db_temp_path, new_cur):
        '''Function to fetch tables from Db and convert to Tab'''
        try:
            new_cur.execute(self.db_fetch_schemas_cmd)
            tables = new_cur.fetchall()
            if len(tables) > 0:
                try:
                    for table_name in tables:
                        table_name = table_name[2]
                        for chunk in pd.read_sql_query("SELECT * from %s" % table_name, cnxn, chunksize=1000000):
                            chunk.to_csv(os.path.join(folder_path + '\\' + table_name + '.tab',), mode='a', sep='\t', index=False, encoding='utf-8')
                    log.info("{0} - File sucssfully converted to TAB".format(db_file))
                except Exception as e:
                    log.error(str(e.args))
                # for table_name in tables:
                #     table_name = table_name[2]
                #     table = pd.read_sql_query("SELECT * from %s" % table_name, cnxn)
                #     table.to_csv(folder_path + '\\' + table_name + '.TAB', index=False, sep='\t')
                # log.info("{0} - File sucssfully converted to TAB".format(db_file))
                new_cur.execute('USE master')
                new_cur.execute(self.db_alter_single_cmd.format(db_file))
                db = "{0}".format(db_file)
                new_cur.execute((self.db_drop_cmd), db)
                log.info("{0} - Dropped from database Successfully".format(db))
                self.ftp_util_obj.delete_folder_contents(db_temp_path)
                log.info("Cleared Db_temp_path folder")
                cnxn.close()
                return folder_path
        except Exception as e:
            log.error(str(e))

    def sql_get_conx_str(self, file_fullpath, db_file, server):
        '''Connection Stings for Sql Server Express'''
        try:
            cnxn_str = (
                r'DRIVER=ODBC Driver 17 for SQL Server;'
                r'autocommit=True;'
                r'SERVER={2};'
                r'Trusted_Connection=yes;'
                r'DATABASE={1};'
                r'AttachDbFileName={0};'.format(file_fullpath, db_file, server)
            )
            cnxn = pyodbc.connect(cnxn_str)
            print(pyodbc.drivers())
            log.info("Connetion to SQL server Successfully")
            return cnxn
        except Exception as e:
            log.error("SQL Server authentication failure")
            log.error(str(e))

if __name__ == '__main__':
    file_name = "Goochland Real Estate Extracts_1212020.bak"
    root_filepath = "C:/Users/ISC-SA-EDG-SLA/Downloads/BAKFiles/"
    db_temp_path = "C:/Db_temp_backup/"
    obj = ConvertDBFiles_TAB()
    obj.convert_dbfiles_to_tab(file_name,root_filepath,db_temp_path)

