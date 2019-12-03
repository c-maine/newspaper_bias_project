DROP TABLE articles_tab;
DROP TABLE newspapers_tab;
DROP TABLE countries_tab;
DROP TABLE dates_tab;
DROP TABLE categories_tab;


CREATE TABLE countries_tab(
	country_iso VARCHAR(10) PRIMARY KEY,
	country_name TEXT NOT NULL,
	population INTEGER,
	n_languages INTEGER,
	eng_language INTEGER,
	area INTEGER,
	capital VARCHAR(30),
	region VARCHAR(30) NOT NULL,
	subregion VARCHAR(30) NOT NULL,
	continent_name VARCHAR(100) NOT NULL
);

CREATE TABLE dates_tab(
	date_id DATE PRIMARY KEY
);

CREATE TABLE newspapers_tab(
	newspaper_id VARCHAR(50) PRIMARY KEY,
    newspaper_title VARCHAR(60)
);

CREATE TABLE categories_tab(
	category VARCHAR(300) PRIMARY KEY
);


CREATE TABLE articles_tab(
	art_id VARCHAR(30) PRIMARY KEY,
	title TEXT NOT NULL,
	date_id DATE NOT NULL,
	CONSTRAINT FOREIGN KEY (date_id) REFERENCES dates_tab (date_id),
	newspaper_id VARCHAR(50) NOT NULL,
	CONSTRAINT FOREIGN KEY (newspaper_id) REFERENCES newspapers_tab (newspaper_id) ON DELETE RESTRICT ON UPDATE CASCADE,
	country_iso VARCHAR(10) NOT NULL,
	CONSTRAINT FOREIGN KEY (country_iso) REFERENCES countries_tab (country_iso) ON DELETE RESTRICT ON UPDATE CASCADE,
	url VARCHAR(1000) NOT NULL,
	sentiment FLOAT,
	category VARCHAR(300)
);


