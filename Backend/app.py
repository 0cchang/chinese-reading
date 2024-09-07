from flask import Flask, render_template, request
from gameFunctions import loadLevelMCQ, playMCQ, runGame
import os
import gameFunctions


app = Flask(__name__, template_folder = os.getcwd()) 

@app.route('/')
def index():
    runGame(5)
    data_array = [1, 2, 3, 4, 5]
    return render_template('index.html', data_array=data_array)

@app.route('/handle_click', methods=['POST'])
def handle_click():
    # Get the index of the clicked button
    index = request.form['index']
    print(f"Button with index {index} was clicked")

    # You can add logic to handle the clicked button here
    # e.g., processing the array element based on the index

    # For now, we just redirect back to the main page
    return index

if __name__ == '__main__':
    app.run(debug=True)