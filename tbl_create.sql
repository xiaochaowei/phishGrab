create database if not exists PhishTank;
USE PhishTank;
drop table if exists phishSite;
CREATE TABLE phishSite(
	phish_id integer primary key,
	url varchar(255) not null,
	phish_detail_url varchar(255),
	submission_time DATETIME,
	verified varchar(3),
	verification_time DATETIME,
	online varchar(3),
	target varchar(32),
	grab integer(1),
	ip varchar(32)
);

CREATE TRIGGER insertphishSite
BEFORE INSERT on phishSite FOR EACH ROW SET NEW.grab = 0;
