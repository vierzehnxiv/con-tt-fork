# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

def lfsr(seed, cycles):
    result = seed
    mask = 0b0000_1000_1000_1100_1000_1000_1001_0010
    for i in range(cycles):
        xor = 0
        for j in range(32):
            if (mask & (1 << j)) != 0:
                if (result & (1 << j)) != 0:
                    xor ^= 1
        result = ((result << 1) | xor) & (2**32 - 1)
    return result

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0

    # read seed from reset DUT
    seed = int(dut.user_project.lfsr_output.value)
    dut._log.info("LFSR Test")
    dut._log.info("Seed: {}".format(seed))

    # Set the input values you want to test
    dut.ui_in.value = 20
    dut.uio_in.value = 30

    # Wait for one clock cycle to see the output values
    await ClockCycles(dut.clk, 2)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    assert dut.uo_out.value == lfsr(seed, 1) & 0xFF

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
