`timescale 1ns/1ps

module tb_alu;

    reg [7:0] a;
    reg [7:0] b;
    reg [2:0] op;
    wire [7:0] result;
    wire zero;

    integer pass_count;
    integer fail_count;
    integer i;

    reg [7:0] expected_result;
    reg expected_zero;

    alu dut (
        .a(a),
        .b(b),
        .op(op),
        .result(result),
        .zero(zero)
    );

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_alu);
    end

    initial begin
        #100000;
        $display("TIMEOUT");
        $finish;
    end

    task check_output;
        input [7:0] exp_res;
        input exp_z;
        begin
            #1; // Wait for combinational logic to settle
            if (result === exp_res && zero === exp_z) begin
                pass_count = pass_count + 1;
            end else begin
                fail_count = fail_count + 1;
                $display("FAIL: a=%h, b=%h, op=%b | expected result=%h zero=%b | got result=%h zero=%b", 
                         a, b, op, exp_res, exp_z, result, zero);
            end
            #9; // Advance time before next test
        end
    endtask

    initial begin
        pass_count = 0;
        fail_count = 0;

        // Directed Tests
        // Test op 000: ADD
        op = 3'b000;
        a = 8'h00; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'hFF; b = 8'h01; check_output(8'h00, 1'b1);
        a = 8'h10; b = 8'h20; check_output(8'h30, 1'b0);

        // Test op 001: SUB
        op = 3'b001;
        a = 8'h00; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'h00; b = 8'h01; check_output(8'hFF, 1'b0);
        a = 8'h20; b = 8'h10; check_output(8'h10, 1'b0);

        // Test op 010: AND
        op = 3'b010;
        a = 8'hFF; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'hAA; b = 8'h55; check_output(8'h00, 1'b1);
        a = 8'hF0; b = 8'h30; check_output(8'h30, 1'b0);

        // Test op 011: OR
        op = 3'b011;
        a = 8'h00; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'hAA; b = 8'h55; check_output(8'hFF, 1'b0);
        a = 8'hF0; b = 8'h0F; check_output(8'hFF, 1'b0);

        // Test op 100: XOR
        op = 3'b100;
        a = 8'h00; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'hAA; b = 8'h55; check_output(8'hFF, 1'b0);
        a = 8'hFF; b = 8'hFF; check_output(8'h00, 1'b1);

        // Test op 101: NOT a
        op = 3'b101;
        a = 8'h00; b = 8'h00; check_output(8'hFF, 1'b0);
        a = 8'hFF; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'hAA; b = 8'h00; check_output(8'h55, 1'b0);

        // Test op 110: SHL a
        op = 3'b110;
        a = 8'h01; b = 8'h00; check_output(8'h02, 1'b0);
        a = 8'h80; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'hFF; b = 8'h00; check_output(8'hFE, 1'b0);

        // Test op 111: SHR a
        op = 3'b111;
        a = 8'h02; b = 8'h00; check_output(8'h01, 1'b0);
        a = 8'h01; b = 8'h00; check_output(8'h00, 1'b1);
        a = 8'hFF; b = 8'h00; check_output(8'h7F, 1'b0);

        // Random Tests
        for (i = 0; i < 100; i = i + 1) begin
            a = $random;
            b = $random;
            op = $random;
            
            case (op)
                3'b000: expected_result = a + b;
                3'b001: expected_result = a - b;
                3'b010: expected_result = a & b;
                3'b011: expected_result = a | b;
                3'b100: expected_result = a ^ b;
                3'b101: expected_result = ~a;
                3'b110: expected_result = a << 1;
                3'b111: expected_result = a >> 1;
            endcase
            expected_zero = (expected_result == 8'b0);
            
            check_output(expected_result, expected_zero);
        end

        // Final Summary
        if (fail_count == 0) begin
            $display("PASS: %0d tests passed", pass_count);
        end else begin
            $display("FAIL: %0d tests failed", fail_count);
        end
        
        $finish;
    end

endmodule