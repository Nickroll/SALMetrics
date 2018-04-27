README
==================

A statistical analysis package used for League of Legends analysis. 
it requires a data frame and will preform some basic analysis on the data.

calc_expected_champ
---------------------
This method of the SalMetrics class will find the expected values passed to
it for the champion passed to it. This only occurs if the champion was played 
at least 3 times to avoid outliers. 

calc_actual_champ
---------------------
Similar to calc_expected_champ but in this case only calculates the data
for champions that the player has played. 

Other Functions
---------------------
There are other functions that are included for data analysis:

    1) fight_metric
    2) calc_act_vs_expt
    3) lane_lead
    4) kda_metric
    5) harass_metric
    6) find_champ_avg
    7) avg_across
    
These functions work on the dictionaries returned from the SalMetrics methods.

Contact
----------------

My e-mail is rick.nickroller@gmail.com if you would like to contact me for any reason. 

