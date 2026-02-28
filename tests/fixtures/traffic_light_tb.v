`timescale 1ns/1ps

module tb_traffic_light;

    reg clk;
    reg rst_n;
    reg sensor;
    wire [1:0] state;
    wire red;
    wire yellow;
    wire green;

    integer pass_count = 0;
    integer fail_count = 0;

    traffic_light dut (
        .clk(clk),
        .rst_n(rst_n),
        .sensor(sensor),
        .state(state),
        .red(red),
        .yellow(yellow),
        .green(green)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_traffic_light);
    end

    initial begin
        #100000;
        $display("Timeout");
        $finish;
    end

    task check_outputs;
        input [1:0] exp_state;
        input exp_red;
        input exp_yellow;
        input exp_green;
        begin
            if (state === exp_state && red === exp_red && yellow === exp_yellow && green === exp_green) begin
                pass_count = pass_count + 1;
            end else begin
                fail_count = fail_count + 1;
                $display("FAIL at %0t: Expected state=%b, red=%b, yellow=%b, green=%b | Got state=%b, red=%b, yellow=%b, green=%b",
                         $time, exp_state, exp_red, exp_yellow, exp_green, state, red, yellow, green);
            end
        end
    endtask

    initial begin
        // Initialize
        rst_n = 0;
        sensor = 0;
        
        // Apply reset
        #12;
        rst_n = 1;
        #8; // Align to clock edge
        
        // Check IDLE state
        check_outputs(2'b00, 1'b0, 1'b0, 1'b0);
        
        // Keep sensor 0, should stay IDLE
        #10;
        check_outputs(2'b00, 1'b0, 1'b0, 1'b0);
        
        // Set sensor 1, should go to GREEN on next clock
        sensor = 1;
        #10;
        check_outputs(2'b01, 1'b0, 1'b0, 1'b1);
        
        // Next clock should go to YELLOW
        sensor = 0; // Sensor value shouldn't matter for GREEN->YELLOW
        #10;
        check_outputs(2'b10, 1'b0, 1'b1, 1'b0);
        
        // Next clock should go to RED
        #10;
        check_outputs(2'b11, 1'b1, 1'b0, 1'b0);
        
        // Next clock should go to IDLE
        #10;
        check_outputs(2'b00, 1'b0, 1'b0, 1'b0);
        
        // Set sensor 1 again, keep it 1
        sensor = 1;
        #10;
        check_outputs(2'b01, 1'b0, 1'b0, 1'b1);
        #10;
        check_outputs(2'b10, 1'b0, 1'b1, 1'b0);
        #10;
        check_outputs(2'b11, 1'b1, 1'b0, 1'b0);
        #10;
        check_outputs(2'b00, 1'b0, 1'b0, 1'b0);
        #10;
        check_outputs(2'b01, 1'b0, 1'b0, 1'b1); // Goes back to GREEN because sensor is 1

        if (fail_count == 0) begin
            $display("PASS: %0d tests passed", pass_count);
        end else begin
            $display("FAIL: %0d tests failed", fail_count);
        end
        $finish;
    end

endmodule
