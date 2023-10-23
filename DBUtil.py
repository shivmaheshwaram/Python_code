import pyodbc as db
import pymysql


class DatabaseUtil:
    def __init__(self, conn_type, server, db_name, user_name='', password='', port_num = 3703):
        try:
            con = None
            print(">> Connecting to database : {}".format(db_name))
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
            print(">> Connection to {0} database Successful".format(db_name))
        except Exception as e:
            print(e.args)

    def fetch_data(self, query):
        print(query)
        self.cur.execute(query)
        return self.cur
