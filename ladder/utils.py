
def calc_ladder_score(winning_team, losing_team):
    old_sum_win_scores = 0.;
    old_sum_lose_scores = 0.;

    for e in winning_team:
        old_sum_win_scores += e.ladder_score;
    for e in losing_team:
        old_sum_lose_scores += e.ladder_score;

    avr = (old_sum_win_scores + old_sum_lose_scores) / (len(winning_team) + len(losing_team))
    K = get_K(avr)

    winning_team_e = 1. / (1. + pow(10, (old_sum_lose_scores - old_sum_win_scores) / 400.))
    winning_team_r = old_sum_win_scores + K * (1. - winning_team_e)

    losing_team_e = 1. / (1. + pow(10, (old_sum_win_scores - old_sum_lose_scores) / 400.))
    losing_team_r = old_sum_lose_scores + K * (0. - losing_team_e)

    winning_team_obtained_score = winning_team_r - old_sum_win_scores
    losing_team_obtained_score = losing_team_r - old_sum_lose_scores

    for e in winning_team:
        e.ladder_score += winning_team_obtained_score
        e.ladder_score = round(e.ladder_score)
    for e in losing_team:
        e.ladder_score += losing_team_obtained_score
        e.ladder_score = round(e.ladder_score)

def get_K(score):
    if score < 2100:
        return 32
    elif score < 2400:
        return 24
    else:
        return 16

def calc_rating(my_team, opponent_team):
    return 1. / (1. + pow(10, (opponent_team - my_team) / 400.))
