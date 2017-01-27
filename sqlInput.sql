use geonames;
CREATE TABLE geoname (geonameid INT, name VARCHAR(200), asciiname VARCHAR(200), alternatenames VARCHAR(10000), latitude DECIMAL(10, 8) NOT NULL, longitude DECIMAL(11, 8) NOT NULL, featureclass CHAR(1), featurecode VARCHAR(10), countrycode CHAR(2), cc2 VARCHAR(200), admin1code VARCHAR(20), admin2code VARCHAR(80), admin3code VARCHAR(20), admin4code VARCHAR(20), population BIGINT, elevation INT, dem INT, timezone VARCHAR(40), modificationdate DATE);
LOAD DATA LOCAL INFILE '/var/lib/mysql/allCountries.txt' INTO TABLE geoname;
