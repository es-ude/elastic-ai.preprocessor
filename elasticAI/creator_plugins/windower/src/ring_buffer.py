from collections.abc import Iterable
from elasticai.creator.ir2verilog import (
    type_handler_iterable,
    Implementation,
    Code,
    TemplateDirector,
)
from importlib import resources as res


@type_handler_iterable
def ringbuffer(impl: Implementation) -> Iterable[Code]:
    package_path = "elasticai.creator_plugins.windower"
    code = list()

    path2file = "verilog/ring_buffer.v"

    _template = (
        TemplateDirector()
        .parameter("BITWIDTH")
        .parameter("SAMPLES")
        .add_module_name()
        .set_prototype(res.read_text(package_path, path2file))
        .build()
    )
    code.append((impl.name, _template.substitute(impl.attributes)))
    return code
