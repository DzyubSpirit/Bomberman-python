import numpy as np
import codecs, json
import requests

from src import constants as consts
from src import board

class Player(object):
    """Klasa obsługująca poszczególnych graczy."""

    def __init__(self, name, x, y):
        """Domyślne ustawienia klasy

            Args:
                name (string): Nazwa gracza
                x (int): Pozycja x gracza
                y (int): Pozycja y gracza

        """
        self.name = name
        self.pos_x = x
        self.pos_y = y
        self.bombs = 1
        self.isDead = False

    def action(self, board):
        a = board.tiles
        b = a.tolist()
        matrixstring = "{  field = "+json.dumps(b)
        positionssting = " x = " + str(self.pos_x) + "y = " + str(self.pos_y)
        #print(str(self.pos_x)+"Hello"+matrixstring)
        
        url = 'http://localhost:8080'
        

        x = requests.post(url, data = positionssting + matrixstring)
        return np.random.randint(consts.DO_NOTHING, consts.PLANT_BOMB+1)
        

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
