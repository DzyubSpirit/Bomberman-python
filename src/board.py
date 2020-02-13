from PyQt5.QtCore import QTimer

import numpy as np
import random

from src import constants as consts
from src import player

playerInitialPositions = [
    [],
    [(1, 1)],
    [(1, 1), (consts.BOARD_WIDTH - 2, consts.BOARD_HEIGHT - 2)],
]


class Board(object):
    """Klasa obsługująca tworzenie i zarządzanie planszą."""

    def __init__(self, playerNames):
        """Domyślne ustawienia klasy

            Args:
                players (int): Ilość wszystkich graczy

        """
        self.width = consts.BOARD_WIDTH
        self.height = consts.BOARD_HEIGHT
        self.tiles = np.zeros((self.width, self.height), dtype=int)

        initPos = playerInitialPositions[len(playerNames)]
        self.players = [
            player.Player(name, initPos[i][0], initPos[i][1]) for i, name in enumerate(playerNames)]

        self.create_board()
        self.board_history = []

        for x in range(self.width):
            for y in range(self.height):
                move = '@' + str(x) + '*' + str(y) + '*' + \
                    str(self.tiles[x, y]) + '*!'
                self.board_history.append(move)
        self.board_history.append('#')

    def all_dead(self):
        return all([player.isDead for player in self.players])

    def create_board(self):
        """Tworzenie planszy"""

        # Tworzenie murów
        for i in range(self.width):
            for j in range(self.height):
                self.tiles[i, j] = consts.WALL

        # Tworzenie trawy
        for i in range(1, self.width - 1):
            for j in range(1, self.height - 1):
                self.tiles[i, j] = consts.GRASS

        # Tworzenie losowej siatki zniszczalnych murów
        for i in range(1, self.width - 1):
            for j in range(1, self.height - 1):
                self.tiles[i, j] = random.randint(consts.GRASS, consts.WOOD)
        # Zapełnienie siatką murów co 2 wiersz i kolumnę
        self.tiles[2::2, ::2] = consts.WALL

        initPos = playerInitialPositions[len(self.players)]
        for player in self.players:
            for iy in range(player.pos_y - 1, player.pos_y + 2):
                if self.tiles[player.pos_x, iy] != consts.WALL:
                    self.tiles[player.pos_x, iy] = consts.GRASS
            for ix in range(player.pos_x - 1, player.pos_x + 2):
                if self.tiles[ix, player.pos_y] != consts.WALL:
                    self.tiles[ix, player.pos_y] = consts.GRASS
            self.tiles[player.pos_x, player.pos_y] = consts.PLAYER_FRONT

    def save_change(self, previous_board):
        """Zapisuje zmianę pól planszy pomiędzy kolejnymi klatkami

            Args:
                previous_board (int array): Poprzednia wersja planszy
        """
        for x in range(self.width):
            for y in range(self.height):
                if previous_board[x, y] != self.tiles[x, y]:
                    move = '@' + str(x) + '*' + str(y) + '*' + \
                        str(self.tiles[x, y]) + '*!'
                    self.board_history.append(move)

        self.board_history.append('#')

    def try_move(self, x, y):
        """Zwraca aktualną pozycje gracza

            Args:
                x (int): Pozycja x ruchu do sprawdzenia
                y (int): Pozycja y ruchu do sprawdzenia

            Returns:
                True - jeżeli jest możliwy taki ruch

        """
        if self.tiles[x, y] != consts.WALL and self.tiles[x, y] != consts.WOOD and self.tiles[x, y] != consts.BOMB:
            return True
        else:
            return False

    def move(self, player_id, x, y):
        """Przesunięcie gracza na daną pozycje

            Args:
                x (int): Pozycja x bomby
                y (int): Pozycja y bomby

        """
        player = self.players[player_id]
        if self.tiles[player.pos_x, player.pos_y] == consts.PLAYER_FRONT:
            self.tiles[player.pos_x, player.pos_y] = consts.GRASS
        else:
            self.tiles[player.pos_x, player.pos_y] = consts.BOMB
        player.move(x, y)
        self.tiles[x, y] = consts.PLAYER_FRONT

    def place_bomb(self, game, player):
        """Ustawienie bomby na danej pozycji"""
        if not player.place_bomb():
            return

        x, y = player.pos_x, player.pos_y
        self.tiles[x, y] = consts.BOMB

        timer = QTimer(game)
        timer.setInterval(consts.BOMB_SPEED)
        timer.timeout.connect(lambda: game.explode(player, x, y))
        timer.timeout.connect(timer.stop)

        game.timers.append(timer)
        timer.start()

    def do_bot_actions(self, game):
        for i, player in enumerate(self.players):
            action = player.action(self)
            if action == consts.DO_NOTHING:
                continue
            if action == consts.PLANT_BOMB:
                self.place_bomb(game, player)
                continue

            moves = {
                consts.MOVE_LEFT: (-1, 0),
                consts.MOVE_UP: (0, -1),
                consts.MOVE_RIGHT: (1, 0),
                consts.MOVE_DOWN: (0, 1),
            }
            dx, dy = moves[action]
            nx, ny = player.pos_x + dx, player.pos_y + dy
            if self.try_move(nx, ny):
                self.move(i, nx, ny)

    def explode(self, bomb_x, bomb_y):
        """Tworzy efekt eksplozji bomby

            Args:
                bomb_x (int): Pozycja x początku eksplozji
                bomb_y (int): Pozycja y początku eksplozji

        """
        self.tiles[bomb_x, bomb_y] = consts.EXPLOSION

        for ray in consts.EXPLOSION_RAYS:
            for dx, dy in ray:
                x, y = bomb_x + dx, bomb_y + dy
                if x < 0 or y < 0 or x >= self.width or y >= self.height:
                    break

                if self.tiles[x, y] == consts.WALL:
                    break
                if self.tiles[x, y] == consts.WOOD:
                    self.tiles[x, y] = consts.EXPLOSION
                    break

                for player in self.players:
                    if player.pos_x == x and player.pos_y == y:
                        player.isDead = True
                        break

                self.tiles[x, y] = consts.EXPLOSION

    def clear_explosion(self, bomb_x, bomb_y):
        """Czyszczenie efektu eksplozji bomby

            Args:
                bomb_x (int): Pozycja x początku eksplozji
                bomb_y (int): Pozycja y początku eksplozji

        """
        self.tiles[bomb_x, bomb_y] = consts.GRASS
        for ray in consts.EXPLOSION_RAYS:
            for dx, dy in ray:
                x, y = bomb_x + dx, bomb_y + dy
                if x < 0 or y < 0 or x >= self.width or y >= self.height:
                    break

                if self.tiles[x, y] == consts.EXPLOSION:
                    self.tiles[x, y] = consts.GRASS
