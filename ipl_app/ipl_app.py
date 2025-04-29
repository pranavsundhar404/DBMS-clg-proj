import streamlit as st
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('ipl2024.db', check_same_thread=False)
cursor = conn.cursor()

# --- Helper Functions ---
def get_teams():
    cursor.execute("SELECT * FROM teams")
    return cursor.fetchall()

def get_players():
    cursor.execute("""
        SELECT players.id, players.name, teams.name AS team, runs, wickets 
        FROM players 
        JOIN teams ON players.team_id = teams.id
    """)
    return pd.DataFrame(cursor.fetchall(), columns=["ID", "Name", "Team", "Runs", "Wickets"])

def get_points_table():
    cursor.execute("""
        SELECT teams.name AS Team, matches_played, wins, points 
        FROM points_table 
        JOIN teams ON points_table.team_id = teams.id
        ORDER BY points DESC
    """)
    return pd.DataFrame(cursor.fetchall(), columns=["Team", "Matches Played", "Wins", "Points"])

def add_player(name, team_id, runs, wickets):
    cursor.execute("INSERT INTO players (name, team_id, runs, wickets) VALUES (?, ?, ?, ?)", (name, team_id, runs, wickets))
    conn.commit()

def delete_player(player_id):
    cursor.execute("DELETE FROM players WHERE id=?", (player_id,))
    conn.commit()

def update_player(player_id, name, team_id, runs, wickets):
    cursor.execute("UPDATE players SET name=?, team_id=?, runs=?, wickets=? WHERE id=?", 
                   (name, team_id, runs, wickets, player_id))
    conn.commit()

def update_points_table(team_id, matches_played, wins, points):
    cursor.execute("UPDATE points_table SET matches_played=?, wins=?, points=? WHERE team_id=?", 
                   (matches_played, wins, points, team_id))
    conn.commit()

def get_top_runs():
    cursor.execute("""
        SELECT players.name, teams.name AS team, runs 
        FROM players 
        JOIN teams ON players.team_id = teams.id 
        ORDER BY runs DESC 
        LIMIT 5
    """)
    return pd.DataFrame(cursor.fetchall(), columns=["Player", "Team", "Runs"])

def get_top_wickets():
    cursor.execute("""
        SELECT players.name, teams.name AS team, wickets 
        FROM players 
        JOIN teams ON players.team_id = teams.id 
        ORDER BY wickets DESC 
        LIMIT 5
    """)
    return pd.DataFrame(cursor.fetchall(), columns=["Player", "Team", "Wickets"])

# --- Streamlit UI ---
st.title("🏏 IPL 2024 Dashboard")

menu = st.sidebar.radio("Navigation", [
    "Home", "Show Teams", "Show Players", "Points Table", 
    "Add Player", "Update Player", "Delete Player",
    "Update Points", "Orange Cap", "Purple Cap"
])

teams = get_teams()
team_dict = {team[1]: team[0] for team in teams}

# Home Page
if menu == "Home":
    st.header("Welcome to IPL 2024!")
    st.image("/Users/pranavsundhar26/ipl_app/ipllogo.png", width=300)
    st.markdown("### Manage your favorite IPL teams, players, and performance stats in one place.")
    st.markdown("- Add or update player data")
    st.markdown("- Track top run scorers and wicket takers")
    st.markdown("- View team standings and stats")
    st.markdown("Get started using the sidebar!")

elif menu == "Show Teams":
    st.subheader("All Teams")
    st.table(pd.DataFrame(teams, columns=["ID", "Team Name"]))

elif menu == "Show Players":
    st.subheader("All Players")
    st.dataframe(get_players())

elif menu == "Points Table":
    st.subheader("🏆 Points Table")
    st.dataframe(get_points_table())

elif menu == "Add Player":
    st.subheader("➕ Add New Player")
    name = st.text_input("Name")
    team = st.selectbox("Team", list(team_dict.keys()))
    runs = st.number_input("Runs", 0)
    wickets = st.number_input("Wickets", 0)
    if st.button("Add"):
        add_player(name, team_dict[team], runs, wickets)
        st.success("Player added!")

elif menu == "Update Player":
    st.subheader("✏️ Update Player")
    players_df = get_players()
    player_options = {f"{row['Name']} ({row['Team']})": row for idx, row in players_df.iterrows()}
    selected = st.selectbox("Select Player", list(player_options.keys()))
    selected_data = player_options[selected]

    new_name = st.text_input("New Name", selected_data["Name"])
    new_team = st.selectbox("Team", list(team_dict.keys()), index=list(team_dict.keys()).index(selected_data["Team"]))
    new_runs = st.number_input("Runs", 0, value=selected_data["Runs"])
    new_wickets = st.number_input("Wickets", 0, value=selected_data["Wickets"])

    if st.button("Update"):
        update_player(selected_data["ID"], new_name, team_dict[new_team], new_runs, new_wickets)
        st.success("Player updated!")

elif menu == "Delete Player":
    st.subheader("❌ Delete Player")
    players_df = get_players()
    player_options = {f"{row['Name']} ({row['Team']})": row["ID"] for idx, row in players_df.iterrows()}
    selected = st.selectbox("Select Player to Delete", list(player_options.keys()))
    if st.button("Delete"):
        delete_player(player_options[selected])
        st.success("Player deleted!")

elif menu == "Update Points":
    st.subheader("🔁 Update Points Table")
    for team in teams:
        team_name = team[1]
        team_id = team[0]
        st.markdown(f"#### {team_name}")
        matches = st.number_input(f"{team_name} Matches Played", 0, key=f"mp_{team_id}")
        wins = st.number_input(f"{team_name} Wins", 0, key=f"wins_{team_id}")
        points = st.number_input(f"{team_name} Points", 0, key=f"pts_{team_id}")
        if st.button(f"Update {team_name}", key=f"btn_{team_id}"):
            update_points_table(team_id, matches, wins, points)
            st.success(f"{team_name} points updated!")

elif menu == "Orange Cap":
    st.subheader("🟠 Orange Cap - Top Run Scorers")
    st.table(get_top_runs())

elif menu == "Purple Cap":
    st.subheader("🟣 Purple Cap - Top Wicket Takers")
    st.table(get_top_wickets())
