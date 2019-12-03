#!/usr/bin/env python
# coding: utf-8

# In[3]:


### Connects to AWS and deletes all tables, recreates them empty

import sqlalchemy as sql
### create engine to connect
database_address = 'INSERT_YOUR_DATABASE_ADDRESS_HERE'
db = sql.create_engine(database_address)

#database chloe
#db = sql.create_engine('mysql+pymysql://admin:datawarehousing@database-2.ce6ggy1gznka.us-east-2.rds.amazonaws.com:3306/dbtest')

# Open the .sql file
sql_file = open('create_new_tables.sql','r')

# Create an empty command string
sql_command = ''

# Iterate over all lines in the sql file
for line in sql_file:
    # Ignore commented lines
    if not line.startswith('--') and line.strip('\n'):
        # Append line to the command string
        sql_command += line.strip('\n')

        # If the command string ends with ';', it is a full statement
        if sql_command.endswith(';'):
            # Try to execute statement and commit it
            try:
                db.execute(str(sql_command))
                #db.commit()

            # Assert in case of error
            except:
                print('Ops')
                

            # Finally, clear command string
            finally:
                sql_command = ''


# In[ ]:




