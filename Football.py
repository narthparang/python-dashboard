from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

def getMatches(leagueId, leagueName, Season):
    html = urlopen(f"https://fbref.com/en/comps/{str(leagueId)}/schedule/{Season}-{leagueName}-Scores-and-Fixtures")
    bs = BeautifulSoup(html, 'html.parser')
    table = bs.find_all("table")[0]
    rows = table.find_all("tr")
    tableHeaders = list(map(lambda x: x.text, rows[0].find_all("th")[1:]))
    tableData = []

    for row in rows[1:]:
        rowData = list(map(lambda x: x.text, row.find_all("td")))
        tableData.append(rowData)

    return pd.DataFrame(tableData, columns=tableHeaders)


def getLeagueTable(leagueId, leagueName, Season, tableTypes='all'):
    def createTable(rows):
        table = []

        for row in rows:
            rank = row.find("th").text
            stats = row.find_all("td")
            table.append({**{'rank': rank}, **{stat['data-stat']: stat.text for stat in stats}})

        return table

    html = urlopen(f"https://fbref.com/en/comps/{leagueId}/{Season}/{Season}-{leagueName}-Stats")
    bs = BeautifulSoup(html, 'html.parser')

    if tableTypes == 'all':
        tables = list(filter(lambda x: 'overall' in x["id"] or 'home_away' in x["id"], bs.find_all("table")))
        mappedTables = list(map(lambda x: createTable(x.find_all("tr")[1:]), tables))
        return {'Overall': mappedTables[0], 'Home/Away': mappedTables[1]}

    elif tableTypes == 'overall':
        tables = list(filter(lambda x: 'overall' in x["id"], bs.find_all("table")))
        mappedTables = list(map(lambda x: createTable(x.find_all("tr")[1:]), tables))
        return {'Overall': mappedTables[0]}

    elif tableTypes == 'home_away':
        tables = list(filter(lambda x: 'home_away' in x["id"], bs.find_all("table")))
        mappedTables = list(map(lambda x: createTable(x.find_all("tr")[1:]), tables))
        return {'Home/Away': mappedTables[0]}


def getMatchLineups(matchURL):
    html = urlopen(matchURL)
    bs = BeautifulSoup(html, 'html.parser')

    HomeAway = ['Home', 'Away']
    team = 0
    matchLineups = []

    lineups = bs.find_all("div", {'class': 'lineup'})

    for lineup in lineups:
        teamAndFormation = lineup.find("tr").text
        formationIndex = teamAndFormation.index("(")
        teamName = teamAndFormation[:formationIndex].strip()
        formation = teamAndFormation[(formationIndex + 1):-1].strip()

        players = lineup.find_all("td")

        teamLineup = {
            teamName: {
                'Formation': formation,
                'Home/Away': HomeAway[team],
                'Starters': [f"{players[i].text} - {players[i + 1].text}" for i in range(0, 22, 2)],
                'Substitutes': [f"{players[i].text} - {players[i + 1].text}" for i in range(22, len(players), 2)]
            }
        }

        team += 1
        matchLineups.append(teamLineup)

    return matchLineups


def getMatchEvents(matchURL):
    def createEventDict(event):

        eventData = list(
            map(lambda x: x.text.replace('\n', '').replace('\t', '').replace('\xa0', ''), event.find_all("div")))
        minuteIndex = eventData[0].index('’')
        minute = eventData[0][:minuteIndex]
        eventArray = eventData[1].split('—')

        if 'Assist' in eventArray[0]:
            player = eventArray[0].replace('Assist:', ' ( ') + " )"
        else:
            player = eventArray[0]

        action = eventArray[1].strip()

        eventDict = {
            'Minute': minute,
            'Player': player,
            'Action': action
        }

        return eventDict

    html = urlopen(matchURL)
    bs = BeautifulSoup(html, 'html.parser')

    eventsWrap = bs.find("div", {"id": "events_wrap"})
    eventsHome = list(map(createEventDict, eventsWrap.find_all('div', {'class': 'event a'})))
    eventsAway = list(map(createEventDict, eventsWrap.find_all('div', {'class': 'event b'})))

    lineups = bs.find_all("div", {'class': 'lineup'})

    formationIndex = lineups[0].find("tr").text.index("(")
    homeName = lineups[0].find("tr").text[:formationIndex].strip()

    formationIndex = lineups[1].find("tr").text.index("(")
    awayName = lineups[1].find("tr").text[:formationIndex].strip()

    eventsDict = {
        homeName: eventsHome,
        awayName: eventsAway,
    }
    return eventsDict


def getMatchStats(matchURL):
    html = urlopen(matchURL)
    bs = BeautifulSoup(html, 'html.parser')

    stats = bs.find('div', {'id': 'team_stats'}).find_all('tr')
    home = stats[0].find_all('th')[0].text.replace('\n', '').replace('\t', '').replace('\xa0', '')
    away = stats[0].find_all('th')[1].text.replace('\n', '').replace('\t', '').replace('\xa0', '')

    homeStats = {}
    awayStats = {}

    for i in range(1, len(stats), 2):
        statName = stats[i].text.replace('\n', '').replace('\t', '').replace('\xa0', '')
        homeStats[statName] = stats[i + 1].find_all('td')[0].text.replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                              '').replace(
            '—', ' — ')
        awayStats[statName] = stats[i + 1].find_all('td')[1].text.replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                              '').replace(
            '—', ' — ')

    extraStats = bs.find('div', {'id': 'team_stats_extra'})
    extraStatsArray = extraStats.find_all('div')

    for extraStats in extraStatsArray:

        extraStatsValues = extraStats.find_all('div')[3:]

        for j in range(0, len(extraStatsValues), 3):
            extraStatName = extraStatsValues[j + 1].text
            homeStats[extraStatName] = extraStatsValues[j].text.replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                            '').replace(
                '-', ' — ')
            awayStats[extraStatName] = extraStatsValues[j + 2].text.replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                                '').replace(
                '-', ' — ')

    matchStatsDict = {
        home.strip(): homeStats,
        away.strip(): awayStats
    }

    return matchStatsDict


def getPlayersMatchStats(matchURL):
    html = urlopen(matchURL)
    bs = BeautifulSoup(html, 'html.parser')
    table = bs.find("table", {'id': "stats_bba7d733_summary"})

    rows = table.find_all("tr")[2:]
    playersStats = []

    for row in rows:
        player = row.find("th").text.replace('\xa0', '')
        stats = row.find_all("td")

        statsDict = {**{'player': player}, **{stat['data-stat']: stat.text for stat in stats}}
        playersStats.append(statsDict)

    return playersStats


def getShotsTable(matchURL):
    html = urlopen(matchURL)
    bs = BeautifulSoup(html, 'html.parser')
    table = bs.find("table", {'id': "shots_all"})

    ShotsStats = []
    rows = table.find_all("tr")[2:]

    for row in rows:
        stats = row.find_all("td")
        statsDict = {stat['data-stat']: stat.text for stat in stats}
        ShotsStats.append(statsDict)

    return ShotsStats


def getTeamsSeasonStats(leagueId, leagueName):
    def createTeamsSeasonDict(table, against=False):
        rows = list(map(lambda x: x.find_all("td"), table.find_all("tr")[2:]))
        teams = list(map(lambda x: x.find("th").text[3:] if against else x.find("th").text,
                         table.find_all("tr")[2:]))

        return [
            {**{'team': teams[row]}, **{rows[row][i]['data-stat']: rows[row][i].text for i in range(len(rows[row]))}}
            for row in range(len(rows))]

    html = urlopen(f"https://fbref.com/en/comps/{leagueId}/stats/{leagueName}-Stats")
    bs = BeautifulSoup(html, 'html.parser')

    tableFor = bs.find("table", {'id': 'stats_squads_standard_for'})
    tableAgainst = bs.find("table", {'id': 'stats_squads_standard_against'})

    statsDict = {
        'For': createTeamsSeasonDict(tableFor),
        'Against': createTeamsSeasonDict(tableAgainst, against=True)
    }

    return statsDict


def getTeamsIds(leagueId, leagueSlug, season):
    html = urlopen(f"https://fbref.com/en/comps/{leagueId}/{season}/stats/{season}/{leagueSlug}-Stats")
    bs = BeautifulSoup(html, 'html.parser')

    teams = bs.find_all("tr")[2:]
    URLs = list(map(lambda x: x.find('th').findChildren('a'), teams))
    teamsDict = {}

    for url in URLs:
        try:

            teamName = url[0].text
            teamId = url[0]['href'].split('/')[-2]
            teamSlug = url[0]['href'].split('/')[-1][:-6]
            teamsDict[teamName] = {'id': teamId, 'slug': teamSlug}
            # print(teamsDict)
        except:
            break

    return teamsDict


def getMatchesURLs(leagueId, leagueName):
    html = urlopen(f"https://fbref.com/en/comps/{leagueId}/schedule/{leagueName}-Scores-and-Fixtures")
    bs = BeautifulSoup(html, 'html.parser')
    table = bs.find_all("table")[0]
    rows = table.find_all("tr")[1:]

    matchURLs = list(map(lambda x: x.find_all("td", {'data-stat': 'score'}), rows))
    matchURLs = list(filter(lambda x: len(x[0].text) > 0, matchURLs))
    matchURLs = list(map(lambda x: 'https://fbref.com' + x[0].findChildren("a")[0]['href'], matchURLs))

    return matchURLs

def getLeagueIds():
    html = urlopen(f"https://fbref.com/en/comps/")
    bs = BeautifulSoup(html, 'html.parser')
    rows = bs.find_all("tr")
    idsDict = {}

    for row in rows:
        try:
            child = row.findChildren("a")[0]
            idsDict[child.text] = {'slug': child['href'].split("/")[-1][:-8],
                                   'id': child['href'].split("/")[-3]}
        except:
            continue
    return idsDict


def getTeamPlayers(teamId, teamSlug):
    html = urlopen(f"https://fbref.com/en/squads/{teamId}/{teamSlug}-Stats")
    bs = BeautifulSoup(html, 'html.parser')

    table = bs.find("table", {"id": "stats_standard_10"})
    rows = table.find_all("tr")
    statsList = []

    for row in rows[2:]:
        player = row.find("th").text.replace('\xa0', '')
        stats = row.find_all("td")

        statsDict = {**{'player': player}, **{stat['data-stat']: stat.text for stat in stats}}
        statsList.append(statsDict)

    return statsList


def getTeamSeasonMatches(teamId, teamSlug, type='completed'):
    html = urlopen(f"https://fbref.com/en/squads/{teamId}/{teamSlug}-Stats")
    bs = BeautifulSoup(html, 'html.parser')
    table = bs.find("table", {"id": "matchlogs_for"})
    rows = table.find_all("tr")
    matchesList = []

    for row in rows[2:]:
        rowData = row.find_all("td")
        matchDict = {}

        for data in rowData:
            if data['data-stat'] == 'match_report':
                url = data.findChildren("a")[0]['href']
                matchDict[data['data-stat']] = url
            else:
                matchDict[data['data-stat']] = data.text

            matchesList.append(matchDict)

    if type == 'completed':
        return list(filter(lambda x: len(x['result']) > 0, matchesList))
    elif type == 'next':
        return list(filter(lambda x: len(x['result']) == 0, matchesList))
    else:
        return matchesList


def getMatchH2H(homeId, awayId, homeSlug, awaySlug):
    html = urlopen(f"https://fbref.com/en/stathead/matchup/teams/{homeId}/{awayId}/{homeSlug}-vs-{awaySlug}-History")
    bs = BeautifulSoup(html, 'html.parser')
    table = bs.find("table", {"id": "games_history_all"})
    rows = table.find_all("tr")
    matchesList = []

    for row in rows[3:]:
        league = row.find("th").text
        rowData = row.find_all("td")

        matchDict = {}

        for data in rowData:
            if data['data-stat'] == 'match_report':
                url = data.findChildren("a")[0]['href']
                matchDict[data['data-stat']] = url
            else:
                matchDict[data['data-stat']] = data.text

            matchesList.append(matchDict)

    return matchesList


def getDayMatches(day):
    html = urlopen(f"https://fbref.com/en/matches/{day}")
    bs = BeautifulSoup(html, 'html.parser')
    tables = bs.find_all("table")

    matchesList = []

    for table in tables:

        country = table.findChildren("caption")[0].findChildren("span")[0].text
        league = table.findChildren("caption")[0].findChildren("a")[0].text
        leagueId = table.findChildren("caption")[0].findChildren("a")[0]['href'].split("/")[3]
        rows = table.find_all("tr")[1:]

        for row in rows:
            rowData = row.find_all("td")
            matchDict = {'country': country, 'league': league, 'leagueId': leagueId}

            for data in rowData:
                if data['data-stat'] == 'match_report':
                    try:
                        url = data.findChildren("a")[0]['href']
                    except:
                        url = ''

                    matchDict[data['data-stat']] = url
                else:
                    matchDict[data['data-stat']] = data.text

                matchesList.append(matchDict)

    return matchesList

from urllib.request import urlopen, Request
from urllib.error import HTTPError
import time

def getTeamPassingStats(leagueId, teamId, season, teamSlug, leagueSlug, team):
    def toJSON(rows, team):
        jsonList = []
        if not rows:
            return jsonList

        for row in rows:
            try:
                date = row.find("th").text if row.find("th") else ""
                data_cells = row.find_all("td")
                
                # Create base dictionary with required columns
                dataJson = {
                    'Date': date,
                    'Result': '',
                    'Home': '',
                    'Away': '',
                    'Home Goals': 0,
                    'Away Goals': 0,
                    'Total Goals': 0,
                    'Home Corners': 0,
                    'Away Corners': 0,
                    'Total Corners': 0
                }

                # Update with available data
                for cell in data_cells:
                    stat_name = cell.get('data-stat', '')
                    stat_value = cell.text.strip()
                    
                    if stat_name:
                        dataJson[stat_name] = stat_value

                # Set home/away teams
                venue = dataJson.get('venue', '')
                opponent = dataJson.get('opponent', '')
                
                if venue == "Home":
                    dataJson['Home'] = team
                    dataJson['Away'] = opponent
                else:
                    dataJson['Home'] = opponent
                    dataJson['Away'] = team

                # Extract goals from score if available
                score = dataJson.get('score', '')
                if score and '–' in score:  # Note: this is an en dash, not a hyphen
                    try:
                        home_goals, away_goals = map(int, score.split('–'))
                        dataJson['Home Goals'] = home_goals
                        dataJson['Away Goals'] = away_goals
                        dataJson['Total Goals'] = home_goals + away_goals
                    except:
                        pass

                jsonList.append(dataJson)
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        return jsonList

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        url = f"https://fbref.com/en/squads/{teamId}/{season}/matchlogs/c{leagueId}/passing_types/{teamSlug}-Match-Logs-{leagueSlug}"
        req = Request(url=url, headers=headers)
        
        # Add delay to avoid rate limits
        time.sleep(2)
        
        html = urlopen(req)
        bs = BeautifulSoup(html, 'html.parser')

        tableFor = bs.find("table", {"id": "matchlogs_for"})
        tableAgainst = bs.find("table", {"id": "matchlogs_against"})

        # Create DataFrame with mandatory columns
        stats = {
            'For': toJSON(tableFor.find_all("tr")[2:] if tableFor else [], team),
            'Against': toJSON(tableAgainst.find_all("tr")[2:] if tableAgainst else [], team),
        }

        # Convert to DataFrame and ensure all required columns exist
        for key in stats:
            if stats[key]:
                df = pd.DataFrame(stats[key])
                # Ensure all required columns exist with default values
                required_columns = [
                    'Date', 'Result', 'Home', 'Away', 'Home Goals', 'Away Goals',
                    'Total Goals', 'Home Corners', 'Away Corners', 'Total Corners'
                ]
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = 0 if 'Goals' in col or 'Corners' in col else ''
                stats[key] = df.to_dict('records')

        return stats

    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return {'For': [], 'Against': []}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {'For': [], 'Against': []}

    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        # Return empty data structure instead of failing
        return {'For': [], 'Against': []}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {'For': [], 'Against': []}
    
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
        # Return empty DataFrame with required columns
        return pd.DataFrame(columns=required_columns)
