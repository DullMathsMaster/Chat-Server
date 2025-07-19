CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient uniqueidentifier NOT NULL,
    sender uniqueidentifier NOT NULL,
    time TIMESTAMP NOT NULL,
    read BOOL NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (recipient) REFERENCES user_profiles(user_id),
    FOREIGN KEY (sender) REFERENCES user_profiles(user_id)
);

CREATE TABLE user_profiles (
    user_id uniqueidentifier NOT NULL PRIMARY KEY,
    image TEXT,
    name TEXT NOT NULL,
    bio TEXT
);

CREATE TABLE group_chats (
    group_id uniqueidentifier NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
);

CREATE TABLE group_members (
    group_id uniqueidentifier NOT NULL,
    user_id uniqueidentifier NOT NULL,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES group_chats(group_id),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

CREATE TABLE group_messages (
    group_id uniqueidentifier NOT NULL,
    sender uniqueidentifier NOT NULL,
    time TIMESTAMP NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES group_chats(group_id),
    FOREIGN KEY (sender) REFERENCES user_profiles(user_id)
);

-- INSERT INTO messages(recipient, sender, time, read, content) 
-- VALUES ('alice', 'bob', CURRENT_TIMESTAMP, 0, "hi");

SELECT * FROM messages;
-- DROP TABLE messages;