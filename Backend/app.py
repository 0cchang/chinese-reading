from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from gameFunctions import loadLevelMCQ, playMCQ  # Import your functions
from platform import system
import logging

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your_secret_key'  # Needed for session management

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle button click
        selected_choice = request.form.get('choice')
        if selected_choice:
            # Process the selected choice here
            print("Selected choice:", selected_choice)
            # Implement logic to update game state based on user input
            # For example, decrement the number of times left and update state
            # session['times'] -= 1
            # session['choices'] = update_choices_based_on_selection(selected_choice)

    # Initialize or update game state
    times = session.get('times', 5)
    pinyin = session.get('pinyin', '')
    english = session.get('english', '')
    reveal = session.get('reveal', [])
    currReveal = session.get('currReveal', 0)
    choices = session.get('choices', [])
    correctQueue = session.get('currectQueue', []) 
    dispChoices = session.get('dispChoices', 0)
    correctQueue = session.get('correctQueue', [])
    level = session.get('level', loadLevelMCQ("Backend/levels/chinese-words.txt") ) # or your appropriate file path

    pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level = playMCQ(
        pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level)

    # Update session
    session.update({
        'times': times,
        'pinyin': pinyin,
        'english': english,
        'reveal': reveal,
        'currReveal': currReveal,
        'choices': choices,
        'correctQueue': correctQueue,
        'dispChoices': dispChoices,
        'level': level
    })

    return render_template('index.html', pinyin=pinyin, english=english, reveal=reveal, choices=choices, choiceMap = level[2])

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/handle_click', methods=['POST'])
def handle_click():
    logging.info("Handle click route was triggered")
    # Retrieve session variables
    times = session.get('times', 0)
    pinyin = session.get('pinyin', [])
    english = session.get('english', [])
    reveal = session.get('reveal', [])
    currReveal = session.get('currReveal', 0)
    choices = session.get('choices', [])
    correctQueue = session.get('correctQueue', [])
    dispChoices = session.get('dispChoices', [])
    level = session.get('level', ([], [], []))

    wordMap, charMap, choiceMap = level

    # Get the selected character index
    answer = int(request.form.get('char', -1))

    if answer < 0 or answer >= len(dispChoices):
        return redirect(url_for('index'))  # Handle invalid answer index

    # Grading
    if correctQueue and correctQueue[0] == charMap.get(dispChoices[answer]):
        reveal[currReveal] = choiceMap.get(correctQueue.pop(0), '')
        currReveal += 1
        choices.pop(answer)
    else:
        if charMap.get(dispChoices[answer]) not in correctQueue:
            choices.pop(answer)

    # If word is fully revealed or times is 0, update the game state
    if not correctQueue:
        times -= 1  # Decrement the number of rounds
        if times > 0:
            # Start a new round
            pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level = \
                playMCQ(pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level)
        else:
            return jsonify({'game_over': True}), 200

    # Update the session with new game state
    session.update({
        'times': times,
        'pinyin': pinyin,
        'english': english,
        'reveal': reveal,
        'currReveal': currReveal,
        'choices': choices,
        'correctQueue': correctQueue,
        'dispChoices': dispChoices,
        'level': level
    })

    # Re-render the page with updated state
    return jsonify({
        'times': times,
        'pinyin': pinyin,
        'english': english,
        'reveal': reveal,
        'currReveal': currReveal,
        'choices': choices,
        'correctQueue': correctQueue,
        'dispChoices': dispChoices,
        'level': level
    })


if __name__ == '__main__':
    app.run(debug=True)
