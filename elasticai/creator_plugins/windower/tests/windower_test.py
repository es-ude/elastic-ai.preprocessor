import cocotb
import pytest
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from random import Random

from elasticai.creator.testing import CocotbTestFixture, eai_testbench
from elasticai.creator_plugins.windower.utils import load_and_plugin


def build_testdata(bitwidth: int, samples: int, num_shift: int, repeats: int = 8) -> list[int]:
    max_value = 2**bitwidth - 1
    rng = Random((bitwidth << 16) + (samples << 8) + num_shift)

    data = [rng.randint(0, max_value) for _ in range(repeats * samples)]

    if len(data) >= 1:
        data[0] = 0
    if len(data) >= 2:
        data[1] = max_value

    return data


def build_check(data_in: list[int], bitwidth: int, samples: int, num_shift: int) -> list[int]:
    shifted_values: list[int] = []
    check: list[int] = []

    for idx, value in enumerate(data_in, start=1):
        shifted_values.append(value)

        if idx % num_shift == 0:
            window = list(reversed(shifted_values[-samples:]))
            window.extend([0] * (samples - len(window)))

            packed_window = 0
            for sample_idx, sample in enumerate(window):
                packed_window |= (sample) << (sample_idx * bitwidth)

            check.append(packed_window)

    return check


@cocotb.test()
@eai_testbench
async def check_transfer_function(dut, bitwidth: int, samples: int, num_shift: int, data_in: list[int], check: list[int]):
    period_clk = 5

    # Initialize signals
    dut.CLK_SYS.value = 0
    dut.RSTN.value = 0
    dut.EN.value = 0
    dut.DO_SHIFT.value = 0
    dut.DATA_IN.value = 0

    # Start clock and making reset
    cocotb.start_soon(Clock(dut.CLK_SYS, period_clk, unit='ns').start())

    for _ in range(8):
        await RisingEdge(dut.CLK_SYS)

    for idx in range(4):
        await RisingEdge(dut.CLK_SYS)
        dut.RSTN.value = idx % 2
        await RisingEdge(dut.CLK_SYS)

    dut.RSTN.value = 1

    for _ in range(2):
        await RisingEdge(dut.CLK_SYS)

    await FallingEdge(dut.CLK_SYS)

    # Set Trigger
    dut.EN.value = 1
    await Timer(1, unit="ps")
    assert dut.DVALID.value == 0

    data_buf_out: list[int] = []

    async def collect_if_valid() -> None:
        await Timer(1, unit="ps")
        if dut.DVALID.value == 1:
            data_buf_out.append(dut.DATA_BUF.value.to_unsigned())

    for value in data_in:
        await RisingEdge(dut.CLK_SYS)
        await collect_if_valid()

        dut.DATA_IN.value = value
        dut.DO_SHIFT.value = 1

        await RisingEdge(dut.CLK_SYS)
        await collect_if_valid()

        dut.DO_SHIFT.value = 0

        for _ in range(2):
            await RisingEdge(dut.CLK_SYS)
            await collect_if_valid()

    for _ in range(num_shift + 2):
        await RisingEdge(dut.CLK_SYS)
        await collect_if_valid()

    assert data_buf_out == check


@pytest.mark.simulation
@pytest.mark.parametrize("bitwidth", [8])
@pytest.mark.parametrize("samples", [32])
@pytest.mark.parametrize("num_shift", [4])
def test_windower(
    cocotb_test_fixture: CocotbTestFixture,
    bitwidth: int,
    samples: int,
    num_shift: int,
):
    data_in = build_testdata(bitwidth=bitwidth, samples=samples, num_shift=num_shift, repeats=8)
    check = build_check(data_in=data_in, bitwidth=bitwidth, samples=samples, num_shift=num_shift)
    cocotb_test_fixture.write({"data_in": data_in, "check": check})

    cocotb_test_fixture.set_top_module_name("WINDOWER")
    cocotb_test_fixture.clear_srcs()

    cocotb_test_fixture.add_srcs_from_package("windower", "verilog/ring_buffer.v",)
    cocotb_test_fixture.add_srcs_from_package("windower","verilog/windower.v",)

    cocotb_test_fixture.run(
        params={
            "BITWIDTH": bitwidth,
            "SAMPLES": samples,
            "NUM_SHIFT": num_shift,
        },
        defines={},
    )


@pytest.mark.simulation
@pytest.mark.parametrize("bitwidth", [8])
@pytest.mark.parametrize("samples", [32])
@pytest.mark.parametrize("num_shift", [4])
def test_windower_build(
    cocotb_test_fixture: CocotbTestFixture,
    bitwidth: int,
    samples: int,
    num_shift: int,
):
    data_in = build_testdata(bitwidth=bitwidth, samples=samples, num_shift=num_shift, repeats=8, )
    check = build_check(data_in=data_in, bitwidth=bitwidth, samples=samples, num_shift=num_shift)
    cocotb_test_fixture.write({"data_in": data_in, "check": check})
    
    build_dir = cocotb_test_fixture.get_artifact_dir() / "verilog"

    load_and_plugin(
        type="windower",
        id="",
        params={"BITWIDTH": bitwidth, "SAMPLES": samples, "NUM_SHIFT": num_shift,},
        packages=["windower"],
        path2save=build_dir,
        add_ringbuffer=True,
    )

    cocotb_test_fixture.clear_srcs()
    cocotb_test_fixture.add_srcs_from_artifact_dir("verilog/*.v")
    cocotb_test_fixture.set_top_module_name("WINDOWER")
    cocotb_test_fixture.run(params={}, defines={})