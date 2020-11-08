\c lotterydb

CREATE TABLE mini_loto (
  "lottery_date" TIMESTAMP NOT NULL,
  "times" VARCHAR(50) NOT NULL,
  "number_1"  VARCHAR(3) NOT NULL,
  "number_2" VARCHAR(3) NOT NULL,
  "number_3" VARCHAR(3) NOT NULL,
  "number_4" VARCHAR(3) NOT NULL,
  "number_5" VARCHAR(3) NOT NULL,
  "bonus_number_1" VARCHAR(3) NOT NULL,
  PRIMARY KEY (times)
);

CREATE TABLE loto_six (
  "lottery_date" TIMESTAMP NOT NULL,
  "times" VARCHAR(50) NOT NULL,
  "number_1"  VARCHAR(3) NOT NULL,
  "number_2" VARCHAR(3) NOT NULL,
  "number_3" VARCHAR(3) NOT NULL,
  "number_4" VARCHAR(3) NOT NULL,
  "number_5" VARCHAR(3) NOT NULL,
  "number_6" VARCHAR(3) NOT NULL,
  "bonus_number_1" VARCHAR(3) NOT NULL,
  PRIMARY KEY (times)
);

CREATE TABLE loto_seven (
  "lottery_date" TIMESTAMP NOT NULL,
  "times" VARCHAR(50) NOT NULL,
  "number_1"  VARCHAR(3) NOT NULL,
  "number_2" VARCHAR(3) NOT NULL,
  "number_3" VARCHAR(3) NOT NULL,
  "number_4" VARCHAR(3) NOT NULL,
  "number_5" VARCHAR(3) NOT NULL,
  "number_6" VARCHAR(3) NOT NULL,
  "number_7" VARCHAR(3) NOT NULL,
  "bonus_number_1" VARCHAR(3) NOT NULL,
  "bonus_number_2" VARCHAR(3) NOT NULL,
  PRIMARY KEY (times)
);