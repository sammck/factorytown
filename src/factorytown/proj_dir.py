from .internal_types import *

import os
from functools import cache

@cache
def get_virtualenv_dir() -> Optional[str]:
    """
    Get the directory of the current python virtualenv, if any.
    """
    return os.environ.get('VIRTUAL_ENV')

@cache
def get_project_dir() -> str:
    """
    Get the project directory. This is, in order of decreasing preference:
       1. The value of env var FACTORYTOWN_PROJECT_DIR
       2. The parent directory of the current python virtualenv
    """
    project_dir = os.environ.get('FACTORYTOWN_PROJECT_DIR')
    if project_dir is None:
        venv_dir = get_virtualenv_dir()
        if venv_dir is not None:
            project_dir = os.path.dirname(venv_dir)
    if project_dir is None:
        raise FactoryTownError("Could not determine project directory")
    return project_dir
