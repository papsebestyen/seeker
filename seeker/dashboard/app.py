import streamlit as st
from seeker.project_config import ProjectConfig, load_all_config
# from seeker.search.numeric import NumericModel #change the import to image or text model
from seeker.search.text import TextModel #change the import to image or text model

st.set_page_config(
    page_title="Seeker",
    page_icon="👋",
)

DEBUG = True
DEFAULT_PROJECT = "Select project"


if "app_state" not in st.session_state:
    st.session_state["app_state"] = "select_project"
if "project" not in st.session_state:
    st.session_state["project"] = DEFAULT_PROJECT
if "project_name" not in st.session_state:
    st.session_state["project_name"] = None
if "project_type" not in st.session_state:
    st.session_state["project_type"] = None
# if "query_search" not in st.session_state:
#     st.session_state["query_search"] = ""


def sidebar_new_project():
    st.text_input(label="Project name", key="project_name", value="")
    st.selectbox(label="Project type", key="project_type", options=["text", "image"])
    uploaded_files = st.file_uploader(
        label="Files",
        key="file_uploader",
        # type=TYPE_CONF[project_type],
        accept_multiple_files=True,
    )

    def callback():
        project_name = st.session_state["project_name"]
        project_type = st.session_state["project_type"]
        if project_name != "" and project_name is not None:
            conf = ProjectConfig(name=project_name, dtype=project_type)
            conf.save_config()
        if uploaded_files is not None:
            for file in uploaded_files:
                (conf.data_dir / file.name).write_bytes(file.getvalue())
            model = NumericModel(conf=conf)
            model.extend_vectors(
                model.preprocess_all(
                    [(model.conf.data_dir / fp.name) for fp in uploaded_files]
                )
            )
            model.build_tree()

        st.session_state["app_state"] = "select_project"
        st.session_state["project"] = project_name

    st.button("Submit", on_click=callback)

    def callback():
        st.session_state["app_state"] = "select_project"
        st.session_state["project"] = DEFAULT_PROJECT

    st.button("Cancel", on_click=callback)


def sidebar_show_project():
    conf = ProjectConfig.from_name(name=st.session_state["project"])
    st.write(f"Name: {conf.name}")
    st.write(f"Type: {conf.dtype}")
    st.write(f"Files: {conf.get_file_count()}")  # TODO
    st.write(f"Size: X MB")  # TODO

    def callback():
        ...  # TODO

    st.button(label="Modify", on_click=callback)


def sidebar_select_project():
    st.selectbox(
        label="Select project",
        key="project",
        options=[DEFAULT_PROJECT, *[c.name for c in load_all_config()]],
    )

    if (
        st.session_state["project"] != DEFAULT_PROJECT
        and st.session_state["project"] is not None
    ):
        sidebar_show_project()

    def callback():
        st.session_state["app_state"] = "new_project"

    st.button(label="New project", on_click=callback)


def content_text():
    st.text_area(
        label="Text to search",
        key="query_search",
        value="10 20 50",
    )

    project_name = st.session_state["project"]
    conf = ProjectConfig.from_name(name=project_name)
    model = TextModel(conf=conf) # Change this for image or text model
    result_fnames = model.search(query=st.session_state["query_search"])

    for fname in result_fnames:
        with st.container():
            st.caption(fname)
            st.text(model.read_file(model.conf.data_dir / fname))


def content_image():
    ...


def main():
    sidebar_pages = {
        "new_project": sidebar_new_project,
        "select_project": sidebar_select_project,
    }
    content_pages = {"text": content_text, "image": content_image}

    with st.sidebar:
        sidebar_pages[st.session_state["app_state"]]()

    if DEBUG:
        st.write(st.session_state["app_state"])
        st.write(st.session_state["project"])
        st.write(st.session_state["project_name"])
        st.write(st.session_state["project_type"])
        # st.write(st.session_state["query_search"])

    st.title("Seeker content")
    if st.session_state["project"] != DEFAULT_PROJECT:
        content_pages["text"]()

if __name__ == "__main__":
    main()
