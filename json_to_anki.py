import os
import random
import shutil

import genanki
import json


# This function parses a JSON file and returns a list of sections.
# Each section will get its own Anki note.
# The tuple (front, back) represents a section.
def parse_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    sections = []
    for item in data:
        front = item.get('front', '')
        back = item.get('back', '')
        sections.append((front, back))

    return sections


def main():
    # Delete 'output' dir if it exists
    # This is needed to clean up the directory before creating a new deck
    if os.path.exists('output'):
        shutil.rmtree('output')

    # Create 'output' dir
    os.makedirs('output')

    # Create a new Anki deck
    deck = genanki.Deck(
        deck_id=random.randint(1000000000, 9999999999),  # This is a random ID for the deck
        name='Atomic Habits',
        description='Anki deck for Atomic Habits generated from JSON generated by ChatGPT.',
    )

    model = genanki.Model(
        random.randint(1000000000, 9999999999),
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

    sections = parse_json_file('data/atomic_habits.json')
    for front, back in sections:
        note = genanki.Note(
            model=model,
            fields=[front, back],
            tags=['atomic_habits'],
        )
        deck.add_note(note)


    # Save the deck to a file
    genanki.Package(deck).write_to_file('output/atomichabits.apkg')


if __name__ == "__main__":
    main()