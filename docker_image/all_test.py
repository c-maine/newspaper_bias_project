import requests
from country_list import countries_for_language
import pandas as pd
import sqlalchemy as sql
import restcountries_py.restcountry as rc
import random
import datetime
import time
from dotenv import load_dotenv
import os
from pathlib import Path  # python3 only

def c_search():
    all_countries = []
    for country in rc.find_all():
        country_dict = {}
        country_dict["country_iso"] = country.alpha3Code
        country_dict["country_name"] = country.country_name
        country_dict["population"] = country.population
        country_dict["n_languages"] = len(country.languages)
        country_dict["eng_language"] = sum([i=='en' for i in country.languages])
        country_dict["area"] = country.area
        country_dict["capital"] = country.capital
        country_dict["subregion"] = country.subregion
        country_dict["region"] = country.region
        all_countries.append(country_dict)
    return (all_countries)


def create_tabs(db):
    fd = open('/home/useful_files/create_new_tables.sql','r')
    sql_file = fd.read()
    fd.close()
    # split file into single commands
    sql_commands = sql_file.split(';')
    # Execute every command separately in order to be able to keep track of errors
    for command in sql_commands:
        # skip errors and report them
        try:
            db.execute(command)
        except(OperationalError, msg):
            print("Command skipped: ", msg)


def get_countries_df():
    ## get list of dicionaries
    all_countries = rc.find_all()
    country_list = c_search()
    # convert it to dataframe
    country_df=pd.DataFrame(country_list)
    ## drop two irrelevant countries with string encoding issues
    country_df=country_df.drop(index=[79,146])
    
    return country_df


def write_country_to_db(df,engine):
    df.to_sql('countries_tab', con=engine, if_exists='append',index=False)


def fill_countries_tab(db):
    #function to write countries info in the countries table in the database
    country_df = get_countries_df()
    countries_encoding_df=country_df[['country_iso','country_name']].copy()
    countries_rest_dict = countries_encoding_df.set_index('country_name')['country_iso'].to_dict()
    write_country_to_db(country_df,db) 


def get_articles(country, source, from_d, to_d, api_key):
    # actual request to the news api, if the status of the response is ok we have the data we need
    # otherwise we return an empty list
    c = 'q='+country+'&'
    s = 'sources='+source+'&'
    url = 'https://newsapi.org/v2/everything?'+s+'sort=relevancy&from='+str(from_d)+'&to='+str(to_d)+'&pagesize=100&lenguage=en&'+c+'apiKey='+api_key
    response = requests.get(url).json()
    if response['status'] == 'ok':
        tot_res = response['totalResults']
        resp_articles = response['articles']
        return resp_articles, tot_res
    return [],0


def news_data(countries, sources, api_keys, from_d, to_d):
    # For each country and for each newspaper run get_articles to get data from news api,
    news_all = {}
    counter_all = []
    for ind,source in enumerate(sources):
        for country in countries:
            response, count = get_articles(country, source, from_d, to_d, api_keys[ind])
            if country == 'US':
                country = 'United States'
            if country == 'UK':
                country = 'United Kingdom'
            #add count data
            counter_all.append([source,country, count])
            #get results andd put them into a dictionary that has as keys country names and
            #as values a list of articles
            if country in news_all.keys():
                news_all[country] += response
            else:
                news_all[country] = response
        time.sleep(120)
    return news_all, counter_all


def get_tables(newspapers, api_keys, big_fill=False):
    # function to get data from the news api
    #get list of the countries we are interested in, remove from minor countries
    #and shuffle the list so that if we run out of token dureing the request (but shouldn't happen)
    #the countries for which we don't get data are random
    countries_pd = get_countries_df()[['country_name','country_iso']]
    countries = list(countries_pd['country_name'])
    drop_countries = ['British Indian Ocean Territory','United States Minor Outlying Islands','Virgin Islands (British)',
                     'Virgin Islands (U.S.)','Christmas Island','Cocos (Keeling) Islands','Cook Islands','French Southern and Antarctic Lands',
                     'Gibraltar','Heard Island and McDonald Islands','Saint Barthélemy','Saint Helena','Saint Kitts and Nevis',
                     'Saint Lucia','Saint Martin','Saint Pierre and Miquelon','Saint Vincent and the Grenadines','Turks and Caicos Islands',
                     'Wallis and Futuna']
    for country in drop_countries:
        countries.remove(country)
    countries += ['US','UK']
    random.shuffle(countries)

    # get what day was yesterday (for 1 day fill), 30 days ago and two days ago (for backward fill)  
    yesterday = str(datetime.datetime.now().date() - datetime.timedelta(days=1))
    this_month = str(datetime.datetime.now().date() - datetime.timedelta(days=30))
    two_days_ago = str(datetime.datetime.now().date() - datetime.timedelta(days=2))

    # get actual data either for past month or for yesterday
    if big_fill is True:
        nw2, contatore2 = news_data(countries,newspapers,api_keys, this_month,two_days_ago)
    else:
        nw2, contatore2 = news_data(countries,newspapers, api_keys, yesterday,yesterday)
    
    #clean the list of dictionaries (articles) we get from the function news_data into a pandas dataframe    
    dataset = pd.DataFrame()
    for country in nw2:
        df = pd.DataFrame(nw2[country])
        df['country'] = [country for i in range(len(nw2[country]))]
        dataset = pd.concat([dataset, df], axis = 0)
    dataset['source'] = dataset['source'].map(lambda x: x['id'])
    dataset.drop(columns = ['content','author','urlToImage'],inplace = True)
    dataset = pd.merge(dataset, countries_pd, how = 'inner', left_on='country', right_on = 'country_name').drop(columns=['country','country_name'])
        
    dataset=dataset.reset_index(drop = True)
    dataset['date_published'] = pd.to_datetime(dataset['publishedAt']).dt.date
    dataset=dataset.drop(columns = ['publishedAt'])
    
    #Prepare counter data(# of articles per day) and put it into a  pandas dataframe
    counter = pd.DataFrame(contatore2, columns = ['source','country','count'])
    counter['fill_date'] = [datetime.datetime.now().date() for i in range(counter.shape[0])]
    counter = pd.merge(counter, countries_pd, how = 'inner', left_on='country', right_on = 'country_name').drop(columns=['country','country_name'])
    
    #return the two pandas dataframes
    return dataset, counter    


def write_main_to_df(main_df,engine):
    main_df.to_sql('count_tab_news', con=engine, if_exists='append',index=False)


def write_articles(main_df,engine):
    main_df.to_sql('articles_tab_news', con=engine, if_exists='append',index=False)


def fill_tabs(db, newspapers, api_keys, big_fill = False):
    articles_data, count_data = get_tables(newspapers, api_keys, big_fill)
    write_main_to_df(count_data, db)
    write_articles(articles_data, db)


def start():
#main function, reads api keys, database address, and newspapers of interest from the .env file
    env_path = Path('/home/useful_files')/ '.env'
    load_dotenv(dotenv_path=env_path)
    api_keys = os.getenv("API").split(' ')
    database_address = os.getenv("ADDRESS")
    db = sql.create_engine(database_address)
    newspapers = ['the-new-york-times','al-jazeera-english','news24','the-hindu']
# reads tables in the database    
    tabs = db.execute('SHOW TABLES').fetchall()
        
    if len(tabs) == 0:
        # if there are no tables:
        #create tables
        create_tabs(db)
        # fill the countries table
        fill_countries_tab(db)
        # fill with data from the last 30 days
        fill_tabs(db, newspapers, api_keys, True)
    else:
        # if there are tables, the database has already been set up, just need to fill it
        #with data for the past day
        fill_tabs(db, newspapers, api_keys, False)



start()


