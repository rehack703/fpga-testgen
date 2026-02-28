module counter #(
    parameter WIDTH = 8
)(
    input wire clk,
    input wire rst_n,
    input wire enable,
    output reg [WIDTH-1:0] count,
    output wire overflow
);

assign overflow = (count == {WIDTH{1'b1}});

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        count <= {WIDTH{1'b0}};
    else if (enable)
        count <= count + 1'b1;
end

endmodule
