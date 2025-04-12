import random

def make_decision(client_data, score):
    """
    Determine whether to accept or reject a client based on their data and the current score.
    """

    #TODO: Analyze client_data

    if score == 9:
        decision = "Reject"
    elif score == 10:
        decision = "Reject"
    elif score >= 11:
        decision = random.choice(["Accept", "Reject"])
    else:
        decision = "Accept"

    return 1 if decision == "Accept" else 0