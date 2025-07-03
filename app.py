from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jogar')
def jogar():
    subprocess.Popen(['python', 'tower_game_pixel.py'])
    return "Jogo iniciado!"

if __name__ == '__main__':
    app.run(debug=True)