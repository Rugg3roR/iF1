import requests
import datetime
import time
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

race_points = None

sprint_points = None


basic_url = 'https://f1api.dev/api/'

rounds = []

sprint_rounds = []

all_data = []

def get_race_points(year, roundn, points=None):

    url = f'{basic_url}{year}/{roundn}/race'

    response = requests.get(url)

    time.sleep(0.3)

    if response.status_code != 200:
        return None

    data = response.json()

    rows = []

    for result in data['races']['results']:

        rows.append({
            'year': data['season'],
            'round': data['races']['round'],
            'driverId': result['driver']['driverId'],
            'position': result['position'],
            'points': result['points'],
            'constructorId': result['team']['teamId'],
            'circuitId': data['races']['circuit']['circuitId'],
            'event_type': 'Race'
        })

    df = pd.DataFrame(rows)

    pos = pd.to_numeric(df['position'], errors='coerce')

    df['position_clean'] = np.where(pos.notna(), pos, 'DNF')

    dnf = (df['position_clean'] == 'DNF').sum()

    if points is None:

        pointsfinishers = [float(i) for i in range(len(df), dnf, -1)]

    else:

        finishers = len(df) - dnf

        pointsfinishers = (points + [0.0]*finishers)[:finishers]

    df['points_rr'] = pointsfinishers + [0.0]*dnf

    return df

def get_sprint_points(year, roundn, points=None):

    url = f'{basic_url}{year}/{roundn}/sprint/race'

    response = requests.get(url)

    time.sleep(0.3)

    if response.status_code != 200:

        return None

    data = response.json()

    rows = []

    for result in data['races']['sprintRaceResults']:

        rows.append({
            'year': data['season'],
            'round': data['races']['round'],
            'driverId': result['driver']['driverId'],
            'position': result['position'],
            'points': result['points'],
            'constructorId': result['team']['teamId'],
            'circuitId': data['races']['circuit']['circuitId'],
            'event_type': 'Sprint'
        })

    df = pd.DataFrame(rows)

    pos = pd.to_numeric(df['position'], errors='coerce')

    df['position_clean'] = np.where(pos.notna(), pos, 'DNF')

    dnf = (df['position_clean'] == 'DNF').sum()

    if points is None:

        pointsfinishers = [float(i)/2 for i in range(len(df), dnf, -1)]

    else:

        finishers = len(df) - dnf

        pointsfinishers = (points + [0.0]*finishers)[:finishers]

    df['points_rr'] = pointsfinishers + [0.0]*dnf

    return df

def get_completed_rounds(year):

    global rounds, sprint_rounds

    rounds.clear()

    sprint_rounds.clear()

    round_num = 1

    while True:

        race_url = f'{basic_url}{year}/{round_num}/race'

        race_response = requests.get(race_url)

        if race_response.status_code != 200:

            break

        try:

            race_json = race_response.json()

        except ValueError:

            break

        if not race_json.get('races'):

            break

        rounds.append(round_num)

        sprint_url = f'{basic_url}{year}/{round_num}/sprint/race'

        sprint_response = requests.get(sprint_url)

        if sprint_response.status_code == 200:

            try:

                sprint_json = sprint_response.json()

                if sprint_json.get('races'):

                    sprint_rounds.append(round_num)

            except ValueError:

                pass
              
        round_num += 1

for year in range(2024, 2026):

    get_completed_rounds(year)

    if not rounds:

        continue

    print(f"{len(rounds)} races in {year}")

    for round_num in rounds:

        race_df = get_race_points(year, round_num)

        if race_df is not None:

            all_data.append(race_df)

        if round_num in sprint_rounds:

            sprint_df = get_sprint_points(year, round_num)

            if sprint_df is not None:
              
                all_data.append(sprint_df)

        print(f"loaded data for: {year}, round: {round_num}")

final_df = pd.concat(all_data, ignore_index=True)

#final_df = final_df.drop(columns=['position_clean', 'points_rr', 'event_type', 'points'])

print(final_df.to_string())