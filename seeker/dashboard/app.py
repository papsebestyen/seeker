import streamlit as st
from seeker.project_config import ProjectConfig, load_all_config

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
if "query_search" not in st.session_state:
    st.session_state["query_search"] = None


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
    st.text_input(label="Text search", key="query_search")


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

    content_pages["text"]()

    if DEBUG:
        st.write(st.session_state["app_state"])
        st.write(st.session_state["project"])
        st.write(st.session_state["project_name"])
        st.write(st.session_state["project_type"])


# if project_conf is not None:
#     from seeker.search.numerical.preprocess import preprocess_numeric_data, read_numeric_data, search_numeric
#     search_input = st.slider(label='Search for num:')
#     data = read_numeric_data(project_conf)
#     data.shape
#     tree = preprocess_numeric_data(data)
#     tree
#     dist, ind = search_numeric(tree, [search_input, search_input, search_input])
#     ind

if __name__ == "__main__":
    main()
