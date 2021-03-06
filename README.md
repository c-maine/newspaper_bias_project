# A newspaper_bias_project

**Short description of project**

 - With this github repository you can create a tool that collects data from NewsAPI (https://newsapi.org/) and stores it in a Maria DB server. In our setup we created an AWS RDS as MariaDB server and collect the data by requesting from newsAPI on a daily basis. This requests are executed by a docker-image that is run daily via cron-jobs on an EC2 instance. See architecture pdf for a very graphic representation of the architecture.
 The data collected will eventually be visualised in a dashboard in order to show the frequency of country-mentions per newspaper and perhaps also a sentiment analysis of the content. You can connect to the database, eg. using sqlalchemy, via: 
 
 database_address = 'mysql+pymysql://admin:datawarehousing@database-1.cl6uila8iago.eu-central-1.rds.amazonaws.com:3306/news_db'
 
 db = sql.create_engine(database_address)


**Instructions**

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


**Additional information**

1) The structure of the data in the AWS Maria DB is set up with the following tables:
  - Articles table containing article ID, title, URL, description. The articles table references all other tables. 
  - Newspapers table, containing newspaper ID (URL) and title 
  - Countries table, containing country, country name, population, number of official languages, english language (present as official language TRUE/FALSE), area, capital, region and subregion
  - Dates table containing date (date published)

5) b) & c) The big_fill image is designed to:
           i) Get all countries information from the restcountries_py Python package and write this information in the 
           countries_tab_news table in the database.
           ii) For each newspaper in our newspapers list, and for each country, send a request to NEWS API for all the articles 
           published in the last 30 days that contain the country name as a keyword. From each request, we extract the total 
           number of results and a subset of 25 complete articles, that include article title, url, and description. We organize 
           this data in two pandas dataframes, one containing only count information and the other the articles information.
           The count information is written in the count_tab_news table, the articles in the articles_tab_news table in the 
           database.
The daily_fill image repeats step ii) of the big_fill, but limits the request to the previous day.

Initially we used the API EventRegistry (https://eventregistry.org) and we queried for all articles for a day for specific newspapers; we filtered for articles with country tags and additionally searched for names of countries in the article title. This is very inefficient because EventRegistry only has country tags for few articles and few newspapers and we were quickly running out of tokens. For this reason, we switched to NewsAPI to enable us to query per newspaper per country and count directly in the SQL query. This results in a greater number of SQL queries. However, every article we receive has a country tag. Nevertheless, the Eventregistry database is still up and we continue collecting data. The corresponding files, a Readme with information on how to connect to the database and a short description of the files can be found in the folder Eventregistry.

3)  e)  As NewsAPI limits requests to 500 per day and 250 per 12h, we created several accounts and run one cron job per newspaper per day.
