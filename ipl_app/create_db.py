import sqlite3

# Connect or create the database
conn = sqlite3.connect("ipl2024.db")
cursor = conn.cursor()

# Create Teams table
cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")

# Create Players table
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    team_id INTEGER,
    runs INTEGER DEFAULT 0,
    wickets INTEGER DEFAULT 0,
    FOREIGN KEY(team_id) REFERENCES teams(id)
)
""")

# Create Points table
cursor.execute("""
CREATE TABLE IF NOT EXISTS points_table (
    team_id INTEGER PRIMARY KEY,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    FOREIGN KEY(team_id) REFERENCES teams(id)
)
""")

# Insert Teams
teams = ['CSK', 'MI', 'RCB', 'KKR']
for team in teams:
    cursor.execute("INSERT OR IGNORE INTO teams (name) VALUES (?)", (team,))

# Insert Players (dummy 2 per team)
players = {
    'CSK': [('Ruturaj Gaikwad', 540, 0), ('MS Dhoni', 120, 0)],
    'MI': [('Rohit Sharma', 360, 0), ('Jasprit Bumrah', 10, 21)],
    'RCB': [('Virat Kohli', 630, 0), ('Harshal Patel', 5, 18)],
    'KKR': [('Shreyas Iyer', 410, 0), ('Andre Russell', 300, 16)],
}

# Insert Players
for team, player_list in players.items():
    cursor.execute("SELECT id FROM teams WHERE name=?", (team,))
    team_id = cursor.fetchone()[0]
    for name, runs, wickets in player_list:
        cursor.execute("INSERT INTO players (name, team_id, runs, wickets) VALUES (?, ?, ?, ?)",
                       (name, team_id, runs, wickets))

# Insert Points Table
cursor.execute("SELECT id FROM teams")
for (team_id,) in cursor.fetchall():
    cursor.execute("INSERT OR IGNORE INTO points_table (team_id, matches_played, wins, points) VALUES (?, 0, 0, 0)", (team_id,))

conn.commit()
conn.close()
print("Database created successfully as ipl2024.db")
