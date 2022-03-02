import re
from pygments import highlight
import streamlit as st
from pprint import pprint

# Clean raw text by removing lines, tabs and other unnecessary whitespaces
def clean_data(text):
    base_dict = {"book_name": "", "authors": [], "highlights": {}}
    highlight_dict = {"highlight:": "", "location": "", "added_timestamp": ""}
    highlights = []
    # Remove "=" that separates the highlights
    cleaned_text = [t.splitlines() for t in re.split(r"=+", text)]

    # Remove empty elements in list
    cleaned_text = [list(filter(None, t)) for t in cleaned_text]

    return cleaned_text


def main():

    st.title("Kindle Highlights Manager")
    file = st.file_uploader("Upload Clippings File", type="txt")
    if file is not None:
        raw_text = str(file.read(), "utf-8")
        st.text(raw_text)
        highlights = clean_data(raw_text)

        pprint(highlights)


if __name__ == "__main__":
    main()
