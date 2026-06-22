from pathlib import Path
from typing import Any

import elasticai.creator_plugins.adders as adders
import elasticai.creator_plugins.mac as mac
import elasticai.creator_plugins.multipliers as mult

from elasticai.preprocessor import get_path_to_project
from elasticai.preprocessor.translation import load_and_build_form_plugin


def load_and_plugin(
    type: str,
    id: str,
    params: dict[str, Any],
    packages: list,
    path2save: Path = get_path_to_project() / "build",
) -> None:
    load_and_build_form_plugin(type, id, params, packages, path2save)
    load_and_build_form_plugin(
        "mac",
        "",
        params={"BITWIDTH": params["BITWIDTH"]},
        packages=[mac],
        path2save=path2save,
    )
    load_and_build_form_plugin(
        "mult_dsp",
        "",
        params={"BITWIDTH": params["BITWIDTH"]},
        packages=[mult, adders],
        path2save=path2save,
    )
