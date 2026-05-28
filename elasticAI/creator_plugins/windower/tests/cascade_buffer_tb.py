import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from pathlib import Path
import numpy as np

from elasticai.creator.testing.cocotb_runner import run_cocotb_sim_for_src_dir
import elasticai.creator_plugins.windower as test_dut


cocotb_settings = dict(
    src_files=['shift_register.v', 'ring_buffer.v', 'cascade_buffer.v'],
    top_module_name='CASCADE_BUFFER',
    cocotb_test_module='elasticai.creator_plugins.windower.tests.cascade_buffer_tb',
    path2src=Path(test_dut.__file__).parent / 'verilog',
    params={"BITWIDTH": 8, "SAMPLES": 6}
)


@cocotb.test()
async def cascade_buffer_tb(dut):
    period_clk = 5
    print(dir(dut))
    used_bitwidth = int(dut.BITWIDTH.value)
    used_adrwidth = int(dut.SAMPLES.value)
    #data_in_array = [np.random.randint(low=0, high=2**used_bitwidth-1) for _ in range(used_adrwidth)]
    data_in_array = [int(2**(used_bitwidth-1) * (1 + np.cos(2 * np.pi * idx / used_adrwidth))) for idx in range(used_adrwidth)]
    data_in_array = [val if val >= 0 else 0 for val in data_in_array]
    data_in_array = [2**used_bitwidth-1 if val >= 2**used_bitwidth-1 else val for val in data_in_array]
    print(data_in_array)

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
    ite = 0
    dut.EN.value = 1
    assert dut.DVALID.value == 0
    for idx in range(8 * used_adrwidth):
        ite += 1
        await RisingEdge(dut.CLK_SYS)
        dut.DO_SHIFT.value = 1
        dut.DATA_IN.value = data_in_array[idx % used_adrwidth]
        await RisingEdge(dut.CLK_SYS)
        #assert dut.DVALID.value == 0
        dut.DO_SHIFT.value = 0
        for _ in range(2):
            await RisingEdge(dut.CLK_SYS)
        #assert dut.DATA_BUF0.value == dut.DATA_BUF1.value
        #assert dut.DATA_OUT0.value == dut.DATA_OUT1.value
        #assert dut.DVALID.value == 1


if __name__ == "__main__":
    run_cocotb_sim_for_src_dir(**cocotb_settings)
