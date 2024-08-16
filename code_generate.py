import google.generativeai as genai
import os
import re

# Set up your Google Gemini API key
genai.configure(api_key='AIzaSyC9ztlMxH0g9lotzLH4iJX8tNAMcoJFGlg')

# Set up the model
model = genai.GenerativeModel('gemini-pro')


def clean_generated_code(generated_code):
    # Remove markdown code block syntax
    code = re.sub(r'```python\s*|```\s*', '', generated_code)

    # Remove any leading/trailing whitespace
    code = code.strip()

    return code


def generate_strategy_code(player_name, strategy_description):
    prompt = f"""
Create a Python function called 'make_choice' for a Prisoner's Dilemma game strategy.
The function should take two parameters:
1. own_choices: a list of boolean values representing the player's past choices (True for cooperate, False for defect)
2. opponent_choices: a list of boolean values representing the opponent's past choices

The function should return True for cooperate or False for defect.

Strategy description: {strategy_description}

Please implement this strategy as a Python function named 'make_choice'.
Only provide the Python code, without any explanations or markdown formatting.
"""

    response = model.generate_content(prompt)

    generated_code = clean_generated_code(response.text)

    # Add necessary imports and docstring
    full_code = f"""import random

# Strategy: {strategy_description}

{generated_code}
"""

    return full_code


def save_strategy_file(player_name, code):
    filename = f"{player_name}.py"
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(code)
        print(f"Strategy file '{filename}' has been created.")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")


def main():
    while True:
        player_name = input("Enter player name (or 'quit' to exit): ")
        if player_name.lower() == 'quit':
            break

        strategy_description = input("Describe the player's strategy: ")

        try:
            generated_code = generate_strategy_code(player_name, strategy_description)
            save_strategy_file(player_name, generated_code)
        except Exception as e:
            print(f"An error occurred: {e}")

        print("\n")


if __name__ == "__main__":
    main()