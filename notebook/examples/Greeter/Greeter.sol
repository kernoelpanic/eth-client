// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

contract Greeter {
    bool private greetbool;
    string public greeting;
    uint256 public greetbit;

    constructor() {
        greeting = 'Hello';
    }

    function setGreeting(string memory _greeting) public {
        greeting = _greeting;
    }

    function getGreeting() view public returns (string memory) {
        return greeting;
    }

    function setGreetbool(bool _bool) public {
        greetbool = _bool;
    }

    function getGreetbool() view public returns (bool) {
        return greetbool; 
    }

    function setGreetbit(uint256 _bit) public {
        greetbit = _bit;
    }

    fallback() external payable {
        greetbit = greetbit ^ 1;
    }

    receive() external payable {
        greetbool = !greetbool;
    }
}
