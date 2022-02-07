import streamlit as st
from io import StringIO


def get_clippings():
    file = st.file_uploader("Upload Clippings File", type="txt")

    if file:
        stringio = StringIO(file.getvalue().decode("utf-8"))
        return stringio


def main():
    st.title("Kindle Highlights Manager")
    clippings = get_clippings()
    books = []
    if clippings:
        clippings = clippings.read()

        for i in range(0, len(clippings.read), 3):
            st.header(clippings[i])
            st.header(clippings[i + 1])
            st.subheader(clippings[i + 2])

        st.sidebar.selectbox("Books", ("The Power of Habit", "Dune"))


if __name__ == "__main__":
    main()
