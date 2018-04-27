import pandas as pd
import sqlite3
from StatsTest import SalMetrics as sm


# Reading in the data from sqlite3
conn = sqlite3.connect('/Users/NicholasRoller/Documents/Projects/Riot Crawler/scripts/data/Player_stats.db')
df = pd.read_sql_query('SELECT * from playerStats', conn)

# Creating the per minute columns needed to do the stats calculations
df['dmg/min'] = df['totalDamageDealtToChampions'] / df['gameDuration']
df['dmgTaken/min'] = df['totalDamageTaken'] / df['gameDuration']
df['dmgMit/min'] = df['damageSelfMitigated'] / df['gameDuration']
df['cc/min'] = df['totalTimeCrowdControlDealt'] / df['gameDuration']
df['vs/min'] = df['visionScore'] / df['gameDuration']

# Performing top analysis
top_analysis = sm.SalMetrics('top', df)

# Getting all the champions that were played.
champs = list(top_analysis.data['championId'].unique())

# Creating necessary params for the functions
calc_dict = {'dmg': 'dmg/min',
             'dmgTaken': 'dmgTaken/min',
             'dmgMit': 'dmgMit/min',
             'cc': 'cc/min',
             'vs': 'vs/min',
             'harass': 'dTPMD0to10'}

fight_stats = ['dmg', 'dmgTaken', 'dmgMit', 'cc']
list_stats = list(calc_dict.keys())
list_stats.append('fightMetric')

# Calculating the expected damage for all of the champions played
stats_dict = top_analysis.calc_expected_champ(champs, 'championId', 'win', calc_dict)

# Adding the fight metric
sm.fight_metric(stats_dict, fight_stats)

# Getting the list of summoners. Oddly enough Ziv's name is sometimes AHQ and other ahq so going to just upper the whole
# summoner list
summoner_list = list(top_analysis.data['summonerName'].str.upper().value_counts().index)

stat_avg_df = pd.DataFrame()
# Looping through all the players and getting their avg % difference on each champion
for summoner in summoner_list:

    # Getting the actual stats for each player
    act_dict = top_analysis.calc_actual_champ(summoner, 'summonerName', champs, 'championId', 'win', calc_dict)

    # Adding fight metric
    sm.fight_metric(act_dict, fight_stats)

    # Getting the %diff
    sm.calc_act_vs_expt(act_dict, stats_dict, inplace=True)

    # Creating a total average across all champions
    avg_dict = sm.avg_across(act_dict, list_stats)
    avg_dict['player'] = summoner

    # Appending data to a final data frame
    avg_df = pd.DataFrame.from_records([avg_dict])
    stat_avg_df = stat_avg_df.append(avg_df, ignore_index=True)


stat_avg_df.set_index('player', inplace=True)
stat_avg_df.to_csv('../TempData/avg_top_diff.csv')
