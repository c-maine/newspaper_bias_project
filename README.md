# A newspaper_bias_project
Brought to you by Max, Francesco & Chloe

A (periodically) live dashboard exploring the bias of different newspapers around the world 

Short description of project

 - With this github repository you can create a tool that collects data from NewsAPI (https://newsapi.org/) and stores it in an existing AWS Maria DB server; specifically the newspaper source and countries tagged. Following this, the tool visualises the data in a dashboard showing the frequency of country-mentions per newspaper. If you are lucky, this tool will also conduct a sentiment analysis of the countries discussed. 


Steps in order to reproduce our setup:

1) Set up an AWS Maria DB:
     
     a) Enable public availability
     
     b) Ensure security group settings enable access
     
     c) Make sure to specify a database name

2) Clone this repository locally or on an AWS instance

3) Modify these files to your hostname and tokens : TO BE EDITED

4) Execute setup_all.sh; this file performs the following steps:
   
   a) Install docker
   
   b) Create Docker image: tables_init
     
   c) Create Docker image: tables_fill
   
   d) Runs tables_init (creates necessary tables and performs initial fill)
  
   e) Sets up a cron job to run tables_fill once per day per newspaper
 






Additional information

1) The structure of the data in the AWS Maria DB is set up with the following tables:
  - Articles table containing article ID, title, URL, description. The articles table references all other tables. 
  - Newspapers table, containing newspaper ID (URL) and title 
  - Countries table, containing country, country name, population, number of official languages, english language (present as official language TRUE/FALSE), area, capital, region and subregion
  - Dates table containing date (date published)

3) b) & c)  Initially we used the API EventRegistry (https://eventregistry.org) and we queried for all articles for a day for specific newspapers; we filtered for articles with country tags and additionally searched for names of countries in the article title. This is very inefficient because EventRegistry only has country tags for very few newspapers and we were running out of tokens. For this reason, we switched to NewsAPI to enable us to query per newspaper per country and count directly in the SQL query. This results in a greater number of SQL queries however every article we receive has a country tag. Instead of saving all the complete articles and their metadata, we only need to store the counts. We however still store a subset of complete articles in the hope of later performing the sentiment analysis.

3)  e)  As NewsAPI limits requests to 200 per day, we created several accounts and run one cron job per newspaper per day.
