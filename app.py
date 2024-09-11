from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import db, QuestionAnswer, UpcomingEvent, ImportantCommunication  # Import models
from chatbot import ChatBot  # Import the ChatBot class
import logging
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

# Configure SQLite (for simplicity) or switch to PostgreSQL/MySQL if needed
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Instantiate the chatbot
chat_bot = ChatBot()

def is_valid_text(text):
    """Validates user input to ensure it's non-empty and non-whitespace"""
    return text and not text.isspace()

# --------- Routes ---------

@app.route("/")
def home():
    # Render a basic HTML page to welcome users
    return render_template('home.html')


# Chatbot routes
@app.route("/predict", methods=["POST"])
def predict():
    try:
        text = request.get_json().get("message")

        if not is_valid_text(text):
            return jsonify({"error": "Invalid text input"}), 400

        response = chat_bot.get_response(text)
        message = {"answer": response}
        return jsonify(message)

    except Exception as e:
        logging.error(f"Error in /predict: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


@app.route("/learn", methods=["POST"])
def learn():
    try:
        data = request.get_json()
        question = data.get("question")
        answer = data.get("answer")

        if not is_valid_text(question) or not is_valid_text(answer):
            return jsonify({"error": "Invalid input"}), 400

        chat_bot.learn_response(question, answer)
        return jsonify({"message": "Response learned!"}), 200

    except Exception as e:
        logging.error(f"Error in /learn: {str(e)}")
        return jsonify({"error": "An error occurred while learning the new response."}), 500


@app.route("/qa", methods=["GET"])
def get_all_questions_answers():
    try:
        # Fetch all questions and answers from the database
        qa_list = QuestionAnswer.query.all()
        
        # Format the output as a list of dictionaries
        questions_answers = [
            {"id": qa.id, "question": qa.question, "answer": qa.answer} for qa in qa_list
        ]

        # Return the list as JSON
        return jsonify(questions_answers), 200

    except Exception as e:
        logging.error(f"Error in /qa: {str(e)}")
        return jsonify({"error": "An error occurred while fetching questions and answers."}), 500


@app.route("/qa/<int:id>", methods=["PUT", "DELETE"])
def manage_qa(id):
    try:
        qa_item = QuestionAnswer.query.get_or_404(id)

        if request.method == "PUT":
            data = request.get_json()
            qa_item.question = data.get("question", qa_item.question)
            qa_item.answer = data.get("answer", qa_item.answer)
            db.session.commit()
            return jsonify({"message": "QA updated!"}), 200

        elif request.method == "DELETE":
            db.session.delete(qa_item)
            db.session.commit()
            return jsonify({"message": "QA deleted!"}), 200

    except Exception as e:
        logging.error(f"Error in /qa/<int:id>: {str(e)}")
        return jsonify({"error": "An error occurred while updating or deleting the QA."}), 500


# --------- Upcoming Events Routes ---------

@app.route("/events", methods=["POST", "GET"])
def manage_events():
    try:
        if request.method == "POST":
            data = request.get_json()
            event = UpcomingEvent(
                title=data["title"],
                description=data["description"],
                date=datetime.fromisoformat(data["event_date"]).replace(tzinfo=timezone.utc)
            )
            db.session.add(event)
            db.session.commit()
            return jsonify({"message": "Event added!"}), 201

        elif request.method == "GET":
            events = UpcomingEvent.query.all()
            return jsonify([{
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "event_date": event.date.isoformat()
            } for event in events]), 200

    except Exception as e:
        logging.error(f"Error in /events: {str(e)}")
        return jsonify({"error": "An error occurred while managing events."}), 500


@app.route("/events/<int:id>", methods=["PUT", "DELETE", "GET"])
def modify_event(id):
    try:
        event = UpcomingEvent.query.get_or_404(id)

        if request.method == "PUT":
            data = request.get_json()
            event.title = data.get("title", event.title)
            event.description = data.get("description", event.description)
            event.date = datetime.fromisoformat(data.get("event_date", event.date.isoformat())).replace(tzinfo=timezone.utc)
            db.session.commit()
            return jsonify({"message": "Event updated!"}), 200

        elif request.method == "DELETE":
            db.session.delete(event)
            db.session.commit()
            return jsonify({"message": "Event deleted!"}), 200
        elif request.method == "GET":
            return jsonify({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "event_date": event.date.isoformat()
            }), 200

    except Exception as e:
        logging.error(f"Error in /events/<int:id>: {str(e)}")
        return jsonify({"error": "An error occurred while updating or deleting the event."}), 500


# --------- Important Communication Routes ---------

@app.route("/communications", methods=["POST", "GET"])
def manage_communications():
    try:
        if request.method == "POST":
            data = request.get_json()
            communication = ImportantCommunication(
                title=data["title"],
                message=data["message"],
                date_posted=datetime.now(timezone.utc)
            )
            db.session.add(communication)
            db.session.commit()
            return jsonify({"message": "Communication added!"}), 201

        elif request.method == "GET":
            communications = ImportantCommunication.query.all()
            return jsonify([{
                "id": comm.id,
                "title": comm.title,
                "message": comm.message,
                "date_posted": comm.date_posted.isoformat()
            } for comm in communications]), 200

    except Exception as e:
        logging.error(f"Error in /communications: {str(e)}")
        return jsonify({"error": "An error occurred while managing communications."}), 500


@app.route("/communications/<int:id>", methods=["PUT", "DELETE"])
def modify_communication(id):
    try:
        communication = ImportantCommunication.query.get_or_404(id)

        if request.method == "PUT":
            data = request.get_json()
            communication.title = data.get("title", communication.title)
            communication.message = data.get("message", communication.message)
            communication.date_posted = datetime.now(timezone.utc)  # Automatically update the post time
            db.session.commit()
            return jsonify({"message": "Communication updated!"}), 200

        elif request.method == "DELETE":
            db.session.delete(communication)
            db.session.commit()
            return jsonify({"message": "Communication deleted!"}), 200

    except Exception as e:
        logging.error(f"Error in /communications/<int:id>: {str(e)}")
        return jsonify({"error": "An error occurred while updating or deleting the communication."}), 500


# --------- Documentation Route ---------

@app.route("/doc")
def documentation():
    doc_info = {
        "routes": [
            {"path": "/", "method": "GET", "description": "Home route with a welcome message."},
            {"path": "/predict", "method": "POST", "description": "Returns the chatbot's response based on the message."},
            {"path": "/learn", "method": "POST", "description": "Teach the bot a new question-answer pair."},
            {"path": "/qa", "method": "GET", "description": "Returns all questions and answers stored in the database."},
            {"path": "/events", "method": "GET/POST", "description": "Get or add upcoming events."},
            {"path": "/communications", "method": "GET/POST", "description": "Get or add important communications."}
        ]
    }
    return render_template('documentation.html', doc_info=doc_info)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database and tables if they don't exist
    app.run(host="0.0.0.0", debug=True)
