from pathlib import Path


def get_path_to_project(new_folder: str = "") -> Path:
    """Function for getting the path to find the project folder structure in application.
    :param new_folder:  New folder path
    :return:            String of absolute path to start the project structure
    """
    max_levels = 5
    current = Path("..").absolute()

    def is_project_root(p: Path) -> bool:
        return (p / "pyproject.toml").exists()

    for _ in range(max_levels):
        if is_project_root(current):
            continue
        current = current.parent
    if new_folder:
        return current.absolute() / new_folder
    else:
        return current.absolute()
