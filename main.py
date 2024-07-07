from flask import Flask, render_template, request, redirect, url_for, session
import copy

app = Flask(__name__)
app.secret_key = "supersecretkey"

class Mancala:
    def __init__(self):
        self.board = [3] * 6 + [0] + [3] * 6 + [0]  # 6 Mulden pro Spieler + 1 Mancala pro Spieler
        self.current_player = 1  # Spieler 1 startet

    def is_game_over(self):
        return all(x == 0 for x in self.board[0:6]) or all(x == 0 for x in self.board[7:13])

    def make_move(self, pit):
        if self.current_player == 1 and pit not in range(6):
            return False
        if self.current_player == 2 and pit not in range(7, 13):
            return False

        stones = self.board[pit]
        if stones == 0:
            return False

        self.board[pit] = 0
        index = pit

        while stones > 0:
            index = (index + 1) % 14
            if self.current_player == 1 and index == 13:
                continue
            if self.current_player == 2 and index == 6:
                continue
            self.board[index] += 1
            stones -= 1

        # Check for capturing stones
        if self.current_player == 1 and 0 <= index < 6 and self.board[index] == 1:
            self.board[6] += self.board[index] + self.board[12 - index]
            self.board[index] = 0
            self.board[12 - index] = 0
        elif self.current_player == 2 and 7 <= index < 13 and self.board[index] == 1:
            self.board[13] += self.board[index] + self.board[12 - index]
            self.board[index] = 0
            self.board[12 - index] = 0

        # Switch player if move did not end in the player's own mancala
        if self.current_player == 1 and index != 6:
            self.current_player = 2
        elif self.current_player == 2 and index != 13:
            self.current_player = 1

        # Check if a player has no more stones in their pits
        if all(x == 0 for x in self.board[0:6]):
            self.board[13] += sum(self.board[7:13])
            for i in range(7, 13):
                self.board[i] = 0
        elif all(x == 0 for x in self.board[7:13]):
            self.board[6] += sum(self.board[0:6])
            for i in range(0, 6):
                self.board[i] = 0

        return True if index == 6 or index == 13 else False

    def get_winner(self):
        if self.board[6] > self.board[13]:
            return "Player 1"
        elif self.board[6] < self.board[13]:
            return "Player 2"
        else:
            return "Draw"

    def to_dict(self):
        return {
            'board': self.board,
            'current_player': self.current_player
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls()
        instance.board = data['board']
        instance.current_player = data['current_player']
        return instance

@app.route('/')
def index():
    if 'game' not in session:
        session['game'] = Mancala().to_dict()
    game = Mancala.from_dict(session['game'])
    return render_template('index.html', game=game)

@app.route('/move/<int:pit>')
def move(pit):
    game = Mancala.from_dict(session['game'])
    if game.is_game_over():
        return redirect(url_for('index'))
    game.make_move(pit)
    session['game'] = game.to_dict()
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    session['game'] = Mancala().to_dict()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
