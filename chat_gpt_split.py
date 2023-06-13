"""
Module: chat_gpt_split

This module provides functionality for interacting with OpenAI's ChatGPT model through a Tkinter-based GUI. It allows users to prime the model with a text document, send queries to the model, and view the conversation history and responses.

History:
- Version 1.0 (2023-06-12):
    - Initial release of the module.

Author:
- Percy Rotteveel (percy@rotteveel.ca)

Usage:
- To prime the model with a text document:
    - Enter the file path in the Primer section.
    - Click the "Browse" button to select the file.
    - Click the "Prime" button to prime the model.

- To send queries to the model:
    - Enter the queries in the Chat section.
    - Click the "Submit" button to send the queries and receive responses.

Dependencies:
- os
- openai
- time
- tkinter
- json
- tkinter.filedialog
- tkinter.messagebox

Constants:
- DEBUG: Set to True for debugging mode, which prints additional information.
- CHAT_GPT_WAIT_SEC: Time to wait between subsequent ChatGPT calls.
- CHAT_GPT_MAX_CHUNK: Maximum characters to upload to ChatGPT.
- WAIT_GPT: Status message indicating that the request has been sent to ChatGPT and awaiting response.
- DONE_GPT: Status message indicating that a response has been received from ChatGPT.
- WAIT_START: Status message indicating waiting time before the next call to ChatGPT.
- WAIT_DONE: Status message indicating the waiting time is complete.
- CHUNKS_DONE: Status message indicating that the priming of ChatGPT is done.

Variables:
- openai.api_key: API key for the ChatGPT API.
- conversation_history: List to keep track of the conversation history.

Functions:
- set_priming_done(): Sets the status field to indicate that priming is done.
- set_status(message): Sets the status field with the provided message.
- extract_prompt_content(prompt): Extracts the content from a prompt and returns it as a string.
- extract_response_content(response): Extracts the content from a response and returns it as a string.
- write_message(what, message): Writes the provided message to the specified field.
- write_request(prompt): Writes the request extracted from the prompt to the request_text field.
- write_exception(message): Writes the provided exception message to the response_text field.
- write_response(response): Writes the response extracted from the response to the response_text field.
- split_text_into_chunks(text, chunk_size): Splits the given text into chunks of the specified size and returns a list of chunks.
- deliver_chunks_to_chatGPT(chunks): Sends each chunk to ChatGPT for processing.
- ask_question(): Handles asking questions to ChatGPT based on the entered text in the chat_text field.
- browse_file(entry): Allows browsing and selecting a file using the filedialog and inserts the file path into the entry field.
- primer(): Handles priming the model with the text document specified in the primer_entry field.

Classes:
- None

"""

import os
import openai
import time
import tkinter as tk
import json
from tkinter import filedialog, messagebox

# For debugging purpose you can print what is happening by setting DEBUG to True
DEBUG = True

# The time to wait between subsequent ChatGPT calls
CHAT_GPT_WAIT_SEC = 10

# The maximum characters to upload to ChatGPT
CHAT_GPT_MAX_CHUNK = 4000

# Various status messages
WAIT_GPT =    "Sent request to ChatGPT, awaiting response ..."
DONE_GPT =    "Response received."
WAIT_START =  "Waiting " + str(CHAT_GPT_WAIT_SEC) + " seconds before the next call to ChatGPT ..."
WAIT_DONE  =  "Waiting is done."
CHUNKS_DONE = "Priming of ChatGPT is done."

# My own chatGPT API key
openai.api_key = "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"

# Keep track of the conversation
conversation_history = []

def set_priming_done():
    # Set the text to white
    status_entry.configure(fg='white')
    # Clear the field
    status_entry.delete(0, tk.END)
    status_entry.insert(0, CHUNKS_DONE)
    # Update the GUI to display the changes immediately
    window.update_idletasks()    

def set_status(message):
    # Set the text to light grey
    status_entry.configure(fg='lightgrey')
    # Get the current content of the Entry widget
    current_text = status_entry.get()
    # Set the new content
    if len(current_text) == 0:
        new_content = message
    else:
        new_content = message + " > " + current_text
    # Set the new content
    status_entry.delete(0, tk.END)
    status_entry.insert(0, new_content)
    # Update the GUI to display the changes immediately
    window.update_idletasks()    

# Extract the content from a prompt
def extract_prompt_content(prompt):
    content_string = ''
    for item in prompt:
        content = item['content']
        if content.endswith('.') or content.endswith('!') or content.endswith('!'):
            content += '\n'
        content_string += content

    return content_string

# Extract the content from a response
def extract_response_content(response):
    content = response["choices"][0]["message"]["content"]
    content = content.replace("\\n", "\n")
    return content

def write_message(what, message):
    # Only print the message to the console if we are running in debug mode
    if DEBUG:
        print("\n",what,":\n",message)
    # Clear the existing text
    chat_text.delete("1.0", tk.END)
    # Insert the new text
    chat_text.insert(tk.END, message)
    # Update the GUI to display the changes immediately
    window.update_idletasks()    

def write_request(prompt):
    # Get the request
    message = extract_prompt_content(prompt)
    # Only print the prompt to the console if we are running in debug mode
    if DEBUG:
        print("\nPrompt:\n",message)
    # Clear the existing text
    request_text.delete("1.0", tk.END)
    # Insert the new text
    request_text.insert(tk.END, message)
    # No response received for this request, so clear the response field
    response_text.delete("1.0", tk.END)
    # Update the GUI to display the changes immediately
    window.update_idletasks()    

def write_exception(message):
    # Only print the response to the console if we are running in debug mode
    if DEBUG:
        print("\nException:\n",message)
    # Clear the existing text
    response_text.delete("1.0", tk.END)
    # Insert the new text
    response_text.insert(tk.END, message)
    # Update the GUI to display the changes immediately
    window.update_idletasks()    
    
def write_response(response):
    # Get the response
    message = extract_response_content(response)
    # Only print the response to the console if we are running in debug mode
    if DEBUG:
        print("\nResponse:\n",message)
    # Clear the existing text
    response_text.delete("1.0", tk.END)
    # Insert the new text
    response_text.insert(tk.END, message)
    # Update the GUI to display the changes immediately
    window.update_idletasks()    

def split_text_into_chunks(text, chunk_size):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size
    return chunks

def deliver_chunks_to_chatGPT(chunks):
    # Set the initial prompt
    first_prompt=[
        {"role":"system","content":"Act like a document/text loader until you load and remember all content of the following document.","name":"protteveel"},
        {"role":"user","content":"You will receive the document by chunks.","name":"protteveel"},
        {"role":"user","content":"Each chunk start will be noted as [START CHUNK x/TOTAL],","name":"protteveel"},
        {"role":"user","content":" and the end of this chunk will be noted as [END CHUNK x/TOTAL],","name":"protteveel"},
        {"role":"user","content":" where x is number of current chunk and TOTAL is the total number number of chunks you will receive.","name":"protteveel"},
        {"role":"user","content":"You will receive multiple messages with chunks, for each message just reply OK: [CHUNK x/TOTAL].","name":"protteveel"},
        {"role":"user","content":"Do not reply anything else neither explain the text!","name":"protteveel"},
        {"role":"user","content":"Here we go:","name":"protteveel"}]
    # Track whether or not this is the first prompt
    is_first_prompt = True
    # Calculate the total number of chunks    
    total_chunks = len(chunks)
    # Pass each chunk to ChatGPT
    for i, chunk in enumerate(chunks, 1):
        chunk_prompt=[
            {"role":"user","content":"[START CHUNK " + str(i) + "/" + str(total_chunks) +"]","name":"protteveel"},
            {"role":"user","content":"" + chunk + "","name":"protteveel"},
            {"role":"user","content":"[END CHUNK " + str(i) + "/" + str(total_chunks) +"]","name":"protteveel"},
            {"role":"user","content":"Reply with OK: [CHUNK x/TOTAL], do not reply anything else neither explain the text!","name":"protteveel"}]
        if is_first_prompt:
            # Concatenate the two prompts
            prompt= first_prompt + chunk_prompt
            # No longer first prompt
            is_first_prompt = False
        else:
            prompt=chunk_prompt
        # Append the conversation history to the prompt list
        prompt.extend(conversation_history)
        # Try to send the chunks to ChatGPT
        response = None
        while response is None:
            try:
                # Display the request
                write_request(prompt)
                # Update the status
                set_status(WAIT_GPT)
                # Send the chunk to ChatGPT
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
                # Update the status
                set_status(DONE_GPT)
            except Exception as e:
                # Update the status
                set_status("An exception occurred (deliver_chunks_to_chatGPT)")
                # Display the response
                write_exception(str(e))
                # Update the status
                set_status(WAIT_START)
                # Wait before retrying
                time.sleep(CHAT_GPT_WAIT_SEC)
                # Update the status
                set_status(WAIT_DONE)
        # Display the response
        write_response(response)
        # Extract the relevant information or context and append it to the conversation history.
        conversation_history.append({"role": "assistant", "content": response["choices"][0]["message"]["content"]})
        if i < total_chunks:
            # Update the status
            set_status(WAIT_START)
            # Wait before the next call
            time.sleep(CHAT_GPT_WAIT_SEC)
            # Update the status
            set_status(WAIT_DONE)
    # The priming is done
    set_priming_done()

def ask_question():
    # Get the question(s)
    questions = chat_text.get("1.0", tk.END).strip()
    if not questions:
        messagebox.showerror("Ask Question", "Question cannot be empty, try again, please.")
    else:
        # Initialize the prompt
        prompt = []
        # Create the prompt
        lines = questions.split('\n')
        for question in lines:
            new_entry = {"role":"user","content":question,"name":"protteveel"}
            prompt.append(new_entry)
        # Append the conversation history to the prompt list
        prompt.extend(conversation_history)
        # Try to send the chunks to ChatGPT
        response = None
        while response is None:
            try:
                # Display the request
                write_request(prompt)
                # Update the status
                set_status(WAIT_GPT)
                # Send the question(s) to ChatGPT
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
                # Clear the chat field
                chat_text.delete("1.0", tk.END)
                # Update the status
                set_status(DONE_GPT)
            except Exception as e:
                # Update the status
                set_status("An exception occurred (ask_question)")
                # Display the response
                write_exception(str(e))
                # Update the status
                set_status(WAIT_START)
                # Wait before retrying
                time.sleep(CHAT_GPT_WAIT_SEC)
                # Update the status
                set_status(WAIT_DONE)
        # Display the response
        write_response(response)
        # Extract the relevant information or context and append it to the conversation history.
        conversation_history.append({"role": "assistant", "content": response["choices"][0]["message"]["content"]})

def browse_file(entry):
    filepath = filedialog.askopenfilename()
    if filepath:
        entry.delete(0, tk.END)
        entry.insert(tk.END, filepath)

def primer():
    primer = primer_entry.get().strip()
    if not primer:
        messagebox.showerror("Primer Error", "Primer cannot be empty, try again, please.")
    else:
        # Get the file name from the primer
        primer_file_name = os.path.basename(primer)
        # Read the text file
        with open(primer, 'r') as file:
            text = file.read()
        # Split the text into chunks
        chunk_size = CHAT_GPT_MAX_CHUNK
        chunks = split_text_into_chunks(text, chunk_size)
        #Deliver each chunk to ChatGPT
        deliver_chunks_to_chatGPT(chunks)

# Create the main window
window = tk.Tk()
window.title("ChatGPT Query")

# Set the window dimensions
window.geometry("1024x768")  # Set the width and height as desired

# Primer section
primer_label = tk.Label(window, text="Primer:")
primer_label.grid(row=0, column=0, sticky="e")

primer_entry = tk.Entry(window, width=100)
primer_entry.grid(row=0, column=1, padx=5, pady=5)

browse_primer_button = tk.Button(window, text="Browse", command=lambda: browse_file(primer_entry))
browse_primer_button.grid(row=0, column=2, padx=5, pady=5)

primer_button = tk.Button(window, text="Prime", command=primer)
primer_button.grid(row=1, column=2, columnspan=3, padx=5, pady=10)

# Status section
status_label = tk.Label(window, text="Status:")
status_label.grid(row=1, column=0, sticky="e")

status_entry = tk.Entry(window, width=89, bg="black", fg="lightgrey", font=("Courier", 11), state=tk.NORMAL)
status_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

# Request section
request_label = tk.Label(window, text="Request:")
request_label.grid(row=3, column=0, sticky="e")

request_text = tk.Text(window, height=10, width=100, bg="black", fg="lime", font=("Courier", 11), wrap=tk.WORD, state=tk.NORMAL)
request_text.grid(row=3, column=1, padx=5, pady=5, columnspan=2)

request_scrollbar_y = tk.Scrollbar(window, command=request_text.yview)
request_scrollbar_y.grid(row=3, column=3, sticky='ns')
request_text.configure(yscrollcommand=request_scrollbar_y.set)

request_scrollbar_x = tk.Scrollbar(window, command=request_text.xview, orient='horizontal')
request_scrollbar_x.grid(row=4, column=1, columnspan=2, sticky='ew')
request_text.configure(xscrollcommand=request_scrollbar_x.set)

# Response section
response_label = tk.Label(window, text="Response:")
response_label.grid(row=5, column=0, sticky="e")

response_text = tk.Text(window, height=10, width=100, bg="black", fg="aqua", font=("Courier", 11), wrap=tk.WORD, state=tk.NORMAL)
response_text.grid(row=5, column=1, padx=5, pady=5, columnspan=2)

response_scrollbar_y = tk.Scrollbar(window, command=request_text.yview)
response_scrollbar_y.grid(row=5, column=3, sticky='ns')
response_text.configure(yscrollcommand=response_scrollbar_y.set)

response_scrollbar_x = tk.Scrollbar(window, command=request_text.xview, orient='horizontal')
response_scrollbar_x.grid(row=6, column=1, columnspan=2, sticky='ew')
request_text.configure(xscrollcommand=response_scrollbar_x.set)

# Chat section
chat_label = tk.Label(window, text="Chat:")
chat_label.grid(row=7, column=0, sticky="e")

chat_text = tk.Text(window, height=10, width=112, bg="white", fg="darkgrey", font=("Arial", 11), wrap=tk.WORD, state=tk.NORMAL)
chat_text.grid(row=7, column=1, padx=5, pady=5, columnspan=2, sticky='w')

chat_scrollbar_y = tk.Scrollbar(window, command=chat_text.yview)
chat_scrollbar_y.grid(row=7, column=3, sticky='ns')
chat_text.configure(yscrollcommand=chat_scrollbar_y.set)

chat_scrollbar_x = tk.Scrollbar(window, command=chat_text.xview, orient='horizontal')
chat_scrollbar_x.grid(row=8, column=1, columnspan=2, sticky='ew')
chat_text.configure(xscrollcommand=chat_scrollbar_x.set)

# Submit button
submit_button = tk.Button(window, text="Submit", command=ask_question)
submit_button.grid(row=9, column=0, columnspan=3, padx=5, pady=10)

# Start the GUI event loop
window.mainloop()
