import glob
import os
import shutil

import markdown
import genanki
from bs4 import BeautifulSoup


# This function parses a markdown file and returns a list of sections.
# Each section will get its own Anki note.
# The tuple (title, body) represents a section.
def parse_markdown_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, 'html.parser')

    sections = []
    current_h2_tag = ''
    current_body = ''

    # Replace the src attribute of img tags with just the filename
    # This is needed because Anki requires all media files to be in the same directory as the deck
    for img in soup.find_all('img'):
        img['src'] = os.path.basename(img['src'])

    for tag in soup:
        if tag.name == 'h2':
            # If there's a previous h2 tag, append it and its body to the sections
            if current_h2_tag:
                sections.append((current_h2_tag, current_body))
            # Start a new section
            current_h2_tag = tag.text
            current_body = ''
        else:
            # Append other tags to the body of the current section
            current_body += str(tag)

    # Append the last section
    if current_h2_tag:
        sections.append((current_h2_tag, current_body))

    return sections


def main():
    # Delete 'output' dir if it exists
    # This is needed to clean up the directory before creating a new deck
    if os.path.exists('output'):
        shutil.rmtree('output')

    # Create 'output' dir
    os.makedirs('output')

    # Copy all .png images from 'designdeck/res' to 'output' directory
    # Anki requires all media files to be in the same directory as the deck.
    # We will create a new deck with the images in the 'output' directory.
    # For more info:
    #   - https://github.com/kerrickstaley/genanki/blob/main/README.md
    #   - https://gist.github.com/jlumbroso/e17abff02d89be04240072191af09ab2
    for file in glob.glob('designdeck/res/*.png'):
        shutil.copy(file, 'output')

    # Create a new Anki deck
    deck = genanki.Deck(
        deck_id=2059400110,  # This is a random ID for the deck
        name='Design Deck',
        description='Anki deck generated from https://github.com/teivah/designdeck?tab=readme-ov-file.',
    )

    model = genanki.Model(
        1607392319,  # This is a random ID for the model
        'Simple Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        # Templates and CSS are copied from the "Basic" model in Anki
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}<p style="font-size:15px;font-style:italic;">{{Tags}}</p>',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ],
        css=".card {font-family: arial; font-size: 20px; color: black; background-color: white;}"
    )

    # Get a list of all markdown files that will be converted to Anki notes
    markdown_files = [f for f in os.listdir('designdeck') if
                      f.endswith('.md') and f != 'README.md' and f != 'LICENSE.md']

    for markdown_file in markdown_files:
        name_without_extension = os.path.splitext(markdown_file)[0]
        sections = parse_markdown_file(os.path.join('designdeck', markdown_file))
        for title, body in sections:
            note = genanki.Note(
                model=model,
                fields=[title, body],
                tags=[name_without_extension],
            )
            deck.add_note(note)

    # Get a list of all media files in the 'output' directory
    media_files = [os.path.join('output', f) for f in os.listdir('output') if f.endswith('.png')]
    # Save the deck to a file
    genanki.Package(deck, media_files=media_files).write_to_file('output/designdeck.apkg')


if __name__ == "__main__":
    main()
