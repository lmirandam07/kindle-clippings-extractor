import streamlit as st
from io import StringIO


def clean_text(text):
    highlights = [l.splitlines() for l in text]

    return [list(filter(None, h)) for h in highlights]


def main():
    st.title("Kindle Highlights Manager")
    file = st.file_uploader("Upload Clippings File", type="txt")
    if file is not None:
        raw_text = str(file.read(), "utf-8")
        st.text(raw_text)

        raw_text = raw_text.split("==========")

        highlights = clean_text(raw_text)

        print(highlights)


if __name__ == "__main__":
    main()
