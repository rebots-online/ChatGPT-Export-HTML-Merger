# ChatGPT-Export-HTML-Merger
Ever wish the ChatGPT Data Export was in some way navigable, if not useful? :p
Copyright (C)2024 Robin L. M. Cheung, MBA
Licensed under MIT License; see  LICENSE.txt for details.

# Conversations Export to HTML

This project provides a tool to convert exported ChatGPT conversations from a zip file into HTML files, styled with a chat/SMS theme. Each conversation is displayed with clear speaker differentiation and a Table of Contents is generated for easy navigation.

## Features
- **Extracts conversations** from a JSON file within the zip archive.
- **Converts messages** to HTML format, providing a readable chat interface.
- **Generates an index** (Table of Contents) for easy access to individual conversations.

## Installation
Ensure that Python 3.x is installed on your system and then clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

## Usage
Run the script from the command line with the path to the zip file of conversations:

```bash
python mergerv10.py <path-to-zip-file>
```

This will generate an `index.html` file along with individual conversation HTML files in a `Conversations_HTML` directory.

## Requirements
- `argparse`
- `json`
- `os`
- `tempfile`
- `datetime`
- `zipfile`
- `concurrent.futures`
- `itertools`
- `tqdm`

## Contributing
Feel free to send a pull request or open an issue for any bugs or feature requests.

## License
This project is licensed under the MIT License.
