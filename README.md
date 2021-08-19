# x-contracts

## Function for clients


```
function swap(
    uint256 fromTokenAmount,
    SwapInfo[] calldata swapInfos,
    SwapInfo[] calldata targetChainSwapInfo,
    address receiver
)
```

ABI of contract could be found in this [file](https://github.com/XY-Finance/x-contracts/blob/main/build/contracts/Swapper.json).

Following are introductions of each parameter of the ```swap``` function.
> #### ```fromTokenAmount```
> > amount of token that a client swaps from

> #### ```swapInfos```
> > array of ```SwapInfo```, containing information of each step on source chain. ```SwapInfo``` would be explained in the last.

> #### ```targetChainSwapInfo```
> > array of ```SwapInfo```, containing information of each step on target chain.

> #### ```receiver```
> > address of the user that receives asset on target chain



> ```
> struct SwapInfo {
>     uint8 chainId;
>     address dex;
>     IERC20 fromToken;
>     IERC20 toToken;
>     bytes swapData;
> }
> ```
> ##### ```chainId```
> > ID of the chain that this swapInfo would be performed on. For example, if a client attempts to swap from ETH to BSC, ```chain_id``` of swapInfos would be ```1```; ones of ```targetChainSwapInfos``` would be ```56```.
> ##### ```dex```
> > The "to" address of the swap action.
> ##### ```fromToken```
> > The token planned to be swapped from of the swap action.
> ##### ```toToken```
> > The token planned to be swapped for of the swap action.
> ##### ```swapData```
> > The calldata that would be sent to ```dex```.
