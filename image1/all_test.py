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
env_path = Path('/home') / '.env'

print(env_path)
load_dotenv(dotenv_path=env_path)

api_keys = os.getenv("API").split(' ')
database_address = os.getenv("ADDRESS")

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
    pass


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
    country_df = get_countries_df()
    countries_encoding_df=country_df[['country_iso','country_name']].copy()
    countries_rest_dict = countries_encoding_df.set_index('country_name')['country_iso'].to_dict()
    countries_rest = list(countries_encoding_df['country_name']) # not needed, but useful for checks
    write_country_to_db(country_df,db) 


def get_articles(country, source, from_d, to_d, api_key):
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
    news_all = {}
    counter_all = []
    for ind,source in enumerate(sources):
        for country in countries:
            response, count = get_articles(country, source, from_d, to_d, api_keys[ind])
            counter_all.append([source,country, count])
            if country == 'US':
                country = 'United States'
            if country == 'UK':
                country = 'United Kingdom'
            if country in news_all.keys():
                news_all[country] += response
            else:
                news_all[country] = response
        time.sleep(120)
    return news_all, counter_all


def get_tables(newspapers, api_keys, big_fill=False):
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

    yesterday = str(datetime.datetime.now().date() - datetime.timedelta(days=1))
    this_month = str(datetime.datetime.now().date() - datetime.timedelta(days=30))
    two_days_ago = str(datetime.datetime.now().date() - datetime.timedelta(days=2))

    if big_fill is True:
        nw2, contatore2 = news_data(countries,newspapers,api_keys, this_month,two_days_ago)
    else:
        nw2, contatore2 = news_data(countries,newspapers, api_keys, yesterday,yesterday)
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
        
    counter = pd.DataFrame(contatore2, columns = ['source','country','count'])
    counter['fill_date'] = [datetime.datetime.now().date() for i in range(counter.shape[0])]
    counter = pd.merge(counter, countries_pd, how = 'inner', left_on='country', right_on = 'country_name').drop(columns=['country','country_name'])
    return dataset, counter    


def write_main_to_df(main_df,engine):
    main_df.to_sql('count_tab_news', con=engine, if_exists='append',index=False)


def write_articles(main_df,engine):
    main_df.to_sql('articles_tab_news', con=engine, if_exists='append',index=False)


def fill_tabs(db, newspapers, api_keys, big_fill = False):
    articles_data, count_data = get_tables(newspapers, api_keys, big_fill)
    write_main_to_df(count_data, db)
    write_articles(articles_data, db)


###Actual code
db = sql.create_engine(database_address)
newspapers = ['the-new-york-times','al-jazeera-english','news24','the-hindu']
tabs = db.execute('SHOW TABLES').fetchall()
if len(tabs) == 0:
    create_tabs(db)
    fill_countries_tab(db)
    fill_tabs(db, newspapers, api_keys, True)
else:
    fill_tabs(db, newspapers, api_keys, False)
    






