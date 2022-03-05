import re
import streamlit as st
from datetime import datetime
from collections import defaultdict

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
    book_dict = defaultdict()
    highlights = []

    data = clean_data(text)

    for d in data:
        highlight_dict = defaultdict()
        n_high = len(highlights)

        # Regex for getting book name and book authors from first position in text
        pattern = re.search(r"^(.+) \((.+|.+;.+)\)$", d[0])
        book_dict["name"] = pattern.group(1)
        book_dict["authors"] = clean_authors(pattern.group(2))

        # Regex for getting highlight location, and timestamp from second position in text
        pattern = re.search(
            r"^.+ ([0-9]+-[0-9]+) \| .+ ([a-zA-Z]+ [0-9]{0,2}, [0-9]{4} [0-9]{0,2}:[0-9]{0,2}:[0-9]{0,2} (PM|AM))$",
            d[1],
        )

        highlight_dict["text"] = d[2]
        highlight_dict["location"] = pattern.group(1)
        timestamp_str = pattern.group(2)
        highlight_dict["added_timestamp"] = datetime.strptime(
            timestamp_str, "%B %d, %Y %I:%M:%S %p"
        )

        book_diff_prev_book = (
            True
            if len(highlights) == 0
            else book_dict["name"] != highlights[n_high - 1]["name"]
        )
        # If it's the first book or the book is different from the previous one
        if n_high == 0 or book_diff_prev_book:
            book_dict["highlights"] = []

        book_dict["highlights"].append(highlight_dict.copy())

        if book_diff_prev_book:
            highlights.append(book_dict.copy())

    return highlights


def construct_sidebar(books, authors):
    with st.sidebar:
        st.selectbox("Books", books)


def main():

    st.title("Kindle Highlights Manager")
    file = st.file_uploader("Upload Clippings File", type="txt")
    if file is not None:
        raw_text = str(file.read(), "utf-8").replace("\ufeff", "")
        highlights = get_highlights(raw_text)

        books_names = [h["name"] for h in highlights]
        books_authors = [h["authors"] for h in highlights]

        construct_sidebar(books_names, books_authors)


if __name__ == "__main__":
    main()
