from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from seeker.project_config import ProjectConfig
from seeker.search.text import TextModel
from seeker.search.image import ImageModel
import streamlit as st

if TYPE_CHECKING:
    from seeker.search.base import BaseModel

DEFAULT_PROJECT = ProjectConfig(name="Select project", dtype="text")

DEFAULT_TEXT_SEARCH = ""
DEFAULT_IMAGE_SEARCH = "#FFFFFF"
MODEL_MAPPING = {"text": TextModel, "image": ImageModel}


class SearchNames:
    text: str = "text_to_search"
    document: str = "doc_to_search"
    color: str = "color_to_search"
    image: str = "image_to_search"


class AppState:
    new = "new_project"
    modify = "modify_project"
    select = "select_project"
    show = "show_project"


DEFAULT_SESSION = {
    "app_state": AppState.select,
    "config": ProjectConfig(name="Select project", dtype="text"),
    "search": None,
}


@dataclass
class SessionState:
    app_state: str
    config: ProjectConfig
    search: Any

    @classmethod
    def get_default(cls):
        default = dict()
        for k, v in DEFAULT_SESSION.items():
            if k not in st.session_state:
                st.session_state[k] = v
            default[k] = st.session_state[k]
        return cls(**default)


SESSION = SessionState.get_default()
