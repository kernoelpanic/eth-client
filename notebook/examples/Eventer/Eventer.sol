// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

contract Eventer {

    event create(uint256 v);
    event funcall(address caller,uint256 value);
    event funcall2(address indexed caller,uint256 indexed value);
    event fallcall(address caller);

    constructor() {
        emit create(1);
    }

    function func1(uint256 v) public {
        emit funcall(msg.sender,v);
    }

    function func2(uint256 v) public {
        emit funcall2(msg.sender,v);
    }

    receive() external payable{
        emit fallcall(msg.sender);
    }

}
