import pymysql

def send_data_to_sql(data, connection_settings):

    try:
        # Open database connection
        db_conn = pymysql.connect(host=connection_settings['host'], port=connection_settings['port'], user=connection_settings['user'], passwd=connection_settings['password'], db=connection_settings['database_name'])

        # prepare a cursor object using cursor() method
        cursor = db_conn.cursor()

        for data_entry in data:
            lables = ""
            values = ""

            for data_field in data_entry:
                lables += "%s, " % (data_field['label'])
                if isinstance(data_field['value'], (int, float)):
                    values += "%s, " % (data_field['value'])
                else:
                    values += "'%s', " % (data_field['value'])

            # remove last delimiter
            lables = lables[:-2]
            values = values[:-2]

            # Prepare SQL query to INSERT a record into the database.
            sql = "INSERT INTO Air_Quality(%s) VALUES (%s)" % (lables, values)

            try:
               # Execute the SQL command
               cursor.execute(sql)
               # Commit your changes in the database
               db_conn.commit()
            except:
               # Rollback in case there is any error
               db_conn.rollback()
               print ("SQL query error")

        # disconnect from server
        db_conn.close()

        return True
    except:
        return False
