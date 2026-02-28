`timescale 1ns/1ps

module tb_counter;

    parameter WIDTH = 8;

    reg clk;
    reg rst_n;
    reg enable;
    wire [WIDTH-1:0] count;
    wire overflow;

    integer pass_count;
    integer fail_count;
    integer i;

    counter #(
        .WIDTH(WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .count(count),
        .overflow(overflow)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        #100000;
        $display("TIMEOUT");
        $finish;
    end

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_counter);

        pass_count = 0;
        fail_count = 0;

        // Reset test
        rst_n = 0;
        enable = 0;
        @(negedge clk);
        @(negedge clk);
        if (count === 8'h00 && overflow === 1'b0) begin
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Reset failed. count=%h, overflow=%b", count, overflow);
            fail_count = fail_count + 1;
        end

        rst_n = 1;
        @(negedge clk);

        // Test counting
        enable = 1;
        for (i = 1; i <= 254; i = i + 1) begin
            @(negedge clk);
            if (count === i[WIDTH-1:0] && overflow === 1'b0) begin
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: Count failed at %d. count=%h, overflow=%b", i, count, overflow);
                fail_count = fail_count + 1;
            end
        end

        // Test overflow
        @(negedge clk);
        if (count === 8'hFF && overflow === 1'b1) begin
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Overflow failed. count=%h, overflow=%b", count, overflow);
            fail_count = fail_count + 1;
        end

        // Test wrap around
        @(negedge clk);
        if (count === 8'h00 && overflow === 1'b0) begin
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Wrap around failed. count=%h, overflow=%b", count, overflow);
            fail_count = fail_count + 1;
        end

        // Test enable = 0
        enable = 0;
        @(negedge clk);
        @(negedge clk);
        if (count === 8'h00 && overflow === 1'b0) begin
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Enable=0 failed. count=%h, overflow=%b", count, overflow);
            fail_count = fail_count + 1;
        end

        if (fail_count == 0) begin
            $display("PASS: %0d tests passed", pass_count);
        end else begin
            $display("FAIL: %0d tests failed", fail_count);
        end

        $finish;
    end

endmodule
