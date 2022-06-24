import tempfile
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

from seeker.dashboard.naming import (
    DEFAULT_IMAGE_SEARCH,
    DEFAULT_PROJECT,
    DEFAULT_TEXT_SEARCH,
    MODEL_MAPPING,
    SESSION,
    AppState,
    SearchNames,
)
from seeker.dashboard.sidebar import (
    sidebar_modify_project,
    sidebar_new_project,
    sidebar_select_project,
    sidebar_show_project,
)
from seeker.namings import TYPE_CONF

DEBUG = False

st.set_page_config(
    page_title="Seeker",
    page_icon="👋",  # TODO
)


def content_text():

    model = MODEL_MAPPING[SESSION.config.dtype](conf=SESSION.config)

    def callback():
        SESSION.search = st.session_state[SearchNames.text]

    st.text_area(
        label="Text to search",
        key=SearchNames.text,
        value=DEFAULT_TEXT_SEARCH,
        on_change=callback,
    )

    def callback():
        if st.session_state[SearchNames.document] is not None:
            search_file = st.session_state[SearchNames.document]
            with tempfile.TemporaryDirectory() as tmp_dir:
                file_path = Path(tmp_dir) / search_file.name
                file_path.write_bytes(search_file.getvalue())
                SESSION.search = model.read_file(file_path)

    st.file_uploader(
        label="Document to search",
        type=TYPE_CONF["text"],
        accept_multiple_files=False,
        key=SearchNames.document,
        on_change=callback,
    )

    if isinstance(SESSION.search, str) and SESSION.search.strip() != "":
        st.header("Search results")

        result_fnames = model.search(query=SESSION.search)

        for fname in result_fnames:
            with st.expander(label=fname, expanded=False):
                st.text(model.read_file(model.conf.data_dir / fname))


def load_image(path: "Path"):
    return Image.open(path.as_posix())


def content_image():
    model = MODEL_MAPPING[SESSION.config.dtype](conf=SESSION.config)

    def callback():
        SESSION.search = model.rgb_hex_to_dec(st.session_state[SearchNames.color])

    st.color_picker(
        "Color to search",
        value=DEFAULT_IMAGE_SEARCH,
        key=SearchNames.color,
        on_change=callback,
    )

    def callback():
        if st.session_state[SearchNames.image] is not None:
            search_file = st.session_state[SearchNames.image]
            with tempfile.TemporaryDirectory() as tmp_dir:
                file_path = Path(tmp_dir) / search_file.name
                file_path.write_bytes(search_file.getvalue())
                SESSION.search = model.read_file(file_path)

    st.file_uploader(
        label="Image to search",
        type=TYPE_CONF["image"],
        accept_multiple_files=False,
        key=SearchNames.image,
        on_change=callback,
    )

    if isinstance(SESSION.search, (np.ndarray, np.generic)):
        st.header("Search results")
        result_fnames = model.search(query=SESSION.search)
        for fname in result_fnames:
            with st.expander(label=fname, expanded=False):
                st.image(load_image(model.conf.data_dir / fname))


def main():
    sidebar_pages = {
        AppState.new: sidebar_new_project,
        AppState.modify: sidebar_modify_project,
        AppState.select: sidebar_select_project,
        AppState.show: sidebar_show_project,
    }
    content_pages = {"text": content_text, "image": content_image}

    with st.sidebar:
        sidebar_pages[SESSION.app_state]()

    if DEBUG:
        "session", SESSION

    st.title("Seeker")
    if SESSION.config.name != DEFAULT_PROJECT.name:
        content_pages[SESSION.config.dtype]()
    else:
        st.markdown(Path("description.md").read_text())


if __name__ == "__main__":
    main()
