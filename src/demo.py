import nltk
from joblib import dump, load

def get_name(user_name):
    dump(user_name, 'user_name.joblib')
    loaded_object = load('user_name.joblib')
    return loaded_object

def main():
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        user_name = get_name(user_input)
        print(f"Bot: Hi {user_name}")

if __name__ == '__main__':
    main()