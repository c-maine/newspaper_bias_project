# A newspaper_bias_project
Brought to you by Max, Francesco & Chloe

A dashboard exploring the bias of different newspapers around the world 

Short description of project

 - With this github repository you can create a tool that collects data from NewsAPI (https://newsapi.org/) and stores it in an AWS Maria DB server. The data collected will eventually be visualised the data in a dashboard in order to show the frequency of country-mentions per newspaper and perhaps also a sentiment analysis of the content. You can connect to the database, eg. using sqlalchemy, via: 
 
 database_address = 'mysql+pymysql://admin:datawarehousing@database-1.cl6uila8iago.eu-central-1.rds.amazonaws.com:3306/news_db'
 
 db = sql.create_engine(database_address)




In order to reproduce our setup, please follow these steps:

1) Set up an AWS MariaDB RDS instance:
     
     a) Enable public availability
     
     b) Ensure security group settings enable access
     
     c) Make sure to specify a database name

2) Clone this repository locally or on an AWS EC2 instance

3) Replace the database_address in clear_aws_tables.py, true_init.py and fill.py with the database address of your database

4) In order to request data from newsAPI there are 2 options:
     a) You use our existing 4 keys that are specified in fill.py and true_init.py. If you do so, please make sure to run 
     setup_all.sh (see step 5) in the morning (between 07:00 and 11:00), because otherwise we will run out of tokens for the requests of that day and lose data
     b) You create your own 4 keys for newsAPI and insert them in true_init.py and fill.py 

5) Execute init_everything.sh
    this file performs the following steps:
   
   a) Install docker
   
   b) Create Docker image: big_fill
     
   c) Create Docker image: daily_fill
   
   d) Runs tables_init (creates necessary tables and performs big_fill fill)
  
   e) Sets up a cron job to run daily_fill once per day
 






Additional information

1) The structure of the data in the AWS Maria DB is set up with the following tables:
  - Articles table containing article ID, title, URL, description. The articles table references all other tables. 
  - Newspapers table, containing newspaper ID (URL) and title 
  - Countries table, containing country, country name, population, number of official languages, english language (present as official language TRUE/FALSE), area, capital, region and subregion
  - Dates table containing date (date published)

5) b) & c)  Initially we used the API EventRegistry (https://eventregistry.org) and we queried for all articles for a day for specific newspapers; we filtered for articles with country tags and additionally searched for names of countries in the article title. This is very inefficient because EventRegistry only has country tags for few articles and few newspapers and we were quickly running out of tokens. For this reason, we switched to NewsAPI to enable us to query per newspaper per country and count directly in the SQL query. This results in a greater number of SQL queries however every article we receive has a country tag. Instead of saving all the complete articles and their metadata, we only need to store the counts. We however still store a subset of complete articles in the hope of later performing the sentiment analysis. Nevertheless, the Eventregistry database is still up and we continue collecting data. The corresponding files, a Readme with information on how to connect to the database and a short description of the files can be found in the folder Eventregistry.

3)  e)  As NewsAPI limits requests to 500 per day and 250 per 12h, we created several accounts and run one cron job per newspaper per day.
