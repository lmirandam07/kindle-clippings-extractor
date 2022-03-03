import re
import streamlit as st
from datetime import datetime
from pprint import pprint

# Clean raw text by removing lines, tabs and other unnecessary whitespaces
def clean_data(text):
    # Remove "=" that separates the highlights
    clean_text = [t.splitlines() for t in re.split(r"={10}", text)]

    # Remove empty elements in list and sort by books name
    clean_text = list(filter(None, [list(filter(None, t)) for t in clean_text]))

    # Remove incomplete highlights
    clean_text = [x for x in clean_text if len(x) == 3]
    # Sort by book name
    clean_text.sort()

    return clean_text


def clean_authors(authors):
    clean_authors = []

    # Check if there is more than one author
    authors_list = authors.split(";") if ";" in authors else [authors]
    for author in authors_list:

        # Swap names and last names to put names first
        if re.match(r"[a-zA-Z]+, [a-zA-Z]", author):
            author = author.split(",")
            clean_authors.append(f"{author[1].strip()} {author[0]}")

        else:
            clean_authors.append(author)

    return clean_authors


def get_highlights(text):
    book_dict = {"name": "", "authors": [], "highlights": {}}
    highlight_dict = {"text:": "", "location": "", "added_timestamp": ""}
    highlights = []

    data = clean_data(text)
    pprint(data[:5])

    for i, d in enumerate(data):
        # Regex for getting book name and book authors from first position in text
        pattern = re.search(r"^(.+) \((.+|.+;.+)\)$", d[0])
        book_name = pattern.group(1)
        book_authors = clean_authors(pattern.group(2))

        # Regex for getting highlight location, and timestamp from second position in text
        pattern = re.search(
            r"^.+ ([0-9]+-[0-9]+) \| .+ ([a-zA-Z]+ [0-9]{0,2}, [0-9]{4} [0-9]{0,2}:[0-9]{0,2}:[0-9]{0,2} (PM|AM))$",
            d[1],
        )

        high_location = pattern.group(1)

        # TODO turn timestamp string to datetime: https://thispointer.com/python-how-to-convert-a-timestamp-string-to-a-datetime-object-using-datetime-strptime/
        high_timestamp = pattern.group(2)
        high_text = d[2]

        if book_dict["name"] == "":
            book_dict["name"] = book_name
            book_dict["authors"].append(book_authors)

        if book_dict["name"] == book_name:
            # TODO Save highlight in book_dict
            pass
        else:
            highlights.append(book_dict.copy())
            book_dict["name"] = book_name
            book_dict["authors"] = []
            book_dict["authors"].append(book_authors)
            # TODO Save highlight in book_dict

        if i == len(data) - 1:
            highlights.append(book_dict)

    st.json(highlights)

    return highlights


def main():

    st.title("Kindle Highlights Manager")
    file = st.file_uploader("Upload Clippings File", type="txt")
    if file is not None:
        raw_text = str(file.read(), "utf-8").replace("\ufeff", "")

        highlights = get_highlights(raw_text)

        # pprint(highlights)


if __name__ == "__main__":
    main()
