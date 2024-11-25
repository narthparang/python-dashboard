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

from NBA import *
from Styles import *

@st.cache_data
def getSeasonTeamStats(season):
    stats = getTeamStats(season)
    return stats

@st.cache_data
def getSeasonTeams(season):
    teams = getTeams(season)
    return teams

@st.cache_data
def getStandings(season):
    tables = getConferenceStandings(season)
    return tables

@st.cache_data
def getFullSeason(season):
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    fullSchedule = []

    for month in months:
        try:
            monthSchedule = getNBASchedule(season, month)
            fullSchedule += monthSchedule
        except:
            print(month)
            continue

    orderedSchedule = sorted(fullSchedule, key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))

    df = pd.DataFrame(orderedSchedule)
    df.drop_duplicates(inplace=True)

    return df

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

    data = data[['team', 'wins', 'losses', 'win_loss_pct', 'gb', 'pts_per_g', 'opp_pts_per_g']]
    data.rename({'team': 'Team', 'wins': 'Wins', 'losses': 'Losses', 'win_loss_pct': 'Win / Loss Percentage',
                 'gb': 'GB', 'pts_per_g': 'Points Per Game', 'opp_pts_per_g': 'Opponents Points Per Game'},
                 axis=1, inplace=True)
    styled_data = data.style.apply(lambda row: highlight_rows(row), axis=1)
    st.dataframe(styled_data)

    st.markdown("---")

def makeLastMatchesTable(completedMatches, selectedTeam):

    # Apply the conditional formatting to the 'Result' column
    df = completedMatches[
        ['Date', 'Result', 'home_team_name', 'visitor_team_name', 'home_pts', 'visitor_pts', 'Total Points']]

    df.rename({'home_team_name': 'Home', 'visitor_team_name': 'Away', 'home_pts': 'Home Points', 'visitor_pts': 'Visitor Points'},
              axis=1, inplace=True)
    styled_df = df.style.applymap(highlight_positive)

    st.header(f"Last Matches")
    st.dataframe(styled_df, hide_index=True)

    st.markdown("---")

def makePercentagesTablesAndMetrics(completedMatches, selectedTeam, teamStats):

    jsonData = json.loads(completedMatches.to_json(orient="records"))
    teamScored = list(
        map(lambda x: int(x['home_pts']) if x['home_team_name'] == selectedTeam else int(x['visitor_pts']), jsonData))
    teamConceded = list(
        map(lambda x: int(x['home_pts']) if x['visitor_team_name'] == selectedTeam else int(x['visitor_pts']),
            jsonData))
    teamTotal = list(map(lambda x: int(x['Total Points']), jsonData))

    scoringTypes = [teamScored, teamConceded, teamTotal]
    rowKeys = ['Scoring', 'Conceading', 'Total']
    scoringMarkers = {
        'Scoring': [99.5, 104.5, 109.5, 114.5, 119.5],
        'Conceading': [99.5, 104.5, 109.5, 114.5, 119.5],
        'Total': [199.5, 204.5, 209.5, 214.5, 219.5, 224.5, 229.5, 234.5, 239.5]
    }

    rows = {}

    for i in range(len(scoringTypes)):
        rows[rowKeys[i]] = [[f'Over {item}', "{:.2%}".format(
            len(list(filter(lambda x: x > item, scoringTypes[i]))) / len(scoringTypes[i]))]
                            for item in scoringMarkers[rowKeys[i]]]

    st.header(f"{selectedTeam} Percentages")

    writeColumns('dataframe', [f"**{selectedTeam} Points Scored**", rows['Scoring']],
                 [f"**{selectedTeam} Points Conceded**", rows['Conceading']],
                 [f"**{selectedTeam} Total Points**", rows['Total']])

    st.markdown("---")

    makeMetrics(selectedTeam, teamStats, teamScored, teamConceded, teamTotal)

def makeMetrics(selectedTeam, teamStats, teamScored, teamConceded, teamTotal):
    st.header(f"{selectedTeam} Metrics")

    # statsFor = list(filter(lambda x: x['team'] == selectedTeam, teamStats['For']))[0]
    # statsAgainst = list(filter(lambda x: x['team'] == selectedTeam, teamStats['Against']))[0]

    # st.write("### **Points Percentages**")

    # writeColumns('metric', {'label': f"{selectedTeam} Scoring average", 'value': "{:.2f}".format(np.mean(teamScored))},
    #              {'label': f"{selectedTeam} Conceading average", 'value': "{:.2f}".format(np.mean(teamConceded))},
    #              {'label': f"{selectedTeam} Total average", 'value': "{:.2f}".format(np.mean(teamTotal))})

    # st.text("")

    # st.write("### **Field Goals and Assists**")
    # writeColumns('metric', {'label': f"Field Goal For Percentage", 'value': "{:.2f}".format(float(statsFor['fg_pct']))},
    #              {'label': f"2 Point Field Goal For Percentage", 'value': "{:.2f}".format(float(statsFor['fg2_pct']))},
    #              {'label': f"3 Point Total For Percentage", 'value': "{:.2f}".format(float(statsFor['fg3_pct']))},
    #              {'label': f"Assists For", 'value': "{:.2f}".format(float(statsFor['ast']))})

    # writeColumns('metric', {'label': f"Field Goal Against Percentage",
    #                         'value': "{:.2f}".format(float(statsAgainst['opp_fg_pct']))},
    #              {'label': f"2 Point Field Goal Against Percentage",
    #               'value': "{:.2f}".format(float(statsAgainst['opp_fg2_pct']))},
    #              {'label': f"3 Point Total Against Percentage",
    #               'value': "{:.2f}".format(float(statsAgainst['opp_fg3_pct']))},
    #              {'label': f"Assists Against", 'value': "{:.2f}".format(float(statsAgainst['opp_ast']))})
    # st.text("")

    # st.write("### **Rebounds**")
    # writeColumns('metric', {'label': f"Rebounds For", 'value': "{:.2f}".format(float(statsFor['trb']))},
    #              {'label': f"Offensive Rebounds For", 'value': "{:.2f}".format(float(statsFor['orb']))},
    #              {'label': f"Defensive Rebounds For", 'value': "{:.2f}".format(float(statsFor['drb']))})

    # writeColumns('metric', {'label': f"Rebounds Against", 'value': "{:.2f}".format(float(statsAgainst['opp_trb']))},
    #              {'label': f"Offensive Rebounds Against", 'value': "{:.2f}".format(float(statsAgainst['opp_orb']))},
    #              {'label': f"Defensive Rebounds Against", 'value': "{:.2f}".format(float(statsAgainst['opp_drb']))})
    # st.text("")

    # st.write("### **Steals, Blocks and Turnovers**")
    # writeColumns('metric', {'label': f"Steals For", 'value': "{:.2f}".format(float(statsFor['stl']))},
    #              {'label': f"Blocks For", 'value': "{:.2f}".format(float(statsFor['blk']))},
    #              {'label': f"Turnovers Comitted", 'value': "{:.2f}".format(float(statsFor['tov']))})

    # writeColumns('metric', {'label': f"Steals Against", 'value': "{:.2f}".format(float(statsAgainst['opp_stl']))},
    #              {'label': f"Blocks Against", 'value': "{:.2f}".format(float(statsAgainst['opp_blk']))},
    #              {'label': f"Turnovers Forced", 'value': "{:.2f}".format(float(statsAgainst['opp_tov']))})

    # st.markdown("---")

def main():

    st.set_page_config(page_title="NBA", page_icon="🏀")

    st.title("NBA Dashboard")
    st.text("Select a Season and a team and use this dashboard to check all the team information for this team at the selected season")

    today = datetime.today()
    currentYear = today.year if today.month < 8 else today.year + 1
    seasons = np.arange(currentYear, 1960, -1)
    selectedSeason = st.selectbox(label="Select a Season", options=seasons, index=None)

    if selectedSeason:
        seasonSchedule = getFullSeason(selectedSeason)
        teams = getSeasonTeams(selectedSeason)
        teamStats = getSeasonTeamStats(selectedSeason)
        standings = getStandings(selectedSeason)
        
        selectedTeam = st.selectbox(label="Select a Team", options=list(teams.keys()), index=None)

        if selectedTeam:
            st.image(f"https://cdn.ssref.net/req/202311071/tlogo/bbr/{teams[selectedTeam][6:10]}-{selectedSeason}.png", width=50)
            teamSeason = seasonSchedule[(seasonSchedule['home_team_name'] == selectedTeam) | (seasonSchedule['visitor_team_name'] == selectedTeam)]
            completedMatches = teamSeason[(teamSeason['home_pts'] != '')]

            homeScore = completedMatches['home_pts'].values.astype(dtype='int')
            awayScore = completedMatches['visitor_pts'].values.astype(dtype='int')

            completedMatches["Result"] = np.where(( ((completedMatches['home_team_name'].values == selectedTeam) &
                                                  (np.array(homeScore) > np.array(awayScore))) ) |
                                                  ((completedMatches['home_team_name'].values != selectedTeam) &
                                                   (np.array(homeScore) < np.array(awayScore))), 'W', 'L')

            completedMatches['Total Points'] = homeScore + awayScore

            type = st.selectbox(label=f"Select if Overall, Home or Away", options=['Overall', 'Home', 'Away'])

            if type == 'Home':
                completedMatches = completedMatches[(completedMatches['home_team_name'] == selectedTeam)]
            elif type == 'Away':
                completedMatches = completedMatches[(completedMatches['home_team_name'] != selectedTeam)]
            else:
                pass

            makeConferenceTable(standings, selectedTeam)
            makeLastMatchesTable(completedMatches, selectedTeam)
            makePercentagesTablesAndMetrics(completedMatches, selectedTeam, teamStats)
          
main()
