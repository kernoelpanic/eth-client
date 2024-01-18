// SPDX-License-Identifier: MIT
/**

Look Mom, I coded my first wallet contract to learn solidity!
It even supports multiple owners!

**/

pragma solidity 0.8.19;

contract NotAWallet{

	address public owner;
    address public student;
    mapping (address => bool) owners;
   
    constructor(address _student) payable{
        student = _student;
        owner = msg.sender;
    }

    function deposit() public payable  { 
        // recieve coins
    }   

    function addOwner(address newowner) public {
        require (owners[msg.sender] == true || msg.sender == owner);
        owners[newowner] = true;
    }   

    function removeOwner(address oldowner) public rightStudent {
        require(owners[msg.sender] = true); 
				owners[oldowner] = false;
    }

    function withdraw(uint256 amount) public {
        // only owners can withdraw funds
        require(owners[msg.sender] == true);
        payable(msg.sender).transfer(amount);
    }

    function isOwner(address testowner) public view returns (bool) {
            if (owners[testowner] == true) {
                return true;
            } else {
                return false;
            }
    }

	// ensure that only designated student has access to this challenge
    modifier rightStudent() {
        require(msg.sender == student || msg.sender == owner, "Access dendied!");
        _;
    }
    // helper function to check if interacting with right contract
    function getStudent() public view returns (address) {
        return student;
    }

}

