from PyQt5.QtWidgets import QWidget, qApp
from PyQt5.QtCore import QTimer, Qt, QEvent
from PyQt5.QtGui import QPainter, QPixmap

import xml.dom.minidom as xml
import numpy as np

from src import constants as consts
from src import board
from src.game_timer import GameTimer

# noinspection PyArgumentList


class Game(QWidget):
    """Klasa obsługująca mechanikę gry"""

    def __init__(self, replay=False):
        """Domyślne ustawienia klasy

            Args:
                players (int): Ilość wszystkich graczy

        """
        super(Game, self).__init__()
        qApp.installEventFilter(self)
        self.released = True

        self.nr_frame = 0
        if replay:
            doc = xml.parse("autosave.xml")
            self.frames = doc.getElementsByTagName("frame")
            return

        self.frames = []
        self.frame = np.ones(
            (consts.BOARD_WIDTH, consts.BOARD_HEIGHT), dtype=int)
        self.doc = xml.Document()
        self.root = self.doc.createElement('save')

    def start(self, bots):
        self.bots = bots
        self.board = board.Board(bots)
        self.timers = set()

        self.repaintTimer = QTimer(self)
        self.repaintTimer.setInterval(consts.GAME_SPEED)
        self.repaintTimer.timeout.connect(self.repaint)
        self.repaintTimer.start()

        self.botTimer = QTimer(self)
        self.botTimer.setInterval(consts.BOT_SPEED)
        self.botTimer.timeout.connect(lambda: self.board.do_bot_actions(self))
        self.botTimer.start()

    def paintEvent(self, event):
        """Obsługa rysowania na ekranie"""
        painter = QPainter()
        painter.begin(self)
        self.draw_board(painter)
        painter.end()

    def draw_board(self, painter):
        """Wyświetlenie planszy na ekranie"""
        width = consts.TILE_WIDTH
        height = consts.TILE_HEIGHT

        self.nr_frame += 1
        if len(self.bots) == 0:
            self.get_from_xml()

        for x in range(consts.BOARD_WIDTH):
            for y in range(consts.BOARD_HEIGHT):
                pos_x = x * width
                pos_y = y * height

                if self.board.tiles[x, y] == consts.WALL:
                    painter.drawPixmap(pos_x, pos_y, width, height, QPixmap(
                        '../res/images/wall.png'))
                elif self.board.tiles[x, y] == consts.GRASS:
                    painter.drawPixmap(pos_x, pos_y, width, height, QPixmap(
                        '../res/images/grass.png'))
                elif self.board.tiles[x, y] == consts.WOOD:
                    painter.drawPixmap(pos_x, pos_y, width, height, QPixmap(
                        '../res/images/wood.png'))
                elif self.board.tiles[x, y] == consts.PLAYER_FRONT:
                    painter.drawPixmap(pos_x, pos_y, width, height, QPixmap(
                        '../res/images/player_front.png'))
                elif self.board.tiles[x, y] == consts.BOMB:
                    painter.drawPixmap(pos_x, pos_y, width, height, QPixmap(
                        '../res/images/bomb.png'))
                elif self.board.tiles[x, y] == consts.EXPLOSION:
                    painter.drawPixmap(pos_x, pos_y, width, height, QPixmap(
                        '../res/images/explosion.png'))
                else:
                    painter.drawPixmap(pos_x, pos_y, width, height, QPixmap(
                        '../res/images/wall.png'))

        if len(self.bots) != 0:
            self.check_changes()

        if self.board.all_dead() and len(self.timers) == 0:
            self.repaintTimer.stop()

    def eventFilter(self, obj, event):
        """Obsługa klawiatury"""
        if event.type() == QEvent.KeyRelease:
            self.released = True

        return super(Game, self).eventFilter(obj, event)

    def explode(self, player, x, y):
        """Wybuch bomby

            Args:
                x (int): Pozycja x bomby
                y (int): Pozycja y bomby

        """
        self.board.explode(x, y)
        player.give_bomb()

        timer = GameTimer(self)
        timer.setInterval(consts.EXPLOSION_SPEED)
        timer.timeout.connect(lambda: self.board.clear_explosion(x, y))
        timer.timeout.connect(timer.stop)
        timer.start()

    def check_changes(self):
        """Sprawdzenie czy klatki się różnią"""
        if not np.array_equal(self.frame, self.board.tiles):
            self.board.save_change(self.frame)
            self.frame = np.copy(self.board.tiles)
            self.frames.append(self.nr_frame)

        if self.board.all_dead():
            self.save_xml()

    def save_xml(self):
        """Zapisywanie rozgrywki do dokumentu XML"""
        i = 0
        element = self.board.board_history[i]
        for nr_frame in self.frames:
            frame = self.doc.createElement("frame")
            frame.setAttribute("id", str(nr_frame))
            self.root.appendChild(frame)
            moves = []
            while element != '#':
                moves.append(element)
                i += 1
                element = self.board.board_history[i]

            line = self.doc.createTextNode(str(moves))
            frame.appendChild(line)
            if i < len(self.board.board_history) - 1:
                i += 1
                element = self.board.board_history[i]

        self.doc.appendChild(self.root)
        self.doc.writexml(open('autosave.xml', 'w'),
                          indent="  ", addindent="  ", newl='\n')
        self.doc.unlink()

    def get_from_xml(self):
        for frame in self.frames:
            if int(frame.getAttribute("id")) == self.nr_frame:
                line = frame.firstChild.data
                ignore = True
                selected = 0
                x = ""
                y = ""
                value = ""
                for char in line:
                    if char == "!":
                        ignore = True
                    if char == "@":
                        ignore = False
                    if not ignore:
                        if char == '*':
                            if selected == 2:
                                selected = 0
                                self.board.tiles[int(x), int(y)] = int(value)
                                x = ""
                                y = ""
                                value = ""
                            else:
                                selected += 1
                        else:
                            if char != '@':
                                if selected == 0:
                                    x += char
                                if selected == 1:
                                    y += char
                                if selected == 2:
                                    value += char
