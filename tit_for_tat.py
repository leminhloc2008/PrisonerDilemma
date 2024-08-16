# tit_for_tat.py

def make_choice(own_choices, opponent_choices):
    if not opponent_choices:
        return True  # Cooperate on first move
    return opponent_choices[-1]  # Copy opponent's last move