// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract CUSDT is ERC20 {
    constructor() ERC20("Commitment USDT", "CUSDT") {
        _mint(msg.sender, 100_000_000 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }
}
