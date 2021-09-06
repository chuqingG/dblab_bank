create database mybank;
use mybank;

-- drop table if exists alembic_version;
-- create table alembic_version (
-- 	version_num VARCHAR(32) Not NULL,
-- 	constraint alembic_version_pkc Primary Key (version_num)
-- );

-- insert into alembic_version VALUES('ad38f79691b');

drop table if exists branches;
create  table branches (
    name VARCHAR(100) NOT NULL,
    city VARCHAR(20),
    asset INTEGER,
    constraint branches_pk PRIMARY KEY (name)
);

INSERT INTO branches VALUES('合肥第一支行','合肥',2000000);
INSERT INTO branches VALUES('合肥第二支行','合肥',3000000);
INSERT INTO branches VALUES('合肥第三支行','合肥',4000000);
INSERT INTO branches VALUES('南京第一支行','南京',1000000);

drop table if exists clients;
create table clients(
    id VARCHAR(20) NOT NULL,
	name VARCHAR(20),
	phone VARCHAR(15),
	address VARCHAR(256),
	contact_name VARCHAR(20),
	contact_phone VARCHAR(15),
	contact_email VARCHAR(30),
	contact_relation VARCHAR(40),
    constraint clients_pk PRIMARY KEY(id)
);

INSERT INTO clients VALUES('27485638','朱节中','10086','肥西路','周志华','10010','fhedcj@qq.com','同事');
INSERT INTO clients VALUES('47293924','皓都','12345','流云观','乐嫣','54321','','配偶');
INSERT INTO clients VALUES('85294791','Petterson','12742','America','Hennessy','','','好友');

drop table if exists employees;
create table employees (
    id VARCHAR(20) NOT NULL,
	branch_name VARCHAR(100),
	name VARCHAR(20),
	phone VARCHAR(15),
	address VARCHAR(256),
	enroll_date DATETIME,
	constraint employees_pk PRIMARY KEY (id),
	constraint employees_fk FOREIGN KEY(branch_name) REFERENCES branches (name)
);

INSERT INTO employees VALUES('138942','合肥第一支行','张三','111222','黄山路','2020-03-06');
INSERT INTO employees VALUES('019013','合肥第二支行','李四','222333','槽郢路','2018-09-12');
INSERT INTO employees VALUES('216458','合肥第三支行','王五','999222','官亭路','2019-08-19');
INSERT INTO employees VALUES('117027','合肥第一支行','赵六','777766','滨湖路','2021-06-04');
INSERT INTO employees VALUES('812732','南京第一支行','无名','123456','合肥路','2021-06-24');

drop table if exists loans;
create table loans(
    id VARCHAR(20) NOT NULL,
	branch_name VARCHAR(100),
	employee_id VARCHAR(20),
	amount FLOAT, 
	status VARCHAR(20),
	constraint loans_pk PRIMARY KEY (id),
	constraint loans_fk_name FOREIGN KEY(branch_name) REFERENCES branches (name),
	constraint loans_fk_id FOREIGN KEY(employee_id) REFERENCES employees (id)
);

INSERT INTO loans VALUES('045','合肥第一支行','117027',3000.0,'未开始发放');
INSERT INTO loans VALUES('078','合肥第三支行','216458',5000.0,'未开始发放');
INSERT INTO loans VALUES('091','南京第一支行','812732',2000.0,'未开始发放');
drop table if exists savings;
create table savings(
    id VARCHAR(20) NOT NULL,
	branch_name VARCHAR(100),
	employee_id VARCHAR(20),
	balance FLOAT,
	open_date DATETIME,
	interest_rate FLOAT,
	currency_type VARCHAR(5),
	last_access_date DATETIME,
	constraint savings_pk PRIMARY KEY (id),
	constraint savings_fk_name FOREIGN KEY(branch_name) REFERENCES branches (name),
	constraint savings_fk_id FOREIGN KEY(employee_id) REFERENCES employees (id)
);

INSERT INTO savings VALUES('s01','合肥第一支行','138942',500.0,'2021-05-15 21:46:16','2.8','CNY','2021-06-23 21:46:16');
INSERT INTO savings VALUES('s02','合肥第二支行','019013',2000.0,'2020-08-25 23:59:38','3.6','EUR','2020-08-25 23:59:38');
INSERT INTO savings VALUES('s11','合肥第三支行','216458',1030.4,'2021-03-12 00:04:39','3.2','CNY','2021-03-12 00:04:39');

drop table if exists checks;
create table checks(
    id VARCHAR(20) NOT NULL,
	branch_name VARCHAR(100),
	employee_id VARCHAR(20),
	balance FLOAT,
	open_date DATETIME,
	over_draft FLOAT,
	last_access_date DATETIME,
	constraint checks_pk PRIMARY KEY (id),
	constraint checks_fk_name FOREIGN KEY(branch_name) REFERENCES branches (name),
	constraint checks_fk_id FOREIGN KEY(employee_id) REFERENCES employees (id)
);

INSERT INTO checks VALUES('c12','合肥第一支行','138942',1000.0,'2020-08-29 02:06:38',1000.0,'2020-08-29 02:06:38');
INSERT INTO checks VALUES('c31','合肥第二支行','019013',4000.0,'2020-12-19 05:16:53',2000.0,'2020-12-19 05:16:53');

drop table if exists hasloans;
create table hasloans(
    client_id VARCHAR(20) NOT NULL,
	loan_id VARCHAR(20) NOT NULL,
	PRIMARY KEY (client_id, loan_id),
	constraint hasloans_pk FOREIGN KEY(client_id) REFERENCES clients (id),
	constraint hasloans_fk FOREIGN KEY(loan_id) REFERENCES loans (id)
);
INSERT INTO hasloans VALUES('27485638','045');
INSERT INTO hasloans VALUES('85294791','078');
INSERT INTO hasloans VALUES('211284188806271372','091');

drop table if exists  clientsavings;
create table clientsavings (
	client_id VARCHAR(20) NOT NULL,
	saving_id VARCHAR(20) NOT NULL,
	constraint  clients_pk PRIMARY KEY (client_id, saving_id),
	constraint  clients_fk_id FOREIGN KEY(client_id) REFERENCES clients (id),
	constraint  clients_fk_sid FOREIGN KEY(saving_id) REFERENCES savings (id)
);
INSERT INTO clientsavings VALUES('85294791','s01');
INSERT INTO clientsavings VALUES('47293924','s02');
INSERT INTO clientsavings VALUES('47293924','s11');


drop table if exists clientchecks;
CREATE TABLE clientchecks (
	client_id VARCHAR(20) NOT NULL,
	check_id VARCHAR(20) NOT NULL,
	constraint  clientcheck_pk PRIMARY KEY (client_id, check_id),
	constraint  clientcheck_fk_id1 FOREIGN KEY(client_id) REFERENCES clients (id),
	constraint  clientcheck_fk_id2 FOREIGN KEY(check_id) REFERENCES checks (id)
);

INSERT INTO clientchecks VALUES('27485638','c12');
INSERT INTO clientchecks VALUES('47293924','c31');


drop table if exists loanlogs;
create table loanlogs (
    id VARCHAR(30) NOT NULL,
	loan_id VARCHAR(20),
	date DATETIME,
	amount FLOAT,
	constraint loanlogs_pk PRIMARY KEY (id),
	constraint loanlogs_fk FOREIGN KEY(loan_id) REFERENCES loans (id)
);

drop table if exists savingconstraints;
CREATE TABLE savingconstraints (
	client_id VARCHAR(20) NOT NULL,
	branch_name VARCHAR(100) NOT NULL,
	saving_id VARCHAR(20) NOT NULL,
	constraint savingconstraints_pk PRIMARY KEY (client_id, branch_name, saving_id),
	CONSTRAINT con1 UNIQUE (client_id, branch_name),
	constraint savingconstraints_fk_id1 FOREIGN KEY(client_id) REFERENCES clients (id),
	constraint savingconstraints_fk_name FOREIGN KEY(branch_name) REFERENCES branches (name),
	constraint savingconstraints_fk_id2 FOREIGN KEY(saving_id) REFERENCES savings (id)
);

INSERT INTO savingconstraints VALUES('47293924','合肥第一支行','s01');
INSERT INTO savingconstraints VALUES('47293924','合肥第二支行','s02');
INSERT INTO savingconstraints VALUES('27485638','合肥第三支行','s11');

drop table if exists checkconstraint;
CREATE TABLE checkconstraint (
	client_id VARCHAR(20) NOT NULL,
	branch_name VARCHAR(100) NOT NULL,
	check_id VARCHAR(20) NOT NULL,
	constraint checkconstraint_pk PRIMARY KEY (client_id, branch_name, check_id),
	CONSTRAINT con1 UNIQUE (client_id, branch_name),
	constraint checkconstraint_fk_id1 FOREIGN KEY(client_id) REFERENCES clients (id),
	constraint checkconstraint_fk_name FOREIGN KEY(branch_name) REFERENCES branches (name),
	constraint checkconstraint_fk_id2 FOREIGN KEY(check_id) REFERENCES checks (id)
);

INSERT INTO checkconstraint VALUES('47293924','合肥第一支行','c12');
INSERT INTO checkconstraint VALUES('85294791','合肥第二支行','c31');

drop table if exists branchrecords;
CREATE TABLE branchrecords (
	id INTEGER NOT NULL,
	branch_name VARCHAR(100),
	OpType VARCHAR(4),
	OpTime DATETIME,
	OpMoney FLOAT,
	constraint branchrecords_pk PRIMARY KEY (id),
	constraint branchrecords_fk FOREIGN KEY(branch_name) REFERENCES branches (name)
);

drop table if exists system_user;
CREATE TABLE system_user (
	id INTEGER NOT NULL,
	username VARCHAR(64),
	password_hash VARCHAR(128),
	constraint system_user_pk PRIMARY KEY (id),
	UNIQUE (username)
);
INSERT INTO system_user VALUES(0,'honecker','pbkdf2:sha256:150000$wDG6c4AF$dfeef6ab6b3a534d203d065b29820f1409d6617e9a80b54bb65eb1d9d59bd47c');
INSERT INTO system_user VALUES(1,'bc','pbkdf2:sha256:150000$3Bk5TlWO$56b9cfc9df16f9e90dcfb5483a23d08f7fe9353b5175e70ace4667ac76547aac');
INSERT INTO system_user VALUES(2,'xc','pbkdf2:sha256:150000$EU6M1CU3$68db5364b9fa6466930663faebd1c802a33187a26e492fb7c8c3ee999d891308');
INSERT INTO system_user VALUES(3,'qwe','pbkdf2:sha256:150000$WHncQdlY$e525ba97ed553efe22e384c22d6427b190ab517eea2bd974521d00d7c49f200d');