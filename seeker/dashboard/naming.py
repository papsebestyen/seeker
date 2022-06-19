from seeker.project_config import ProjectConfig

DEFAULT_PROJECT = ProjectConfig(name="Select project", dtype="text")

DEFAULT_TEXT_SEARCH = "Keress rá valamire"
DEFAULT_IMAGE_SEARCH = "F000000"

class SearchNames:
    text: str = "text_to_search"
    document: str = "doc_to_search"
    color: str = "color_to_search"
    image: str = "image_to_search"


class AppState:
    new = 'new_project'
    modify = 'modify_project'
    select = 'select_project'
