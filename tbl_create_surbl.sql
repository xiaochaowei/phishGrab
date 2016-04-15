create database if not exists PhishSurbl;
USE PhishSurbl;
drop table if exists phishSite;
CREATE TABLE phishSite(
	phish_id integer primary key auto_increment,
	url varchar(255) not null,
	submission_time DATETIME,
	grab integer(1),
	ip varchar(32)
);

CREATE TRIGGER insertsurbl
BEFORE INSERT on PhishSite FOR EACH ROW SET NEW.grab = 0, NEW.submission_time = NOW();
