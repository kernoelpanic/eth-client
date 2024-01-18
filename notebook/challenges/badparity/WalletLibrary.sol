// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract WalletLibrary {
     address walletLibrary; 
     address payable owner;
     address payable student;

     event LogValue(uint256 exitcode,uint256 amount);

     function initWallet(address payable _owner) public payable {
        owner = _owner;
     }

     function getOwner() public view returns (address payable) {
        return owner;
     }

     function changeOwner(address payable new_owner) public returns (bool success) {
        if (msg.sender == owner) {
            owner = new_owner;
            return true;
        } else {
            return false;
        }
     }

     function withdraw(uint256 amount) public returns (bool success) {
         if (msg.sender == owner) {
             return owner.send(amount);
         } else {
             return false;
         }
     }
    
     fallback() external payable {
         emit LogValue(200,msg.value);
     }
}
