// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

contract Visibility {
    uint256 constant public cpub_int = 0x10; //set at compile time
    uint256 public pub_int;   //getter is created automatically 
    uint256 internal int_int; //no getter but available in derived contracts 
    uint256 private priv_int;

    event echange(uint256 indexed v);
    event ichange(uint256 indexed v);
    event pchange(uint256 indexed v);

    constructor() payable {
        pub_int = 0x20;
        int_int = 0x30;
        priv_int = 0x40;
    }
    
    // Function _should_ only be called from external accounts/contracts
    // Although can also be called form this contract with this.
    function ext_change() external returns (uint256) {
        priv_int += 1;
        emit echange(priv_int);
        return priv_int;
    }
    
    // Internal functions cannot be called directly from external accounts/contracts
    // Only indirectly 
    function int_change() internal returns (uint256) {
        int_int += 1;
        emit ichange(int_int);
        return int_int;
    }

    // Public functions are callable from everywhere
    function pub_change() public returns (uint256) {
        this.ext_change();
        int_change();

        pub_int += 1;
        emit pchange(pub_int);  
        return pub_int;
    }

    // view:
    // * Not modify any state (only enforced by compiler since 0.5.0!) 
    //   Enforced by STATICALL at runtime since byzantium. 
    function view_priv_int(uint256 v) view public returns (uint256) {
        //priv_int = v; 
        return v + priv_int;
    }
   
    // pure:
    // * Not modify any state
    // * Not read any state (cannot by enforced since blockchain is public)
    function pure_priv_int(uint256 v) pure public returns (uint256) {
        //Those three lines will not compile:
        //priv_int += 1;
        //priv_int = v;
        //return priv_int;
        return v + 1;
    }
}
