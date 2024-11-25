from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import streamlit as st
import json
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import sys
sys.path.append("WebScraping")

from NHL import *
from Styles import *

@st.cache_data
def getSeasonTeamStats(season):
    stats = getNHLTeamStats(season)
    return stats

@st.cache_data
def getSeasonTeams(season):
    urls = getNHLTeamsURLs(season)
    return urls

@st.cache_data
def getStandings(season):
    tables = getNHLConferenceStandings(season)
    return tables

@st.cache_data
def getFullSeason(season):
    return pd.DataFrame(getNHLSchedule(season))

def makeConferenceTable(standings, selectedTeam):

    easternTeams = list(map(lambda x: x['team'], standings['East']))

    if selectedTeam in easternTeams:
        st.header(f"Eastern Conference Table")
        data = pd.DataFrame(standings['East'], index=np.arange(1, len(standings['East']) + 1, 1))
    else:
        st.header(f"Western Conference Table")
        data = pd.DataFrame(standings['West'], index=np.arange(1, len(standings['West']) + 1, 1))


    def highlight_rows(row):
        return ['background-color: khaki' if row['Team'] == selectedTeam else '' for _ in row]

    data = data[['team', 'games', 'wins', 'losses', 'points', 'points_pct', 'goals', 'opp_goals']]
    data.rename({'team': 'Team', 'games': 'Games', 'wins': 'Wins', 'losses': 'Losses', 'points': 'Points',
                 'points_pct': 'Points Percentage', 'goals': 'Goals For', 'opp_goals': 'Goals Against'},
                 axis=1, inplace=True)
    styled_data = data.style.apply(lambda row: highlight_rows(row), axis=1)
    st.dataframe(styled_data)

    st.markdown("---")

def makeLastMatchesTable(completedMatches):

    # Apply the conditional formatting to the 'Result' column
    df = completedMatches[
        ['Date', 'Result', 'home_team_name', 'visitor_team_name', 'home_goals', 'visitor_goals', 'Total Goals']]

    df.rename({'home_team_name': 'Home', 'visitor_team_name': 'Away', 'home_goals': 'Home Goals', 'visitor_goals': 'Visitor Goals'},
              axis=1, inplace=True)
    df.drop_duplicates(inplace=True)

    styled_df = df.style.applymap(highlight_positive)

    st.header(f"Last Matches")
    st.dataframe(styled_df, hide_index=True)

    st.markdown("---")

def makePercentagesTablesAndMetrics(completedMatches, selectedTeam):

    jsonData = json.loads(completedMatches.to_json(orient="records"))
    teamScored = list(
        map(lambda x: int(x['home_goals']) if x['home_team_name'] == selectedTeam else int(x['visitor_goals']), jsonData))
    teamConceded = list(
        map(lambda x: int(x['home_goals']) if x['visitor_team_name'] == selectedTeam else int(x['visitor_goals']),
            jsonData))
    teamTotal = list(map(lambda x: int(x['Total Goals']), jsonData))

    scoringTypes = [teamScored, teamConceded, teamTotal]
    rowKeys = ['Scoring', 'Conceading', 'Total']
    scoringMarkers = {
        'Scoring': [1.5, 2.5, 3.5, 4.5, 5.5],
        'Conceading': [1.5, 2.5, 3.5, 4.5, 5.5],
        'Total': [2.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
    }

    rows = {}

    for i in range(len(scoringTypes)):
        rows[rowKeys[i]] = [[f'Over {item}', "{:.2%}".format(
            len(list(filter(lambda x: x > item, scoringTypes[i]))) / len(scoringTypes[i]))]
                            for item in scoringMarkers[rowKeys[i]]]

    st.header(f"{selectedTeam} Percentages")

    writeColumns('dataframe', [f"**Points Scored**", rows['Scoring']],
                 [f"**Points Conceded**", rows['Conceading']],
                 [f"**Total Goals**", rows['Total']])

    st.markdown("---")

    makeMetrics(selectedTeam, teamScored, teamConceded, teamTotal)

def makeMetrics(selectedTeam, teamScored, teamConceded, teamTotal):
    st.header(f"{selectedTeam} Metrics")

    writeColumns('metric', {'label': f"Scoring average", 'value': "{:.2f}".format(np.mean(teamScored))},
                 {'label': f"Conceading average", 'value': "{:.2f}".format(np.mean(teamConceded))},
                 {'label': f"Total average", 'value': "{:.2f}".format(np.mean(teamTotal))})

def main():

    st.set_page_config(page_title="NHL", page_icon="🏒")

    st.title("NHL Dashboard")
    st.text("Select a Season and a team and use this dashboard to check all the team information for this team at the selected season")

    today = datetime.today()
    currentYear = today.year if today.month < 8 else today.year + 1
    seasons = np.arange(currentYear, 1960, -1)
    selectedSeason = st.selectbox(label="Select a Season", options=seasons, index=None)

    if selectedSeason:
        seasonSchedule = getFullSeason(selectedSeason)
        teams = getSeasonTeams(selectedSeason)
        standings = getStandings(selectedSeason)

        selectedTeam = st.selectbox(label="Select a Team", options=list(teams.keys()), index=None)

        if selectedTeam:
            st.image(f"https://cdn.ssref.net/req/202311071/tlogo/hr/{teams[selectedTeam][7:10]}-{selectedSeason}.png", width=50)
            teamSeason = seasonSchedule[(seasonSchedule['home_team_name'] == selectedTeam) | (seasonSchedule['visitor_team_name'] == selectedTeam)]
            completedMatches = teamSeason[(teamSeason['home_goals'] != '')]

            homeScore = completedMatches['home_goals'].values.astype(dtype='int')
            awayScore = completedMatches['visitor_goals'].values.astype(dtype='int')

            completedMatches["Result"] = np.where(( ((completedMatches['home_team_name'].values == selectedTeam) &
                                                  (np.array(homeScore) > np.array(awayScore))) ) |
                                                  ((completedMatches['home_team_name'].values != selectedTeam) &
                                                   (np.array(homeScore) < np.array(awayScore))), 'W', 'L')

            completedMatches['Total Goals'] = homeScore + awayScore

            type = st.selectbox(label=f"Select if Overall, Home or Away", options=['Overall', 'Home', 'Away'])

            if type == 'Home':
                completedMatches = completedMatches[(completedMatches['home_team_name'] == selectedTeam)]
            elif type == 'Away':
                completedMatches = completedMatches[(completedMatches['home_team_name'] != selectedTeam)]
            else:
                pass

            makeConferenceTable(standings, selectedTeam)
            makeLastMatchesTable(completedMatches)
            makePercentagesTablesAndMetrics(completedMatches, selectedTeam)
main()
