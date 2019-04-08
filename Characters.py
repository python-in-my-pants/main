import Item
import Weapon

Debug = True


class Character:
    name = "default_character"
    Health = [100, 100, 100, 100, 100, 100]
    #          0    1    2    3    4    5
    #        kopf larm rarm Torso lbein rbein
    # armor = 0
    dexterity = 0
    strength = 0
    stamina = 1000
    speed = 1
    height = 1
    pos = [0, 0]
    bleed =[False, False, False, False, False, False]
    bleedt =[0, 0, 0, 0, 0, 0]
    #         siehe Health
    burning = False
    burnt = 0
    poison= False
    poisont = 0
    blind = False
    blindt = 0
    items = []
    weapons = []
    #TODO Gear variable

    def get_drawable(self):
        pass

    def __init__(self, name="default_character", health=[100, 100, 100, 100, 100, 100,], armor=0, dexterity=25, strength=15,
                 stamina=1000, speed=1, height=1, pos=[0, 0], bleed=[False, False, False, False, False, False], bleedt=[0, 0, 0, 0, 0, 0],
                 burn=False, burnt=0, poison=False, poisont=0, blind=False, blindt=0, items=[], weapons=[]):
        self.name = name
        self.health = health
        self.dexterity = dexterity
        self.strength = strength
        self.armor = armor
        self.stamina = stamina
        self.speed = speed
        self.height = height
        self.pos = pos
        self.bleed = bleed
        self.bleedt = bleedt
        self.burn = burn
        self.burnt = burnt
        self.poison = poison
        self.poisont = poisont
        self.blind = blind
        self.blindt = blindt
        self.items = items
        self.weapons = weapons

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

    def shoot(self, dude, weapon, partind):
        dude.get_damaged(weapon.dmg, partind)

    def get_damaged(self, dmg, partind):
        if partind == 3:
            if self.armor > 0:
                if self.armor < dmg:
                    self.armor -= dmg
                    if self.armor < 0:
                        self.health[3] -= abs(self.armor)
                        self.armor = 0
                else:
                    self.armor -= dmg
        elif self.health[partind] > 0:
            self.health[partind] -= dmg
        if self.health[0] <= 0 or self.health[3] <= 0:
            self.dead()
        self.hitprint(dmg, partind)
        self.get_bleed(partind)
        self.statchange()

    def status_timer(self):
        if self.burnt > 0:
            self.burnt -= 1

        if self.poisont > 0:
            self.poisont -= 1

        if self.blindt > 0:
            self.blindt -= 1

        if self.bleedt[0] > 1 or self.bleedt[1] > 1 or self.bleedt[2] > 1 or self.bleedt[3] > 1 or self.bleedt[4] > 1 or \
                self.bleedt[5] > 1:
            for x in self.bleedt:
                if self.bleedt[x] > 0:
                    self.bleedt[x] -= 1

    def get_burn(self):
        self.burn = True
        self.burnt = 10
        self.statusprint(0)

    def get_poison(self):
        self.poison = True
        self.poisont = 10
        self.statusprint(1)

    def get_blind(self):
        self.blind = True
        self.blindt = 10
        self.statusprint(3)

    def get_bleed(self, partind):
        if not self.bleed[partind]:
            self.bleed[partind] = True
            self.statusprint(2)

    def change_stance(self, modifier):
        #0 stehend 1 hocke 2 liegen
        if modifier == 0:
            self.height = 1
        if modifier == 1:
            self.height = 0.5
        if modifier == 2:
            self.height = 0.2

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

if Debug:
    boi = Character()
    boi2 = Character()
    #Character.get_damaged(boi, 150, 4)
    #Character.get_damaged(boi, 150, 5)
    #Character.get_damaged(boi, 150, 1)
    #Character.get_damaged(boi, 150, 2)
    #Character.i_need_healing(boi, 25, 1)
    #print(boi.health)
    #print(boi.speed)
    #print(boi.strength)
    #print(boi.dexterity)
    boi.item_add(Item.Armor1())
    boi.item_add(Item.Bandage())
    boi.item_add(Item.Defdope())
    boi.item_add(Item.Healstation())
    boi.item_drop(2)
    boi.item_change(Item.Medkit(), 2)
    print(boi.items)



    '''wep = Weapon.Pistole()
    boi.weapon_add(wep)
    print(boi.weapons[0].name)
    boi.shoot(boi2, wep, 0)
    print(boi2.health[0])'''









