import sys
import os
sys.path.append(os.path.abspath("../"))
import myutil as util


w3 = util.connect()
interface = util.compile_contract("./Greeter.sol")
receipt = util.deploy_contract(cabi=interface["abi"],cbin=interface["bin"])
contract = util.get_contract_instance(caddress=receipt["contractAddress"],cabi=interface["abi"],concise=True)

def test_initial():
    assert contract.greet() == "Hello"


def test_update():
    contract.setGreeting("Nihao", transact={"from": w3.eth.accounts[0]})
    assert contract.greet() == "Nihao"


