import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from zipfile import ZipFile
from concurrent.futures import ThreadPoolExecutor
import itertools
from tqdm import tqdm


def process_conversations(conversation):
    # Initialize an empty string for Markdown content
    md = ""
    # Retrieve the mapping of conversation nodes
    nodes = conversation['mapping']
    # Extract the root ID of the conversation, defaulting to None if not present
    root_id = conversation.get('root', None)
    # If root ID is absent, get the first node as the root
    if root_id is None and nodes:
        root_id = next(iter(nodes))
    # Initialize a queue for breadth-first traversal of conversation nodes
    queue = [root_id]
    # List to hold all messages in the conversation
    messages = []
    
    while queue:
        # Pop the first node from the queue
        node_id = queue.pop(0)
        # Get the corresponding node data
        node = nodes[node_id]
        # Extract the message for this node
        message = node['message']
        # Determine the role of the author (user or assistant)
        author_role = message['author']['role'] if message is not None else None
        # Initialize an empty string for message content
        content = ""
        if message is not None:
            # Get the parts of the message, defaulting to an empty dict
            content_parts = message['content'].get('parts', [{}])
            # Concatenate all content parts into a single string
            for part in content_parts:
                if isinstance(part, str):
                    content += part
        # Append the message based on the author role
        if author_role == 'user':
            messages.append(('Me', content))
        elif author_role == 'assistant':
            messages.append(('CG', content))
        # Add child nodes to the queue for processing
        queue.extend(node['children'])
    
    return messages

def save_to_html(conversation, messages, output_dir):
    # Prepare the HTML template for displaying the conversation
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Conversation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                padding: 20px;
            }}
            .chat-container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .chat-bubble {{
                padding: 10px 15px;
                border-radius: 20px;
                margin-bottom: 10px;
                display: inline-block;
                max-width: 80%;
            }}
            .user {{
                background-color: #daf8cb;
                margin-right: auto;
            }}
            .assistant {{
                background-color: #f1f0f0;
                margin-left: auto;
            }}
            .timestamp {{
                font-size: 0.8em;
                color: gray;
                margin-bottom: 5px;
            }}
            .speaker {{
                font-weight: bold;
                margin-bottom: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="chat-container">
    """
    
    # Add messages with speaker demarcation to HTML content
    for role, content in messages:
        speaker = "Me" if role == 'Me' else "CG"
        html_content += f'<div class="speaker">{speaker}:</div>\n'
        if role == 'Me':
            html_content += f'<div class="chat-bubble user">{content}</div>\n'
        elif role == 'CG':
            html_content += f'<div class="chat-bubble assistant">{content}</div>\n'

    # Close HTML content after messages
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Generate the filename, sanitizing the title
    title = conversation.get('title', 'Untitled_Conversation')
    file_name = sanitize_filename(title) + ".html"
    # Create file path in the output directory
    file_path = os.path.join(output_dir, file_name)
    
    # Write the HTML content to the new file
    with open(file_path, "w") as f:
        f.write(html_content)
    
    return file_name

def sanitize_filename(filename):
    # Removes invalid characters from a filename
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

def create_index_html(conversations, output_dir, html_files):
    # Create the index.html file for linking to each conversation
    index_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Table of Contents</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                padding: 20px;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                margin: 5px 0;
            }}
            a {{
                text-decoration: none;
                color: #1a73e8;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <h1>Conversations Index</h1>
        <ul>
    """
    
    # Populate the index with titles and file links
    for conversation, html_file in zip(conversations, html_files):
        title = conversation.get('title', 'Untitled Conversation')
        index_content += f'<li><a href="{html_file}">{title}</a></li>\n'
    
    # Close the unordered list in HTML
    index_content += """
        </ul>
    </body>
    </html>
    """
    
    # Write the index content to index.html
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(index_content)

def main(zip_path):
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Unzip the archive to the temporary directory
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        # Open the conversations.json file to read the conversation data
        with open(os.path.join(tmp_dir, 'conversations.json')) as f:
            data = json.load(f)

        # Create output directory for HTML files
        output_dir = os.path.join(os.getcwd(), "Conversations_HTML")
        os.makedirs(output_dir, exist_ok=True)

        # Add progress bar and process conversations
        total_conversations = len(data)
        html_files = []
        with ThreadPoolExecutor() as executor:
            # Process each conversation concurrently
            for conversation in tqdm(data, total=total_conversations):
                messages = process_conversations(conversation)
                html_file = save_to_html(conversation, messages, output_dir)
                html_files.append(html_file)
        
        # Create the index.html (Table of Contents)
        create_index_html(data, output_dir, html_files)


if __name__ == "__main__":
    # Create the argument parser to handle command-line arguments
    parser = argparse.ArgumentParser(description="Convert a ChatGPT conversation export into HTML files with a chat/SMS theme.")
    parser.add_argument('zip_file', help="Path to the zip file containing the conversation export.")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Execute the main function with the provided zip file path
    main(args.zip_file)
