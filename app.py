import re
import base64
import pandas as pd
import streamlit as st
from collections import namedtuple


class KindleClippings:
    # Define the pattern for each element we want to extract
    BOOK_PATTERN = re.compile(r"^(.*?)[(](.*?)[)]$")
    HIGHLIGHT_PATTERN = re.compile(
        r"- Your (?:Highlight|Bookmark) on(?: page ([\dxvi]+))?(?: \|)? Location (\d+(?:-\d+)?) \| Added on (.*?)$"
    )
    Clipping = namedtuple(
        "Clipping", ["title", "author", "page", "location", "added_on", "highlight"]
    )

    def __init__(self):
        self.clippings = []

    def parse_book_info(self, line):
        author_match = re.search(r"\(([^)]+)\)$", line)
        if author_match:
            author = author_match.group(1)
            title = line[: author_match.start()].strip()
            return title, author

    def parse_highlight_info(self, line):
        match = self.HIGHLIGHT_PATTERN.match(line)
        if match:
            page = match.group(1)
            page = (
                self.roman_to_int(page)
                if isinstance(page, str) and page.isalpha()
                else page
            )
            page = int(page) if page else None
            return page, match.group(2), pd.to_datetime(match.group(3))

    def parse_clipping(self, file_iter):
        try:
            book_info = self.parse_book_info(next(file_iter))
            highlight_info = self.parse_highlight_info(next(file_iter))
            next(file_iter)  # Skip the blank line

            # Read the next line. If it's the separator line, ignore it and set highlight_text to an empty string.
            # Otherwise, treat it as the highlight text.
            line = next(file_iter)
            if line.strip() == "==========":
                highlight_text = ""
            else:
                highlight_text = line.strip()
                next(file_iter)  # Skip the "==========" line

            if book_info and highlight_info:
                return self.Clipping(*book_info, *highlight_info, highlight_text)

        except StopIteration:
            # If we've reached the end of the file, return None
            return None

    @staticmethod
    def create_download_link_CSV(df, filename="data.csv"):
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        b64 = base64.b64encode(csv.encode("utf-8-sig"))
        return f'<a href="data:file/csv;base64,{b64.decode()}" download="{filename}">Download csv file</a>'

    @staticmethod
    def roman_to_int(s):
        roman_numerals = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50,
            "C": 100,
            "D": 500,
            "M": 1000,
        }
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

    @staticmethod
    def normalize_author_name(name):
        parts = name.split(",")
        if len(parts) > 1:
            return " ".join(reversed([part.strip() for part in parts]))
        else:
            return name.strip()

    def extract_clippings(self, uploaded_file):
        if uploaded_file is not None:
            file = (
                str(uploaded_file.read(), "utf-8")
                .replace("\ufeff", "")
                .replace("\r", "")
                .split("\n")
            )
            file_iter = iter(file)
            while True:
                clipping = self.parse_clipping(file_iter)
                if clipping is None:
                    break
                self.clippings.append(clipping)

        df = pd.DataFrame(self.clippings)
        df["author"] = df["author"].apply(self.normalize_author_name)
        df = df[df["highlight"].replace(r"^\s*$", None, regex=True).notna()]

        return df


def main():
    st.title("Kindle Clippings Extractor")

    uploaded_file = st.file_uploader("Upload your MyClippings.txt file", type=["txt"])

    if uploaded_file:
        kc = KindleClippings()
        df = kc.extract_clippings(uploaded_file)

        if df.empty:
            st.write("No data to display.")
        else:
            st.dataframe(df)

        if df.empty:
            st.write("No data to download.")
        else:
            st.markdown(kc.create_download_link_CSV(df), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
