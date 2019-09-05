class Turn:

    def __init__(self, actions=[]):

        self.actions = actions[:]

    def add_action(self, action):

        self.actions.append(action)

    def assure_integrity(self):

        if self.actions:
            t = self.actions[0].player_a.team

            for act in self.actions:
                if act.player_a.team is not t:
                    return False

        return True


class Action:

    def __init__(self, player_a, player_b=None, destination=None, dmg2b=0, dmg2a=0):

        # tells where player a has moved and how much damage he inflicted to player b and himself in that time

        self.player_a = player_a  # action player
        self.player_b = player_b  # has value if target for fight was selected
        self.destination = destination  # has value if moved
        self.dmg2b = dmg2b  # has value if damage >0 was inflicted
        self.dmg2a = dmg2a  # has value if player a damaged himself (eg rocket launcher) OR he healed himself, in
                            # this case the dmg is <0
