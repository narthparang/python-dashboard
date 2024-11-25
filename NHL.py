from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

def getNHLSchedule(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_games.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "games"})
  rows = table.find_all("tr")
  matchesList = []

  for row in rows[1:]:
    date = row.find("th").text
    rowData = row.find_all("td")
    matchDict = {}

    for data in rowData:
      if data['data-stat'] == 'box_score_text':
        url = data.findChildren("a")[0]['href'] if len(data.findChildren("a")) > 0 else ''
        matchDict[data['data-stat']] = url
      else:
        matchDict[data['data-stat']] = data.text

      matchDict["Date"] = date
      matchesList.append(matchDict)

  return matchesList

def getNHLConferenceStandings(season):
  def tableToJSON(rows):

    jsonList = []

    for row in rows:
      try:
        rowData = row.find_all("td")
        team = row.find("th").findChildren("a")[0].text.split("\xa0")[0].strip()
        dataJson = {data['data-stat']: data.text for data in rowData}
        dataJson['team'] = team
        jsonList.append(dataJson)

      except AttributeError:
        continue

    return jsonList

  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}.html")
  bs = BeautifulSoup(html, 'html.parser')

  tableEast = bs.find("table", {"id": "standings_EAS"})
  tableWest = bs.find("table", {"id": "standings_WES"})

  standings = {
      'East': tableToJSON(tableEast.find_all("tr")[2:]),
      'West': tableToJSON(tableWest.find_all("tr")[2:]),
  }

  return standings

def getNHLTeamsURLs(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_games.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "games"})
  rows = table.find_all("tr")
  teams = [list(filter(lambda x: x['data-stat'] == 'home_team_name', row.find_all("td") )) for row in rows[1:]]
  teamsDict = {team[0].text: team[0].findChildren("a")[0]['href'] for team in teams}

  return teamsDict

def getNHLTeamRoster(season, teamCode):
  html = urlopen(f"https://www.hockey-reference.com/teams/{teamCode}/{season}.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "roster"})

  return list(map(lambda x: {**{'number': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[1:]))

def getNHLTeamH2HResults(season, teamCode):
  html = urlopen(f"https://www.hockey-reference.com/teams/{teamCode}/{season}_headtohead.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "head2head"})
  rows = table.find_all("tr")[1:]
  opponentsDict = {}

  for row in rows:
    rowData = row.find_all("td")
    teamName = rowData[0].text
    opponentsDict[teamName] = {data['data-stat']: data.text for data in rowData[1:]}

  return opponentsDict

def getNHLTeamGamelog(season, teamCode):
  html = urlopen(f"https://www.hockey-reference.com/teams/{teamCode}/{season}_gamelog.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "tm_gamelog_rs"})

  return list(map(lambda x: {data['data-stat']: data.text for data in x.find_all("td")} , table.find_all("tr")[2:]))

def getNHLInjuries():
  html = urlopen(f"https://www.hockey-reference.com/friv/injuries.cgi")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "injuries"})

  return list(map(lambda x: {**{'player': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[1:]))

def getNHLSkatersStatistics(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_skaters.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "stats"})

  return list(map(lambda x: {**{'player': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[2:]))

def getNHLGoalieStatistics(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_goalies.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "stats"})

  return list(map(lambda x: {**{'player': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[1:]))

def getNHLSkatersBasicStatistics(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_skaters.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "stats"})

  return list(map(lambda x: {**{'player': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[1:]))

def getNHLSkatersAdvancedStatistics(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_skaters-advanced.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "stats_adv_rs"})

  return list(map(lambda x: {**{'player': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[1:]))

def getNHLCaptains(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_captains.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "captains"})

  return list(map(lambda x: {**{'team': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[1:]))

def getNHLSkaterShootouts(season):
  html = urlopen(f"https://www.hockey-reference.com/leagues/NHL_{season}_penalty-shots.html")
  bs = BeautifulSoup(html, 'html.parser')

  table = bs.find("table", {"id": "penalty_shots"})
  return table
  return list(map(lambda x: {**{'team': x.find("th").text}, **{data['data-stat']: data.text for data in x.find_all("td")} }, table.find_all("tr")[1:]))
