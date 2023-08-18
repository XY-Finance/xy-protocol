// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

import "./openzeppelin/ERC20.sol";
import "./openzeppelin/Ownable.sol";

contract XYERC20 is ERC20, Ownable {

    constructor(string memory __name, string memory __symbol, address vault, uint256 amount) ERC20(__name, __symbol) {
        _mint(vault, amount);
    }

    mapping (address => bool) public isMinter;

    modifier onlyMinter {
        require(isMinter[msg.sender], "ERR_NOT_MINTER");
        _;
    }

    function setMinter(address minter, bool _isMinter) external onlyOwner {
        isMinter[minter] = _isMinter;

        emit SetMinter(minter, _isMinter);
    }

    function mint(address account, uint256 amount) external onlyMinter {
        _mint(account, amount);
    }

    function burn(address account, uint256 amount) external onlyMinter {
        _burn(account, amount);
    }

    event SetMinter(address minter, bool isMinter);
}
