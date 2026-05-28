import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from pathlib import Path
import numpy as np

from elasticai.creator.testing.cocotb_runner import run_cocotb_sim_for_src_dir
import elasticai.creator_plugins.windower as test_dut


cocotb_settings = dict(
    src_files=['ring_buffer.v'],
    top_module_name='RING_BUFFER',
    cocotb_test_module='elasticai.creator_plugins.windower.tests.ring_buffer_tb',
    path2src=Path(test_dut.__file__).parent / 'verilog',
    params={"BITWIDTH": 8, "SAMPLES": 14}
)


@cocotb.test()
async def ring_register_tb(dut):
    period_clk = 5
    period_data = 100

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
    dut.EN.value = 1
    for _ in range(4):
        await RisingEdge(dut.CLK_SYS)
    cocotb.start_soon(Clock(dut.DO_SHIFT, period_data, unit='ns').start())
    await FallingEdge(dut.CLK_SYS)
    assert dut.DVALID.value == 0

    ite = 0
    for _ in range(3):
        for val in data_in_array:
            await RisingEdge(dut.DO_SHIFT)
            dut.DATA_IN.value = val
            await FallingEdge(dut.CLK_SYS)
            assert dut.DVALID.value == 0

            await RisingEdge(dut.DVALID)
            if ite < used_adrwidth:
                assert dut.DATA_OUT.value == 0
            else:
                assert dut.DATA_OUT.value == data_in_array[ite % used_adrwidth]
            ite += 1


if __name__ == "__main__":
    run_cocotb_sim_for_src_dir(**cocotb_settings)
