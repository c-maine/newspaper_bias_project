DROP TABLE articles_tab_news;
DROP TABLE count_tab_news;
DROP TABLE countries_tab;

CREATE TABLE countries_tab(
	country_iso VARCHAR(10) PRIMARY KEY,
	country_name TEXT NOT NULL,
	population INTEGER,
	n_languages INTEGER,
	eng_language INTEGER,
	area INTEGER,
	capital VARCHAR(30),
	region VARCHAR(30) NOT NULL,
	subregion VARCHAR(30) NOT NULL
);

CREATE TABLE articles_tab_news(
    description VARCHAR(500),
    title VARCHAR(150) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    date_published DATE,
    source VARCHAR(50) NOT NULL,
    country_iso VARCHAR(3) NOT NULL,
	CONSTRAINT FOREIGN KEY (country_iso) REFERENCES countries_tab (country_iso) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE count_tab_news(
    country_iso VARCHAR(10) NOT NULL,
	CONSTRAINT FOREIGN KEY (country_iso) REFERENCES countries_tab (country_iso) ON DELETE RESTRICT ON UPDATE CASCADE,
	source VARCHAR(50) NOT NULL,
	fill_date DATE,
	count INT
);

