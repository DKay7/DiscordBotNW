CREATE TABLE IF NOT EXISTS warns (
 UserID integer,
 NumWarns integer DEFAULT 0,
 LastReasons text DEFAULT "",
 GuildID integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS temp_bans (
 UserID integer,
 EndTime timestamp,
 GuildID integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS temp_mutes (
 UserID integer,
 EndTime timestamp,
 MuteType text,
 GuildID integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS temp_roles (
 UserID integer,
 EndTime timestamp,
 GuildID integer,
 PRIMARY KEY(UserID, GuildID)
);