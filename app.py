import re
import base64
from pprint import pprint
import pandas as pd
import streamlit as st
from collections import namedtuple

# Define the pattern for each element we want to extract
book_pattern = re.compile(r"^(.*?)\((.*?)\)$")
highlight_pattern = re.compile(
    r"- Your Highlight on(?: page ([\dxvi]+))?(?: \|)? Location (\d+(?:-\d+)?) \| Added on (.*?)$"
)


# Define a namedtuple to hold the information for a single clipping
Clipping = namedtuple(
    "Clipping", ["title", "author", "page", "location", "added_on", "highlight"]
)


def parse_book_info(line):
    """Parse the book title and author from a line."""
    match = book_pattern.match(line)
    if match:
        return match.group(1).strip(), match.group(2).strip()


def parse_highlight_info(line):
    """Parse the page, location, and date from a line."""
    match = highlight_pattern.match(line)
    print(line)
    if match:
        page = match.group(1)
        page = roman_to_int(page) if isinstance(page, str) and page.isalpha() else page
        page = int(page) if page else None
        return page, match.group(2), pd.to_datetime(match.group(3))


def parse_clipping(file):
    """Read and parse a single clipping from the file."""
    try:
        book_info = parse_book_info(next(file))
        highlight_info = parse_highlight_info(next(file))
        # Skip potential blank lines
        while True:
            line = next(file).strip()
            if line:
                highlight_text = line
                break
        # Skip lines until the next "==========" line
        while True:
            line = next(file)
            if line.strip() == "==========":
                break
        if book_info and highlight_info:
            return Clipping(*book_info, *highlight_info, highlight_text)
    except StopIteration:
        # If we've reached the end of the file, return None
        return None


def roman_to_int(s):
    """Converts a Roman numeral string to an integer."""
    roman_numerals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    s = s.upper()
    total = 0
    while s:
        if len(s) == 1 or roman_numerals[s[0]] >= roman_numerals[s[1]]:
            total += roman_numerals[s[0]]
            s = s[1:]
        else:
            total += roman_numerals[s[1]] - roman_numerals[s[0]]
            s = s[2:]
    return total


def create_download_link_csv(df, filename="data.csv"):
    """Generates a link allowing the data in a given panda dataframe to be downloaded as csv"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode())
    return f'<a href="data:file/csv;base64,{b64.decode()}" download="{filename}">Download csv file</a>'


def main():
    # Initialize a list to store the Clipping objects
    clippings = []

    st.title("Kindle Clippings Extractor")

    uploaded_file = st.file_uploader("Upload your MyClippings.txt file", type=["txt"])
    if uploaded_file is not None:
        file = (
            str(uploaded_file.read(), "utf-8")
            .replace("\ufeff", "")
            .replace("\r", "")
            .split("\n")
        )
        file_iter = iter(file)
        while True:
            clipping = parse_clipping(file_iter)
            if clipping is None:
                break
            clippings.append(clipping)

    # Create a DataFrame from the list of Clipping objects
    df = pd.DataFrame(clippings)

    if df.empty:
        st.write("No data to display.")
    else:
        st.dataframe(df)

    if st.button("Download DataFrame as CSV"):
        if df.empty:
            st.write("No data to download.")
        else:
            st.markdown(create_download_link_csv(df), unsafe_allow_html=True)

    return df


if __name__ == "__main__":
    df = main()
