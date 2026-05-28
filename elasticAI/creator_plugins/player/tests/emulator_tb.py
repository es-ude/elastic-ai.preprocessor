import cocotb
from shutil import copyfile
from pathlib import Path
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, FallingEdge

from elasticai.creator.file_generation import find_project_root
import elasticai.creator_plugins.player as test_dut
from elasticai.creator.testing.cocotb_runner import run_cocotb_sim_for_src_dir


filename = "data.mem"
_path2data = str((Path(test_dut.__file__).parent / 'verilog' / filename).absolute())


cocotb_settings = dict(
    src_files=["emulator.v"],
    path2src=Path(test_dut.__file__).parent / 'verilog',
    top_module_name='DATA_EMULATOR',
    cocotb_test_module="elasticai.creator_plugins.simulator.tests.emulator_tb",
    params={'BITWIDTH': 12, 'NUM_VALUES': 19}
)


@cocotb.test()
async def emulator_check(dut):
    print(dir(dut))
    period_clk = 5

    bitwidth = dut.BITWIDTH.value.to_unsigned()
    numwidth = dut.NUM_VALUES.value.to_unsigned()

    dut.CLK_ADC.value = 0
    dut.RSTN.value = 0
    dut.EN.value = 0

    # Start clock and make reset
    cocotb.start_soon(Clock(dut.CLK_ADC, period_clk, unit='ns').start())
    await Timer(4 * period_clk, unit='ns')
    for idx in range(4):
        await RisingEdge(dut.CLK_ADC)
        dut.RSTN.value = idx % 2
    await RisingEdge(dut.CLK_ADC)
    dut.RSTN.value = 1
    for _ in range(4):
        await RisingEdge(dut.CLK_ADC)

    assert dut.DATA_OUT.value == 0
    assert dut.DATA_END.value == 0

    dut.EN.value = 1

    for _ in range(4):
        for idx in range(numwidth):
            await FallingEdge(dut.CLK_ADC)
            assert dut.DATA_OUT.value == idx
            assert dut.cnt_pos.value == idx
    for _ in range(8):
        await RisingEdge(dut.CLK_ADC)
        dut.EN.value = 0


if __name__ == "__main__":
    copyfile(_path2data, str((Path(find_project_root()) / 'build_sim' / filename).absolute()))
    run_cocotb_sim_for_src_dir (**cocotb_settings)
