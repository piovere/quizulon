CREATE TABLE user (
id INTEGER PRIMARY KEY,
name TEXT,
email TEXT NOT NULL,
password_hash BLOB NOT NULL,
created_date TEXT,
last_login TEXT);

CREATE TABLE question (
id INTEGER PRIMARY KEY,
text TEXT NOT NULL,
creator INTEGER,
FOREIGN KEY (creator) REFERENCES user(id));

CREATE TABLE choice (
id INTEGER PRIMARY KEY,
text TEXT NOT NULL,
correct BOOLEAN NOT NULL,
question_id INTEGER NOT NULL,
FOREIGN KEY (question_id) REFERENCES question(id));
