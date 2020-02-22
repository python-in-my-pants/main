class Turn:

    def __init__(self, actions=[]):

        self.actions = actions[:]

    def add_action(self, action):

        self.actions.append(action)

    def assure_integrity(self):  # this only checks if the right team is acting

        if self.actions:
            acting_team = self.actions[0].player_a.team

            for act in self.actions:
                if act.player_a.team is not acting_team:
                    return False

        return True


class Action:

    def __init__(self, player_a, player_b=None, path=None, dmg2b=0, dmg2a=0, pos_a_dmg2b_index=None, pos_a_dmg2a_index=None):

        # tells how player A has moved and how much damage he inflicted to player b and himself in that time

        self.player_a = player_a  # action player
        self.player_b = player_b  # has value if target for fight was selected
        # self.destination = destination  # has value if moved
        self.path = path  # holds list of positions starting from player pos on action begin and ending in destination

        self.dmg2b = dmg2b  # has value if damage >0 was inflicted, holds LIST for bodyparts
        self.dmg2a = dmg2a  # has value if player A damaged himself (eg rocket launcher) OR he healed himself, in
                            # this case the dmg is <0, holds LIST for bodyparts
        self.pos_a_dmg2b = ...  # holds index of pos in path of player a when the damage to B was inflicted
        self.pos_a_dmg2a = ...  # holds index of pos of player a when he healed or damaged himself
