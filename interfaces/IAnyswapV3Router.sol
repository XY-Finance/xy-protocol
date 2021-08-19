pragma solidity ^0.6.0;

interface IAnyswapV3Router {
    function anySwapOutUnderlying(address token, address to, uint amount, uint toChainID) external;
}