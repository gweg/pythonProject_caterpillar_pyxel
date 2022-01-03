import pyxel
import random
import subprocess
import pygame  # to play map3 only

pygame.mixer.init(22050)
sound_apple_crunch = pygame.mixer.Sound("assets//BitePotato.mp3")


class Things():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 0, self.width, self.height)


class Directions():
    north = 1
    east = 2
    south = 3
    west = 4
    none = 0


class Case_Code():
    wall = 10
    background = 12
    apple = 15
    virus = 20


class Case():
    xpos = 0
    ypos = 0
    code = 0
    last_xpos = 0
    last_ypos = 0


class RingType():
    head = 1
    sadHead = 2
    opennedMouthHead = 3
    ring = 4
    tail = 5


class Ring():
    xpos = 0
    ypos = 0

    ringType = None


class Caterpillar():

    def __init__(self, x, y, rings_nb):
        """ constructor take x y in case witdh n height"""

        self.rings = []
        self.size = rings_nb
        self.direction = Directions.south
        self.growing = False

        self.timeToDie = -1
        self.alive = True  # to start dead timer
        self.dead = False  # to go to game over
        self.death_delay = 0  #

        # creation de la tête de la chenille ( qui est un anneau de type tete de  chenille )

        ring = Ring()  # on cree un nouvel anneau
        ring.xpos = x  # on affacter au nouvel anneau les positions x et y transmisent lors de l'instanciation de la classe Caterpillar
        ring.ypos = y
        ring.ringType = RingType.head  # on definit cet anneau comme anneau de type tête
        self.rings.append(ring)  # on ajout ce nouveal anneau à la liste de anneau de la chenille

    def death(self):

        if self.alive == False:
            if self.death_delay == 0:
                self.death_delay = 5
                if len(self.rings) < 2:
                    self.dead = True
                else:
                    self.rings = self.rings[:-1]
            self.death_delay -= 1

    def update(self):


        # agrandissement de la chenille ? : si oui on ajoute un anneau de plus à la queue de la chenille
        if self.growing:
            self.size += 1  # augmentation du nombre d'anneau de la chenille
            ring = Ring()  # instanciation d' un anneau de la chenille. ou création d'un nouvel anneau à partir de la classe Ring
            self.rings.append(ring)  # on ajoute ce nouvel anneau tout frais à la liste des anneaux de la chenille.
            # self.rings[self.size].xpos=self.rings[self.size-1].xpos
            # self.rings[self.size].ypos=self.rings[self.size-1].ypos
            self.rings[self.size].ringType = RingType.ring

            self.growing = False  # on annule l'était d'agrandissement, car il vient d'être effectué.

        # gestion du déplacement de la chenille
        # si la chenille fait moins de 2 anneau (tête plus un anneau), on affecte les coordonnees de l'anneau à celle de la tête (avant que cette derniere ne bouge)
        if self.direction is not Directions.none:  # dans le cas d'une direction non nulle
            if self.size < 2:
                self.rings[1].xpos = self.rings[0].xpos
                self.rings[1].ypos = self.rings[0].ypos
                pass
            else:  # si la chenille est d'une taille supérieur à 2 anneaux, alors on applique un algorithme de décallage de position sur l'ensemble des anneaux
                for i in range(self.size, 0, -1):
                    self.rings[i].xpos = self.rings[i - 1].xpos
                    self.rings[i].ypos = self.rings[i - 1].ypos

        # déplacement de la tête . la tête se trouve en début de chenille, donc toujouts à la postition de l'anneau zéro
        if self.direction == Directions.south:
            self.rings[0].ypos += 1
            self.rings[0].xpos += 0
        if self.direction == Directions.north:
            self.rings[0].ypos -= 1
            self.rings[0].xpos += 0
        if self.direction == Directions.west:
            self.rings[0].ypos += 0
            self.rings[0].xpos += -1
        if self.direction == Directions.east:
            self.rings[0].ypos += 0
            self.rings[0].xpos += 1
        # la tête rencontre un élément:

        if self.alive == False:
            self.death()
    # caterpillar collision with himself ? (except with the head)
    def ringscollision(self,rings):
        for ring in rings:
            if (rings[0].xpos==ring.xpos and rings[0].ypos==ring.ypos and ring.ringType!=RingType.head):
                return True
        return False




    # collision detection between the caterpillar head and other element
    def HeadDetectElement(self, world_cases):
        # detection de la chenille qui va sur un élément environnant
        for case in world_cases:
            if case.xpos == self.rings[0].xpos and case.ypos == self.rings[0].ypos:
                # if we eat an apple
                if case.code == Case_Code.apple:
                    self.growing = True
                    case.code = Case_Code.background
                    # on ouvre la bouche
                    self.rings[0].ringType = RingType.opennedMouthHead
                    sound_apple_crunch.play()
                    return 10  # score point
                else:  # sinon la bouche est fermée
                    self.rings[0].ringType = RingType.head
                # collision with the wall
                if case.code == Case_Code.wall:  # dans le mur !
                    self.alive = False
                if self.ringscollision(self.rings):  # dans lui même !
                    self.alive = False
                # recontre un virus
                if case.code == Case_Code.virus:
                    self.alive = False
                # tete triste / sad head
                if self.alive == False:
                    self.rings[0].ringType = RingType.sadHead
                    self.timeToDie = 10
                    self.alive = False
                    return 0
        return 0
        # detection de la chenille qui se mange son propre corps... ^^
        for ring in self.rings:
            if ring.xpos == self.rings[0].xpos and ring.ypos == self.rings[0].ypos:
                if ring.ringType == RingType.ring:
                    self.alive = False
                    break


class World():
    def __init__(self, nbhorizontalcases, nbverticalcases, casessize):
        self.casessize = casessize
        self.cases = []
        self.nbHorizontalCases = nbhorizontalcases
        self.nbVerticalCases = nbverticalcases
        for y in range(0, self.nbVerticalCases):
            for x in range(0, self.nbHorizontalCases):
                case = Case()
                case.xpos = x
                case.ypos = y
                if x == 0 or x == self.nbHorizontalCases - 1:
                    case.code = Case_Code.wall
                    self.cases.append(case)
                elif y == 0 or y == self.nbVerticalCases - 1:
                    case.code = Case_Code.wall
                    self.cases.append(case)
                else:
                    case.code = Case_Code.background
                    self.cases.append(case)
    def get_apple_count(self):
        apple_count=0
        for case in self.cases:
            if case.code==Case_Code.apple:
                apple_count+=1
        return apple_count

    def elementsGenerate(self, case_code, rand_range):
        element_count=0
        # on parcours toutes les cases du décor.
        for case in self.cases:
            if case.code == Case_Code.background:
                if random.randint(1, rand_range) == 1:
                    case.code = case_code
                    element_count+=1
        return element_count

    def draw(self, caterpillar_rings):
        """ draw world """
        for case in self.cases:
            pyxel.blt(case.xpos * self.casessize, case.ypos * self.casessize, 0, 0, 48, self.casessize,
                          self.casessize)
            if case.code == Case_Code.wall:
                pyxel.blt(case.xpos * self.casessize, case.ypos * self.casessize, 0, 0, 32, self.casessize,
                          self.casessize,0)
            if case.code == Case_Code.apple:
                pyxel.blt(case.xpos * self.casessize, case.ypos * self.casessize, 0, 0, 16, self.casessize,
                          self.casessize,0)
            if case.code == Case_Code.virus:
                pyxel.blt(case.xpos * self.casessize, case.ypos * self.casessize, 0, 32, 48, self.casessize,
                          self.casessize,0)
        """ draw caterpillar"""
        for ring in caterpillar_rings:
            if ring.ringType == RingType.ring:
                pyxel.blt(ring.xpos * self.casessize, ring.ypos * self.casessize, 0, 0, 0, self.casessize,
                          self.casessize,0)
            if ring.ringType == RingType.head:
                pyxel.blt(ring.xpos * self.casessize, ring.ypos * self.casessize, 0, 16, 0, self.casessize,
                          self.casessize,0)
            if ring.ringType == RingType.sadHead:
                pyxel.blt(ring.xpos * self.casessize, ring.ypos * self.casessize, 0, 16, 16, self.casessize,
                          self.casessize,0)
            if ring.ringType == RingType.opennedMouthHead:
                pyxel.blt(ring.xpos * self.casessize, ring.ypos * self.casessize, 0, 32, 0, self.casessize,
                          self.casessize,0)


class CaterpillarApp():
    """ use as static object """
    caterpillar = None
    gameover = True


    def init_game(self):
        self.caterpillar = Caterpillar(int((255 / 16) / 2), int((255 / 16) / 2), 0)

        """ on calcul le nombre de cases à l'écran en fonction de la résolution de la fenetre du jeu """
        self.world = World(int(255 / 16), int(255 / 16), 16)

        self.world.elementsGenerate(Case_Code.apple, 10)
        self.world.elementsGenerate(Case_Code.virus, 30)

        # la chenille grandie dès le début du jeu afin d'avoir au moins une tête et un anneau de corps.
        self.caterpillar.growing = True
        self.apple_count=0

    def __init__(self):

        self.score = 0

        pyxel.init(255, 255, scale=2, caption="caterpillar", fps=60)
        pyxel.load("assets/my_resource.pyxres")
        self.things = Things(0, 0)

        self.ticForNextFrame = 10


        # création de la chenille avec au moins un anneau (la tête)

        self.init_game()

        pyxel.run(self.update, self.draw)

    def update(self):



        # gestion du clavier.
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.caterpillar.direction = Directions.east
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.caterpillar.direction = Directions.west
        if pyxel.btnp(pyxel.KEY_UP):
            self.caterpillar.direction = Directions.north
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.caterpillar.direction = Directions.south

        if pyxel.btnp(pyxel.KEY_SPACE):

            self.gameover = False


        if not self.gameover:

            # check if caterpillar is still alive
            if not self.caterpillar.alive:
                self.caterpillar.death()  # start deathing

            # if caterpillar is not still alive
            if self.caterpillar.alive == False:
                self.caterpillar.direction = Directions.none

            self.ticForNextFrame -= 1

            if self.ticForNextFrame == 0:
                self.caterpillar.update()

                self.ticForNextFrame = 10
                # head collision
                if self.caterpillar.alive:
                    self.score = self.score + self.caterpillar.HeadDetectElement(self.world.cases)

            if self.world.get_apple_count() == 0:
                self.gameover = True
                self.caterpillar.alive = False
                self.init_game()

            if self.caterpillar.dead:

                self.gameover=True
                self.caterpillar.alive=False
                self.init_game()
                #pyxel.quit()
                '''
            if self.caterpillar.dead==True:
                for i in range(1,100):
                    self.caterpillar.update()
                    self.draw()
                pyxel.quit()
            '''
        else:
            pass


    def draw(self):
        pyxel.cls(0)
        # pyxel.rect(10,10,50,50,11)

        # dessin de tous les éléménts du jeu : chenille + autres sujets + décor
        self.world.draw(self.caterpillar.rings)
        if self.gameover:
            pyxel.text(85, 30, "CATERPILLAR GAME!", 7)
            pyxel.text(80, 40, "PRESS A KEY TO START!", pyxel.frame_count % 16)
        else:


            pyxel.text(100, 4, "SCORE :" + str(self.score), 7)


CaterpillarApp()
