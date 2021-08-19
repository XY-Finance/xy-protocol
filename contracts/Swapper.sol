pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "./Withdrawable.sol";
import "../interfaces/IAnyswapV3Router.sol";

contract Swapper is Withdrawable {

    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    address payable public oneInchAggregator;
    address public anyswapRouter;
    mapping (address => bool) public proxies;
    mapping (address => bool) public operators;
    mapping (address => address) public anyTokenMapping;  // example: USDC -> anyUSDC
    address public ETHER_ADDRESS = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;
    uint256 public swapId;

    event SourceChainSwap(uint256 indexed _swapId, address _sender, uint8 _chainId, SwapInfo _swapInfo, uint256 _fromTokenAmount);
    event TargetChainSwap(uint256 indexed _swapId, address _receiver, uint8 _chainId, SwapInfo _swapInfo);
    event SwapForCompleted(uint256 indexed _swapId, address _receiver, address _toToken, uint256 _toTokenAmount);
    event OneInchSwapFailed(address _token);

    struct SwapInfo {
        uint8 chainId;
        address dex;
        IERC20 fromToken;
        IERC20 toToken;
        bytes swapData;
    }

    constructor() public {}

    receive() external payable {}

    function setOneInchAggregator(address payable _oneInchAggregator) external onlyOwner {
        oneInchAggregator = _oneInchAggregator;
    }

    function setProxyAccount(address _addr, bool _flag) external onlyOwner {
        proxies[_addr] = _flag;
    }

    function setOperatorAccount(address _addr, bool _flag) external onlyOwner {
        operators[_addr] = _flag;
    }

    function setAnyswapRouter(address _addr) external onlyOwner {
        anyswapRouter = _addr;
    }

    function setAnyTokenMapping(address token, address anyToken) external onlyOwner {
        anyTokenMapping[token] = anyToken;
    }

    function getTokenBalance(IERC20 token) private view returns (uint256 balance) {
        balance = address(token) == ETHER_ADDRESS ? address(this).balance : token.balanceOf(address(this));
    }

    function approveToken(IERC20 token, address spender, uint256 amount) private {
        if (address(token) == ETHER_ADDRESS) return;

        uint256 allowance = token.allowance(address(this), spender);
        if (allowance > 0)
            token.safeApprove(spender, 0);
        token.safeIncreaseAllowance(spender, amount);
    }

    function safeTransferAsset(address receiver, IERC20 token, uint256 amount) private {
        if (address(token) == ETHER_ADDRESS) {
            payable(receiver).transfer(amount);
        } else {
            token.safeTransfer(receiver, amount);
        }
    }

    function swap(
        uint256 fromTokenAmount,
        SwapInfo[] calldata swapInfos,
        SwapInfo[] calldata targetChainSwapInfo,
        address receiver
    ) payable external {
        IERC20 fromToken = swapInfos[0].fromToken;
        if (address(fromToken) == ETHER_ADDRESS)
            require(msg.value == fromTokenAmount, "ERR_INVALID_AMOUNT");
        else {
            uint256 _fromTokenBalance = getTokenBalance(fromToken);
            fromToken.safeTransferFrom(msg.sender, address(this), fromTokenAmount);
            require(getTokenBalance(fromToken).sub(_fromTokenBalance) == fromTokenAmount, "ERR_INVALID_AMOUNT");
        }

        IERC20 toToken = swapInfos[0].fromToken;
        for (uint8 i; i < swapInfos.length; i++) {
            fromToken = swapInfos[i].fromToken;
            require(address(fromToken) == address(toToken), "ERR_INCONTINUOUS_SWAP_PATH");
            toToken = swapInfos[i].toToken;
            require(address(fromToken) != address(toToken), "ERR_INVALID_TO_TOKEN");

            if (swapInfos[i].dex == oneInchAggregator) {
                approveToken(fromToken, oneInchAggregator, fromTokenAmount);
                uint256 toTokenAmount = getTokenBalance(toToken);
                (bool success, ) = oneInchAggregator.call{value: msg.value}(swapInfos[i].swapData);
                require(success, "ERR_DEX_SWAP_FAILED");
                fromTokenAmount = getTokenBalance(toToken).sub(toTokenAmount);
            } else if (proxies[swapInfos[i].dex] || swapInfos[i].dex == receiver) {
                safeTransferAsset(swapInfos[i].dex, fromToken, fromTokenAmount);
            } else if (swapInfos[i].dex == anyswapRouter) {
                require(targetChainSwapInfo.length > 0, "ERR_TARGET_CHAIN_SWAP_INFO");
                approveToken(fromToken, anyswapRouter, fromTokenAmount);
                IAnyswapV3Router(anyswapRouter).anySwapOutUnderlying(anyTokenMapping[address(fromToken)], address(this), fromTokenAmount, targetChainSwapInfo[0].chainId);
            } else revert("ERR_INVALID_DEX");

            emit SourceChainSwap(swapId, msg.sender, swapInfos[i].chainId, swapInfos[i], fromTokenAmount);
        }

        for (uint8 i; i < targetChainSwapInfo.length; i++) {
            emit TargetChainSwap(swapId, receiver, targetChainSwapInfo[i].chainId, targetChainSwapInfo[i]);
        }

        swapId += 1;
    }

    function _swapFor(
        uint256 _swapId,
        uint256 fromTokenAmount,
        SwapInfo[] calldata swapInfos,
        address receiver
    ) private {
        IERC20 fromToken;
        for (uint8 i; i < swapInfos.length; i++) {
            fromToken = swapInfos[i].fromToken;
            IERC20 toToken = swapInfos[i].toToken;
            address to = swapInfos[i].dex;

            if (to == oneInchAggregator) {
                approveToken(fromToken, oneInchAggregator, fromTokenAmount);
                uint256 toTokenAmount = getTokenBalance(toToken);
                (bool success, ) = oneInchAggregator.call{value: msg.value}(swapInfos[i].swapData);
                if (!success) {
                    safeTransferAsset(receiver, fromToken, fromTokenAmount);
                    emit OneInchSwapFailed(address(fromToken));
                    break;
                }
                fromTokenAmount = getTokenBalance(toToken).sub(toTokenAmount);
            } else if (to == receiver) {
                    safeTransferAsset(receiver, fromToken, fromTokenAmount);
                break;
            }
        }
        emit SwapForCompleted(_swapId, receiver, address(fromToken), fromTokenAmount);
    }

    // AnySwapV3
    function swapForByOperator(
        uint256 _swapId,
        uint256 fromTokenAmount,
        SwapInfo[] calldata swapInfos,
        address receiver
    ) payable external {
        require(operators[msg.sender], "ERR_OPERATOR_ACCOUNT");
        _swapFor(_swapId, fromTokenAmount, swapInfos, receiver);
    }

    function swapForByProxy(
        uint256 _swapId,
        uint256 fromTokenAmount,
        SwapInfo[] calldata swapInfos,
        address receiver
    ) payable external {
        require(proxies[msg.sender], "ERR_PROXY_ACCOUNT");

        IERC20 fromToken = swapInfos[0].fromToken;
        if (address(fromToken) == ETHER_ADDRESS)
            require(msg.value == fromTokenAmount, "ERR_INVALID_AMOUNT");
        else {
            fromToken.safeTransferFrom(msg.sender, address(this), fromTokenAmount);
        }
        _swapFor(_swapId, fromTokenAmount, swapInfos, receiver);
    }
}
