from tkinter import *
import random
from PIL import ImageTk, Image
from pathlib import Path
import time

class Game(Tk):
    def __init__(self):
        super().__init__()
        self.initInterface()
        self.initSystem()
    
    def initInterface(self):
        # Ecran de jeu séparé en 3 lignes (avec chacunes 3 colonnes) :
        top = Frame(self)
        mid = Frame(self)
        bot = Frame(self)
        top.grid(row=0, sticky=NSEW)
        mid.grid(row=1, sticky=NSEW)
        bot.grid(row=2, sticky=NSEW)

        # Configuration du poid des lignes
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=3)
        self.columnconfigure(0, weight=1)

        # Configuration du poid des colonnes de chaque lignes
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=15)
        top.columnconfigure(1, weight=50)
        top.columnconfigure(2, weight=35)
        mid.rowconfigure(0, weight=1)
        mid.columnconfigure(0, weight=10)
        mid.columnconfigure(1, weight=80)
        mid.columnconfigure(2, weight=10)
        bot.rowconfigure(0, weight=1)
        bot.columnconfigure(0, weight=30)
        bot.columnconfigure(1, weight=60)
        bot.columnconfigure(2, weight=10)

        # Création des éléments de l'écran
        self.pile = Pile(top, self)
        self.playersIcons = PlayersIcons(top, self)
        self.log = Log(top, self)
        self.arrowL = Arrows(mid, "L", self)
        self.train = Train(mid, self)
        self.arrowR = Arrows(mid, "R", self)
        self.manche = Manche(bot, self)
        self.cards = Cards(bot, self)
        self.draw = Draw(bot, self)
    
    def initSystem(self):
        self.ghost = Players(0, "ghost")
        self.belle = Players(1, "belle")
        self.cheyenne = Players(2, "cheyenne")
        self.tuco = Players(3, "tuco")
        self.django = Players(4, "django")
        self.doc = Players(5, "doc")
        self.marshal = Players(6, "marshal")
        self.playerlist = [self.ghost, self.belle, self.cheyenne, self.tuco, self.django, self.doc]
        random.shuffle(self.playerlist)
        self.currentPlayer = self.playerlist[0]
        self.bind("<Configure>", self.timedRefresh)
        self.bind("<space>", self.refresh)
        self.protocol("WM_DELETE_WINDOW", self.onExit)
        self.timer = time.time()+1
        # booléens du gameplay :
        self.wait = BooleanVar(value=False)
        self.choosingChar = True
        self.choosingCard = False
        self.choosingIA = False
        self.arrowMoveTrain = False
        self.arrowMovePlayer = False
        self.arrowMovePlayerUP = False
        self.arrowMoveMarshal = False
        self.confirmedMovePlayerUp = False
        self.targetingShoot = False
        self.targetingPunch = False
        self.skipAction = False
        self.action = False
        # buttons state :
        self.pileBS = False
        self.playersIconsBS = True
        self.arrowBS = False
        self.cardsBS = False
        self.drawBS = False
        self.initialPlayerPosition()
        #self.preparation()
        self.start()

    def refresh(self, nothing):
        if self.timer < time.time():
            self.pile.refresh()
            self.manche.refresh()
            self.playersIcons.refresh()
            self.cards.refresh()
            self.train.refresh()
            self.arrowL.refresh()
            self.arrowR.refresh()
            self.draw.refresh()
            self.timer = time.time()+0.1

    def timedRefresh(self, nothing):
        if self.timer < time.time():
            self.refresh(True)
            self.timer = time.time()+1

    def start(self):
        self.chooseCharacter() # On choisi le perso qu'on va joué
        for eachManche in range(5): # Chaque manche du jeu, 5 en tout
            self.preparation() # On prépare pour la manche suivante
            self.log.addLog(f"Manche N°{eachManche+1} | Event : {self.manche.isEvent}")
            #if self.manche.isEvent:
            #    self.log.addLog(f"Manche N°{eachManche} | Event : {self.manche.isEvent}") # Annonce du type de l'event
            self.log.addLog(f"Manche N°{eachManche+1} : Programmation")
            for eachTurn in range(self.manche.nmb): # Pour le nombre de carte a posé :
                self.log.addLog(f"Tour N°{eachTurn+1} | Type : {self.manche.manche[eachTurn]}")
                if self.manche.manche[eachTurn] == "inversed": # Si on a une manche spécial inversé, l'ordre des joueur s'inverse donc
                    self.playerlist.reverse()
                for player in self.playerlist: # Chaque joueur va mettre une carte
                    self.currentPlayer = player
                    if (self.manche.manche[eachTurn] == "hidden" or player.name == "ghost" and eachTurn == 0):
                        self.chooseCard(player, True) # Carte face caché si c'est la manche l'oblige (ou ghost au premier tour)
                    else:
                        self.chooseCard(player, False) # Carte normal sinon
                    if (self.manche.manche[eachTurn] == "double"):
                        self.chooseCard(player, False) # Mais il se peut qu'on doit posé 2 cartes a la suites
            self.log.addLog(f"Manche N°{eachManche+1} : Action")
            self.beginAction() # On commence le tour d'action
            if (self.manche.isEvent): # Si a la fin de la manche, un événement est la
                self.manche.event() # Le faire
            self.changePlayerOrder() # On change l'ordre du premier joueur

    def preparation(self):
        self.manche.preparation()
        self.cards.preparation()

    def chooseCard(self, player, hidden):
        if player.notIA:
            self.choosingCard = True
            self.cardsBS = True
            self.drawBS = True
        else:
            self.choosingIA = True
            self.pileBS = True
        self.refresh(True)
        self.wait_variable(self.wait)
        self.pile.switch(hidden)

    def beginAction(self):
        self.arrowMoveTrain = False
        self.action = True
        self.pile.actionStart()

    def changePlayerOrder(self):
        self.playerlist.append(self.playerlist.pop(0))

    def chooseCharacter(self):
        self.wait_variable(self.wait)
        self.wait.set(False)

    def initialPlayerPosition(self):
        for i in range(6):
            if i%2 == 0:
                self.playerlist[i].position = 0
                self.train.fullTrain[0].add("player", self.playerlist[i], False)
            elif i%2 == 1:
                self.playerlist[i].position = 1
                self.train.fullTrain[1].add("player", self.playerlist[i], False)
        self.marshal.position = 6
        self.train.fullTrain[6].add("player", self.marshal, False)

    def getPlayer(self, name):
        if name == "ghost":
            return self.ghost
        elif name == "belle":
            return self.belle
        elif name == "cheyenne":
            return self.cheyenne
        elif name == "tuco":
            return self.tuco
        elif name == "django":
            return self.django
        elif name == "doc":
            return self.doc

    def focusPlayer(self, player):
        if player.position == 0:
            self.train.current = [0, 1, 2]
            self.train.train = [self.train.fullTrain[0], self.train.fullTrain[1], self.train.fullTrain[2]]
        elif player.position == 6:
            self.train.current = [4, 5, 6]
            self.train.train = [self.train.fullTrain[4], self.train.fullTrain[5], self.train.fullTrain[6]]
        else:
            self.train.current = [player.position-1, player.position, player.position+1]
            self.train.train = [self.train.fullTrain[player.position-1], self.train.fullTrain[player.position], self.train.fullTrain[player.position+1]]

    def onExit(self):
        self.destroy()
        self.wait.set(True)
        exit(0)


class Pile():
    def __init__(self, screen, game):
        self.frame = Frame(screen, width=180, height=180)
        self.frame.grid(row=0, column=0, padx=10, pady=2)
        self.path = Path("Assets/Cards")
        self.mainGame = game
        self.firstTimeRefresh = False

        self.pile = []
        self.hidden = False

    def refresh(self):
        if (self.hidden and not self.mainGame.action) or self.pile == []:
            if (self.firstTimeRefresh):
                self.frontCard.pack_forget()
            else:
                self.firstTimeRefresh = True
            self.imgS = Image.open(self.path / "card_back.png")
            self.imgS.thumbnail((int(self.mainGame.winfo_width()/6), int(self.mainGame.winfo_height()/3)), Image.Resampling.LANCZOS)
            self.img = ImageTk.PhotoImage(self.imgS)
            self.frontCard = Button(self.frame, image=self.img, width=self.img.width(), height=self.img.height(), command=self.click)
            self.frontCard.pack(expand=True)
        else:
            if (self.firstTimeRefresh):
                self.frontCard.pack_forget()
            else:
                self.firstTimeRefresh = True
            self.imgS = Image.open(self.path / f"{self.pile[-1][0]}_{self.pile[-1][1]}.png")
            self.imgS.thumbnail((int(self.mainGame.winfo_width()/6), int(self.mainGame.winfo_height()/3)), Image.Resampling.LANCZOS)
            self.img = ImageTk.PhotoImage(self.imgS)
            self.frontCard = Button(self.frame, image=self.img, width=self.img.width(), height=self.img.height(), command=self.click)
            self.frontCard.pack(expand=True)
        if self.mainGame.pileBS == True:
            self.frontCard.config(state=NORMAL)
        else:
            self.frontCard.config(state=DISABLED)

    def click(self):
        if self.mainGame.choosingIA:
            self.mainGame.cards.chooseRandom()
            self.mainGame.choosingIA = False
            self.mainGame.pileBS = False
            self.mainGame.wait.set(True)

    def switch(self, state):
        self.hidden = state

    def addCard(self, card):
        self.pile.append(card)

    def actionStart(self):
        while self.pile != []:
            self.mainGame.choosingChar = False
            self.mainGame.choosingCard = False
            self.mainGame.choosingIA = False
            self.mainGame.arrowMoveTrain = False
            self.mainGame.arrowMovePlayer = False
            self.mainGame.arrowMovePlayerUP = False
            self.mainGame.arrowMoveMarshal = False
            self.mainGame.confirmedMovePlayerUp = False
            self.mainGame.targetingShoot = False
            self.mainGame.targetingPunch = False
            self.mainGame.skipAction = False
            self.mainGame.action = False
            self.mainGame.pileBS = False
            self.mainGame.playersIconsBS = False
            self.mainGame.arrowBS = False
            self.mainGame.cardsBS = False
            self.mainGame.drawBS = False
            self.action(self.pile.pop(0))

    def action(self, card):
        self.cPlayer = self.mainGame.getPlayer(card[0])
        if card[1] == "move":
            if self.cPlayer.notIA:
                if self.cPlayer.up:
                    self.mainGame.arrowMovePlayerUP = True
                else:
                    self.mainGame.arrowMovePlayer = True
                self.mainGame.arrowBS = True
                self.mainGame.drawBS = True
                self.mainGame.focusPlayer(self.cPlayer)
                self.mainGame.refresh(True)
                self.mainGame.wait_variable(self.mainGame.wait)
                self.mainGame.wait.set(False)
                self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
            else:
                self.mainGame.skipAction = True
                self.mainGame.drawBS = True
                if self.cPlayer.up:
                    choice = random.choice([-3, -2, -2, -1, -1, -1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3])
                    while 0 <= self.cPlayer.position+choice >= 6:
                        choice = random.choice([-3, -2, -2, -1, -1, -1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3])
                    self.mainGame.train.move(self.cPlayer, choice)
                    self.mainGame.focusPlayer(self.cPlayer)
                    self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
                    self.mainGame.refresh(True)
                    self.mainGame.wait_variable(self.mainGame.wait)
                    self.mainGame.wait.set(False)
                else:
                    if self.cPlayer.position == 0:
                        self.mainGame.train.move(self.cPlayer, 1)
                    elif self.cPlayer.position == 6:
                        self.mainGame.train.move(self.cPlayer, -1)
                    else:
                        self.mainGame.train.move(self.cPlayer, random.choice([-1, -1, 1, 1, 1]))
                    self.mainGame.focusPlayer(self.cPlayer)
                    self.mainGame.wait_variable(self.mainGame.wait)
                    self.mainGame.wait.set(False)
        elif card[1] == "change":
            self.mainGame.skipAction = True
            self.mainGame.drawBS = True
            self.mainGame.train.climb(self.cPlayer)
            self.mainGame.focusPlayer(self.cPlayer)
            self.mainGame.refresh(True)
            self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
            self.mainGame.wait_variable(self.mainGame.wait)
            self.mainGame.wait.set(False)
        elif card[1] == "marshal":
            if self.cPlayer.notIA:
                self.mainGame.arrowBS = True
                self.mainGame.arrowMoveMarshal = True
                self.mainGame.focusPlayer(self.cPlayer)
                self.mainGame.refresh(True)
                self.mainGame.wait_variable(self.mainGame.wait)
                self.mainGame.wait.set(False)
                self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
            else:
                self.mainGame.skipAction = True
                self.mainGame.drawBS = True
                if self.mainGame.marshal.position == 0:
                    self.mainGame.train.move(self.mainGame.marshal, 1)
                elif self.mainGame.marshal.position == 6:
                    self.mainGame.train.move(self.mainGame.marshal, -1)
                else:
                    self.mainGame.train.move(self.mainGame.marshal, random.choice([-1, -1, 1]))
                self.mainGame.focusPlayer(self.cPlayer)
                self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
                self.mainGame.refresh(True)
                self.mainGame.wait_variable(self.mainGame.wait)
                self.mainGame.wait.set(False)
        elif card[1] == "shoot":
            if self.cPlayer.notIA:
                self.mainGame.targetingShoot = True
                self.mainGame.playersIconsBS = True
                self.mainGame.drawBS = True
                self.mainGame.refresh(True)
                self.mainGame.wait_variable(self.mainGame.wait)
                self.mainGame.wait.set(False)
                self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
            else:
                self.mainGame.skipAction = True
                self.mainGame.drawBS = True
                target_list = []
                target = None
                for player in self.mainGame.playerlist:
                    if player.position+1 == self.cPlayer.position or player.position-1 == self.cPlayer.position and player.up == self.cPlayer.up:
                        target_list.append(player)
                    if player.position == self.cPlayer.position and player.up != self.cPlayer.up and self.cPlayer.name == "tuco":
                        target_list.append(player)
                if target_list != []:
                    target = target_list.pop()
                    if target.name == "belle" and target_list != []:
                        target = target_list.pop()
                self.mainGame.train.shoot(self.cPlayer, target)
                self.mainGame.focusPlayer(self.cPlayer)
                self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
                self.mainGame.refresh(True)
                self.mainGame.wait_variable(self.mainGame.wait)
                self.mainGame.wait.set(False)
        elif card[1] == "steal":
            self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
            self.mainGame.skipAction = True
            self.mainGame.drawBS = True
            item = self.mainGame.train.steal(self.cPlayer.position, self.cPlayer.up)
            if item[0] != "nothing":
                self.cPlayer.items.append(item)
                self.cPlayer.money += item[1]
            self.mainGame.focusPlayer(self.cPlayer)
            self.mainGame.refresh(True)
            self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
            self.mainGame.wait_variable(self.mainGame.wait)
            self.mainGame.wait.set(False)
        elif card[1] == "punch":
            if self.cPlayer.notIA:
                self.mainGame.targetingShoot = True
                self.mainGame.playersIconsBS = True
                self.mainGame.drawBS = True
                self.mainGame.refresh(True)
                self.mainGame.wait_variable(self.mainGame.wait)
                self.mainGame.wait.set(False)
                self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
            else:
                self.mainGame.skipAction = True
                self.mainGame.drawBS = True
                target_list = []
                for player in self.mainGame.playerlist:
                    if player.position == self.cPlayer.position and player.up == self.cPlayer.up and player.name != self.cPlayer.name:
                        target_list.append(player)
                if target_list != []:
                    target = target_list.pop()
                    if target.name == "belle" and target_list != []:
                        target = target_list.pop()
                    if target.position == 1:
                        self.mainGame.train.punch(self.cPlayer, target, 1)
                    elif target.position == 6:
                        self.mainGame.train.punch(self.cPlayer, target, -1)
                    else:
                        self.mainGame.train.punch(self.cPlayer, target, random.choice([-1, 1]))
                self.mainGame.focusPlayer(self.cPlayer)
                self.mainGame.log.addLog(f"{self.cPlayer.name} : {card[1]}")
                self.mainGame.refresh(True)
                self.mainGame.wait_variable(self.mainGame.wait)
                self.mainGame.wait.set(False)

class PlayersIcons():
    def __init__(self, screen, game):
        self.frame = Frame(screen, width=600, height=180)
        self.frame.grid(row=0, column=1, padx=2, pady=2)
        self.path = Path("Assets/Icons")
        self.pathItems = Path("Assets/Items")
        self.mainGame = game
        self.firstTimeRefresh = False

    def refresh(self):
        if (self.firstTimeRefresh):
            for button in self.buttons:
                button.grid_forget()
        else:
            self.firstTimeRefresh = True
            self.itemsImg = [None]*3
            self.iImg = [None]*3
            self.items = [None]*3*6
            self.moneyLabel = [None]*6
            self.itemsImg[0] = Image.open(self.pathItems / "bag.png")
            self.itemsImg[0].thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/20)), Image.Resampling.LANCZOS)
            self.iImg[0] = ImageTk.PhotoImage(self.itemsImg[0])
            self.itemsImg[1] = Image.open(self.pathItems / "gem.png")
            self.itemsImg[1].thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/20)), Image.Resampling.LANCZOS)
            self.iImg[1] = ImageTk.PhotoImage(self.itemsImg[1])
            self.itemsImg[2] = Image.open(self.pathItems / "briefcase.png")
            self.itemsImg[2].thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/20)), Image.Resampling.LANCZOS)
            self.iImg[2] = ImageTk.PhotoImage(self.itemsImg[2])
            for i in range(6):
                self.items[0+i*3] = Label(self.frame, text="", image=self.iImg[0], compound=CENTER)
                self.items[0+i*3].grid(column=0+i*3, row=1)
                self.items[1+i*3] = Label(self.frame, text="", image=self.iImg[1], compound=CENTER)
                self.items[1+i*3].grid(column=1+i*3, row=1)
                self.items[2+i*3] = Label(self.frame, text="", image=self.iImg[2], compound=CENTER)
                self.items[2+i*3].grid(column=2+i*3, row=1)
                self.moneyLabel[i] = Label(self.frame, text="Money : 0")
                self.moneyLabel[i].grid(column=i*3, row=2, columnspan=3, pady=5)

        self.imgIcons = [None]*6
        self.icons = [None]*6
        self.buttons = [None]*6
        for i in range(6):
            self.imgIcons[i] = Image.open(self.path / f"{self.mainGame.playerlist[i].name}.png")
            self.imgIcons[i].thumbnail((int(self.mainGame.winfo_width()/6), int(self.mainGame.winfo_height()/6)), Image.Resampling.LANCZOS)
            self.icons[i] = ImageTk.PhotoImage(self.imgIcons[i])
            self.buttons[i] = Button(self.frame, image=self.icons[i], command=lambda player=self.mainGame.playerlist[i]: self.click(player))
            self.buttons[i].grid(column=i*3, row=0, padx=10, pady=10, columnspan=3)
            self.items[0+i*3].config(text=f"{self.mainGame.playerlist[i].howMany('bag')}")
            self.items[1+i*3].config(text=f"{self.mainGame.playerlist[i].howMany('gem')}")
            self.items[2+i*3].config(text=f"{self.mainGame.playerlist[i].howMany('briefcase')}")
            self.moneyLabel[i].config(text=f"Money : {self.mainGame.playerlist[i].money}")
            if self.mainGame.playersIconsBS == True:
                self.buttons[i].config(state=NORMAL)
            else:
                self.buttons[i].config(state=DISABLED)

    def click(self, player):
        if self.mainGame.choosingChar:
            player.notIA = True
            self.mainGame.log.addLog(f"Le joueur a choisi : {player.name}")
            self.mainGame.choosingChar = False
            self.mainGame.playersIconsBS = False
            self.mainGame.arrowBS = True
            self.mainGame.arrowMoveTrain = True
            self.refresh()
            self.mainGame.wait.set(True)
        elif self.mainGame.targetingShoot:
            target_list = []
            for p in self.mainGame.playerlist:
                if p.position+1 == self.mainGame.pile.cPlayer.position or p.position-1 == self.mainGame.pile.cPlayer.position and p.up == self.mainGame.pile.cPlayer.up:
                    target_list.append(p)
                if p.position == self.mainGame.pile.cPlayer.position and p.up != self.mainGame.pile.cPlayer.up and self.mainGame.pile.cPlayer.name == "tuco":
                    target_list.append(p)
            if player in target_list:
                if player.name == "belle" and len(target_list) >= 2:
                    target = target_list.pop()
                    if target.name == "belle":
                        target = target_list.pop()
                self.mainGame.train.shoot(self.mainGame.pile.cPlayer, player)
        elif self.mainGame.targetingPunch:
            target_list = []
            for p in self.mainGame.playerlist:
                if p.position == self.mainGame.pile.cPlayer.position and p.up == self.mainGame.pile.cPlayer.up and p.name != self.mainGame.pile.cPlayer.name:
                    target_list.append(p)
            if player in target_list:
                if player.name == "belle" and len(target_list) >= 2:
                    target = target_list.pop()
                    if target.name == "belle":
                        target = target_list.pop()
                if player.position == 1:
                    self.mainGame.train.punch(self.mainGame.pile.cPlayer, player, 1)
                elif player.position == 6:
                    self.mainGame.train.punch(self.mainGame.pile.cPlayer, player, -1)
                else:
                    self.mainGame.train.punch(self.mainGame.pile.cPlayer, player, random.choice([-1, 1]))

class Log():
    def __init__(self, screen, game):
        self.frame = Frame(screen, width=420, height=180)
        self.frame.grid(row=0, column=3, padx=2, pady=2)
        self.mainGame = game
        self.listbox = Listbox(self.frame, width=50, height=10)
        self.elements = []
        self.listbox.pack(expand=True)

    def addLog(self, message):
        self.elements = [message] + self.elements
        self.listbox.delete(0, END)
        for i in self.elements:
            self.listbox.insert('end', i)

class Train():
    def __init__(self, screen, game):
        self.frame = Frame(screen, width=960, height=240)
        self.frame.grid(row=0, column=1, padx=2, pady=2)
        self.pathTrain = Path("Assets/Train")
        self.pathPersos = Path("Assets/Persos")
        self.pathItems = Path("Assets/Items")
        self.mainGame = game
        self.firstTimeRefresh = False

        self.fullTrain = [None]*7
        self.train = [None, None, None]
        self.current = [0, 1, 2]
        for i in range(7):
            self.fullTrain[i] = Wagons()
            if i < 3:
                self.train[i] = self.fullTrain[i]

    def refresh(self):
        # Les items de chaque wagons :
        if (self.firstTimeRefresh):
            for wagon in self.up:
                wagon.grid_forget()
            for wagon in self.down:
                wagon.grid_forget()
        else:
            self.firstTimeRefresh = True
            self.itemsImg = [None]*18
            self.iImg = [None]*18
            self.itemsLabel = [None]*18
            self.down = [None]*3
            self.up = [None]*3
            for row in range(6):
                for colunm in range(3):
                    if row%3 == 0:
                        self.itemsImg[colunm+row*3] = Image.open(self.pathItems / "bag.png")
                        self.itemsImg[colunm+row*3].thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/20)), Image.Resampling.LANCZOS)
                        self.iImg[colunm+row*3] = ImageTk.PhotoImage(self.itemsImg[colunm+row*3])
                        if row <= 2:
                            self.itemsLabel[colunm+row*3] = Label(self.frame, text=f"{len(self.train[colunm].bagOut)}", image=self.iImg[colunm+row*3], compound=CENTER)
                        else:
                            self.itemsLabel[colunm+row*3] = Label(self.frame, text=f"{len(self.train[colunm].bagIn)}", image=self.iImg[colunm+row*3], compound=CENTER)
                        self.itemsLabel[colunm+row*3].grid(row=row, column=colunm*2+1)
                    if row%3 == 1:
                        self.itemsImg[colunm+row*3] = Image.open(self.pathItems / "gem.png")
                        self.itemsImg[colunm+row*3].thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/20)), Image.Resampling.LANCZOS)
                        self.iImg[colunm+row*3] = ImageTk.PhotoImage(self.itemsImg[colunm+row*3])
                        if row <= 2:
                            self.itemsLabel[colunm+row*3] = Label(self.frame, text=f"{self.train[colunm].gemOut}", image=self.iImg[colunm+row*3], compound=CENTER)
                        else:
                            self.itemsLabel[colunm+row*3] = Label(self.frame, text=f"{self.train[colunm].gemIn}", image=self.iImg[colunm+row*3], compound=CENTER)
                        self.itemsLabel[colunm+row*3].grid(row=row, column=colunm*2+1)
                    if row%3 == 2:
                        self.itemsImg[colunm+row*3] = Image.open(self.pathItems / "briefcase.png")
                        self.itemsImg[colunm+row*3].thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/20)), Image.Resampling.LANCZOS)
                        self.iImg[colunm+row*3] = ImageTk.PhotoImage(self.itemsImg[colunm+row*3])
                        if row <= 2:
                            self.itemsLabel[colunm+row*3] = Label(self.frame, text=f"{self.train[colunm].briefcaseOut}", image=self.iImg[colunm+row*3], compound=CENTER)
                        else:
                            self.itemsLabel[colunm+row*3] = Label(self.frame, text=f"{self.train[colunm].briefcaseIn}", image=self.iImg[colunm+row*3], compound=CENTER)
                        self.itemsLabel[colunm+row*3].grid(row=row, column=colunm*2+1)
        for row in range(6):
            for colunm in range(3):
                if row%3 == 0:
                    if row <= 2:
                        self.itemsLabel[colunm+row*3].config(text=f"{len(self.train[colunm].bagOut)}")
                    else:
                        self.itemsLabel[colunm+row*3].config(text=f"{len(self.train[colunm].bagIn)}")
                if row%3 == 1:
                    if row <= 2:
                        self.itemsLabel[colunm+row*3].config(text=f"{self.train[colunm].gemOut}")
                    else:
                        self.itemsLabel[colunm+row*3].config(text=f"{self.train[colunm].gemIn}")
                if row%3 == 2:
                    if row <= 2:
                        self.itemsLabel[colunm+row*3].config(text=f"{self.train[colunm].briefcaseOut}")
                    else:
                        self.itemsLabel[colunm+row*3].config(text=f"{self.train[colunm].briefcaseIn}")
        
        # Les wagons :
        self.playerImg = [None]*7
        self.pImg = [None]*7
        self.img = Image.open(self.pathTrain / "wagonBar.png")
        self.img.thumbnail((int(self.mainGame.winfo_width()/5), int(self.mainGame.winfo_height()/5)), Image.Resampling.LANCZOS)
        self.wagonImg = ImageTk.PhotoImage(self.img)
        incr = 0
        for wagon in self.train:
            self.down[incr] = Canvas(self.frame, width=int(self.mainGame.winfo_width()/5), height=int(self.mainGame.winfo_height()/5))
            self.down[incr].create_image(0, 0, image=self.wagonImg, anchor=NW)
            self.up[incr] = Canvas(self.frame, width=int(self.mainGame.winfo_width()/5), height=int(self.mainGame.winfo_height()/5))
            for player in wagon.peopleIn:
                self.playerImg[player.id] = Image.open(self.pathPersos / f"{player.name}.png")
                self.playerImg[player.id].thumbnail((int(self.mainGame.winfo_width()/10), int(self.mainGame.winfo_height()/5)), Image.Resampling.LANCZOS)
                self.pImg[player.id] = ImageTk.PhotoImage(self.playerImg[player.id])
                self.down[incr].create_image(20+player.id*30, 60, image=self.pImg[player.id])
                #self.down[incr].create_oval(15+player.id*40, 60, 25+player.id*40, 70) # position of each player
            for player in wagon.peopleOut:
                self.playerImg[player.id] = Image.open(self.pathPersos / f"{player.name}.png")
                self.playerImg[player.id].thumbnail((int(self.mainGame.winfo_width()/10), int(self.mainGame.winfo_height()/5)), Image.Resampling.LANCZOS)
                self.pImg[player.id] = ImageTk.PhotoImage(self.playerImg[player.id])
                self.up[incr].create_image(20+player.id*30, 60, image=self.pImg[player.id])
                #self.up[incr].create_oval(15+player.id*40, 60, 25+player.id*40, 70) # position of each player
            self.down[incr].grid(row=3, column=incr*2, rowspan=3)
            self.up[incr].grid(row=0, column=incr*2, rowspan=3)
            incr += 1

    def check(self, direction):
        if direction == -1:
            if self.current[0] == 0:
                return False
            else:
                return True
        elif direction == 1:
            if self.current[2] == 6:
                return False
            else:
                return True

    def move(self, player, direction):
        if (player.position == 0 and direction == -1):
            return 0
        if (player.position == 6 and direction == 1):
            return 0
        self.fullTrain[player.position].remove("player", player, player.up)
        player.position += direction
        self.fullTrain[player.position].add("player", player, player.up)

    def climb(self, player):
        self.fullTrain[player.position].remove("player", player, player.up)
        if (player.up):
            player.up = False
        else:
            player.up = True
        self.fullTrain[player.position].add("player", player, player.up)

    def steal(self, position, up):
        return self.fullTrain[position].getBestItem(up)

    def punch(self, player, target, direction):
        item = target.lostLoot()
        if item[0] != "nothing":
            player.money += item[1]
            if item[0] == "bag" and player.name == "cheyenne":
                player.items.append(item)
            else:
                self.fullTrain[player.position].add(item[0], item, player.up)
        if 0 <= target.position+direction <= 6:
            self.move(target, direction)

    def shoot(self, player, target):
        self.mainGame.cards.addToDeck(target, (player.name, "bullet"))
        player.nmbBullets -= 1
        if player.name == "django":
            if player.position < target.position:
                if 0 <= target.position+1 <= 6:
                    self.move(target, 1)
                elif 0 <= target.position-1 <= 6:
                    self.move(target, -1)

class Arrows():
    def __init__(self, screen, side, game):
        self.frame = Frame(screen, width=120, height=240)
        self.path = Path("Assets/Arrows")
        self.mainGame = game
        self.firstTimeRefresh = False
        self.side = side
        Arrows.playerDirectionLengh = 0

    def refresh(self):
        if (self.firstTimeRefresh):
            if self.side == "L":
                self.l.pack_forget()
            elif self.side == "R":
                self.r.pack_forget()
        else:
            self.firstTimeRefresh = True

        if self.side == "L":
            self.left=PhotoImage(file=self.path / "arrowLeft.png")
            self.left = self.left.subsample(4, 4)
            self.l=Button(self.frame, image=self.left, command=lambda direction=-1: self.click(direction))
            self.l.pack(expand=True)
            self.frame.grid(row=0, column=0, padx=2, pady=2)
            if self.mainGame.arrowBS == True and self.mainGame.train.current[0] != 0:
                self.l.config(state=NORMAL)
            else:
                self.l.config(state=DISABLED)
            if (self.mainGame.arrowMovePlayer or self.mainGame.arrowMovePlayerUP or self.mainGame.arrowMoveMarshal):
                if self.mainGame.arrowMoveMarshal and self.mainGame.marshal.position == 1:
                    self.l.config(state=NORMAL)
                if self.mainGame.pile.cPlayer.position == 1:
                    self.l.config(state=NORMAL)
        elif self.side == "R":
            self.right=PhotoImage(file=self.path / "arrowRight.png")
            self.right = self.right.subsample(4, 4)
            self.r=Button(self.frame, image=self.right, command=lambda direction=1: self.click(direction))
            self.r.pack(expand=True)
            self.frame.grid(row=0, column=2, padx=2, pady=2)
            if self.mainGame.arrowBS == True and self.mainGame.train.current[2] != 6:
                self.r.config(state=NORMAL)
            else:
                self.r.config(state=DISABLED)
            if (self.mainGame.arrowMovePlayer or self.mainGame.arrowMovePlayerUP or self.mainGame.arrowMoveMarshal):
                if self.mainGame.arrowMoveMarshal and self.mainGame.marshal.position == 5:
                    self.r.config(state=NORMAL)
                elif self.mainGame.pile.cPlayer.position == 5:
                    self.r.config(state=NORMAL)

    def click(self, direction):
        if self.mainGame.arrowMoveTrain:
            self.move(direction)
        elif self.mainGame.arrowMovePlayer:
            self.mainGame.train.move(self.mainGame.pile.cPlayer, direction)
            self.mainGame.wait.set(True)
        elif self.mainGame.arrowMovePlayerUP:
            if -3 <= Arrows.playerDirectionLengh+direction <= 3:
                Arrows.playerDirectionLengh += direction
                self.mainGame.train.move(self.mainGame.pile.cPlayer, direction)
        elif self.mainGame.arrowMoveMarshal:
            self.mainGame.train.move(self.mainGame.marshal, direction)
            self.mainGame.wait.set(True)

    def move(self, direction):
        old = self.mainGame.train.current
        self.mainGame.train.current = [old[0]+direction, old[1]+direction, old[2]+direction]
        self.mainGame.train.train = [self.mainGame.train.fullTrain[old[0]+direction], self.mainGame.train.fullTrain[old[1]+direction], self.mainGame.train.fullTrain[old[2]+direction]]
        self.mainGame.train.refresh()
        self.refresh()
        
class Manche():
    def __init__(self, screen, game):
        self.frame = Frame(screen, width=360, height=180)
        self.frame.grid(row=0, column=0, padx=2, pady=2)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)
        self.frame.columnconfigure(4, weight=1)
        self.path = Path("Assets/Manche")
        self.mainGame = game
        self.firstTimeRefresh = False

        self.type = ["normal", "hidden", "double", "inversed"]
        self.manche = []
        self.isEvent = False
        self.nmb = 5
        self.mancheNmb = 0
        self.text = f"Manche N°{self.mancheNmb}"

    def refresh(self):
        if self.manche != []:
            self.label = Label(self.frame, text=self.text)
            self.label.grid(row=0, column=0, columnspan=2)
            self.imgS1 = Image.open(self.path / f"{self.manche[0]}.png")
            self.imgS1.thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/10)), Image.Resampling.LANCZOS)
            self.img1 = ImageTk.PhotoImage(self.imgS1)
            self.imgS2 = Image.open(self.path / f"{self.manche[1]}.png")
            self.imgS2.thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/10)), Image.Resampling.LANCZOS)
            self.img2 = ImageTk.PhotoImage(self.imgS2)
            self.imgS3 = Image.open(self.path / f"{self.manche[2]}.png")
            self.imgS3.thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/10)), Image.Resampling.LANCZOS)
            self.img3 = ImageTk.PhotoImage(self.imgS3)
            self.imgS4 = Image.open(self.path / f"{self.manche[3]}.png")
            self.imgS4.thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/10)), Image.Resampling.LANCZOS)
            self.img4 = ImageTk.PhotoImage(self.imgS4)
            self.m1 = Label(self.frame, image=self.img1)
            self.m1.grid(row=1, column=0)
            self.m2 = Label(self.frame, image=self.img2)
            self.m2.grid(row=1, column=1)
            self.m3 = Label(self.frame, image=self.img3)
            self.m3.grid(row=1, column=2)
            self.m4 = Label(self.frame, image=self.img4)
            self.m4.grid(row=1, column=3)
            if self.nmb == 5:
                self.imgS5 = Image.open(self.path / f"{self.manche[4]}.png")
                self.imgS5.thumbnail((int(self.mainGame.winfo_width()/20), int(self.mainGame.winfo_height()/10)), Image.Resampling.LANCZOS)
                self.img5 = ImageTk.PhotoImage(self.imgS5)
                self.m5 = Label(self.frame, image=self.img5)
                self.m5.grid(row=1, column=4)

    def makeRandom(self):
        self.nmb = random.randint(4, 5)
        for i in range(self.nmb):
            rand = random.randint(1, 100)
            if 0 < rand <= 45:
                self.manche.append(self.type[0])
            elif 45 < rand <= 70:
                self.manche.append(self.type[1])
            elif 70 < rand <= 90:
                self.manche.append(self.type[2])
            elif 90 < rand <= 100:
                self.manche.append(self.type[3])
        self.isEvent = random.choice([False, False])

    def event(self):
        event = random.choice(["marshalRage", "passagersRage", "endOfRoof", "brake", "briefcase+", "steal", "marshalMad", "driverHostage"])
        if event == "marshalRage":
            pass
        elif event == "passagersRage":
            pass
        elif event == "endOfRoof":
            pass
        elif event == "brake":
            pass
        elif event == "briefcase+":
            pass
        elif event == "steal":
            pass
        elif event == "marshalMad":
            pass
        elif event == "driverHostage":
            pass

    def clear(self):
        self.manche = []
        self.isEvent = False
        self.nmb = 0
        self.mancheNmb += 1
        self.text = f"Manche N°{self.mancheNmb}"

    def preparation(self):
        self.clear()
        self.makeRandom()

class Cards():
    def __init__(self, screen, game):
        self.frame = Frame(screen, width=720, height=180)
        self.frame.grid(row=0, column=1, padx=2, pady=2)
        self.path = Path("Assets/Cards")
        self.mainGame = game
        self.firstTimeRefresh = False

    def refresh(self):
        if (self.firstTimeRefresh):
            for button in self.buttons:
                button.grid_forget()
        else:
            self.firstTimeRefresh = True
        self.imgCards = [None]*len(self.mainGame.currentPlayer.hand)
        self.cards = [None]*len(self.mainGame.currentPlayer.hand)
        self.buttons = [None]*len(self.mainGame.currentPlayer.hand)
        for i in range(len(self.mainGame.currentPlayer.hand)):
            self.imgCards[i] = Image.open(self.path / f"{self.mainGame.currentPlayer.hand[i][0]}_{self.mainGame.currentPlayer.hand[i][1]}.png")
            self.imgCards[i].thumbnail((int(self.mainGame.winfo_width()/10), int(self.mainGame.winfo_height()/5)), Image.Resampling.LANCZOS)
            self.cards[i] = ImageTk.PhotoImage(self.imgCards[i])
            self.buttons[i] = Button(self.frame, image=self.cards[i], command=lambda card=self.mainGame.currentPlayer.hand[i]: self.click(card))
            self.buttons[i].grid(column=i, row=0)
            if self.mainGame.cardsBS == True and self.mainGame.currentPlayer.hand[i][1] != "bullet":
                self.buttons[i].config(state=NORMAL)
            else:
                self.buttons[i].config(state=DISABLED)

    def click(self, card):
        if self.mainGame.choosingCard:
            self.removeFromHand(self.mainGame.currentPlayer, card)
            self.mainGame.choosingCard = False
            self.mainGame.cardsBS = False
            self.mainGame.drawBS = False
            self.mainGame.wait.set(True)

    def addToDeck(self, player, card):
        player.deck.append(card)

    def removeFromHand(self, player, card):
        player.hand.pop(player.hand.index(card))
        self.mainGame.log.addLog(f"{player.name} : met une carte")
        self.mainGame.pile.addCard(card)

    def chooseRandom(self):
        if random.randint(0, self.nmbUsableCard()) == 0:
            self.drawCards(self.mainGame.currentPlayer)
        else:
            cardUsed = self.mainGame.currentPlayer.hand.pop(random.randint(0, len(self.mainGame.currentPlayer.hand)-1))
            while cardUsed[1] == "bullet":
                cardUsed = self.mainGame.currentPlayer.hand.pop(random.randint(0, len(self.mainGame.currentPlayer.hand)-1))
            self.mainGame.log.addLog(f"{self.mainGame.currentPlayer.name} : met une carte")
            self.mainGame.pile.addCard(cardUsed)

    def nmbUsableCard(self):
        incr = 0
        for card in self.mainGame.currentPlayer.hand:
            if card[1] != "bullet":
                incr += 1
        return incr

    def clean(self):
        for player in self.game.playerlist:
            player.deck += player.hand
            player.hand = []

    def giveOne(self, player):
        card = player.deck.pop(random.randint(0, len(player.deck)-1))
        player.hand.append(card)

    def giveRandomHand(self, player):
        for i in range(6):
            self.giveOne(player)
        if player.name == "doc":
            self.giveOne(player)

    def drawCards(self, player):
        if len(player.deck) >= 3:
            self.mainGame.log.addLog(f"{player.name} : pioche 3 cartes")
            self.giveOne(player)
            self.giveOne(player)
            self.giveOne(player)
        elif len(player.deck) >= 2:
            self.mainGame.log.addLog(f"{player.name} : pioche 2 cartes")
            self.giveOne(player)
            self.giveOne(player)
        elif len(player.deck) >= 1:
            self.mainGame.log.addLog(f"{player.name} : pioche 1 carte")
            self.giveOne(player)
        else:
            self.mainGame.log.addLog(f"{player.name} : pioche 0 carte (0 carte restante dans le deck)")

    def preparation(self):
        for player in self.mainGame.playerlist:
            self.giveRandomHand(player)

class Draw():
    def __init__(self, screen, game):
        self.frame = Frame(screen, width=120, height=180)
        self.frame.grid(row=0, column=2, padx=2, pady=2)
        self.mainGame = game
        self.path = Path("Assets/Autre")
        self.firstTimeRefresh = False

    def refresh(self):
        if (self.firstTimeRefresh):
            self.btnDrawCards.pack_forget()
        else:
            self.firstTimeRefresh = True
        self.logo=PhotoImage(file= self.path / "draw.png")
        self.logo = self.logo.subsample(10, 10)
        self.btnDrawCards = Button(self.frame, image=self.logo, command=self.click)
        self.btnDrawCards.pack(expand=True)
        if self.mainGame.drawBS == True:
            self.btnDrawCards.config(state=NORMAL)
        else:
            self.btnDrawCards.config(state=DISABLED)

    def click(self):
        if self.mainGame.choosingCard:
            self.mainGame.cards.drawCards(self.mainGame.currentPlayer)
            self.mainGame.choosingCard = False
            self.mainGame.cardsBS = False
            self.mainGame.drawBS = False
            self.mainGame.wait.set(True)
        elif self.mainGame.skipAction:
            self.mainGame.wait.set(True)
        elif self.mainGame.confirmedMovePlayerUp:
            if Arrows.playerDirectionLengh != 0:
                self.mainGame.wait.set(True)
        elif self.mainGame.targetingShoot:
            target_list = []
            for p in self.mainGame.playerlist:
                if p.position+1 == self.mainGame.pile.cPlayer.position or p.position-1 == self.mainGame.pile.cPlayer.position and p.up == self.mainGame.pile.cPlayer.up:
                    target_list.append(p)
                if p.position == self.mainGame.pile.cPlayer.position and p.up != self.mainGame.pile.cPlayer.up and self.mainGame.pile.cPlayer.name == "tuco":
                    target_list.append(p)
            if target_list == []:
                self.mainGame.wait.set(True)
        elif self.mainGame.targetingPunch:
            target_list = []
            for p in self.mainGame.playerlist:
                if p.position == self.mainGame.pile.cPlayer.position and p.up == self.mainGame.pile.cPlayer.up and p.name != self.mainGame.pile.cPlayer.name:
                    target_list.append(p)
            if target_list == []:
                self.mainGame.wait.set(True)

class Players():
    def __init__(self, id, name):
        self.name = name
        self.money = 250
        self.items = [("bag", 250)]
        self.deck = [(f"{name}", "move"), (f"{name}", "move"), (f"{name}", "change"), (f"{name}", "change"), (f"{name}", "shoot"), (f"{name}", "shoot"), (f"{name}", "steal"), (f"{name}", "steal"), (f"{name}", "punch"), (f"{name}", "marshal")]
        self.hand = []
        self.nmbBullets = 6
        self.notIA = False
        self.position = 0
        self.up = False
        self.id = id

    def howMany(self, type):
        incr = 0
        for item in self.items:
            if item[0] == type:
                incr += 1
        return incr

    def lostLoot(self):
        max = 0
        lost = ("nothing", 0)
        for item in self.items:
            if item[1] > max:
                lost = item
        self.money -= max
        return self.items.pop(self.items.index(item))

class Wagons():
    def __init__(self):
        self.peopleIn = []
        self.peopleOut = []
        self.bagIn = []
        self.bagOut = []
        self.gemIn = 0
        self.gemOut = 0
        self.briefcaseIn = 0
        self.briefcaseOut = 0
        self.initLoot()

    def initLoot(self):
        for i in range(random.randint(0, 2)+1):
            self.bagIn.append(("bag", random.choice([250, 500])))
        self.gemIn = random.randint(0, 1)
        self.briefcaseIn = random.randint(0, 1)

    def add(self, type, objet, up):
        if type == "bag":
            if up:
                self.bagOut.append(objet)
            else:
                self.bagIn.append(objet)
        elif type == "gem":
            if up:
                self.gemOut += 1
            else:
                self.gemIn += 1
        elif type == "briefcase":
            if up:
                self.briefcaseOut += 1
            else:
                self.briefcaseIn += 1
        elif type == "player":
            if up:
                self.peopleOut.append(objet)
            else:
                self.peopleIn.append(objet)
        else:
            assert False, "Error in adding component in Wagon"

    def remove(self, type, objet, up):
        if type == "bag":
            if up:
                self.bagOut.remove(objet)
            else:
                self.bagIn.remove(objet)
        elif type == "gem":
            if up:
                self.gemOut -= 1
            else:
                self.gemIn -= 1
        elif type == "briefcase":
            if up:
                self.briefcaseOut -= 1
            else:
                self.briefcaseIn -= 1
        elif type == "player":
            if up:
                self.peopleOut.remove(objet)
            else:
                self.peopleIn.remove(objet)
        else:
            assert False, "Error in adding component in Wagon"

    def getBestItem(self, up):
        if up:
            if self.briefcaseOut > 0:
                self.briefcaseOut -= 1
                return ("briefcase", 1000)
            elif self.gemOut > 0:
                self.gemOut -= 1
                return ("gem", 500)
            elif len(self.bagOut) > 0:
                return self.bagOut.pop()
            else:
                return ("nothing", 0)
        else:
            if self.briefcaseIn > 0:
                self.briefcaseIn -= 1
                return ("briefcase", 1000)
            elif self.gemIn > 0:
                self.gemIn -= 1
                return ("gem", 500)
            elif len(self.bagIn) > 0:
                return self.bagIn.pop()
            else:
                return ("nothing", 0)





def main():
    coltExpress = Game()
    coltExpress.mainloop()

if __name__ == "__main__":
    main()