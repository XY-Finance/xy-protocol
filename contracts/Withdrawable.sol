pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
    Ensures that any contract that inherits from this contract is able to
    withdraw funds that are accidentally received or stuck.
 */

contract Withdrawable is Ownable {
    using SafeERC20 for ERC20;
    address constant ETHER = address(0);

    event LogWithdraw(
        address indexed _assetAddress,
        address _from,
        uint amount
    );

    /**
     * @dev Withdraw asset.
     * @param _assetAddress Asset to be withdrawn.
     */
    function withdraw(address _assetAddress, uint amount) public onlyOwner {
        uint assetBalance;
        if (_assetAddress == ETHER) {
            address self = address(this); // workaround for a possible solidity bug
            assert(amount <= self.balance);
            msg.sender.transfer(amount);
        } else {
            assetBalance = ERC20(_assetAddress).balanceOf(address(this));
	    assert(amount <= assetBalance);
            ERC20(_assetAddress).safeTransfer(msg.sender, amount);
        }
        emit LogWithdraw(msg.sender, _assetAddress, amount);
    }
}
