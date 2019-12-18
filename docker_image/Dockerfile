FROM python:3.7

RUN pip install pymysql sqlalchemy country_list pandas restcountries_py datetime requests pathlib
RUN pip install -U python-dotenv

ADD . .

CMD [ "python", "./true_init.py" ]

