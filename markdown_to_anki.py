import glob
import os
import shutil

import markdown
import genanki
from bs4 import BeautifulSoup


def parse_markdown_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, 'html.parser')

    sections = []
    current_h1_tag = ''
    current_h2_tag = ''
    current_body = ''

    # Replace the src attribute of img tags with just the filename
    for img in soup.find_all('img'):
        img['src'] = os.path.basename(img['src'])

    for tag in soup:
        if tag.name == 'h1':
            current_h1_tag = tag.text
        elif tag.name == 'h2':
            # If there's a previous h2 tag, append it and its body to the sections
            if current_h2_tag:
                sections.append((current_h1_tag, current_h2_tag, current_body))
            # Start a new section
            current_h2_tag = tag.text
            current_body = ''
        else:
            # Append other tags to the body of the current section
            current_body += str(tag)

    # Append the last section
    if current_h2_tag:
        sections.append((current_h1_tag, current_h2_tag, current_body))

    return sections


def main():
    # Delete 'output' dir if it exists
    if os.path.exists('output'):
        shutil.rmtree('output')

    # Create 'output' dir
    os.makedirs('output')

    # Copy all .png images from 'designdeck/res' to 'output' directory
    for file in glob.glob('designdeck/res/*.png'):
        shutil.copy(file, 'output')

    # Create a new Anki deck
    deck = genanki.Deck(
        deck_id=2059400110,  # This is a random ID for the deck
        name='Design Deck',
        description='Anki deck generated from markdown https://github.com/teivah/designdeck?tab=readme-ov-file.',
    )

    model = genanki.Model(
        1607392319,  # This is a random ID for the model
        'Simple Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}<p style="font-size:15px;font-style:italic;">{{Tags}}</p>',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ],
        css=".card {font-family: arial; font-size: 20px; color: black; background-color: white;}"
    )

    markdown_files = [f for f in os.listdir('designdeck') if
                      f.endswith('.md') and f != 'README.md' and f != 'LICENSE.md']
    for markdown_file in markdown_files:
        sections = parse_markdown_file(os.path.join('designdeck', markdown_file))
        for tag, title, body in sections:
            note = genanki.Note(
                model=model,
                fields=[title, body],
                tags=[tag],
            )
            deck.add_note(note)

    # Get a list of all media files in the 'output' directory
    media_files = [os.path.join('output', f) for f in os.listdir('output') if f.endswith('.png')]
    # Save the deck to a file
    genanki.Package(deck, media_files=media_files).write_to_file('output/designdeck.apkg')


if __name__ == "__main__":
    main()
