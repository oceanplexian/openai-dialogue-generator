import openai
import json
import pyfiglet
import random
import datetime

# Defining the seperator line
sep_line = "\n" + ("-" * 71) + "\n"

# Variable for the input method to facilitate different ways of entering the API key.
# Change to "input" to prompt the user for API keys at runtime
api_key_source = "json"

# Define model to be used
selected_model = "gpt-3.5-turbo"


# Defining a small function for printing styled text to console
def fig_print(text, font):
    fig_output = pyfiglet.figlet_format(text, font=font)
    print(fig_output)


# Wrapping that in a another function to produce to start message for the script
def title_print():
    fig_print("Dialogue Generator", "slant")
    print("Follow the prompts to start generating a dialogue between two characters. "
          + "\n\n" + "Selected model: " + selected_model + "\n" + sep_line)


# Printing the title
title_print()

# Get api keys using one of two methods
if api_key_source == "json":  # Access the keys from a json file in the root directory
    # Defining the json file path containing API information
    json_secrets = "secrets.json"

    # Open JSON file
    #with open(json_secrets) as file:
    #    json_data = json.load(file)

    # Define API values, and setting to openai attributes
    openai.api_type = "azure"
    openai.api_key = "dummy"
    openai.api_base = "http://10.10.0.127:5001"
    openai.api_version = "2023-05-15"

    #openai.api_key = json_data["openai_api_key"]
    #openai.organization = json_data["openai_org_id"]

    deployment_name='test_deployment' 

if api_key_source == "input":  # Prompt for the input of the API keys
    openai.api_key = input("Input the API key:\n").strip()
    openai.organization = input("\nInput the organisation id:\n").strip()
    print(sep_line)


# Wrapping all code in a function so it can be run successively
def run_script():
    # Define the first character
    character_a_description = input("Describe the first character without saying their name:\n")

    # Define the second character
    character_b_description = input("\nDescribe the second character without saying their name:\n")

    # Defining the prompt to get character names
    name_prompt = "1 name idea for a character with the description (name only): "

    # Prompt for the AI to provide the name of the first character
    character_a_message = name_prompt + character_a_description
    character_a_name_input = [{"role": "user", "content": character_a_message}]

    # Prompt for the AI to provide the name of the second character
    character_b_message = name_prompt + character_b_description
    character_b_name_input = [{"role": "user", "content": character_b_message}]

    # Prompting ChatGPT for the name of the first character and then saving that as a variable with newlines removed
    name_a_response = openai.ChatCompletion.create(engine=deployment_name, model=selected_model, messages=character_a_name_input)
    name_a_string_raw = name_a_response["choices"][0]["message"]["content"]
    name_a_string_clean = name_a_string_raw.replace("\n", "")

    # Prompting ChatGPT for the name of the second character and then saving that as a variable with newlines removed
    name_b_response = openai.ChatCompletion.create(engine=deployment_name, model=selected_model, messages=character_b_name_input)
    name_b_string_raw = name_b_response["choices"][0]["message"]["content"]
    name_b_string_clean = name_b_string_raw.replace("\n", "")

    # Creating a description of the characters including their names, to pass to prompts
    the_situation = """1st character's name: %s
1st character's description: %s

2nd character's name: %s
2nd character's description: %s""" % (name_a_string_clean,
                                      character_a_description,
                                      name_b_string_clean,
                                      character_b_description)

    # Print the situation set-up to console
    print(sep_line + "\n" + the_situation + "\n" + sep_line)

    # Set up prompts for certain choices below
    situation_generic = "Generate a conversation between these two characters. Only include the conversation. "
    relatability = "The topic of the conversation should be related to the characters and their potential interests. "
    unrelatability = "The topic of the conversation should be not related to the characters at all. "
    include_spaces = "Always include space between each line of dialogue. "
    dialogue_format = "Always format the dialogue like this 'Person: What they said'"

    # Combining those
    situation_related = situation_generic + relatability + include_spaces + dialogue_format
    situation_unrelated = situation_generic + unrelatability + include_spaces + dialogue_format

    # The selected situation type, which will be altered depending on the control flow below
    situation_selected = situation_related

    # Variable to contain the topic that was chosen for the conversation
    initial_topic = ""

    # Options for beginning the dialogue, where variables are defined to drive other logic
    while True:
        print("How would you like the conversation to begin?")
        print("1. Let the AI decide everything")
        print("2. Define the topic of conversation")
        choice = input("\nEnter a number (1-2):\n")

        # Handle the user's selection
        if choice == "1":  # Let the AI decide everything
            # Randomly determining how the AI should decide on a topic
            if random.random() < 0.5:  # Topic unrelated to the characters
                situation_selected = situation_unrelated
            else:  # Topic is related to the characters somehow
                situation_selected = situation_related
            initial_topic = "Initial Topic: AI decided"
        elif choice == "2":  # Define the topic of conversation
            user_defined_topic = input("\nWhat should the topic of conversation be?:\n")
            situation_selected = situation_generic + "The topic of the conversation should be " + user_defined_topic
            initial_topic = "Initial Topic: " + user_defined_topic
        # What happens if they input the wrong number at the start
        else:
            print("\nInvalid selection. Please enter a number between 1 and 2.\n")
            continue

        # Exit the loop if the user made a valid selection
        break

    # Printing a seperator line
    print(sep_line)

    # Function to get the response object based on a selected model and messages dict
    def get_response(model, messages):
        response_in_func = openai.ChatCompletion.create(engine=deployment_name, model=model, messages=messages)
        return response_in_func

    # Function to return the message dict from the response object
    def get_message_dict(response_obj):
        messages_dict_in_func = response_obj["choices"][0]["message"]
        return messages_dict_in_func

    # Function to return the message content from the response object, with leading newlines removed
    def get_message_content(response_obj):
        messages_content_in_func = response_obj["choices"][0]["message"]["content"]
        messages_content_in_func_lstrip = messages_content_in_func.lstrip('\n')
        return messages_content_in_func_lstrip

    # Defining the list to contain message dictionaries
    rolling_messages = []  # Target format is {"role": "user", "content": "Placeholder"}, ......

    # Combine the set-up elements
    combined_situation = the_situation + "\n\n" + situation_selected

    # Append the setup into the rolling_messages dictionary
    rolling_messages.append({"role": "user", "content": combined_situation})

    # Define a function to generate, append and print a response to the situation set-up
    def generate_response():
        # Get the response object
        response = get_response(selected_model, rolling_messages)
        # Get the response as a object
        message_obj = get_message_dict(response)
        # Get the response as a dictionary
        message_dict = {"role": message_obj["role"], "content": message_obj["content"]}
        # Append that dict to the rolling_messages list
        rolling_messages.append(message_dict)
        # Get just the content of that message as a string
        message_content = get_message_content(response)
        # Print that content
        print(message_content)
        print(sep_line)

    # Generate the initial response, print it, and add it to the rolling messages variable
    generate_response()

    # While loop to continue the conversation based on user input
    while True:
        # Requesting user response
        # print("How should the conversation continue?")
        # print("1. Let the AI decide")
        # print("2. Describe what happens next")
        # print("3. End the conversation")
        # user_response = input("\nEnter a number (1-3):\n")
        user_response = "1"
        # Setting the break condition
        if user_response == "1":
            new_message = "Continue the conversation."
            rolling_messages.append({"role": "user", "content": new_message})
            generate_response()
        elif user_response == "2":
            new_message = input("\nDescribe what happens next:\n")
            new_message = "Continue the conversation where this happens next: " + new_message
            rolling_messages.append({"role": "user", "content": new_message})
            print(sep_line)
            generate_response()
        elif user_response == "3":
            print(sep_line)
            while True:
                # Requesting user response
                print("Do you want to output the conversation into a text file? It will output in the script folder.")
                print("1. Yes")
                print("2. No")
                user_response = input("\nEnter a number (1-2):\n")

                if user_response == "1":
                    # Define the output file name
                    file_name = "dialogue_generator - " + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

                    # Open a file named "output.txt" for writing
                    file = open(file_name + ".txt", "w")

                    # Transform the recorded output for the text file
                    string_to_write = ""

                    # Loops through the list of dictionaries, printing only the response values from the ai
                    for item in rolling_messages[1:]:
                        for key, value in item.items():
                            # Renaming values for the output
                            if key == 'role' and value == 'assistant':
                                string_to_write += selected_model + ":\n"
                            if key == 'role' and value == 'user':
                                string_to_write += "dialogue_generator" + ":\n"
                            if key == 'content':
                                string_to_write += value.lstrip('\n') + "\n" + sep_line + "\n"

                    # Appends descriptive information about the output and the characters
                    string_to_write = (file_name +
                                       "\n" + sep_line + "\n" +
                                       the_situation +
                                       "\n" + sep_line + "\n" +
                                       initial_topic +
                                       "\n" + sep_line + "\n" +
                                       string_to_write)

                    # Write the string to the file
                    file.write(string_to_write)

                    # Close the file
                    file.close()

                    # Output success message
                    print("\nOutput text file will be available in the "
                          "current directory when the script is closed.")

                    break
                elif user_response == "2":
                    break
                else:
                    print("\nInvalid selection. Please enter a number between 1 and 2.\n")
                    continue
            break
        else:
            print("\nInvalid selection. Please enter a number between 1 and 3.\n")
            continue

    # Print seperator line


# Initial run of the script
run_script()

# Looping the script if the user wants to make another conversation
while True:
    print("Do you want to generate another conversation?:")
    print("1. Yes - run script again")
    print("2. No - close script")
    end_response = input("\nEnter a number (1-2):\n")
    if end_response == "1":
        print(sep_line)
        # Re-print the title
        title_print()
        # Run the script again
        run_script()
    elif end_response == "2":
        break
    else:
        print("Invalid selection. Please enter a number between 1 and 2.\n")
        continue

# Final message on script completion
print(sep_line)
fig_print("Script complete", "slant")

# Final input call so the CLI doesn't immediately close
input("Enter any key to close the script:\n")
