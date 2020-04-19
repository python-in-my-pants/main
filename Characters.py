# encoding: UTF-8

import math
import numpy
from Item import *
from Weapon import *
from Game_objects import GameObject, CollAtom
from Data import *
import pygame as pg

Debug = True


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

                 health=[100, 100, 100, 100, 100, 100],
                 gear=[],
                 items=[],
                 weapons=[],

                 dexterity=25,
                 strength=15,
                 stamina=1000,
                 speed=1,
                 height=1,

                 bleed=[False, False, False, False, False, False],
                 burn=False,
                 poison=False,
                 blind=False,

                 burn_t=0,
                 poison_t=0,
                 blind_t=0,
                 bleed_t=[0, 0, 0, 0, 0, 0],
                 ):
        super().__init__(name=name, obj_type=object_type, pos=pos, materials=["player"])
        self.name = name
        self.object_type = object_type
        self.team = team
        self.cost = cost

        self.class_id = class_id  # class id
        self.idi = "c" + str(id(self))  # unique id

        self.health = health[:]
        self.dexterity = dexterity
        self.strength = strength
        self.weight = 0
        self.gear = gear[:]
        self.stamina = stamina
        self.speed = speed
        self.height = height
        self.pos = pos[:]

        self.bleed = bleed[:]
        self.bleed_t = bleed_t[:]
        self.burn = burn
        self.burn_t = burn_t
        self.poison = poison
        self.poison_t = poison_t
        self.blind = blind
        self.blind_t = blind_t

        self.items = items[:]
        self.gear = gear[:]
        self.weapons = weapons[:]
        self.active_slot = None
        self.orientation = orientation

        self.pixs = pos[:]
        self.render_type = "blit"
        self.collider = 0
        self.pixs = [self.pos]
        self.is_selected = False
        self.carry = carry

        self.shot = False
        self.moved = False
        self.dist_moved = 0

    def class_selector(self):
        self.stamina = class_stats[self.class_id][0]
        self.speed = class_stats[self.class_id][1]
        self.dexterity = class_stats[self.class_id][2]
        self.strength = class_stats[self.class_id][3]
        self.weight = class_stats[self.class_id][4]
        self.cost = class_stats[self.class_id][5]

    def weight_calculator(self):
        return self.strength * 11

    def is_dead(self):  # returns if dead
        return self.health[0] <= 0 or self.health[3] <= 0

    def get_pos(self, i):
        return self.pos[i]

    def get_drawable(self):
        return self.pixs

    def move(self, dest):
        # just assume dest is legit
        self.pos = dest
        self.confirm()

    def confirm(self):
        self.collider = pg.sprite.Group(CollAtom(self.pos))

    def get_inner_shoulders(self):  # TODO: approximate sin/cos using Kleinwinkel approximation to optimize runtime

        if self.orientation == 0:
            return [[self.pos[0]+0.15, self.pos[1]+0.5], [self.pos[0]+0.85, self.pos[1]+0.5]]

        #  shoulder positions
        return [[-0.35 * math.cos(360-self.orientation), -0.35 * math.sin(360-self.orientation)],
                [0.35 * math.cos(360-self.orientation), 0.35 * math.sin(360-self.orientation)]]

    def get_drawable_surf(self):
        character_surf = pg.Surface((200, 200))
        character_surf.fill((0, 0, 0))

        # left arm
        pg.draw.circle(character_surf, mat_colour[self.team],
                       [int(character_surf.get_width() * 0.15), int(character_surf.get_height() * 0.5)],
                       int(character_surf.get_width() * 0.15), 0)

        # right arm
        pg.draw.circle(character_surf, mat_colour[self.team],
                       [int(character_surf.get_width() * 0.85), int(character_surf.get_height() * 0.5)],
                       int(character_surf.get_width() * 0.15), 0)

        # torso
        pg.draw.rect(character_surf, mat_colour[self.team],
                     (int(character_surf.get_width() * 0.15),
                      int(character_surf.get_height() * 0.35),
                      int(character_surf.get_width() * 0.75),
                      int(character_surf.get_width() * 0.3)))

        # head
        pg.draw.circle(character_surf, mat_colour[self.team],
                       [int(character_surf.get_width() * 0.5), int(character_surf.get_height() * 0.5)],
                        int(character_surf.get_width() * 0.25), 0)

        if self.is_selected:
            pg.draw.circle(character_surf, (255, 0, 0), [100, 100], 105, 5)

        character_surf.set_colorkey((0, 0, 0))

        return character_surf

    def add_elem(self, material, elem_pixs):  # adds new element to pixs and adjusts mat_ind and materials

        self.mat_ind.append(self.pixs.__len__() - 1)
        self.materials.append(material)
        for elem_pix in elem_pixs:
            self.pixs.append(elem_pix)

    if Debug:
        def dead(self):
            print(self.name + " you are dead!\n Kopf: " + str(self.health[0]) + "\n Linker Arm: " + str(self.health[1]) +
                "\n Rechter Arm: " + str(self.health[2]) + "\n Torso: " + str(self.health[3]) + "\n Linkes Bein: "
                + str(self.health[4]) + "\n Rechtes Bein: " + str(self.health[5]))

    def statchange(self):
        #ändert stats(attribute) des characters
        if self.health[1] <= 0 and self.health[2] <= 0:
            self.strength = 0
            self.dexterity = 0
        elif self.health[1] <= 0 or self.health[2] <= 0 and not(self.health[1] <= 0 and self.health[2]):
            self.strength -= self.strength * 0.5
            self.dexterity -= self.dexterity * 0.5

        if self.health[4] <= 0 and self.health[5] <= 0 and ((self.health[1] <= 0 or self.health[2] <= 0)
                                                              and not(self.health[1] <= 0 and self.health[2] <= 0)):
            self.speed = 0.15
        elif self.health[4] <= 0 and self.health[5] <= 0 and (self.health[1] <= 0 and self.health[2] <= 0):
            self.speed = 0.1
        elif self.health[4] <= 0 and self.health[5] <= 0:
            self.speed = 0.25
        elif self.health[4] <= 0 or self.health[5] <= 0 and not (self.health[4] <= 0 and self.health[5] <= 0):
            self.speed = 0.5

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

    def range(self, dude):
        return abs(numpy.sqrt(((self.pos[0]-dude.pos[0])**2)+((self.pos[1]-dude.pos[1])**2)))

    def shoot(self, dude, partind):
        # Basechance * (0.3 * Dex) - Range + Recoil control
        if isinstance(self.get_chance(dude), tuple):
            chance, dmg, spt, rpg_bool = self.get_chance(dude)
            dmg_done = 0
            dmg_done_list = [0, 0, 0, 0, 0, 0]
            if rpg_bool:
                if numpy.random.randint(0, 101) <= chance:
                    dude.get_damaged(dmg, partind, rpg_bool)
                    dmg_done_list = [dmg, dmg, dmg, dmg, dmg, dmg]
            else:
                for s in range(spt):
                    if numpy.random.randint(0, 101) <= chance:
                        dude.get_damaged(dmg, partind, rpg_bool)
                        dmg_done += dmg
                        dmg_done_list[partind] = dmg_done

            return dmg_done, dmg_done_list
        return "BUBBA HAT NEN NICES ASSHOLE"

    def get_chance(self, dude):
        if not dude.is_dead():
            if not isinstance(self.active_slot, Weapon):
                return "Bruh equip ne Waffe!"
            c_range = self.range(dude)
            dmg = self.calc_dmg(c_range)
            p_range = self.calc_p_range(c_range)
            spt = self.active_slot.spt
            rpg_bool = False

            if isinstance(self.active_slot, (Maschinenpistole, Sturmgewehr, Maschinengewehr)):
                recoil_acc = self.calc_recoil_acc()
                chance = int(self.active_slot.acc * (0.3 * self.dexterity) - p_range + recoil_acc - self.dist_moved)
            elif isinstance(self.active_slot, Raketenwerfer):
                chance = int(self.active_slot.acc * (0.3 * self.dexterity) - p_range - self.dist_moved)
                rpg_bool = True
            else:
                chance = int(self.active_slot.acc * (0.3 * self.dexterity) - p_range - self.dist_moved)
            
            return chance, dmg, spt, rpg_bool
        else:
            return "Bro, he dead yo!"

    def calc_recoil_acc(self):
        if isinstance(self.active_slot, Maschinenpistole):
            return int(self.strength / 5)
        if isinstance(self.active_slot, Sturmgewehr):
            return int(self.strength / 10)
        if isinstance(self.active_slot, Maschinengewehr):
            return int(self.strength / 4)

    def calc_dmg(self, c_range):
        if isinstance(self.active_slot, Pistole):
            if c_range >= 20:
                return self.active_slot.dmg - int((0.2*(c_range-20))+0.5)
            else:
                return self.active_slot.dmg
        if isinstance(self.active_slot, Maschinenpistole):
            if c_range >= 15:
                return self.active_slot.dmg - int((0.3*(c_range-15))+0.5)
            else:
                return self.active_slot.dmg
        if isinstance(self.active_slot, Sturmgewehr):
            if c_range >= 50:
                return self.active_slot.dmg - int((0.2*(c_range-50))+0.5)
            else:
                return self.active_slot.dmg
        if isinstance(self.active_slot, Shotgun):
            if c_range >= 10:
                return self.active_slot.dmg - int((1*(c_range-10))+0.5)
            else:
                return self.active_slot.dmg
        if isinstance(self.active_slot, Maschinengewehr):
            if c_range >= 40:
                return self.active_slot.dmg - int((0.3*(c_range-40))+0.5)
            else:
                return self.active_slot.dmg
        if isinstance(self.active_slot, Sniper):
            if c_range >= 100:
                return self.active_slot.dmg - int((0.2*(c_range-10))+0.5)
            else:
                return self.active_slot.dmg
        if isinstance(self.active_slot, Raketenwerfer):
            return self.active_slot.dmg

    def calc_p_range(self, c_range):
        if isinstance(self.active_slot, Pistole):
            if c_range > 20:
                return c_range-20
            else:
                return 0
        if isinstance(self.active_slot, Maschinenpistole):
            if c_range > 15:
                return c_range-15
            else:
                return 0
        if isinstance(self.active_slot, Sturmgewehr):
            if c_range > 50:
                return c_range-50
            else:
                return 0
        if isinstance(self.active_slot, Shotgun):
            if c_range > 10:
                return c_range-10
            else:
                return 0
        if isinstance(self.active_slot, Maschinengewehr):
            if c_range < 2:
                return 10
            if c_range > 40:
                return c_range-40
            else:
                return 0
        if isinstance(self.active_slot, Sniper):
            if c_range < 5:
                return c_range*10
            if c_range > 100:
                return c_range-100
            else:
                return 0
        if isinstance(self.active_slot, Raketenwerfer):
            if c_range > 20:
                return c_range - 20
            else:
                return 0

    def apply_damaged(self, dmg):
        for i in range(6):
            self.health[i] = dmg[i]

    def get_damaged(self, dmg, partind, rpg_bool):
        if rpg_bool:
            for i in range(6):
                self.health[i] -= 100
        else:
            if partind == 3:
                if self.gear and self.gear[0].durability > 0:
                    dmg *= self.gear[0].reduction
                    self.health[3] -= dmg
                    self.gear[0].durability -= 0
                    if self.gear[0].durability <= 0:
                        self.gear[0].durability = 0
                else:
                    self.health[3] -= dmg
            elif self.health[partind] > 0:
                self.health[partind] -= dmg
            if self.is_dead():
                self.dead()
            self.hitprint(dmg, partind)
            self.statchange()

    def status_timer(self):
        if self.burn_t > 0:
            self.burn_t -= 1

        if self.poison_t > 0:
            self.poison_t -= 1

        if self.blind_t > 0:
            self.blind_t -= 1

        if self.bleed_t[0] > 1 or self.bleed_t[1] > 1 or self.bleed_t[2] > 1 or self.bleed_t[3] > 1 \
                or self.bleed_t[4] > 1 or self.bleed_t[5] > 1:
            for x in self.bleed_t:
                if self.bleed_t[x] > 0:
                    self.bleed_t[x] -= 1

    def get_burn(self):
        self.burn = True
        self.burn_t = 10
        self.statusprint(0)

    def get_poison(self):
        self.poison = True
        self.poison_t = 10
        self.statusprint(1)

    def get_blind(self):
        self.blind = True
        self.blind_t = 10
        self.statusprint(3)

    def get_bleed(self, partind):
        if not self.bleed[partind]:
            self.bleed[partind] = True
            self.statusprint(2)

    def stand(self):
        self.height = 1

    def crouch(self):
        self.height = 0.5

    def laydown(self):
        self.height = 0.2

    def use_item(self, itemind, partind):
        if self.items[itemind].name == "Medkit":
            self.i_need_healing(self.items[itemind].value, partind)

    def i_need_healing(self, amount, partind):
        if self.health[partind] <= 0 and self.bleed[partind] is True:
            self.bleed[partind] = False
            print("Bleeding has stopped")
        elif self.health[partind] == 100:
            print("This part is full on health!")
            return
        elif self.health[partind] + amount >= 100:
            self.health[partind] = 100
        else:
            self.health[partind] += amount
        if self.bleed[partind]:
            self.bleed[partind] = False
            print("Bleeding has stopped")


def create_character(_id, team):  # team holds only name/number of team
    boi = Character(class_id=_id, team=team)
    boi.class_selector()
    return boi

if Debug:
    #boi = create_character(0, [0, 0])
    #boii = create_character(0, [0, 10])
    #boi.weapon_add(make_weapon_by_id(4))
    #boi.change_active_slot(["Weapon", 0])
    #boi.shoot(boii, 2)
    #print(boii.health[2])
    #print(boi.range(boii))

    #boi.add_item(Medkit())
    #boi.get_damaged(15, 2)
    #print(boi.health[2])
    #boi.use_item(0, 2)
    #print(boi.health[2])
    #print(boi.dexterity)
    #print(boi.strength)
    #print(50*2*35*0.18)
    #boi = Character()
    #boi2 = Character()
    #boi.get_damaged(150, 4)
    #boi.get_damaged(150, 5)
    #boi.get_damaged(150, 1)
    #boi.get_damaged(150, 2)
    #boi.i_need_healing(25, 1)
    #print(boi.health)
    #print(boi.speed)
    #print(boi.strength)
    #print(boi.dexterity)
    #boi.item_add(Armor(typ=3))
    #boi.item_add(Bandage())
    #boi.item_add(Defdope())
    #boi.item_add(Healstation())
    #boi.item_drop(2)
    #boi.item_change(Medkit(), 2)
    #print(boi.items)


    '''wep = Pistole()
    boi.weapon_add(wep)
    print(boi.weapons[0].name)
    boi.shoot(boi2, wep, 0)
    print(boi2.health[0])'''