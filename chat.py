from chatbot import ChatBot  # Import ChatBot from the new module

# Test flow that mimics chatbot interaction
def run_chatbot():
    chat_bot = ChatBot()

    print("Let's chat! (type 'quit' to exit)")
    while True:
        user_input = input('You: ')

        if user_input.lower() == 'quit':
            break

        response = chat_bot.get_response(user_input)
        print(f"BOT: {response}")

        if response == "I'm not sure how to respond to that. Can you provide more details?":
            print("BOT: I don't know the answer. Can you teach me?")
            new_answer = input('You (Teaching): ')
            if new_answer.lower() != 'skip':
                confirmation = input(f"Do you want to save the answer: '{new_answer}' for the question: '{user_input}'? (yes/no): ")
                if confirmation.lower() == 'yes':
                    chat_bot.learn_response(user_input, new_answer)
                else:
                    print("Learning skipped.")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        run_chatbot()
