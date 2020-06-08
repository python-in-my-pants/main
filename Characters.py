"""
########################################################################################################################
#                                                                                                                      #
#                                       WICHTIG! RECHTLICHER HINWEIS                                                   #
#                                                                                                                      #
#   Autoren: Daniel Kretschmer, Christian Loose                                                                        #
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

# encoding: UTF-8

import math
import numpy
from Item import *
from Weapon import *
from Game_objects import GameObject, CollAtom
from Data import *
import pygame as pg
import functools

Debug = False


# ToDo active weapon / item
class Character(GameObject):

    def __init__(self,
                 created_num=0,
                 name="default_character",
                 object_type="character",
                 team="team_0",
                 cost=1,
                 pos=[0, 0],
                 orientation=0,
                 carry=0,
                 class_id=0,

                 health=default_hp,
                 gear=[],
                 items=[],
                 weapons=[],

                 dexterity=25,
                 strength=15,
                 stamina=1000,
                 speed=1,
                 height=1,

                 bleed=[0 for _ in range(6)],
                 doped=False,

                 bleed_t=[0 for _ in range(6)],
                 doped_t=0
                 ):
        super().__init__(name=name, obj_type=object_type, pos=pos, materials=["player"])
        self.name = name
        self.object_type = object_type
        self.team = team
        self.cost = cost

        self.class_id = class_id  # class id
        self.idi = "c" + str(id(self))  # unique id but only per client
        self.rand_id = random.randint(0, 1000000000)

        self.health = health[:]
        self.dexterity = dexterity
        self.strength = strength
        self.weight = 0
        self.stamina = stamina
        self.speed = speed
        self.height = height
        self.pos = pos[:]

        # --------------------

        self.bleed = bleed[:]
        self.bleed_t = bleed_t[:]

        self.doped = doped
        self.doped_t = doped_t

        # -------------------------

        self.items = items[:]
        self.gear = gear[:]
        self.weapons = weapons[:]

        # -------------------------

        self.active_slot = None
        self.orientation = orientation

        self.pixs = pos[:]
        self.render_type = "blit"
        self.collider = 0
        self.is_selected = False
        self.carry = carry

        self.shot = False
        self.moved = False
        self.dist_moved = 0
        self.velocity = 0

    def clone_from_other(self, char):

        # DO NOT CLONE THESE AS THEY ARE MODIFIED BY APPLY-OPP-TURN IN RENDER
        # self.health = char.health[:]
        # self.pos = char.pos[:]

        # apply status effects
        self.bleed = char.bleed[:]
        self.bleed_t = char.bleed_t[:]

        self.doped = char.doped
        self.doped_t = char.doped_t

        # -------------------------

        # set gear durability
        for g in char.gear:
            for gs in self.gear:
                # it's the same class of helmet or same class of armor
                if g.my_id == gs.my_id and \
                        (isinstance(g, Helm) and isinstance(gs, Helm)) or \
                        (isinstance(g, Armor) and isinstance(gs, Armor)):
                    gs.durability = g.durability

        # -------------------------

        self.active_slot = char.active_slot
        self.orientation = char.orientation

    def __str__(self):

        helm_tier = armor_tier = -1
        if self.gear:
            for g in self.gear:
                if isinstance(g, Helm):
                    helm_tier = g.my_id+1
                if isinstance(g, Armor):
                    armor_tier = g.my_id-2

        weapon = weapon_stats[self.weapons[0].class_id][0] if self.weapons else -1

        return "{}:\n\t" \
               "\t  Dexterity:\t{}" \
               "\t  Strength:\t{}" \
               "\t     Speed:\t{}" \
               "\t Helm tier:\t{}" \
               "\tArmor tier:\t{}" \
               "        HP:\t\t{}" \
               "\t    Weapon:\t{}".format(character_classes[self.class_id], self.dexterity, self.strength, self.speed,
                                          helm_tier, armor_tier, self.health, weapon)

    def class_selector(self):

        self.stamina = class_stats[self.class_id][0]
        self.speed = class_stats[self.class_id][1]
        self.dexterity = class_stats[self.class_id][2]
        self.strength = class_stats[self.class_id][3]
        self.weight = class_stats[self.class_id][4]
        self.cost = class_stats[self.class_id][5]

    def confirm(self):
        self.collider = pg.sprite.Group(CollAtom(self.pos))

    def add_elem(self, material, elem_pixs):  # adds new element to pixs and adjusts mat_ind and materials

        self.mat_ind.append(self.pixs.__len__() - 1)
        self.materials.append(material)
        for elem_pix in elem_pixs:
            self.pixs.append(elem_pix)

    # --- get status ---

    def get_carryable_weight(self):
        return self.strength * 11

    def get_pos(self, i):
        return self.pos[i]

    def get_drawable(self):
        return self.pixs

    def is_dead(self):  # returns if dead
        return self.health[0] <= 0 or self.health[3] <= 0

    def can_shoot(self):
        return self.health[1] > 0 or self.health[2] > 0 or self.doped

    def can_move(self):
        return self.health[4] > 0 or self.health[4] > 0 or self.doped

    # --- movements ---

    def move(self, dest):
        # just assume dest is legit
        if self.can_move():
            self.dist_moved = self.dist_to_other_pos(dest)
            self.velocity = self.velocity * velocity_decay_factor + self.dist_moved
            self.pos = dest
            self.confirm()

    def stand_up(self):
        self.height = 1

    def crouch(self):
        self.height = 0.5

    def lay_down(self):
        self.height = 0.3

    # --- item and weapon handling ---

    if Debug:
        def dead(self):
            print(
                self.name + " you are dead!\n Kopf: " + str(self.health[0]) + "\n Linker Arm: " + str(self.health[1]) +
                "\n Rechter Arm: " + str(self.health[2]) + "\n Torso: " + str(self.health[3]) + "\n Linkes Bein: "
                + str(self.health[4]) + "\n Rechtes Bein: " + str(self.health[5]))

    if Debug:
        def statusprint(self, statind):
            switcher = {
                0: "You are burning!",
                1: "You got poisoned!",
                2: "You are bleeding!",
                3: "You got blinded!"
            }
            print(switcher[statind])

    if Debug:
        def hitprint(self, dmg, partind):
            switcher = {
                0: "You got hit in the head! Damage done: " + str(dmg),
                1: "You got hit in your left arm! Damage done: " + str(dmg),
                2: "You got hit in your right arm!! Damage done: " + str(dmg),
                3: "You got hit in your torso! Damage done: " + str(dmg),
                4: "You got hit in your left leg! Damage done: " + str(dmg),
                5: "You got hit in your right leg! Damage done: " + str(dmg)
            }
            print(switcher[partind])

    def item_add(self, new_item):
        if self.items.__len__() < 8:
            self.items.append(new_item)
        else:
            print("You can't carry anymore!")

    def item_drop(self, index):
        if self.items.__len__() >= 1:
            self.items.pop(index)
        else:
            print("You don't have any items!")

    def item_change(self, new_item, index):
        if self.items.__len__() >= 1:
            self.items[index] = new_item
        else:
            print("You can't exchange any items!")

    def weapon_add(self, new_wep):
        if self.weapons.__len__() < 4:
            self.weapons.append(new_wep)
        else:
            print("You can't carry any more weapons!")

    def weapon_drop(self, index):
        if self.weapons.__len__() >= 1:
            self.weapons.pop(index)
        else:
            print("You don't carry any weapon!")

    def weapon_change(self, new_weapon, index):
        if self.weapons.__len__() >= 1:
            self.weapons[index] = new_weapon
        else:
            print("You can't exchange any weapons!")

    def use_item(self, itemind, partind=-1):

        self.items[itemind].use(self, partind)

    def change_active_slot(self, t, index):
        # args = [type, index]

        if t == "Weapon" and index < len(self.weapons):
            self.active_slot = self.weapons[index]
            return
        if t == "Item" and index < len(self.items):
            self.active_slot = self.items[index]
            return
        print("Warning! Active slot must hold an item or a weapon!")

    def get_active_slot(self):
        if self.active_slot:
            return self.active_slot
        else:
            if self.weapons:
                self.active_slot = self.weapons[0]
                return self.active_slot
            if self.items:
                self.active_slot = self.items[0]
                return self.active_slot
            return None

    # --- shooting ---

    def dist_to_other_char(self, dude):
        return abs(numpy.sqrt(((self.pos[0] - dude.pos[0]) ** 2) + ((self.pos[1] - dude.pos[1]) ** 2)))

    def dist_to_other_pos(self, pos):
        return abs(numpy.sqrt(((self.pos[0] - pos[0]) ** 2) + ((self.pos[1] - pos[1]) ** 2)))

    def shoot(self, dude, partind):

        if True:

            chance, dmg, spt, rpg_bool = self.get_chance(dude, partind)

            print("Hitchance is ", chance, " and dmg is ", dmg)

            dmg_done = 0
            dmg_done_list = [0 for _ in range(6)]

            if rpg_bool:
                if numpy.random.randint(0, 101) <= chance:
                    dude.get_damaged(dmg, partind, rpg_bool)
                    dmg_done = 600
                    dmg_done_list = [dmg for _ in range(6)]
            else:
                for s in range(spt):
                    if numpy.random.randint(0, 101) <= chance:
                        dmg_done += dude.get_damaged(dmg, partind, rpg_bool)
                dmg_done_list[partind] = dmg_done

            return dmg_done, dmg_done_list

    def shooting_impossible(self, opp):

        if opp.is_dead():
            return "Opponent is already dead"

        if not isinstance(self.active_slot, Weapon):
            return "You don't hold a weapon!"

        if not self.can_shoot():
            return "Your arms are too damaged to shoot!"

        return False

    def get_chance(self, opp, partind):

        dex = self.dexterity  # this contains arm hp already
        x = self.dist_to_other_char(opp)
        l1, l2 = (self.health[4], self.health[5])
        leg_hp_sum = default_hp[4] + default_hp[5]
        v1 = self.velocity
        strength = self.strength

        v2 = opp.velocity

        spt = self.active_slot.spt
        pv = self.active_slot.projectile_v
        pw = self.active_slot.projectile_w
        blen = self.active_slot.barrel_len

        recoil = self.active_slot.recoil
        ran = self.active_slot.ran
        dmg = self.active_slot.get_dmg(x)

        def tanh(_x):
            return numpy.tanh(_x)

        def sign(_x):
            return numpy.sign(_x)

        range_factor = -(tanh((x / (ran * k1)) - (0.1 * ran * k1) - (1 / k1) + (k10 / base_chances[partind]))) / 2 + 0.5
        bar_len_factor = self.active_slot.barrel_len_conversion(blen) / 6.05
        recoil_factor = 1 / ((1 - ((-tanh((recoil / k5) - k9 * strength)) / 2 + 0.5)) * recoil + 1)
        own_speed_factor = sign(v1) * ((l1 + l2) / (leg_hp_sum * ((v1 / k2) + 1))) + 1 - sign(v1)
        opp_speed_factor = 1 / ((v2 / k2) + 1)
        dex_factor = dex / 100

        return 100 * range_factor * bar_len_factor * recoil_factor * own_speed_factor * opp_speed_factor * dex_factor, \
            dmg, \
            spt, \
            self.active_slot.name == "RPG"

    """def get_chance(self, dude, partind):

        if not dude.is_dead():

            if self.health[1] <= 0 and self.health[2] <= 0:
                return "Du hast keine Arme mehr!"

            if not isinstance(self.active_slot, Weapon):
                return "Rüste eine Waffe aus!"

            chance_mod = [15, 10, 10, 2, 7, 7]

            c_range = self.dist_to_other_char(dude)
            dmg = self.calc_dmg(c_range)
            p_range = self.calc_p_range(c_range)
            spt = self.active_slot.spt
            rpg_bool = False

            if self.active_slot.name in ("Maschinenpistole", "Sturmgewehr", "Maschinengewehr"):
                recoil_acc = self.calc_recoil_acc()
                chance = int(self.active_slot.acc * (0.3 * self.dexterity) - p_range + recoil_acc - self.dist_moved)

            elif self.active_slot.name == "Raketenwerfer":
                chance = int(self.active_slot.acc * (0.3 * self.dexterity) - p_range - self.dist_moved)
                rpg_bool = True

            else:
                chance = int(self.active_slot.acc * (0.3 * self.dexterity) - p_range - self.dist_moved)

            if chance > 0:
                chance -= chance_mod[partind]
            if chance <= 0:
                chance = 1

            return chance, dmg, spt, rpg_bool
        else:
            return "Das Ziel ist tot!"

    def calc_recoil_acc(self):
        if self.active_slot.name == "Maschinenpistole":
            return int(self.strength / 5)
        if self.active_slot.name == "Sturmgewehr":
            return int(self.strength / 10)
        if self.active_slot.name == "Maschinengewehr":
            return int(self.strength / 4)

    def calc_dmg(self, c_range):
        if self.active_slot.name == "Pistole":
            if c_range >= 20:
                return self.active_slot.dmg - int((0.2 * (c_range - 20)) + 0.5)
            else:
                return self.active_slot.dmg
        if self.active_slot.name == "Pistole":
            if c_range >= 15:
                return self.active_slot.dmg - int((0.3 * (c_range - 15)) + 0.5)
            else:
                return self.active_slot.dmg
        if self.active_slot.name == "Sturmgewehr":
            if c_range >= 50:
                return self.active_slot.dmg - int((0.2 * (c_range - 50)) + 0.5)
            else:
                return self.active_slot.dmg
        if self.active_slot.name == "Shotgun":
            if c_range >= 10:
                return self.active_slot.dmg - int((1 * (c_range - 10)) + 0.5)
            else:
                return self.active_slot.dmg
        if self.active_slot.name == "Maschinengewehr":
            if c_range >= 40:
                return self.active_slot.dmg - int((0.3 * (c_range - 40)) + 0.5)
            else:
                return self.active_slot.dmg
        if self.active_slot.name == "Sniper":
            if c_range >= 100:
                return self.active_slot.dmg - int((0.2 * (c_range - 10)) + 0.5)
            else:
                return self.active_slot.dmg
        if self.active_slot.name == "Raketenwerfer":
            return self.active_slot.dmg

    def calc_p_range(self, c_range):

        print("active slot name: ", self.active_slot.name)

        if self.active_slot.name == "Pistole":
            if c_range > 20:
                return c_range - 20
            else:
                return 0
        if self.active_slot.name == "Pistole":
            if c_range > 15:
                return c_range - 15
            else:
                return 0
        if self.active_slot.name == "Sturmgewehr":
            if c_range > 50:
                return c_range - 50
            else:
                return 0
        if self.active_slot.name == "Shotgun":
            if c_range > 10:
                return c_range - 10
            else:
                return 0
        if self.active_slot.name == "Maschinengewehr":
            if c_range < 2:
                return 10
            if c_range > 40:
                return c_range - 40
            else:
                return 0
        if self.active_slot.name == "Sniper":
            if c_range < 5:
                return c_range * 10
            if c_range > 100:
                return c_range - 100
            else:
                return 0
        if self.active_slot.name == "Raketenwerfer":
            if c_range > 20:
                return c_range - 20
            else:
                return 0"""

    # --- special stats &  hp modifications ---

    def adjust_stats(self):  # adjusts stats and depends from health

        # --- speed

        self.speed *= (self.health[4] + self.health[5]) / 200

        # only torso and head left
        if self.health[4] <= 0 and self.health[5] <= 0 and self.health[1] <= 0 and self.health[2] <= 0:
            self.speed = 0

        # --- strength and dexterity

        # no arms no cookies
        if self.health[1] <= 0 and self.health[2] <= 0:
            self.strength = 0
            self.dexterity = 0

        # only 1 arm left
        else:
            if self.health[1] <= 0 or self.health[2] <= 0:
                self.strength *= 0.5
                self.dexterity *= 0.2

    def apply_hp_change(self, dmg):  # also negative damage aka heal

        for i in range(6):
            self.health[i] -= dmg[i]
            if dmg[i] > 0:
                self.start_bleeding(i)

            if self.health[i] > default_hp[i]:
                self.health[i] = default_hp[i]

            if self.health[i] < 0:
                self.health[i] = 0

        self.adjust_stats()

    def get_damaged(self, dmg, partind, rpg_bool):  # modifies gear, health and stats

        dmg_done = 0
        helmet = None
        armor = None

        if rpg_bool:
            for i in range(6):
                dmg_done += 100
                self.health[i] -= default_hp[i]
            if Debug:
                self.hitprint(dmg_done, partind)

        else:
            for g in self.gear:
                if isinstance(g, Helm):
                    helmet = g
                if isinstance(g, Armor):
                    armor = g

            if partind == 0:
                if helmet:
                    if helmet.durability > 0:
                        dmg_done = int(dmg * helmet.reduction)

                        self.health[0] -= dmg_done
                        if self.health[0] < 0:
                            self.health[0] = 0

                        self.start_bleeding(partind)

                        # reduce durability by prevented damage
                        helmet.durability -= (dmg - dmg_done)
                        if helmet.durability <= 0:
                            helmet.durability = 0
                            self.gear.remove(helmet)
                else:
                    dmg_done = dmg
                    self.health[0] -= dmg_done
                    if self.health[0] < 0:
                        self.health[0] = 0
                    self.start_bleeding(partind)

            elif partind == 3:
                if armor:
                    if armor.durability > 0:
                        dmg_done = int(dmg * armor.reduction)

                        self.health[3] -= dmg_done
                        if self.health[3] < 0:
                            self.health[3] = 0

                        self.start_bleeding(partind)

                        # reduce durability by prevented damage
                        armor.durability -= (dmg - dmg_done)
                        if armor.durability <= 0:
                            armor.durability = 0
                            self.gear.remove(armor)

                else:
                    dmg_done = dmg
                    self.health[3] -= dmg_done
                    if self.health[3] < 0:
                        self.health[3] = 0

                    self.start_bleeding(partind)

            else:  # not head and not torso

                dmg_done = dmg
                self.health[partind] -= dmg_done
                if self.health[partind] < 0:
                    self.health[partind] = 0

                self.start_bleeding(partind)

            if Debug:
                self.hitprint(dmg_done, partind)

            self.adjust_stats()

        if self.is_dead():
            if Debug:
                self.dead()

        return dmg_done

    def regenerate_hp(self, amount, partind):

        self.health[partind] *= amount

        if self.health[partind] > default_hp[partind]:
            self.health[partind] = default_hp[partind]

        self.adjust_stats()

    def timer_tick(self):
        for x in range(6):
            if self.bleed[x]:
                if self.bleed_t[x] > 0:
                    self.apply_bleed_dmg(x)
                    self.bleed_t[x] -= 1
                else:
                    self.bleed[x] = False

    def decay_velocity(self):  # must only be called if char did not move in this turn
        self.velocity *= velocity_decay_factor

    # --- bleed stuff ---

    def apply_bleed_dmg(self, partind):
        self.health[partind] -= 5

    def start_bleeding(self, partind):
        if not self.bleed[partind]:
            self.bleed[partind] = True
            self.bleed_t[partind] = 1000
            if Debug:
                self.statusprint(2)

    def stop_bleeding(self, partind):  # stops bleeding of body part with this index
        self.bleed[partind] = False
        self.bleed_t[partind] = 0


def create_character(_id, team):  # team holds only name/number of team
    boi = Character(class_id=_id, team=team)
    boi.class_selector()
    return boi
