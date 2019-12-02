# A newspaper_bias_project
Brought to you by Max, Francesco & Chloe

A (periodically) live dashboard exploring the bias of different newspapers around the world 

Short description of project

 - With this github repository you can create a tool that collects data from newsAPI (https://newsapi.org/) and stores it in an existing AWS Maria DB server; specifically the newspaper source and countries tagged. Following this, the tool visualises the data in a dashboard showing the frequency of country-mentions per newspaper. If you are lucky, this tool will also conduct a sentiment analysis of the countries discussed. 


Steps

1) Set up an AWS Maria DB:
     
     a) Enable public availability
     
     b) Ensure security group settings enable access
  
2) Clone this repository locally or on an AWS instance

3) Execute setup_all.sh; this file performs the following steps:
   
   a) Install docker
   
   b) Pull Docker image: tables_init
     
   c) Pull Docker image: tables_fill
   
   d) Performs an initial fill of database by running tables_init
  
   e) Sets up a cron job to run tables_fill once per day per newspaper
 
 N.B. This Docker image cannot be edited for the purposes of connecting to another database. 



Additional information

1) The structure of the data in the AWS Maria DB is set up with the following tables:
  - Articles table containing article ID, title, URL, description. The articles table references all other tables. 
  - Newspapers table, containing newspaper ID (URL) and title 
  - Countries table, containing country, country name, population, number of official languages, english language (present as official language TRUE/FALSE), area, capital, region and subregion
  - Dates table containing date (date published)

3) b) & c)  Initially we used the API EventRegistry (https://eventregistry.org) and we queried for all articles for a day for specific newspapers; we filtered for articles with country tags and additionally searched for names of countries in the article title. This is very inefficient because EventRegistry only has country tags for very few newspapers and we are running out of tokens. For this reason, we switched to NewsAPI to enable us to query per newspaper per country and count directly in the SQL query. This results in a greater number of SQL queries however every article we receive has a country tag. Instead of saving all the complete articles and its metadata, we only need to store the counts. We however still store a subset of complete articles in the hope of later performing the sentiment analysis.

3)  e)  As NewsAPI limits requests to 200 per day, we created several accounts and run one cron job per newspaper per day.
