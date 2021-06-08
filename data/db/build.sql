CREATE TABLE IF NOT EXISTS warns (
 UserID integer,
 GuildID integer,
 NumWarns integer,
 LastReasons text,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS temp_bans (
 UserID integer,
 GuildID integer,
 EndTime timestamp,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS temp_mutes (
 UserID integer,
 GuildID integer,
 EndTime timestamp,
 MuteType text,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS temp_roles (
 UserID integer,
 GuildID integer,
 EndTime timestamp,
 RoleID integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS voice_rating_trace (
 UserID integer,
 GuildID integer,
 StartTime timestamp,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS rating (
 UserID integer,
 GuildID integer,
 Rating float,
 Level integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS marriage (
 UserID integer,
 TargetID integer,
 PRIMARY KEY(UserID, TargetID)
);

CREATE TABLE IF NOT EXISTS marriage_asks (
 UserID integer,
 TargetID integer,
 AskerMessageID integer,
 PRIMARY KEY(UserID, TargetID)
);

CREATE TABLE IF NOT EXISTS sex_asks (
 UserID integer,
 TargetID integer,
 AskerMessageID integer,
 PRIMARY KEY(UserID, TargetID)
);