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

CREATE TABLE IF NOT EXISTS clan_voice_rating_trace (
 UserID integer,
 GroupChannelID integer,
 StartTime timestamp,
 PRIMARY KEY(UserID, GroupChannelID)
);

CREATE TABLE IF NOT EXISTS rating (
 UserID integer,
 GuildID integer,
 Rating float,
 Level integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS clan_rating (
 UserID integer,
 GroupChannelID integer,
 Rating float,
 Level integer,
 PRIMARY KEY(UserID, GroupChannelID)
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

CREATE TABLE IF NOT EXISTS clans (
 ClanName text,
 GroupChannelID integer,
 WinPoints integer DEFAULT 0,
 LeaderRoleId integer,
 DepRoleId integer,
 MemberRoleId integer,
 PRIMARY KEY(ClanName, GroupChannelID)
);

CREATE TABLE IF NOT EXISTS clan_asks (
 TargetID integer,
 GuildID integer,
 AskerMessageID integer,
 ChannelID integer,
 ClanName text,
 Type text,
 PRIMARY KEY(TargetID, GuildID, ClanName, Type)
);

CREATE TABLE IF NOT EXISTS clan_economy (
 UserID integer,
 GroupChannelID integer,
 Money Integer,
 PRIMARY KEY(UserID, GroupChannelID)
);

CREATE TABLE IF NOT EXISTS clan_shops (
 GroupChannelID integer,
 RoleID integer,
 Cost integer,
 PRIMARY KEY(GroupChannelID, RoleID)
);

CREATE TABLE IF NOT EXISTS duel_asks (
 UserID integer,
 TargetID integer,
 AskerMessageID integer,
 Bet integer,
 PRIMARY KEY(UserID, TargetID)
);

CREATE TABLE IF NOT EXISTS economy (
 UserID integer,
 GuildID integer,
 Money Integer,
 PRIMARY KEY(UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS shop (
 GuildID integer,
 RoleID integer,
 Cost integer,
 PRIMARY KEY(RoleID, GuildID)
);

CREATE TABLE IF NOT EXISTS money_symbols (
 GuildID integer,
 Symbol integer DEFAULT "Cr",
 PRIMARY KEY(GuildID)
);

CREATE TABLE IF NOT EXISTS deposit (
 UserID integer,
 GuildID integer,
 DepositMoney Integer,
 PRIMARY KEY(UserID, GuildID)
);

