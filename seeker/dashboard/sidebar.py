import streamlit as st
from seeker.dashboard.naming import DEFAULT_PROJECT, AppState, MODEL_MAPPING, SESSION
from seeker.project_config import ProjectConfig, load_all_config
import pandas as pd


def get_conf_stat(conf: ProjectConfig):
    print(
        pd.DataFrame(
            [
                {
                    "Name": conf.name,
                    "Type": conf.dtype,
                    "Files": conf.get_file_count(),
                    "Size": f"{conf.get_file_size() / 1024 / 1024:.2f} MB",
                }
            ]
        )
        .T.reset_index(drop=False)
        .to_numpy()
    )
    return {
        "Name": conf.name,
        "Type": conf.dtype,
        "Files": conf.get_file_count(),
        "Size": f"{conf.get_file_size() / 1024 / 1024:.2f} MB",
    }
    return (
        pd.DataFrame(
            [
                {
                    "Name": conf.name,
                    "Type": conf.dtype,
                    "Files": conf.get_file_count(),
                    "Size": f"{conf.get_file_size() / 1024 / 1024:.2f} MB",
                }
            ]
        )
        .T.reset_index(drop=False)
        .values
    )


def sidebar_select_project():
    def callback():
        SESSION.config = st.session_state["select_project"]

    st.selectbox(
        label="Select project",
        key="select_project",
        options=[DEFAULT_PROJECT, *load_all_config()],
        format_func=lambda conf: conf.name,
        on_change=callback,
    )
    st.session_state["select_project"]

    if SESSION.config.name != DEFAULT_PROJECT.name:
        sidebar_show_project()

    def callback():
        SESSION.app_state = AppState.new

    st.button(label="New project", on_click=callback)


def sidebar_show_project():
    [st.write(f"{k}: {v}") for k, v in get_conf_stat(SESSION.config).items()]

    def callback():
        SESSION.app_state = AppState.modify

    st.button(label="Modify", on_click=callback)

    def callback():
        [file.unlink() for file in SESSION.config.project_dir.rglob("*")]
        SESSION.config.project_dir.rmdir()
        SESSION.config = DEFAULT_PROJECT
        SESSION.app_state = AppState.select

    st.button(label="Delete", on_click=callback)


def update_project(conf: ProjectConfig, filenames):
    model = MODEL_MAPPING[SESSION.config.dtype](conf=SESSION.config)
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
        SESSION.config = ProjectConfig(
            name=st.session_state["project_name"],
            dtype=st.session_state["project_type"],
        )
        if SESSION.config != DEFAULT_PROJECT.name:
            SESSION.config.save_config()

            uploaded_files = st.session_state["file_uploader"]
            if uploaded_files:
                for file in uploaded_files:
                    (SESSION.config.data_dir / file.name).write_bytes(file.getvalue())
                update_project(conf=SESSION.config, filenames=uploaded_files)

                SESSION.app_state = AppState.select

    st.button("Submit", on_click=callback)

    def callback():
        SESSION.config = DEFAULT_PROJECT
        SESSION.app_state = AppState.select

    st.button("Cancel", on_click=callback)


def sidebar_modify_project():
    st.text_input(label="Project name", value=SESSION.config.name, disabled=True)
    st.text_input(label="Project type", value=SESSION.config.dtype, disabled=True)

    st.file_uploader(
        label="Files",
        key="file_uploader",
        # type=TYPE_CONF[project_type],
        accept_multiple_files=True,
    )

    def callback():
        uploaded_files = st.session_state["file_uploader"]
        if uploaded_files:

            for file in uploaded_files:
                (SESSION.config.data_dir / file.name).write_bytes(file.getvalue())
            update_project(SESSION.config, uploaded_files)

            SESSION.app_state = AppState.select

    st.button("Submit", on_click=callback)

    def callback():
        SESSION.app_state = AppState.select
        SESSION.config = DEFAULT_PROJECT

    st.button("Cancel", on_click=callback)
