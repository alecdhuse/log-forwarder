import pymysql

# Open database connection
db_conn = pymysql.connect(host='localhost', port=3306, user='z_log', passwd='Thisisthez_logpassword', db='Environment_Log')

# prepare a cursor object using cursor() method
cursor = db_conn.cursor()

# Prepare SQL query to INSERT a record into the database.
sql = """INSERT INTO Air_Quality(report_time, pm2_5, aqi_us, pm_10, aqi_us_outdoor, temperature_c, humidity, co2, voc) VALUES ('2017/04/29 8:10:00', 4.0, 33, 2.0, 33, 28.2, 60, 600, -1)"""

try:
   # Execute the SQL command
   cursor.execute(sql)
   # Commit your changes in the database
   db_conn.commit()
except:
   # Rollback in case there is any error
   db_conn.rollback()

# disconnect from server
db_conn.close()
