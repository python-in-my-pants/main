
class Character:
    name = "Tom"
    Health = [100, 100, 100, 100, 100, 100]
    #          0    1    2    3    4    5
    #        kopf larm rarm Torso lbein rbein
    # armor = 0
    dexterity = 0
    strength = 0
    stamina = 1000
    speed = 1
    height = 1
    pos = [25, 10]
    status =[False, False, False, False]
    #           0     1      2      3
    #        Brennt Toxin  Bleed  Blinded

    def get_drawable(self):
        pass

    def __init__(self, name = "Tom", health = [100, 100, 100, 100, 100, 100,], armor = 0, dexterity = 25, strength = 15,
                 stamina = 1000, speed = 1, height = 1, pos = [25, 10], status =[False, False, False, False]):
        self.name = name
        self.health = health
        self.dexterity = dexterity
        self.strength = strength
        self.armor = armor
        self.stamina = stamina
        self.speed = speed
        self.height = height
        self.pos = pos
        self.status = status

    def dead(self):
        print(self.name + " you are dead!\n Kopf: " + str(self.health[0]) + "\n Linker Arm: " + str(self.health[1]) +
              "\n Rechter Arm: " + str(self.health[2]) + "\n Torso: " + str(self.health[3]) + "\n Linkes Bein: "
              + str(self.health[4]) + "\n Rechtes Bein: " + str(self.health[5]))

    def statcheck(self):
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

    def statusprint(self, statind):
            switcher = {
                0: "You are burning!",
                1: "You got poisoned!",
                2: "You are bleeding!",
                3: "You got blinded!"
            }
            print(switcher[statind])

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
        self.get_status(2)
        self.statcheck()

    def get_status(self,statind):
        if not self.status[statind]:
            self.status[statind] = True
            self.statusprint(statind)
        else:
            pass


boi = Character()
#Character.get_damaged(boi, 150, 4)
#Character.get_damaged(boi, 150, 5)
Character.get_damaged(boi, 150, 1)
Character.get_damaged(boi, 150, 2)
Character.get_status(boi, 3)
print(boi.health)
print(boi.speed)
print(boi.strength)
print(boi.dexterity)



