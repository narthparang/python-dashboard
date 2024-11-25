from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def getConferenceStandings(season):
  def tableToJSON(rows):

    jsonList = []
  
    for row in rows:
      rowData = row.find_all("td")
      team = row.find("th").text.split("\xa0")[0].strip()
      dataJson = {data['data-stat']: data.text for data in rowData}
      dataJson['team'] = team
      jsonList.append(dataJson)
  
    return jsonList
  
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}.html")
  bs = BeautifulSoup(html, 'html.parser')

  tableEast = bs.find("table", {"id": "confs_standings_E"})
  tableWest = bs.find("table", {"id": "confs_standings_W"})

  try:
        eastStandings = tableToJSON(tableEast.find_all("tr")[1:])
        westStandings = tableToJSON(tableWest.find_all("tr")[1:])
        standings = {'East': eastStandings, 'West': westStandings}
  except ZeroDivisionError as e:
        print(f"Error in getConferenceStandings: {e}")
        standings = {'East': [], 'West': []}  # Return empty standings on error
  except Exception as e:
        print(f"Unexpected Error in getConferenceStandings: {e}")
        standings = {'East': [], 'West': []}  # Return empty standings on unexpected error

  return standings

from urllib.request import urlopen
from bs4 import BeautifulSoup

def getTeams(season):
    try:
        # Open URL and create BeautifulSoup object
        html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}.html")
        bs = BeautifulSoup(html, 'html.parser')

        # Find both conference tables
        tableEast = bs.find("table", {"id": "confs_standings_E"})
        tableWest = bs.find("table", {"id": "confs_standings_W"})
        tables = [tableEast, tableWest]
        teams = {}

        for table in tables:
            if table is None:  # Skip if table not found
                continue
                
            rows = table.find_all("tr")[1:5]  # Skip header row
            for row in rows:
                # Find team name link
                team_link = row.find("a")
                if team_link:
                    team_name = team_link.text.strip()
                    team_url = team_link['href']
                    teams[team_name] = team_url

    except Exception as e:
        print(f"Unexpected Error in getTeams: {e}")
        teams = {}  # Return empty teams on unexpected error

    return teams

def getTeamStats(season):
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}.html")
  bs = BeautifulSoup(html, 'html.parser')

  tableTeam = bs.find("table", {"id": "per_game-team"})
  tableOpp = bs.find("table", {"id": "per_game-opponent"})

  statsDict = {
      'For': list(map(lambda x: {data['data-stat']: data.text for data in x.find_all("td")}, tableTeam.find_all("tr")[1:])),
      'Against': list(map(lambda x: {data['data-stat']: data.text for data in x.find_all("td")}, tableOpp.find_all("tr")[1:]))
  }
  return statsDict

def getTeamAdvancedStats(season):
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "advanced-team"})

  statsList = list(map(lambda x: {data['data-stat']: data.text for data in x.find_all("td")}, table.find_all("tr")[2:]))

  return statsList

def getTeamsShootingStats(season):
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "shooting-team"})

  statsList = list(map(lambda x: {data['data-stat']: data.text for data in x.find_all("td")}, table.find_all("tr")[2:]))

  return statsList

def getLeagueLeaders(season):
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}_leaders.html")
  bs = BeautifulSoup(html, 'html.parser')

  div = bs.find("div", {"id": "div_leaders"})
  boxes = div.findChildren("div")

  ranksDict = {}

  for i in range(len(boxes)):
    try:
      category = boxes[i].findChildren("table")[0].findChildren("caption")[0].text
      boxRows = boxes[i].find_all("tr")
      categoryList = []

      for row in boxRows:
        data = row.find_all("td")
        player = data[1].findChildren("a")[0].text
        team = data[1].findChildren("span")[0].text
        value = data[2].text.strip()

        playerRank = f"{player} ({team}): {value}"
        categoryList.append(playerRank)

      ranksDict[category] = categoryList
    except:
      continue

  return ranksDict

def getPlayersStats(season):
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "per_game_stats"})

  return list(map(lambda x: {data['data-stat']: data.text for data in x.find_all("td")}, table.find_all("tr")[1:]))

def getNBASchedule(season, month):
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "schedule"})
  rows = table.find_all("tr")
  matchesList = []

  for row in rows[1:]:
    rowData = row.find_all("td")
    matchDict = {}

    date = row.find("th").text
    matchDict['Date'] = datetime.strptime(date, "%a, %b %d, %Y").strftime("%Y-%m-%d")

    for data in rowData:
      if data['data-stat'] == 'box_score_text':
        url = data.findChildren("a")[0]['href'] if len(data.findChildren("a")) > 0 else ''
        matchDict[data['data-stat']] = url
      else:
        matchDict[data['data-stat']] = data.text

      matchesList.append(matchDict)

  return matchesList

def getMatchBoxScore(matchURL):
  def isTeam(tag):
    try:
      return tag['href'].startswith("/teams")
    except:
      return False

  def getPlayersBoxScore(rows):

    statsList = []

    for row in rows:
      player = row.find("th").text
      stats = row.find_all("td")
      statsDict = {**{'player': player}, **{stat['data-stat']: stat.text for stat in stats} }
      statsList.append(statsDict)

    return statsList

  html = urlopen(matchURL)
  bs = BeautifulSoup(html, 'html.parser')

  div = bs.find("div", {"class": "scorebox"})
  teamsTags = list(filter(isTeam, div.find_all("a")))
  teamCodes = list(map(lambda x: x['href'].split("/")[2], teamsTags))
  teamNames = list(map(lambda x: x.text, teamsTags))

  homeTable = bs.find("div", {"id": f"div_box-{teamCodes[0]}-game-basic"})
  awayTable = bs.find("div", {"id": f"div_box-{teamCodes[1]}-game-basic"})

  playersDict = {
      teamNames[0]: getPlayersBoxScore(homeTable.find_all("tr")[2:]),
      teamNames[1]: getPlayersBoxScore(awayTable.find_all("tr")[2:])
  }
  return playersDict

def getQuarterBoxScore(matchURL, quarter):

  def isTeam(tag):
    try:
      return tag['href'].startswith("/teams")
    except:
      return False

  def getPlayersBoxScore(rows):

    statsList = []

    for row in rows:
      player = row.find("th").text
      stats = row.find_all("td")
      statsDict = {**{'player': player}, **{stat['data-stat']: stat.text for stat in stats} }
      statsList.append(statsDict)

    return statsList

  html = urlopen(matchURL)
  bs = BeautifulSoup(html, 'html.parser')

  div = bs.find("div", {"class": "scorebox"})
  teamsTags = list(filter(isTeam, div.find_all("a")))
  teamCodes = list(map(lambda x: x['href'].split("/")[2], teamsTags))
  teamNames = list(map(lambda x: x.text, teamsTags))

  homeTable = bs.find("div", {"id": f"div_box-{teamCodes[0]}-q{quarter}-basic"})
  awayTable = bs.find("div", {"id": f"div_box-{teamCodes[1]}-q{quarter}-basic"})

  playersDict = {
      teamNames[0]: getPlayersBoxScore(homeTable.find_all("tr")[2:]),
      teamNames[1]: getPlayersBoxScore(awayTable.find_all("tr")[2:])
  }
  return playersDict

def getHalfBoxScore(matchURL, half):
  def isTeam(tag):
    try:
      return tag['href'].startswith("/teams")
    except:
      return False

  def getPlayersBoxScore(rows):

    statsList = []

    for row in rows:
      player = row.find("th").text
      stats = row.find_all("td")
      statsDict = {**{'player': player}, **{stat['data-stat']: stat.text for stat in stats} }
      statsList.append(statsDict)

    return statsList

  html = urlopen(matchURL)
  bs = BeautifulSoup(html, 'html.parser')

  div = bs.find("div", {"class": "scorebox"})
  teamsTags = list(filter(isTeam, div.find_all("a")))
  teamCodes = list(map(lambda x: x['href'].split("/")[2], teamsTags))
  teamNames = list(map(lambda x: x.text, teamsTags))

  homeTable = bs.find("div", {"id": f"div_box-{teamCodes[0]}-h{half}-basic"})
  awayTable = bs.find("div", {"id": f"div_box-{teamCodes[1]}-h{half}-basic"})

  playersDict = {
      teamNames[0]: getPlayersBoxScore(homeTable.find_all("tr")[2:]),
      teamNames[1]: getPlayersBoxScore(awayTable.find_all("tr")[2:])
  }
  return playersDict

def getCoaches(season):
  html = urlopen(f"https://www.basketball-reference.com/leagues/NBA_{season}_coaches.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "NBA_coaches"})

  rows = table.find_all("tr")[3:]
  statsList = []

  for row in rows:
    coach = row.find("th").text
    stats = row.find_all("td")
    statsDict = {**{'coach': coach}, **{stat['data-stat']: stat.text for stat in stats} }
    statsList.append(statsDict)

  return statsList
