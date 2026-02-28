module traffic_light (
    input  wire clk,
    input  wire rst_n,
    input  wire sensor,
    output reg [1:0] state,
    output reg red,
    output reg yellow,
    output reg green
);

parameter IDLE   = 2'b00;
parameter GREEN  = 2'b01;
parameter YELLOW = 2'b10;
parameter RED    = 2'b11;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        state <= IDLE;
    else begin
        case (state)
            IDLE:    state <= sensor ? GREEN : IDLE;
            GREEN:   state <= YELLOW;
            YELLOW:  state <= RED;
            RED:     state <= IDLE;
        endcase
    end
end

always @(*) begin
    red    = (state == RED);
    yellow = (state == YELLOW);
    green  = (state == GREEN);
end

endmodule
