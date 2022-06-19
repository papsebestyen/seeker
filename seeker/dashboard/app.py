import streamlit as st
from seeker.project_config import ProjectConfig, load_all_config
from seeker.dashboard.naming import (
    SearchNames,
    AppState,
    DEFAULT_TEXT_SEARCH,
    DEFAULT_IMAGE_SEARCH,
    DEFAULT_PROJECT,
)

from seeker.search.text import TextModel  # change the import to image or text model

import tempfile
from pathlib import Path

MODEL_MAPPING = {"text": TextModel, "image": None}

DEBUG = True

st.set_page_config(
    page_title="Seeker",
    page_icon="👋",
)

if "app_state" not in st.session_state:
    st.session_state["app_state"] = AppState.select
if "config" not in st.session_state:
    st.session_state["config"] = DEFAULT_PROJECT


def update_project(conf: ProjectConfig, filenames):
    model = TextModel(conf=conf)
    model.extend_vectors(
        model.preprocess_all([(model.conf.data_dir / fp.name) for fp in filenames])
    )
    model.build_tree()


def sidebar_new_project():
    st.text_input(label="Project name", key="project_name", value=DEFAULT_PROJECT.name)
    st.selectbox(
        label="Project type",
        key="project_type",
        options=["text", "image"],
        index=0,  # TODO
    )

    st.file_uploader(
        label="Files",
        key="file_uploader",
        # type=TYPE_CONF[project_type],
        accept_multiple_files=True,
    )

    def callback():
        conf = ProjectConfig(
            name=st.session_state["project_name"],
            dtype=st.session_state["project_type"],
        )
        if conf.name != DEFAULT_PROJECT.name:
            conf.save_config()

            uploaded_files = st.session_state["file_uploader"]
            if uploaded_files:  # TODO Print when upload is not finished
                for file in uploaded_files:
                    (conf.data_dir / file.name).write_bytes(file.getvalue())
                update_project(conf=conf, filenames=uploaded_files)

                st.session_state["app_state"] = AppState.select

            st.session_state["config"] = conf

    st.button("Submit", on_click=callback)

    def callback():
        st.session_state["app_state"] = AppState.select
        st.session_state["config"] = DEFAULT_PROJECT

    st.button("Cancel", on_click=callback)


def sidebar_modify_project():
    conf = st.session_state["config"]
    st.text_input(label="Project name", value=conf.name, disabled=True)
    st.text_input(label="Project type", value=conf.dtype, disabled=True)

    st.file_uploader(
        label="Files",
        key="file_uploader",
        # type=TYPE_CONF[project_type],
        accept_multiple_files=True,
    )

    def callback():
        uploaded_files = st.session_state["file_uploader"]
        if uploaded_files:  # TODO Print when upload is not finished

            for file in uploaded_files:
                (conf.data_dir / file.name).write_bytes(file.getvalue())
            update_project(st.session_state["config"], uploaded_files)

            st.session_state["app_state"] = AppState.select

    st.button("Submit", on_click=callback)

    def callback():
        st.session_state["app_state"] = AppState.select
        st.session_state["config"] = DEFAULT_PROJECT

    st.button("Cancel", on_click=callback)


def sidebar_show_project():
    conf = st.session_state["config"]
    st.write(f"Name: {conf.name}")
    st.write(f"Type: {conf.dtype}")
    st.write(f"Files: {conf.get_file_count()}")  # TODO
    st.write(f"Size: X MB")  # TODO

    def callback():
        st.session_state["app_state"] = AppState.modify

    st.button(label="Modify", on_click=callback)


def sidebar_select_project():
    st.selectbox(
        label="Select project",
        key="config",
        options=[DEFAULT_PROJECT, *load_all_config()],
        format_func=lambda conf: conf.name,
    )

    if st.session_state["config"] != DEFAULT_PROJECT.name:
        sidebar_show_project()

    def callback():
        st.session_state["app_state"] = AppState.new

    st.button(label="New project", on_click=callback)


def content_text():

    if "search" not in st.session_state:
        st.session_state["search"] = DEFAULT_TEXT_SEARCH

    conf = st.session_state["config"]
    model = TextModel(conf=conf)  # Change this for image or text model

    def callback():
        st.session_state["search"] = st.session_state[SearchNames.text]

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
                st.session_state["search"] = model.read_file(file_path)

    st.file_uploader(
        label="Document to search",
        type=None,
        accept_multiple_files=False,
        key=SearchNames.document,
        on_change=callback,
    )

    st.header("Search results")

    result_fnames = model.search(query=st.session_state["search"])

    for fname in result_fnames:
        with st.expander(label=fname, expanded=False):
            st.text(model.read_file(model.conf.data_dir / fname))


def content_image():
    ...


def main():
    sidebar_pages = {
        AppState.new: sidebar_new_project,
        AppState.modify: sidebar_modify_project,
        AppState.select: sidebar_select_project,
    }
    content_pages = {"text": content_text, "image": content_image}

    with st.sidebar:
        sidebar_pages[st.session_state["app_state"]]()

    if DEBUG:
        "app_state: ", st.session_state["app_state"]
        "config: ", st.session_state["config"]

    st.title("Seeker content")
    if st.session_state["config"].name != DEFAULT_PROJECT.name:
        content_pages[st.session_state["config"].dtype]()


if __name__ == "__main__":
    main()
