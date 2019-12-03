from country_list import countries_for_language
from eventregistry import *
import pandas as pd
import sqlalchemy as sql
from operator import itemgetter
import restcountries_py.restcountry as rc

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

def get_country_iso(country):
    if country in countries_rest_dict.keys():
            return(countries_rest_dict[country])
    else:
        return(-1)

def get_countries_df():
    ## get list of dicionaries
    all_countries = rc.find_all()
    country_list = c_search()

    # convert it to dataframe
    country_df=pd.DataFrame(country_list)

    ## drop two irrelevant countries with string encoding issues
    country_df=country_df.drop(index=[79,146])
    
    return country_df

### Functions for EventRegistry

def get_place_and_country(article):
    place = article['location']['label']['eng']
    country = article['location']['country']['label']['eng']
    return country,place

def get_data_from_EventRegistry(countries_rest_dict):
    start_date = datetime.date.today() - datetime.timedelta(days=30)
    er = EventRegistry(apiKey = '82e6f207-7add-425c-8ab5-993c5e95c2ab')
    q = QueryArticlesIter(
        dataType = ["news"],
        sourceUri = QueryItems.OR(["aljazeera.com",'nytimes.com']),
        dateStart = str(start_date),
        dateEnd = str(datetime.date.today()),
        )
    # obtain at most maxItems newest articles or blog posts
    resp=q.execQuery(er, sortBy = "date", maxItems = 50000,returnInfo=ReturnInfo(
        articleInfo=ArticleInfoFlags(concepts=False, categories=True, duplicateList=True, location=True),
        categoryInfo = CategoryInfoFlags(),           # details about the categories to return
        locationInfo = LocationInfoFlags(location=True,locationInfo=True,placeCountry=True,population=True,countryArea=True,placeFeatureCode=True),           # details about the locations to return
    ))

    cols = ['art_id','title','sentiment', 'date_id', 'url','country_iso','category']
    main_df = pd.DataFrame(columns = cols)
    category_df = pd.DataFrame(columns = ['category'])
    countries_df = pd.DataFrame(columns = ['label','population', 'area'])
    newspaper_df = pd.DataFrame(columns=['newspaper_id','newspaper_title'])
    for art in resp:
        country = None
        place = None
        main_cat = None
        newspaper_uri=art['source']['uri']
        newspaper_title=art['source']['title']
        country_iso=-1
        newspaper_df=newspaper_df.append({'newspaper_id': newspaper_uri, 'newspaper_title':newspaper_title},ignore_index=True)
        #if a location is given
        if ((art['location'] is not None)):
            # find country 
            if (art['location']['type']=='place'):
                country, place = get_place_and_country(art)
                country_iso = get_country_iso(country)
            elif(art['location']['type']=='country'):
                country=art['location']['label']['eng']
                country_iso=get_country_iso(country)

            #search manually for country tags in headline
            else:
                for country_ in countries_rest_dict.keys():
                    if country_ in '''{}'''.format(art['title']):
                        country=country_
                        country_iso = get_country_iso(country)

        ### get all categories with weights
        if (art['categories'] is not None):
            cat_list = [(el['uri'],el['wgt']) for el in art['categories']]
            if (len(cat_list)>0):
                ## get main category
                main_cat, wgt = max(cat_list,key=itemgetter(1))
                for el in cat_list:
                    uri, wgt = max(cat_list,key=itemgetter(1))
                    if uri not in list(category_df['category']):
                        category_df=category_df.append({'category':uri},ignore_index=True)
        main_df = main_df.append({'art_id': art['uri'], 'title':'''{}'''.format(art['title']), 'sentiment':art['sentiment'], 'date_id':art['date'], 'url':'''{}'''.format(art['url']),'country_iso':country_iso,'category':'''{}'''.format(main_cat),'newspaper_id':'''{}'''.format(newspaper_uri)}, ignore_index=True)
        main_df = main_df[main_df['country_iso']!=-1]
    return main_df,category_df,newspaper_df,countries_df

def write_dates_to_db(main_df,db):
    dates_df=main_df[['date_id']].copy().drop_duplicates()
    dates_in_db=db.execute("SELECT * FROM dates_tab").fetchall()
    dates_in_db=[date.strftime('%Y-%m-%d') for date, in dates_in_db]
    newdates_df=dates_df[~dates_df['date_id'].isin(dates_in_db)]
    newdates_df.to_sql('dates_tab', con=db, if_exists='append',index=False)

def write_newspaper_to_df(newspaper_df,engine):
    newspaper_df.drop_duplicates(inplace=True)
    newspapers_in_db=[id for id, in engine.execute("SELECT newspaper_id FROM newspapers_tab").fetchall()]
    new_newspapers=newspaper_df[~newspaper_df['newspaper_id'].isin(newspapers_in_db)]    
    new_newspapers.to_sql('newspapers_tab', con=engine, if_exists='append',index=False)

def write_main_to_df(main_df,engine):
    main_df.drop_duplicates(inplace=True)
    articles_in_db=[art_id for art_id, in engine.execute("SELECT art_id FROM articles_tab").fetchall()]
    new_articles=main_df[~main_df['art_id'].isin(articles_in_db)]    
    new_articles.to_sql('articles_tab', con=engine, if_exists='append',index=False)

def write_categories_to_df(categories_df,engine):
    categories_df.drop_duplicates(inplace=True)
    categories_in_db=[cat for cat, in engine.execute("SELECT category FROM categories_tab").fetchall()]
    new_categories=categories_df[~categories_df['category'].isin(categories_in_db)]    
    new_categories.to_sql('categories_tab', con=engine, if_exists='append',index=False)

def write_country_to_db(df,engine):
    df.to_sql('countries_tab', con=engine, if_exists='append',index=False)

# create dict for encoding of countries
country_df = get_countries_df()
countries_encoding_df=country_df[['country_iso','country_name']].copy()
countries_rest_dict = countries_encoding_df.set_index('country_name')['country_iso'].to_dict()
countries_rest = list(countries_encoding_df['country_name']) # not needed, but useful for checks

main_df,category_df,newspaper_df,countries_df=get_data_from_EventRegistry(countries_rest_dict)

db = sql.create_engine('mysql+pymysql://admin:datawarehousing@database-1.cl6uila8iago.eu-central-1.rds.amazonaws.com:3306/dbtest')
#db = sql.create_engine('mysql+pymysql://warehousing_team:nandan123@localhost:3306/ds_prog',convert_unicode=True)

## write tables to database, order is important
write_country_to_db(country_df,db) 
write_categories_to_df(category_df,db)
write_dates_to_db(main_df,db)
write_newspaper_to_df(newspaper_df,db)
write_main_to_df(main_df,db)
