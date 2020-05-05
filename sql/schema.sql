-- Might have to use 'PRAGMA foreign_keys = ON' with every new session to enable foreign keys
-- https://stackoverflow.com/questions/5890250/on-delete-cascade-in-sqlite3

DROP TABLE IF EXISTS users;
CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40) NOT NULL,
  filename VARCHAR(64) NOT NULL,
  password VARCHAR(256) NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(username)
);

DROP TABLE IF EXISTS posts;
CREATE TABLE posts(
	postid INTEGER NOT NULL,
	filename VARCHAR(64) NOT NULL,
	owner VARCHAR(20) NOT NULL,
	created DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(postid),
	FOREIGN KEY(owner) REFERENCES users ON DELETE CASCADE
);

DROP TABLE IF EXISTS following;
CREATE TABLE following(
	username1 VARCHAR(20) NOT NULL,
	username2 VARCHAR(20) NOT NULL,
	created DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(username1, username2),
	FOREIGN KEY(username1) REFERENCES users ON DELETE CASCADE,
	FOREIGN KEY(username2) REFERENCES users ON DELETE CASCADE
);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments(
	commentid INTEGER NOT NULL,
	owner VARCHAR(20) NOT NULL,
	postid INTEGER NOT NULL,
	text VARCHAR(1024) NOT NULL,
	created DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(commentid),
	FOREIGN KEY(owner) REFERENCES users ON DELETE CASCADE,
	FOREIGN KEY(postid) REFERENCES posts ON DELETE CASCADE
);

DROP TABLE IF EXISTS likes;
CREATE TABLE likes(
	owner VARCHAR(20) NOT NULL,
	postid INTEGER NOT NULL,
	created DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(owner, postid),
	FOREIGN KEY(owner) REFERENCES users ON DELETE CASCADE,
	FOREIGN KEY(postid) REFERENCES posts ON DELETE CASCADE
);
