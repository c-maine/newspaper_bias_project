FROM python:3.7

RUN pip install pymysql sqlalchemy country_list pandas restcountries_py datetime requests

ADD . .

CMD [ "python", "./fill.py" ]

