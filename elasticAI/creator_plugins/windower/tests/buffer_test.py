import pytest
from copy import deepcopy

from elasticai.creator.testing.cocotb_runner import run_cocotb_sim_for_src_dir
from elasticai.creator_plugins.windower.tests.shift_register_tb import cocotb_settings as sets_shift
from elasticai.creator_plugins.windower.tests.ring_buffer_tb import cocotb_settings as sets_ring


#@pytest.mark.simulation
@pytest.mark.parametrize(
    ["bitwidth", "elements"], [
        (4, 6),
        (4, 32),
        (4, 64),
        (8, 4),
        (8, 8),
        (8, 16),
        (10, 6),
        (10, 22),
        (10, 31),
        (12, 64),
        (12, 128),
        (16, 256),
    ]
)
def test_shift_register(bitwidth: int, elements: int):
    sets = deepcopy(sets_shift)
    sets['params'] = {
        "BITWIDTH": bitwidth,
        "SAMPLES": elements
    }
    run_cocotb_sim_for_src_dir(**sets)


#@pytest.mark.simulation
@pytest.mark.parametrize(
    ["bitwidth", "elements"], [
        (4, 6),
        (4, 32),
        (4, 64),
        (8, 4),
        (8, 8),
        (8, 16),
        (10, 6),
        (10, 22),
        (10, 31),
        (12, 64),
        (12, 128),
        (16, 256),
    ]
)
def test_ring_register(bitwidth: int, elements: int):
    sets = deepcopy(sets_ring)
    sets['params'] = {
        "BITWIDTH": bitwidth,
        "SAMPLES": elements
    }
    run_cocotb_sim_for_src_dir(**sets)


if __name__ == '__main__':
    pytest.main([__file__])
