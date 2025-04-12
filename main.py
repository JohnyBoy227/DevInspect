import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    example_tool_registry,
)
import tkinter as tk

# Load .env variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Validate key presence
if not ANTHROPIC_API_KEY:
    raise ValueError("Claude API key not found in .env!")

# Set up config using Claude 3.5 Sonnet
anthropic_config = Config.from_default(
    llm_provider=LLMProvider.ANTHROPIC,
    llm_model_name=LLMModel.CLAUDE_3_5_SONNET,
    anthropic_api_key=ANTHROPIC_API_KEY
)

# Initialize Portia
portia = Portia(config=anthropic_config, tools=example_tool_registry)

# Function to run Portia for code review
def review_code(diff: str):
    # Run the code review using Portia and get the result
    review_result = portia.run(f"Review the following code for readability, function length, naming conventions, and possible improvements:\n{diff}")
    return review_result  # Return the entire review result (log)

# Accept and Reject buttons
def accept_input():
    print("Reviewing changes...")
    portia_comments_box.config(state=tk.NORMAL)
    content = portia_comments_box.get("1.0", tk.END)
    
    # Store the feedback
    stopIndex = content.find(".")
    substring = content[:stopIndex + 1]
    
    accepted_feedback_box.config(state=tk.NORMAL)
    
    # Get current content
    current_content = accepted_feedback_box.get("1.0", tk.END).strip()

    if current_content:
        accepted_feedback_box.insert(tk.END, "\n" + substring)
    else:
        accepted_feedback_box.insert(tk.END, substring)

    accepted_feedback_box.config(state=tk.DISABLED)

    # Now remove the accepted line from the comments box
    remove_line()


def remove_line():
    portia_comments_box.config(state=tk.NORMAL)
    content = portia_comments_box.get("1.0", tk.END)
    stopIndex = content.find(".")
    if stopIndex != -1:
        newContent = content[stopIndex + 1:].lstrip()
        portia_comments_box.delete("1.0", tk.END)
        portia_comments_box.insert("1.0", newContent)
    portia_comments_box.config(state=tk.DISABLED)

# Review changes callback
def review_changes():
    changes = github_changes_box.get("1.0", tk.END).strip()
    if changes:
        # Get the full review including all output from Portia
        review_feedback = (review_code(changes)).model_dump_json(indent=2)
        
        # Display the entire output in the portia_comments_box
        portia_comments_box.config(state=tk.NORMAL)
        portia_comments_box.delete("1.0", tk.END)

        # Before inserting feedback, we extract the relevant section
        index = review_feedback.find("final_output")
        substring = ""

        if index != -1: 
            review_feedback = review_feedback[index + len("final_output"):]

        index = review_feedback.find("summary")
        
        if index != -1: 
            review_feedback = review_feedback[index + len("summary"):]

        start = review_feedback.find('": ')
        if start != -1:
            start += 4
            end = len(review_feedback) - 13
            value = review_feedback[start:end]

        sentences = [s.strip() for s in value.split('.') if s.strip()]

        for sentence in sentences:
            portia_comments_box.insert(tk.END, sentence + '.\n')

        portia_comments_box.config(state=tk.DISABLED)
    else:
        portia_comments_box.config(state=tk.NORMAL)
        portia_comments_box.insert(tk.END, "No changes to review.\n")
        portia_comments_box.config(state=tk.DISABLED)

# Tkinter GUI Setup
window = tk.Tk()
window.title("Portia Code Review Tool")
window.geometry("800x600")  # Initial window size
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Create a label
label = tk.Label(window, text="Enter your code or changes for review:")
label.grid(row=0, column=0, pady=10, sticky="nsew")

# Multi-line text box for code/changes to review
github_changes_box = tk.Text(window, height=10)
github_changes_box.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

# Create buttons with expand behavior
review_button = tk.Button(window, text="Review Changes", command=review_changes)
review_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

# Multi-line text box to display Portia comments
portia_comments_box = tk.Text(window, height=5)
portia_comments_box.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
portia_comments_box.config(state=tk.DISABLED)

# Multi-line text box to load accepted feedback
accepted_feedback_box = tk.Text(window, height=5)
accepted_feedback_box.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
accepted_feedback_box.config(state=tk.DISABLED)

# Create a Frame to hold the buttons (use grid for this)
button_frame = tk.Frame(window)
button_frame.grid(row=5, column=0, pady=10, sticky="ew")  # Use grid for button frame

# Accept and Reject buttons (use grid for buttons inside button_frame)
accept_button = tk.Button(button_frame, text="Accept Feedback", command=accept_input)
accept_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

reject_button = tk.Button(button_frame, text="Reject Feedback", command=remove_line)
reject_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

# Ensure equal column width for both buttons
button_frame.grid_columnconfigure(0, weight=1)  # Make column 0 expandable (for Accept button)
button_frame.grid_columnconfigure(1, weight=1)  # Make column 1 expandable (for Reject button)

# Run the application
window.mainloop()
