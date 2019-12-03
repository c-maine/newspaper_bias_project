Overview over the files in this folder: 

clear_aws_tables.py
    - pythonfile executing the clear_aws_tables.sql file
    - hostname of database that should be cleared has to specified

clear_aws_tables.sql:
    - deletes and recreates the following tables: 
        - countries_tab
        - newspaper_tab
        - articles_tab     
        - dates_tab
        - categories_tab

init.py
    - requests all articles for specified newspapers from Evenregistry for past 30 days
    - searches for country information
    - fills dataframes and loads them to sql database
    - Eventregistry key, urls of newspapers and hostname of database have to be specified within file

fill.py
    - same as init. py, but requests for past 3 days and does not fill country table

In the same way as for newsAPI, docker images were created and run with Cron from EC2 instances. 

N.B. The database as well as the data collection are up and running, you can connect to it if you want to, e.g.
via python using sqlalchemy: 
sql.create_engine('mysql+pymysql://admin:datawarehousing@database-1.cl6uila8iago.eu-central-1.rds.amazonaws.com:3306/dbtest')

