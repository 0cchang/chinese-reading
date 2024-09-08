from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from gameFunctions import loadLevelMCQ, playMCQ
import logging
import redis
import json

# Configure Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your_secret_key'  # Needed for session management

def initialize_user_levels():
    # Check if user_levels hash exists
    if not redis_client.exists('user_levels'):
        redis_client.hset('user_levels', mapping={})
        print("Initialized user_levels hash in Redis.")

def set_user_level(user_id, level_key):
    redis_client.hset('user_levels', user_id, level_key)

def get_user_level(user_id):
    level_key = redis_client.hget('user_levels', user_id)
    return level_key.decode('utf-8') if level_key else None

def initialize_charmap():
    # Check if charMap and choiceMap exist in Redis
    if not redis_client.exists('character_to_id') or not redis_client.exists('id_to_character'):
        from charMap_data import CHARACTERS, CHINASTART
        charMap = {}  # character -> id
        choiceMap = {}  # id -> character

        for i in range(len(CHARACTERS)):
            if ord(CHARACTERS[i]) < CHINASTART:
                continue
            charMap[CHARACTERS[i]] = str(i + 1)
            choiceMap[str(i + 1)] = CHARACTERS[i]

        # Save the character-to-ID mapping to Redis
        for character, unique_id in charMap.items():
            redis_client.hset('character_to_id', character, unique_id)

        # Save the ID-to-character mapping to Redis
        for unique_id, character in choiceMap.items():
            redis_client.hset('id_to_character', unique_id, character)

        print("Mapping saved to Redis.")

# Call initialize_charmap at startup 
#initialize_charmap()

@app.route('/login', methods=['GET', 'POST'])
def login():
    initialize_charmap() #initializing at login for debugging
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            # Check if the user has an existing level_key
            level_key = get_user_level(user_id)
            
            if not level_key:
                # Create a new level_key if it does not exist
                level_key = f'level:{user_id}'
                level_data = loadLevelMCQ("Backend/levels/chinese-words.txt")
                redis_client.set(level_key, json.dumps(level_data))
                set_user_level(user_id, level_key)
                logging.info(f"New level key created and associated: {level_key}")

            # Store user ID in session
            session['user_id'] = user_id
            session['level_key'] = level_key

            return redirect(url_for('index'))
        else:
            return "User ID is required!", 400
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    level_key = session.get('level_key')

    if not level_key:
        level_key = f'level:{session["user_id"]}'
        level_data = loadLevelMCQ("Backend/levels/chinese-words.txt")
        redis_client.set(level_key, json.dumps(level_data))
        session['level_key'] = level_key

    # Load level data from Redis
    level_json = redis_client.get(level_key)
    if not level_json:
        logging.error("Level data not found in Redis")
        return redirect(url_for('login'))

    try:
        level = json.loads(level_json)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed: {e}")
        return redirect(url_for('login'))

    charMap = redis_client.hgetall('character_to_id')  # Use HGETALL for hash
    choiceMap = redis_client.hgetall('id_to_character')  # Use HGETALL for hash

    if not charMap or not choiceMap:
        print("character_to_id or id_to_character not found in Redis, initializing...")
        initialize_charmap()
        charMap = redis_client.hgetall('character_to_id')
        choiceMap = redis_client.hgetall('id_to_character')

    # Convert from bytes to strings
    charMap = {k.decode('utf-8'): v.decode('utf-8') for k, v in charMap.items()}
    choiceMap = {k.decode('utf-8'): v.decode('utf-8') for k, v in choiceMap.items()}

    times = session.get('times', 5)
    pinyin = session.get('pinyin', '')
    english = session.get('english', '')
    reveal = session.get('reveal', [])
    currReveal = session.get('currReveal', 0)
    choices = session.get('choices', [])
    correctQueue = session.get('correctQueue', [])
    dispChoices = session.get('dispChoices', 0)

    pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level = playMCQ(
        pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level)

    session.update({
        'times': times,
        'pinyin': pinyin,
        'english': english,
        'reveal': reveal,
        'currReveal': currReveal,
        'choices': choices,
        'correctQueue': correctQueue,
        'dispChoices': dispChoices
    })

    return render_template('index.html', pinyin=pinyin, english=english, reveal=reveal, choices=choices, choiceMap=choiceMap)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/handle_click', methods=['POST'])
def handle_click():
    logging.info("Handle click route was triggered")

    times = session.get('times', 0)
    pinyin = session.get('pinyin', [])
    english = session.get('english', [])
    reveal = session.get('reveal', [])
    currReveal = session.get('currReveal', 0)
    choices = session.get('choices', [])
    correctQueue = session.get('correctQueue', [])
    dispChoices = session.get('dispChoices', [])
    incorrect_count = session.get('incorrect_count', 0)  # Track incorrect answers

    level_key = session.get('level_key')
    level_json = redis_client.get(level_key)
    
    if not level_json:
        logging.error("Level data not found in Redis")
        return redirect(url_for('login'))

    level = json.loads(level_json)
    charMap = redis_client.hgetall('character_to_id')  # Use HGETALL for hash
    choiceMap = redis_client.hgetall('id_to_character')  # Use HGETALL for hash

    # Convert from bytes to strings
    charMap = {k.decode('utf-8'): v.decode('utf-8') for k, v in charMap.items()}
    choiceMap = {k.decode('utf-8'): v.decode('utf-8') for k, v in choiceMap.items()}

    answer = request.form.get('char', '')
    logging.info(f"Received answer index: {answer}")

    if not answer or answer == " ":
        logging.info(f"Received null: {answer}")
        return redirect(url_for('index'))
    
    if not answer.isdigit():
        logging.info(f"Received non-digit answer: {answer}")
        return redirect(url_for('index'))

    answer = int(answer)

    if answer < 0 or answer >= len(dispChoices):
        logging.info(f"Answer index out of range: {answer}")
        return redirect(url_for('index'))

    correct_answer_id = charMap.get(dispChoices[answer], -1)

    if correctQueue and correctQueue[0] == correct_answer_id:
        print("correct")
        reveal[currReveal] = choiceMap.get(correctQueue.pop(0), '')
        currReveal += 1
        choices.pop(answer)

    else:
        if correct_answer_id not in correctQueue:
            choices.pop(answer)
            incorrect_count += 1  # Increment incorrect answers count
       
    if not correctQueue:
        times -= 1
        if times > 0:
            pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level = \
                playMCQ("", "", [], 0, [], [], [], level)
        
        else:
            return jsonify({'game_over': True}), 200

    session.update({
        'times': times,
        'pinyin': pinyin,
        'english': english,
        'reveal': reveal,
        'currReveal': currReveal,
        'choices': choices,
        'correctQueue': correctQueue,
        'dispChoices': dispChoices,
        'incorrect_count': incorrect_count  # Update incorrect answers count
    })

    return jsonify({
        'times': times,
        'pinyin': pinyin,
        'english': english,
        'reveal': reveal,
        'currReveal': currReveal,
        'choices': choices,
        'correctQueue': correctQueue,
        'dispChoices': dispChoices,
        'level': level,
        'incorrect_count': incorrect_count  # Send incorrect answers count
    })

if __name__ == '__main__':
    app.run(debug=True)
