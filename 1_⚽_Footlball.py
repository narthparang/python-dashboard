from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import streamlit as st
import json
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from Football import *
from Styles import *

@st.cache_data
def createSeasonOptions(seasons, slashedSeasons):
    options = []
    seasonsCopy, slashedSeasonsCopy = seasons, slashedSeasons

    while len(seasonsCopy) > 0 and len(slashedSeasonsCopy) > 0:
        if len(seasonsCopy) > 0:
            element = seasonsCopy.pop(0)
            options.append(element)
        if len(slashedSeasonsCopy) > 0:
            element = slashedSeasonsCopy.pop(0)
            options.append(element)

    return options

@st.cache_data
def getMatchesStatsForURLs(URLs):
    return list(map(getMatchStats, URLs))

@st.cache_data
def getSelectedTeams(leagueId, leagueSlug, season):
    return getTeamsIds(leagueId, leagueSlug, season)

@st.cache_data
def getSelectedTeamPassingStats(leagueId, teamId, season, teamSlug, leagueSlug, team):
    stats = getTeamPassingStats(leagueId, teamId, season, teamSlug, leagueSlug, team)
    return stats

@st.cache_data
def getSelectedLeagueTable(leagueId, leagueSlug, season):
    table = getLeagueTable(leagueId, leagueSlug, season)
    return table

def makeMatchesTable(matches, type, team):

    df = pd.DataFrame(matches)
    if type == 'Home':
        df = df[(df['Home'] == team)]
    elif type == 'Away':
        df = df[(df['Away'] == team)]
    else:
        pass

    df = df[['Date', 'Result', 'Home', 'Away', 'Home Goals', 'Away Goals', 'Total Goals', 'Home Corners', 'Away Corners', 'Total Corners']]
    styled_df = df.style.applymap(highlight_positive)

    st.header(f"{team} Last Matches")
    st.dataframe(data=styled_df, hide_index=True)


def makeTeamsMetrics(matches, team):

    df = pd.DataFrame(matches)

    st.header(f"{team} Metrics")

    writeColumns('metric', {'label': f"{team} Scoring average", 'value': "{:.2f}".format(np.mean(df['Team Goals'].values))},
                 {'label': f"{team} Conceading average", 'value': "{:.2f}".format(np.mean(df['Opponent Goals'].values))},
                 {'label': f"{team} Total average", 'value': "{:.2f}".format(np.mean(df['Total Goals'].values))})

    writeColumns('metric', {'label': f"{team} Corners for average", 'value': "{:.2f}".format(np.mean(df['Team Corners'].values))},
                 {'label': f"{team} Corners against average", 'value': "{:.2f}".format(np.mean(df['Opponent Corners'].values))},
                 {'label': f"{team} Total Corners average", 'value': "{:.2f}".format(np.mean(df['Total Corners'].values))})


def makeTeamsPercentages(df, team):

    keys = ['Team Goals', 'Opponent Goals', 'Total Goals', 'Team Corners', 'Opponent Corners', 'Total Corners']
    valuesAndFrequencies = {}
    limits = {
        'Team Goals': [0.5, 1.5, 2.5],
        'Opponent Goals': [0.5, 1.5, 2.5],
        'Total Goals': [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
        'Team Corners': [2.5, 3.5, 4.5, 5.5],
        'Opponent Corners': [2.5, 3.5, 4.5, 5.5],
        'Total Corners': [6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5]
    }

    rows = {}

    for key in keys:
        values = df[key].values
        rows[key] = [
            [f'Over {item}', "{:.2%}".format(len(list(filter(lambda x: x > item, values))) / len(values))]
            for item in limits[key]
        ]

    st.header(f"{team} Percentages")

    writeColumns('dataframe', [f"**{team} Goals Scored**", rows['Team Goals']],
                 [f"**{team} Goals Conceded**", rows['Opponent Goals']],
                 [f"**{team} Total Goals**", rows['Total Goals']])

    writeColumns('dataframe', [f"**{team} Corners For**", rows['Team Corners']],
                 [f"**{team} Corners Against**", rows['Opponent Corners']],
                 [f"**{team} Total Corners**", rows['Total Corners']])

def selectPlot(df, chartType, team):

        array = df[chartType].values
        values, counts = np.unique(array, return_counts=True)

        category = 'Goals' if chartType in ['Team Goals', 'Opponent Goals', 'Total Goals'] else 'Corners'
        createBarChart({category: values, 'Count': counts}, x_axis=category, y_axis='Count',
                       title=f"{team} {chartType} Frequency",
                       text='Count')

def makeLeagueTable(leagueTables, type, team, leagueName):

    def highlight_rows(row):
        return ['background-color: khaki' if row['Team'].strip() == team else '' for _ in row]

    if type == "Overall":
        tableRows = leagueTables["Overall"]
        data = pd.DataFrame(tableRows, index=np.arange(1, len(tableRows) + 1, 1))

        data = data[['team', 'games', 'points', 'wins', 'ties', 'losses', 'goals_for',
                     'goals_against', 'goal_diff']]
        data.rename(
            {'team': 'Team', 'points': 'Points', 'games': 'Games', 'wins': 'Wins', 'ties': 'Ties',
             'losses': 'Losses', 'goals_for': 'Goals For', 'goals_against': 'Goals Against',
             'goal_diff': 'Goals Difference'},
            inplace=True, axis=1)

    elif type == "Home":
        table = leagueTables["Home/Away"][1:]
        tableRows = [{key: value for key, value in row.items() if key == 'team' or key.startswith('home')}
                     for row in table]
        data = pd.DataFrame(tableRows, index=np.arange(1, len(tableRows) + 1, 1))
        data = data[['team', 'home_games', 'home_points', 'home_wins', 'home_ties', 'home_losses', 'home_goals_for', 'home_goals_against', 'home_goal_diff']]
        data.rename({'team': 'Team', 'home_points': 'Points', 'home_games': 'Games', 'home_wins': 'Wins', 'home_ties': 'Ties',
                     'home_losses': 'Losses', 'home_goals_for': 'Goals For', 'home_goals_against': 'Goals Against', 'home_goal_diff': 'Goals Difference'},
        inplace=True, axis=1)

    else:
        table = leagueTables["Home/Away"][1:]
        tableRows = [{key: value for key, value in row.items() if key == 'team' or key.startswith('away')}
                     for row in table]
        data = pd.DataFrame(tableRows, index=np.arange(1, len(tableRows) + 1, 1))
        data = data[['team', 'away_games', 'away_points', 'away_wins', 'away_ties', 'away_losses', 'away_goals_for', 'away_goals_against', 'away_goal_diff']]
        data.rename({'team': 'Team', 'away_points': 'Points', 'away_games': 'Games', 'away_wins': 'Wins', 'away_ties': 'Ties',
                     'away_losses': 'Losses', 'away_goals_for': 'Goals For', 'away_goals_against': 'Goals Against', 'away_goal_diff': 'Goals Difference'},
        inplace=True, axis=1)

    styled_data = data.style.apply(lambda row: highlight_rows(row), axis=1)

    st.header(f"{leagueName} Table ({type})")
    st.dataframe(styled_data)
    def process_team_stats(stats):
        try:
            df = pd.DataFrame(stats)
        # Ensure all required columns exist
            required_columns = [
            'Date', 'Result', 'Home', 'Away', 'Home Goals', 'Away Goals',
            'Total Goals', 'Home Corners', 'Away Corners', 'Total Corners'
            ]
        
        # Add missing columns with default values
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0 if 'Goals' in col or 'Corners' in col else ''
                
        # Convert numeric columns to proper type
            numeric_columns = ['Home Goals', 'Away Goals', 'Total Goals', 
                         'Home Corners', 'Away Corners', 'Total Corners']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            return df
        except Exception as e:
            print(f"Error processing team stats: {e}")
        return pd.DataFrame(columns=required_columns)

def main():
    st.set_page_config(page_title="Football", page_icon="⚽")

    st.title("Football Dashboard")
    st.write("Select a league and a team and use this dashboard to check all the team information for this league at the current season")
    Leagues = getLeagueIds()
    leagueNames = list(Leagues.keys())

    today = datetime.today()
    currentYear = today.year if today.month < 8 else today.year + 1
    seasons = np.arange(currentYear, 1960, -1).tolist()
    slashedSeasons = [f"{seasons[i]}-{seasons[i-1]}" for i in range(1, len(seasons), 1)]
    seasonOptions = createSeasonOptions(seasons, slashedSeasons)
        #[i for j in map(None, seasons, slashedSeasons) for i in j if i is not None]

    league = st.selectbox(label="Select a League", options=leagueNames, index=None)

    if league:

        leagueId, leagueSlug = Leagues[league]['id'], Leagues[league]['slug']

        season = st.selectbox(label=f"Select a Season", options=seasonOptions, index=None)

        if season:

            try:
                leagueTeams = getTeamsIds(leagueId, leagueSlug, season)
                leagueTables = getSelectedLeagueTable(leagueId, leagueSlug, season)
            except:
                st.text(f"{season} Season Unavailable for {league} ... Try a different season")
                return 0

            team = st.selectbox(label=f"Select a team from {league}", options=list(leagueTeams.keys()), index=None)

            if team:

                teamId, teamSlug = leagueTeams[team]['id'], leagueTeams[team]['slug']
                st.image(f"https://cdn.ssref.net/req/202311071/tlogo/fb/{teamId}.png", width=50)
                teamStats = getSelectedTeamPassingStats(leagueId, teamId, season, teamSlug, leagueSlug, team)

                type = st.selectbox(label=f"Select if Overall, Home or Away", options=['Overall', 'Home', 'Away'], index=None)

                if type:
                    matches = [
                        {
                             'Date': teamStats['For'][i]['Date'],
                             'Result': teamStats['For'][i]['result'],
                             'Home': teamStats['For'][i]['Home'],
                             'Away': teamStats['For'][i]['Away'],
                             'Team Goals': int(teamStats['For'][i]['goals_for'][0]),
                             'Opponent Goals': int(teamStats['For'][i]['goals_against'][0]),
                             'Home Goals': int(teamStats['For'][i]['goals_for'][0]) if teamStats['For'][i]['Home'] == team else int(teamStats['For'][i]['goals_against'][0]),
                             'Away Goals': int(teamStats['For'][i]['goals_for'][0]) if teamStats['For'][i]['Home'] != team else int(teamStats['For'][i]['goals_against'][0]),
                             'Total Goals': int(teamStats['For'][i]['goals_for'][0]) + int(teamStats['For'][i]['goals_against'][0]),
                             'Team Corners': int(teamStats['For'][i]['corner_kicks']),
                             'Opponent Corners': int(teamStats['Against'][i]['corner_kicks']),
                             'Home Corners': int(teamStats['For'][i]['corner_kicks'])if teamStats['For'][i]['Home'] == team else int(teamStats['Against'][i]['corner_kicks']),
                             'Away Corners': int(teamStats['For'][i]['corner_kicks']) if teamStats['For'][i]['Home'] != team else int(teamStats['Against'][i]['corner_kicks']),
                             'Total Corners': int(teamStats['For'][i]['corner_kicks']) + int(teamStats['Against'][i]['corner_kicks'])
                        }
                        for i in range(len(teamStats['Against'])) if teamStats['Against'][i]['Date'] != ''
                    ]

                    if type == "Home":
                        matches = list(filter(lambda x: x['Home'] == team, matches))
                    elif type == "Away":
                        matches = list(filter(lambda x: x['Home'] != team, matches))

                    makeLeagueTable(leagueTables, type, team, league)

                    st.markdown("---")

                    makeMatchesTable(matches, type, team)

                    st.markdown("---")

                    makeTeamsMetrics(matches, team)

                    st.markdown("---")

                    makeTeamsPercentages(pd.DataFrame(matches), team)

                    st.markdown("---")

                    st.header(f"{team} Goals and Corners Frequencies")
                    chartOptions=['Team Goals', 'Opponent Goals', 'Total Goals', 'Team Corners', 'Opponent Corners', 'Total Corners']
                    chartType = st.selectbox(label=f"Select the type of stat", options=chartOptions)

                    selectPlot(pd.DataFrame(matches), chartType, team)
    

main()
