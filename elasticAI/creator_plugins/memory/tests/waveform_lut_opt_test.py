import cocotb
import pytest
from cocotb.clock import Clock, Timer
from cocotb.triggers import RisingEdge

from elasticai.creator.testing import eai_testbench, cocotb_test_fixture, CocotbTestFixture


@cocotb.test()
@eai_testbench
async def wvf_lut_read_several_trials(dut, bitwidth: int, num_params: int, num_trials: int, waveform: list[int], check: list[int], is_signed: bool):
    period_clk = 5
    mode_trgg = False if 'WAIT_CYC' in dir(dut) else True
    mode_accs = True if 'LUT_DATA_EXT' in dir(dut) else False

    ramrange = 4* num_params -3

    if mode_trgg:
        dut.TRGG_CNT.value = 0
    else:
        dut.WAIT_CYC.value = 2 ** (dut.WAIT_WIDTH.value.to_unsigned() - 1) -1
    if mode_accs:
        sum_val = 0
        for v in reversed(waveform):
            sum_val = (sum_val << bitwidth)
            sum_val |= v & ((1 << bitwidth) - 1)
        dut.LUT_DATA_EXT.value = sum_val
    dut.CLK_SYS.value = 0
    dut.RSTN.value = 0
    dut.EN_FLAG.value = 0

    # Start clock and make reset
    cocotb.start_soon(Clock(dut.CLK_SYS, period_clk, unit='ns').start())
    for idx in range(4):
        await RisingEdge(dut.CLK_SYS)
    for idx in range(4):
        await RisingEdge(dut.CLK_SYS)
        dut.RSTN.value = idx % 2
    await RisingEdge(dut.CLK_SYS)
    dut.RSTN.value = 1
    for idx in range(4):
        await RisingEdge(dut.CLK_SYS)

    # Make test (several shots, full cycle through RAM)
    dut.EN_FLAG.value = 1
    if mode_trgg:
        cocotb.start_soon(Clock(dut.TRGG_CNT, 20*period_clk, unit='ns').start())
        await Timer(period_clk, unit='ns')

    ram_data_out = list()
    for num_ite in range(num_trials):
        cnt_ram = ramrange if num_ite == 0 or num_ite == num_trials else ramrange -1
        for idx in range(cnt_ram):
            if mode_trgg:
                await RisingEdge(dut.TRGG_CNT)
            else:
                for _ in range(dut.WAIT_CYC.value):
                    await RisingEdge(dut.CLK_SYS)

            dut.EN_FLAG.value = num_ite < num_trials
            ram_data_out.append(dut.LUT_OUT.value.to_signed())
        assert dut.LUT_END.value == 1
    #assert ram_data_out[:num_params] == waveform
    print(len(ram_data_out), ram_data_out)
    print(len(check), check)
    assert ram_data_out == check


@pytest.mark.simulation
@pytest.mark.parametrize("bitwidth, num_params, num_trials", [(6, 9, 3)])
@pytest.mark.parametrize("is_signed", [True, False])
def test_waveform_lut_opt_normal(
    cocotb_test_fixture: CocotbTestFixture,
    bitwidth: int,
    num_params: int,
    num_trials: int,
    is_signed: bool
):
    waveform = [31, 28, 24, 20, 16, 12, 8, 4, 0]
    check = [waveform[-1]]
    offset = -2 ** (bitwidth - 1) if is_signed else 0
    for _ in range(num_trials):
        check.extend(reversed(waveform[:-1]))
        check.extend(waveform[1:])
        check.extend([-val for val in reversed(waveform[:-1])])
        check.extend([-val for val in waveform[1:]])
    check = [offset + val for val in check]

    cocotb_test_fixture.set_top_module_name("LUT_WAVEFORM_OPT")
    cocotb_test_fixture.write({"waveform": waveform, "check": check})

    cocotb_test_fixture.clear_srcs()
    cocotb_test_fixture.add_srcs_from_package("memory", "verilog/waveform_lut_opt.v")
    cocotb_test_fixture.run(
        params={
            "BITWIDTH": bitwidth,
            "WAIT_WIDTH": bitwidth,
            "LUTWIDTH": num_params,
            "SIGNED_OUT": is_signed
        },
        defines={},
    )