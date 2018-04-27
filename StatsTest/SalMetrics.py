import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
from statistics import mean


class SalMetrics(object):
    """
    This class will take a given players name and return specific metrics about them.
    """

    def __init__(self, role: str, data: pd.DataFrame):
        """
        Creates a SalMetrics object that will determine the player stats from.
        
        :param role: The role of the player. Used for determine who to compare to
        :param data: A pandas DataFrame object
        """
        self.role = role.lower()

        if self.role == 'top':
            self.data = data.iloc[::5, ]
        elif (self.role == 'jungle') or (self.role == 'jung'):
            self.data = data.iloc[1::5, ]
        elif (self.role == 'mid') or (self.role == 'middle'):
            self.data = data.iloc[2::5, ]
        elif (self.role == 'bot') or (self.role == 'adc'):
            self.data = data.iloc[3::5, ]
        elif (self.role == 'support') or (self.role == 'supp') or (self.role == 'sup'):
            self.data = data.iloc[4::5, ]
        elif self.role == 'none':
            self.data = data
        else:
            raise Exception('Invalid Role. Use: top, jungle, jung, mid, middle, bot, adc, support, supp, sup, or none')

    def calc_expected_champ(self, champion: list, champ_col: str, result_col: str, calc_dict: dict) -> dict:
        """
        Calculates the expected stats for a given champion or list of champions.

        Formula: f(x) = ((#wins * stat In Wins) + (#loss * stat In Loss)) / (#wins + #loss)

        :param champion: The champion or list of champions to use in the calculation
        :param champ_col: The column to look for champions in
        :param result_col: The column for either win or loss expected to be a 1 or 0
        :param calc_dict: The columns to use for calculation of the stats. Should be in the form of
        { 'dmg' : 'col' }.
        :return: A dict of { champ : { stat : value } }
        """

        # Check to make sure results column is a numerical dtype
        if not is_numeric_dtype(self.data[result_col]):
            raise Exception('Result col needs to be dtype numeric (float/int) it is: {}'.format(
                self.data[result_col].dtype))

        else:
            # Going to store each result in a dict of {champ1 : {key1 : value1}
            #                                          champ2 : {key2 : value2} }
            champ_dict = dict()
            # Loop through the list of champions passed
            for champ in champion:
                champ_df = self.data.query('{} == {}'.format(champ_col, champ))

                # Checking to make sure the champ was played at least 3 times
                if champ_df.shape[0] < 3:
                    continue
                else:
                    win_count = len(champ_df[champ_df[result_col] == 1.0])
                    loss_count = len(champ_df[champ_df[result_col] == 0.0])

                    # Looping through the calc_columns dict and storing the final stats in a dict of { stat : value }
                    stat_dict = dict()
                    for k, v in calc_dict.items():
                        win_stat = champ_df.query('{} == 1.0'.format(result_col))[v].mean()
                        loss_stat = champ_df.query('{} == 0.0'.format(result_col))[v].mean()

                        # The above will return NaN if there is no mean for it so checking that and setting to 0
                        if np.isnan(win_stat):
                            win_stat = 0
                        if np.isnan(loss_stat):
                            loss_stat = 0
                        try:
                            expected = ((win_count * win_stat) + (loss_count * loss_stat)) / (win_count + loss_count)
                        except ZeroDivisionError:
                            continue

                        stat_dict[k] = expected
                    champ_dict[champ] = stat_dict

        return champ_dict

    def calc_actual_champ(self, player: str, player_col: str,  champion: list, champ_col: str, result_col: str,
                          calc_dict: dict) -> dict:
        """
        Calculates the actual stats for a given player on that champion and returns a dict of the values for
        the champion. Uses the same function as calc_expected_dmg

        :param player: The player for who to calculate the stats
        :param player_col: The column player names are stored in
        :param champion: The champion or list of champions to use
        :param champ_col: The column with the champions in it
        :param result_col: The column with the results as wins or losses
        :param calc_dict: The columns and type of stat to be calculated. Ex. { 'dmg' : 'colname' }
        :return: A dict of { 'champ' : { stat : value } }
        """

        if not is_numeric_dtype(self.data[result_col]):
            raise Exception('Result col needs to be dtype numeric (float/int) it is: {}'.format(
                self.data[result_col].dtype))

        else:
            champ_dict = dict()

            # Loop through champion list
            for champ in champion:
                pc_df = self.data.query('({} == {}) & ({}.str.upper() == "{}")'.format(
                    champ_col, champ, player_col, player.upper()
                ))
                win_count = len(pc_df[pc_df[result_col] == 1.0])
                loss_count = len(pc_df[pc_df[result_col] == 0.0])

                stat_dict = dict()
                for k, v in calc_dict.items():
                    win_stat = pc_df.query('{} == 1.0'.format(result_col))[v].mean()
                    loss_stat = pc_df.query('{} == 0.0'.format(result_col))[v].mean()

                    # The above will return NaN if there is no mean for it so checking that and setting to 0
                    if np.isnan(win_stat):
                        win_stat = 0
                    if np.isnan(loss_stat):
                        loss_stat = 0
                    try:
                        expected = ((win_count * win_stat) + (loss_count * loss_stat)) / (win_count + loss_count)
                    except ZeroDivisionError:
                        continue

                    stat_dict[k] = expected

                champ_dict[champ] = stat_dict

        return champ_dict


def fight_metric(actual_dict: dict, fight_stats: list, *col_name: str):
    """
    Returns inplace a metric that is added to the stats for a given champion by summing together the values in the
    fight_stats list.

    :param actual_dict: The dict of { champ : { stat : value } }
    :param fight_stats: The list of stats for be used for creation of the fight stat
    :param col_name: Optional column name to be used instead of fightMetric
    :return: A modified actual dict with 'fightMetric' added to the champ values by default.
    """

    for champ in actual_dict.keys():
        fight_value = 0
        for stat in fight_stats:
            if stat in actual_dict[champ]:
                fight_value += actual_dict[champ][stat]

        if col_name:
            actual_dict[champ][col_name] = fight_value
        else:
            actual_dict[champ]['fightMetric'] = fight_value


def calc_act_vs_expt(actual_dict: dict, expected_dict: dict, inplace: bool =False) -> dict:
    """
    Will calculate the percent difference between the actual and expected for a given dict and change the value
    of the stat to a % difference

    Formula:((actual/expected) -1) * 100

    :param actual_dict: A dict of actual stats. { champ : { stat : value } }
    :param expected_dict: A dict of expected stats. {champ : { stat : value } }
    :param inplace: If you want the function to replace { stat : value } with { stat : %diff }
    :return: The percent difference as a dict
    """

    # Going through all the champions in the actual dict and getting the stats dicts in them
    diff_dict = dict()

    for champ in actual_dict.keys():
        if (champ in actual_dict) and (champ in expected_dict) :
            a_stats = actual_dict[champ]
            e_stats = expected_dict[champ]

            perc_dict = dict()
            # Getting the values for each of the stats and calculating the percent diff fo each stat of
            # a given champion
            for k, _ in a_stats.items():
                a_value = a_stats[k]
                e_value = e_stats[k]
                percent_diff = ((a_value/e_value) - 1) * 100

                perc_dict[k] = percent_diff

            if inplace:
                actual_dict[champ] = perc_dict
            else:
                diff_dict[champ] = perc_dict
        else:
            continue

    if not inplace:
        return diff_dict


def lane_lead(csd10: float, xpd10: float, total_cs: float, total_xp: float, team_prox: float) -> float:
    """
    Returns the lead a player has in lane in terms of cs and xp relative to total cs and xp between the two laners

    Formula: (team_prox * (csd10 + xpd10)) / (total_xp + total_cs)

    :param csd10: Difference in cs at 10 minutes
    :param xpd10: Difference in xp at 10 minutes
    :param total_cs: Total cs of player and opponent
    :param total_xp: Total xp of player and opponent
    :param team_prox: How often a teammate is within 2000px after minute 2
    :return: A float of lane lead metric
    """

    ll_metric = (team_prox * (csd10 + xpd10)) / (total_cs + total_xp)
    return ll_metric


def kda_metric(iso_kills: int, kills_assists: int, iso_deaths: int, deaths: int, **weights: dict) -> float:
    """
    A metric which calculates how well a person is doing in terms of kda.

    Formula: ((iso_kills * w1) + (kills_assists * w2)) / ((iso_deaths * w1) + (deaths * w3))

    :param iso_kills: Kills when no teammate assisted
    :param kills_assists: Total kills plus assists
    :param iso_deaths: Deaths when no enemy teammate assisted
    :param deaths: Total deaths
    :param weights: Optional weights to add to each category as isolated deaths are more punishing. Should be present as
    { 'w1' : value, 'w2 : value }. Values are supplied from a riot survey and used unless changed.
    :return: A new KDA metric
    """

    if not weights:
        # These were taken from a riot survey
        w1 = 0.1336
        w2 = 0.90
        w3 = 0.95

    elif weights:
        try:
            w1 = weights.get('w1')
            w2 = weights.get('w2')
            w3 = weights.get('w3')
        except Exception as e:
            raise Exception(e)

    kda = ((iso_kills * w1) + (kills_assists * w2)) / ((iso_deaths * w1) + (deaths * w3))

    return kda


def harass_metric(damage_taken_p1: float, damage_taken_p2: float) -> float:
    """
    A metric that looks at damage taken as a fraction of total damage dealt in lane.

    Formula: 1 - (damage_taken_p1/(damage_taken_p1 + damage_taken_p2))

    :param damage_taken_p1: Damage taken by player one
    :param damage_taken_p2: Damage taken by player two
    :return: A float of the percent of damage player 1 did to player 2
    """

    hm = 1-(damage_taken_p1 / (damage_taken_p1 + damage_taken_p2))

    return hm


def find_champ_avg(percent_diff: dict, inplace: bool =False) -> dict:
    """
    Returns the average percent different of the champion played.

    :param percent_diff: A dictionary of style { champ : { stat : value } }
    :param inplace: To modify the passed dict in place or not
    :return: A dict of { champ : { avg__of_stats : average } }
    """

    return_dict = dict()
    for champ in percent_diff:
        avg_list = list()
        if inplace:
            for k, v in percent_diff[champ].items():
                avg_list.append(v)

            # Handling cases where there is no games played on that champion
            if len(avg_list) != 0:
                percent_diff[champ] = {'avg_of_stats': mean(avg_list)}
            else:
                continue

        else:
            for k, v in percent_diff[champ].items():
                avg_list.append(v)

            if len(avg_list) != 0:
                return_dict[champ] = {'avg_of_stats': mean(avg_list)}
            else:
                continue

    if not inplace:
        return return_dict


def avg_across(percent_diff: dict, list_of_stats: list) -> dict:
    """
    Calculates the avg percent diff across all champions that were played.

    :param percent_diff: A dict containing percent differences for each champion { champ : { stat : percent_diff } }
    :param list_of_stats: A list of the stats that are present for each champion
    :return: A dict with { stat : avg_diff }
    """

    return_dict = dict()

    for stat in list_of_stats:
        stat_avg = list()
        for champ in percent_diff:
            if stat in percent_diff[champ]:
                stat_avg.append(percent_diff[champ][stat])
            else:
                continue

        return_dict[stat] = mean(stat_avg)

    return return_dict
