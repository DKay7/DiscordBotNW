CREATE TABLE IF NOT EXISTS warns (
 UserID integer PRIMARY KEY,
 NumWarns integer DEFAULT 0,
 LastReasons text DEFAULT ""
);

CREATE TABLE IF NOT EXISTS temp_bans (
 UserID integer,
 EndTime timestamp,
 GuildID integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS muted (
 UserID integer,
 EndTime timestamp,
 Type text,
 GuildID integer,
 PRIMARY KEY(UserID, GuildID)
);