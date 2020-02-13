from PyQt5.QtCore import QTimer


class GameTimer(QTimer):
    def __init__(self, game):
        super(QTimer, self).__init__(game)
        self.timeout.connect(self.remove_from_game)

        game.timers.add(self)
        self.game = game

    def remove_from_game(self):
        self.game.timers.remove(self)
