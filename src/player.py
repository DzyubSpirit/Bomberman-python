import subprocess
import numpy as np

from src import constants as consts


class Player(object):
    """Klasa obsługująca poszczególnych graczy."""

    def __init__(self, bot, x, y):
        """Domyślne ustawienia klasy

            Args:
                name (string): Nazwa gracza
                x (int): Pozycja x gracza
                y (int): Pozycja y gracza

        """
        self.bot = bot
        self.pos_x = x
        self.pos_y = y
        self.bombs = 1
        self.isDead = False

    def action(self, board):
        code_with_args = "console.log(({})({}, {}, {}));".format(
            self.bot.code, board.tiles.tolist(), self.pos_x, self.pos_y)
        sub = subprocess.run(
            ["node"], input=code_with_args, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if sub.returncode:
            print(sub.stderr)
            return 0

        action = int(sub.stdout)
        return action

    def move(self, x, y):
        """Przesunięcie gracza na daną pozycje

            Args:
                x (int): Przesuń gracza na pozycje x
                y (int): Przesuń gracza na pozycje y

        """
        self.pos_x = x
        self.pos_y = y

    def get_pos_x(self):
        """Zwraca aktualną pozycje gracza

            Returns:
                x (int): Zwraca x pozycje gracza

        """
        return self.pos_x

    def get_pos_y(self):
        """Zwraca aktualną pozycje gracza

            Returns:
                y (int): Zwraca y pozycje gracza

        """
        return self.pos_y

    def place_bomb(self):
        """Stawianie bomby na pozycji gracza

            Returns:
                True - zwraca pozycje bomby jeżeli postawiono
                False - zwraca pozycje 0,0 czyli błędną

        """
        if self.bombs >= 1:
            self.bombs -= 1
            return True
        else:
            return False

    def give_bomb(self):
        """Daje graczowi bombę"""
        self.bombs += 1
