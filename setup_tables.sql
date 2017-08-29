CREATE TABLE users (
    user_id varchar (30) PRIMARY KEY,
    firstname varchar (30),
    lastname varchar (30),
    gender varchar (30),
    timezone smallint,
    locale varchar (8),
    profile_pic varchar (160),
    message_first bigint,
    message_previous bigint,
    message_current bigint,
    how_are_you_last bigint,    
	node_current varchar (30),
	node_previous varchar (30)
);

CREATE TABLE logs (
    message_timestamp bigint PRIMARY KEY,
    message_id varchar (50),
    message varchar (360),
    user_id varchar (30),
    node_current varchar (30),
    node_previous varchar (30),
    node_next varchar (30)
);
