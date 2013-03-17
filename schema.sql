CREATE TABLE topics(
	id serial primary key,
	title text,
	created timestamp default now(),
	active boolean default 't' 
);

CREATE TABLE topics(
	id serial primary key,
	topic_id foreign key
	title text,
	created timestamp default now(),
	active boolean default 't' 
);