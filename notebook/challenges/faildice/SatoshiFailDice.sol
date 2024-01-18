// SPDX-License-Identifier: MIT
//pragma solidity ^0.8.4;
pragma solidity 0.7.4;

contract SatoshiFailDice{
    // Hint: use web3.toInt() when converting bytes to soldity uint - else values may not match
    uint private big_secret;
    address student;
    address private owner;

    event EventDiceRoll(address user, uint8 user_roll, uint8 outcome, uint256 bet, bool has_won);
   
    constructor(address _student, uint _big_secret) payable{
        student = _student;
        owner = msg.sender;
        big_secret = _big_secret;
    }

    function rollDice(uint8 user_roll) payable public {
				// You get x10 of your bet if you roll a 42
				
				// ensure only the right student can interact with their contract
        require(tx.origin == student && msg.value > 0);
        require (msg.value > 0 );

        // grab a new random number
        uint8 contract_roll = PRNG(msg.sender);

        bool has_won = (42 == (contract_roll + user_roll ));
 
        if ( has_won ) {
            // Bad luck if you're betting more than you can possibly win
            if ( msg.value*10 >= address(this).balance) {
                payable(msg.sender).transfer(address(this).balance);
            }
            else { 
                // you won 
                payable(msg.sender).transfer(msg.value*10);
            } 
        }
        emit EventDiceRoll(msg.sender, user_roll, contract_roll + user_roll, msg.value, has_won);
        
    }
    
    function PRNG(address sender) private view returns(uint8){
				// Totally "awesome" PRNG
        //return uint8(keccak256(abi.encodePacked(sender, block.coinbase, now, big_secret)));
        return uint8(uint(keccak256(abi.encodePacked(sender, block.coinbase, block.timestamp, big_secret))));
    }

    function getStudent() public view returns (address) {
        return student;
    }

    // allow paying funds 
    receive() external payable { }

    function withdraw(uint256 amount) public {
        require(msg.sender == owner);
        payable(msg.sender).transfer(amount);
    }

}

