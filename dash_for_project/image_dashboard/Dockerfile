FROM python:3.7

RUN pip install dash pymysql sqlalchemy pandas datetime dash_core_components dash_html_components plotly records

ADD . .

CMD [ "python", "./app.py" ]

