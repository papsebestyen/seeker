import streamlit as st
from seeker.project_config import ProjectConfig, load_all_config


def set_session_state(state_name: str, value):
    st.session_state[state_name] = value


st.set_page_config(
    page_title="Seeker",
    page_icon="👋",
)

st.title("Seeker")

st.write("Select a project or upload a new one.")

# UPLOAD PROJECT
project_conf = st.selectbox(
    label="Select project",
    options=["Select a project", *load_all_config()],
    format_func=lambda opt: opt.name if isinstance(opt, ProjectConfig) else opt,
)

if isinstance(project_conf, ProjectConfig):
    with st.sidebar:
        st.write(f"Name: {project_conf.name}")
        st.write(f"Type: text")  # TODO
        st.write(f"Files: XY")  # TODO
        st.write(f"Size: X MB")  # TODO

_, col2, _, col4, _ = st.columns(5)

btn_modify = col2.button(
    label="Modify",
    disabled=True if not isinstance(project_conf, ProjectConfig) else False,
)  # TODO

if "new_project" not in st.session_state:
    set_session_state("new_project", False)

btn_new = col4.button(label="New project")
if btn_new:
    set_session_state("new_project", True)

ph = st.empty()
if st.session_state["new_project"]:
    # key='new_project_form'
    with ph.form(key="new_project_form"):
        project_name = st.text_input(label="Project name", value="")

        uploaded_files = st.file_uploader(
            "Upload files",
            type=["txt"],
            accept_multiple_files=True,
        )

        _, col2, _, col4, _ = st.columns(5)
        btn_submit = col2.form_submit_button(
            "Submit",
        )
        btn_cancel_submit = col4.form_submit_button(
            "Cancel",
        )

        if btn_submit:
            if project_name != '' and project_name is not None:
                conf = ProjectConfig(name=project_name)
                conf.save_config()
            if uploaded_files is not None:
                for file in uploaded_files:
                    (conf.data_dir / file.name).write_bytes(file.getvalue())
            set_session_state('new_project', False)
            ph.empty()
        elif btn_cancel_submit:
            set_session_state('new_project', False)
            ph.empty()
else:
    ph.empty()

search_input = st.slider(label='Search for num:')

# from seeker.search.numerical.preprocess import preprocess_numeric_data, read_numeric_data, search_numeric

if isinstance(project_conf, ProjectConfig):
    st.write(project_conf.name)
    st.write(project_conf.data_dir)
    # data = read_numeric_data(project_conf)
    # st.write(data)
    # tree = preprocess_numeric_data()

    # with st.container():
    #     st.header('text1')
    #     st.write('1')

