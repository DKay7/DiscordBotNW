CREATE TABLE IF NOT EXISTS warns (
 UserID integer PRIMARY KEY,
 NumWarns integer DEFAULT 0,
 LastReasons text DEFAULT ""
);