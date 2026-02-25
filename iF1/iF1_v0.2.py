import requests
import time
import numpy as np
import pandas as pd

basic_url = 'https://f1api.dev/api/'

all_data = []

def get_race_results(year, round_num):
    """Get race results for a specific year and round"""
    url = f'{basic_url}{year}/{round_num}/race'
    
    try:
        response = requests.get(url, timeout=10)
        time.sleep(2.0) 
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if not data.get('races') or not data['races'].get('results'):
            return None
        
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
        
        return pd.DataFrame(rows)
    
    except Exception as e:
        print(f"Error getting race {year}-R{round_num}: {e}")
        return None


def get_sprint_results(year, round_num):
    """Get sprint results for a specific year and round"""
    url = f'{basic_url}{year}/{round_num}/sprint/race'
    
    try:
        response = requests.get(url, timeout=10)
        time.sleep(2.0)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if not data.get('races') or not data['races'].get('sprintRaceResults'):
            return None
        
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
        
        return pd.DataFrame(rows)
    
    except Exception as e:
        print(f"Error getting sprint {year}-R{round_num}: {e}")
        return None


for year in range(2022, 2026):
    print(f"\nProcessing {year}...")
    
    round_num = 1
    consecutive_failures = 0
    
    while consecutive_failures < 3:  # Stop after 3 failed rounds in a row
        
        # Try to get race data
        race_df = get_race_results(year, round_num)
        
        if race_df is not None:
            all_data.append(race_df)
            print(f"✓ Loaded {year} Round {round_num} - Race")
            consecutive_failures = 0  # Reset counter
            
            # Try to get sprint data for this round
            sprint_df = get_sprint_results(year, round_num)
            if sprint_df is not None:
                all_data.append(sprint_df)
                print(f"✓ Loaded {year} Round {round_num} - Sprint")
        else:
            consecutive_failures += 1
            print(f"✗ No data for {year} Round {round_num}")
        
        round_num += 1

# Combine all data
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Clean up position column (convert NC to DNF)
    final_df['position'] = final_df['position'].replace('NC', 'DNF')
    
    print(f"\n{len(final_df)} total results downloaded")
    print(final_df.head(20))
else:
    print("No data downloaded!")

final_df.to_csv('f1_results.csv', index=False)

print("Saved to f1_results.csv")