import logging
import re
from fuzzywuzzy import process
from models import db, QuestionAnswer  # Assuming models.py contains the db model setup

# Set up logging for better tracking of interactions
logging.basicConfig(level=logging.INFO)

class ChatBot:
    def __init__(self):
        pass  # No need to load JSON, we are using the DB now.

    def normalize_text(self, text: str) -> str:
        """
        Normalize the text by converting to lowercase, stripping extra spaces,
        and removing punctuation.
        """
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        return text

    def find_best_match(self, user_question: str) -> str | None:
        """
        Find the best match for the user's question from the database using fuzzy matching.
        """
        # Normalize the user input
        normalized_question = self.normalize_text(user_question)

        # Fetch all questions from the DB and normalize them
        questions = [self.normalize_text(qa.question) for qa in QuestionAnswer.query.all()]

        logging.info(f"Normalized user question: {normalized_question}")
        logging.info(f"Stored questions: {questions}")

        # Find the best match using fuzzywuzzy
        match, score = process.extractOne(normalized_question, questions)
        logging.info(f"Best match: {match} with score: {score}")

        if score > 60:
            # Return the corresponding answer
            best_match = QuestionAnswer.query.filter_by(question=match).first()
            return best_match.answer if best_match else None
        return None

    def get_response(self, text: str) -> str:
        """
        Get the response based on the user's question. If no match is found, ask for more details.
        """
        answer = self.find_best_match(text)
        if answer:
            logging.info(f"Answer found for: {text}")
            return answer
        else:
            logging.warning(f"No match found for: {text}")
            return "I'm not sure how to respond to that. Can you provide more details?"

    def learn_response(self, question: str, answer: str):
        """
        Learn a new response by saving a question-answer pair to the database.
        """
        # Normalize the question before saving it
        normalized_question = self.normalize_text(question)

        # Check if the question already exists
        existing_qa = QuestionAnswer.query.filter_by(question=normalized_question).first()
        if existing_qa:
            logging.info(f"Question already exists. Updating answer for: {normalized_question}")
            existing_qa.answer = answer  # Update the answer for the existing question
        else:
            # Add new question-answer pair to the DB
            new_qa = QuestionAnswer(question=normalized_question, answer=answer)
            db.session.add(new_qa)

        db.session.commit()
        logging.info(f"Learned new response: {normalized_question} -> {answer}")
        print("Thank you! I learned a new response!")

