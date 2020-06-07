"""
########################################################################################################################
#                                                                                                                      #
#                                       WICHTIG! RECHTLICHER HINWEIS                                                   #
#                                                                                                                      #
#   Autoren: Daniel Kretschmer                                                                                         #
#                                                                                                                      #
# Die durch die hier aufgeführten Autoren erstellten Inhalte und Werke unterliegen dem deutschen Urheberrecht.         #
# Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes  #
# bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.                                         #
#                                                                                                                      #
# Die Autoren räumen Dritten ausdrücklich kein Verwertungsrecht an der hier beschriebenen Software oder einer          #
# Kopie/Abwandlung dieser ein.                                                                                         #
#                                                                                                                      #
# Insbesondere untersagt ist das Entfernen und/oder Verändern dieses Hinweises.                                        #
#                                                                                                                      #
# Bei Zuwiderhandlung behalten die Autoren sich ausdrücklich die Einleitung rechtlicher Schritte vor.                  #
#                                                                                                                      #
########################################################################################################################
"""

import random


class Turn:

    def __init__(self, actions=[], win=False):

        self.actions = actions[:]
        self.rand_id = random.randint(0, 100000000)
        self.win = win

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

    def __init__(self,
                 player_a,
                 player_b=None,

                 path=None,

                 dmg2b=0,
                 dmg2a=0,

                 pos_a_dmg2b_index=None,
                 pos_a_dmg2a_index=None,

                 velocityraptor=None,
                 used_item_index=None):

        # tells how player A has moved and how much damage he inflicted to player b and himself in that time

        self.player_a = player_a  # action player
        self.player_b = player_b  # has value if target for fight was selected
        # self.destination = destination  # has value if moved
        self.path = path  # holds list of positions starting from player pos on action begin and ending in destination

        self.dmg2b = dmg2b  # has value if damage >0 was inflicted, holds LIST for body parts
        self.dmg2a = dmg2a  # has value if player A damaged himself (eg rocket launcher) OR he healed himself, in
                            # this case the dmg is <0, holds LIST for bodyparts

        self.pos_a_dmg2b = pos_a_dmg2b_index  # holds index of pos in path of player A when the damage to B was inflicted
                                              # OR the pos from where the dmg was done (is this used?)
        self.pos_a_dmg2a = pos_a_dmg2a_index  # holds index of pos of player a when he healed or damaged himself

        self.velocityraptor = velocityraptor

        self.used_item_index = used_item_index
