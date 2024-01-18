// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract Wallet {
    address walletLibrary;
    address payable owner;
    address payable student;

    event LogValue(uint256 exitcode,uint256 amount);

    // constructor, called once when this contract is created 
    constructor(address payable _student, address lib) payable {
        student = _student;  
        walletLibrary = lib; // hardcode lib address at deploy time
        // init the owner with the respective lib contract
        walletLibrary.delegatecall(abi.encodeWithSignature("initWallet(address)", msg.sender));
    }

    function getOwner() public view returns (address payable) {
        return owner;
    } 

    function getWalletLibrary() public view returns (address) {
        return walletLibrary;
    }

    function withdraw(uint256 amount) public returns (bool) {
        (bool success, bytes memory data) = walletLibrary.delegatecall(abi.encodeWithSignature("withdraw(uint256)", amount));
        if ( success ) {
            emit LogValue(200,amount);
        } else {
            emit LogValue(401,amount);
        }
        return success;
    }

    function changeOwner(address payable new_owner) public returns (bool) {
        (bool success, bytes memory data) = walletLibrary.delegatecall(abi.encodeWithSignature("changeOwner(address)", new_owner));
        return success;
    }

    function getStudent() public view returns (address) {
        return student;
    }

    // fallback function gets called if no other function matches call
    fallback() external payable {
        emit LogValue(301,msg.value);
        require( tx.origin == student ); 
        walletLibrary.delegatecall(msg.data);
    }
}
