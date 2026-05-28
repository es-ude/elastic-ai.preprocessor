//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
//
// Create Date:     22.01.2026
// Copied on: 	    §{date_copy_created}
// Module Name:     Testbench file for playing data sets in FPGA/ASIC simulations
// Target Devices:  ASIC / FPGA
// Tool Versions:   1v0
// Processing:      Emulating pre-recorded data with sampling rate fs = §{sampling_rate} kHz
//
// State: 	        Works!
// Dependencies:    None
// Improvements:    None
// Parameters:      None
//
//////////////////////////////////////////////////////////////////////////////////
// ---------------------------------------------------
// Code Example for Implementation in Testbenches:
// DATA_EMULATOR SIM(
//      .CLK_ADC(clk0),
//      .RSTN(reset_n),
//      .EN(enable_sim)
//      .DATA_OUT(data_sim),
//      .TRGG_OUT(trgg_sim),
//      .DATA_END(sim_end)
// );
// ---------------------------------------------------
//`define ADD_TRIGGER

module DATA_EMULATOR#(
    parameter BITWIDTH = 12,
    parameter NUM_VALUES = 19,
    `ifndef ADD_TRIGGER
        parameter string DATA_FILENAME = "data.mem"
    `else
        parameter string DATA_FILENAME = "data.mem",
        parameter string TRGG_FILENAME = "trgg.mem"
    `endif
)(
    input wire CLK_ADC,
    input wire RSTN,
    input wire EN,
    output wire signed [BITWIDTH-'d1:0] DATA_OUT,
    `ifdef ADD_TRIGGER
        output wire TRGG_OUT,
    `endif
    output wire DATA_END
);

reg [$clog2(NUM_VALUES)-'d1:0] cnt_pos;

`ifdef ADD_TRIGGER
    reg [NUM_VALUES-'d1:0] bram_trgg;
    assign TRGG_OUT = (EN && !DATA_END) ? bram_trgg[cnt_pos] : 1'd0;
`endif

reg signed [BITWIDTH-'d1:0] bram_data [0:NUM_VALUES-'d1];
assign DATA_OUT = (EN) ? bram_data[cnt_pos] : 'd0;
assign DATA_END = (cnt_pos == (NUM_VALUES-'d1));

initial begin
    $readmemh(DATA_FILENAME, bram_data);
    `ifdef ADD_TRIGGER
        $readmemb(TRGG_FILENAME, bram_trgg);
    `endif
end

always@(posedge CLK_ADC) begin
    if(~RSTN) begin
        cnt_pos = 'd0;
    end else begin
        cnt_pos = (cnt_pos == (NUM_VALUES -'d1)) ? 'd0 : (cnt_pos + ((EN) ? 'd1 : 'd0));
    end
end
endmodule
