import web3
import web3.auto as web3auto
from web3.middleware import ExtraDataToPOAMiddleware
# the old way
#from web3.middleware import geth_poa_middleware

import time
import threading
import hashlib
import os
import subprocess
import json
from sha3 import keccak_256

import os
from datetime import datetime, timezone
import time

w3 = None
HOST="127.0.0.1"
PORT="8545"

def connect(host=None,port=None,poa=False):
    global w3
    if host is None:
        host=HOST
    if port is None:
        port=PORT
    if w3 is None or not w3.is_connected():
        w3 = web3.Web3(web3.HTTPProvider(f"http://{host}:{port}", request_kwargs={"timeout": 60 * 1000}))
        if poa:
            # inject PoA compatibility
            # the new way
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            # inject the old ways:
            #w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            #w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    assert w3.is_connected(), "Connecting to local Ethereum node failed!"
    return w3

def check_connection(chain_id=None):
    if not w3.is_connected():
        return False
    if (chain_id is not None) and w3.eth.chain_id == chain_id:
        return False
    return True

def print_conn_info():
    assert w3.is_connected(),"No w3 connection!"
    print(f"Main w3 connection info: ")
    print(f"chain id  = {w3.eth.chain_id}")
    print(f"net   id  = {w3.net.version}")
    print(f"name      = {w3.geth.admin.node_info()['name']}")
    print(f"enode     = {w3.geth.admin.node_info()['enode']}")
    #print(f"mining    = {w3.eth.mining}")
    print(f"syncing   = {w3.eth.syncing}")
    print(f"block ctr = {w3.eth.block_number}")
    print(f"peer ctr  = {w3.net.peer_count}")
    if w3.net.peer_count > 0:
        for peer in w3.geth.admin.peers():
            print(f"\tname  = {peer['name']}")
            print(f"\tenode = {peer['enode']}")
            print(f"\tip    = {peer['network']['remoteAddress']}")
            print(f"\t-------")

def compile_contract_with_libs(compiler_path,src_path,account=None,gas=None,debug=False):
    """ compile a single contract file (with libraries) and manually call the compiler.
    Use only absolute paths its better.
    """
    c_abi = ""
    c_bin = ""
    c_dep = dict() # contract dependencies

    if debug: print(f"compiler path: {compiler_path}")
    # Manually call solc
    output = subprocess.run([compiler_path,"--combined-json","abi,bin",src_path],capture_output=True)
    if output.returncode != 0:
        print("Error: Compiling contract")
        print(output)
        return None
    compiler_output = json.loads(output.stdout)

    if debug: print(f"compiler_output: {compiler_output}")
    # We have compiled a contract with dependencies e.g., on libs
    for sfile in compiler_output["contracts"]:
        directory, filename_with_extension = os.path.split(sfile.split(":")[0])
        if debug:
            print(f"src file: {sfile}")
            print(f"src path: {src_path}")
        if src_path.endswith(filename_with_extension):
            # First identify the base contract
            c_abi = compiler_output["contracts"][sfile]["abi"]
            c_bin = compiler_output["contracts"][sfile]["bin"]
        else:
            # all other contract are either libs or inheritted contracts,
            # the latter can be ignored since they have to be included in the
            # base contracts bytecode anyway (see ABI of base contract for inheritted functions)
            # To identify which is which we translate *all* source file path/name
            # to their replacement hash and later check the base contracts bytecode if this
            # replacement hash occures
            c_dep[sfile] = { "replace_str": "__$" + keccak_256(bytes(sfile, "utf-8")).hexdigest()[:34] + "$__",
                             "address_str": "",
                             "bin_str": compiler_output["contracts"][sfile]["bin"],
                             "abi_str": compiler_output["contracts"][sfile]["abi"] }

    if debug:
        print(f"c_bin: {c_bin}")
        print(f"c_abi: {c_abi}")
    for sfile,sdata in c_dep.items():
        if c_bin.find(sdata["replace_str"]) != -1:
            # replacement string found in compile binary base contract.
            # Deploy that contract and get its address to replace occurances
            print(sfile)
            print(sdata["replace_str"])
            print(sdata["abi_str"])
            print()
            print(sdata["bin_str"])
            tx_receipt = deploy_contract(
                                       cabi=sdata["abi_str"],
                                       cbin=sdata["bin_str"],
                                       account=account,
                                       gas=gas,
                                       argument=None,
                                       argument2=None,
                                       wait=True,
                                       value=0)
            c_dep[sfile]["address_str"] = tx_receipt['contractAddress'].replace("0x","")
            print("address: " + c_dep[sfile]["address_str"])
            c_bin = c_bin.replace(sdata["replace_str"],c_dep[sfile]["address_str"])

    #print()
    #print(c_bin)
    #print()
    #print(c_abi)
    return { "abi": c_abi, "bin": c_bin }.copy()

def deploy_contract(
        cabi,
        cbin,
        account=None,
        gas=None,
        argument=None,
        argument2=None,
        wait=True,
        value=0):
    """ deploy contract from JSON ABI and binary hex string (bin)
        which includes deployment constructor.
        Optinal arguments:
            account from which deployment tx is sent
            gas limit for deployment
            argument to the constructor
    """
    if account is None:
        account = w3.eth.accounts[0]
        w3.eth.default_account = account
    if gas is None:
        # somewhere around max gas
        #gas = 5_000_000 # this is too large for some default chain configs
        gas = 4_500_000

    contract=w3.eth.contract(abi=cabi,
                             bytecode=cbin)

    if argument is not None:
        if argument2 is not None:
            tx_hash = contract.constructor(argument,argument2).transact(
                {"from":account,
                 "gas":gas,
                 "value":value})
        else:
            tx_hash = contract.constructor(argument).transact(
                {"from":account,
                 "gas":gas,
                 "value":value})
    else:
        tx_hash = contract.constructor().transact(
                {"from":account,
                 "gas":gas,
                 "value":value})
    if wait:
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    else:
        return tx_hash

def get_contract_instance(
        caddress,
        cabi,
        account=None,
        concise=False,
        patch_api=False,
        concise_events=False,
        path=None,
        compiler="solc",
        debug=False):
    """ get contract instance from address and abi """

    if cabi is None and path is None:
        print("No ABI or path to source given")
        return None
    elif path is not None:
        cabi=compile_contract_with_libs(compiler,path,debug)["abi"]

    """
    # Depricated since v6:
    #https://web3py.readthedocs.io/en/stable/v5_migration.html#deprecated-concisecontract-and-implicitcontract
    if concise:
        instance = w3.eth.contract(
            address=caddress,
            abi=cabi,
            ContractFactoryClass=web3.contract.ConciseContract)
    else:
        instance = w3.eth.contract(
            address=caddress,
            abi=cabi)

    if concise and patch_api:
        #if concise and patch_api:
        # patch API s.t. all transactions are automatically waited for
        # until tx_receipt is received
        for name, func in instance.__dict__.items():
            if isinstance(func, web3.contract.ConciseMethod):
                instance.__dict__[name] = _tx_executor(func)
    """
    instance = w3.eth.contract(
            address=caddress,
            abi=cabi)
    return instance

def _tx_executor(contract_function):
    """ modifies the contract instance interface function such that whenever a transaction is performed
        it automatically waits until the transaction in included in the blockchain
        (unless wait=False is specified, in the case the default the api acts as usual)
    """
    def f(*args, **kwargs):
        #print(args,kwargs)
        wait = kwargs.pop("wait", True)
        txwait = kwargs.pop("txwait", False)
        #print(args,kwargs)
        #print(wait,txwait)
        if ("transact" in kwargs and wait) or txwait:
            tx_hash = contract_function(*args, **kwargs)
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            return tx_receipt
        return contract_function(*args, **kwargs)
    return f


def compile_and_deploy_contract(path,
        account=None,
        concise=True,
        patch_api=True,
        concise_events=True,
        argument=None,
        argument2=None,
        wait=True,
        value=0,
        gas=None,
        compiler="solc",
        w3conn=None,
        debug=False):
    """ compiles and deploy the given contract (from the ./contracts folder)
        returns the contract instance

        Changed default behaviour to use the installed solc compiler
        with custom flags per default: compiler="solc"
        Change to custom path to compiler location if necessary.
    """
    global w3
    if w3conn is not None:
        w3 = w3conn

    if not w3 or not w3.is_connected():
        connect()
    if account is None:
        if w3.is_address(w3.eth.default_account):
            account = w3.eth.default_account
        else:
            account = w3.eth.accounts[0]
            w3.eth.default_account = account

    # compile manually
    if debug:
        print(f"src path: {path}")
        print(f"compiler path: {compiler}")
    interface = compile_contract_with_libs(compiler_path=compiler,
                                           src_path=path,
                                           account=account,
                                           gas=gas,
                                           debug=debug)

    if debug: print(f"interface abi: {interface['abi']}")
    ret = deploy_contract(
                cabi=interface["abi"],
                cbin=interface["bin"],
                account=account,
                gas=gas,
                argument=argument,
                argument2=argument2,
                wait=wait,
                value=value)
    if wait:
        tx_receipt = ret
        contract = get_contract_instance(
            caddress=tx_receipt['contractAddress'],
            cabi=interface["abi"],
            patch_api=patch_api,
            concise=concise,
            concise_events=concise_events)
        return contract
    else:
        tx_hash = ret
        return tx_hash

# ------------------------------------
# Bulk deployment and check functions
# for the challenge environment

def persist_users(path,users):
    with open(path,'w') as f_output:
        json.dump(users,f_output,default=str)

def load_users(path):
    with open(path,'r') as f_input:
        return json.load(f_input,parse_int=int)

def send_accounts_money(users,amount):
    for u in users:
        account = w3.to_checksum_address(u["account_address"])
        u["seedbalance"] = amount
        w3.eth.send_transaction({"from":w3.eth.default_account,"to":account,"value":amount})
    return

def check_accounts_money(users,predicate=(lambda a, b: a == b)):
    for u in users:
        u_balance = get_balance(w3.to_checksum_address(u["account_address"]),"wei")
        u["balance"] = u_balance
        u_seedbalance = u["seedbalance"]
        if predicate(u_balance,u_seedbalance) == False:
            print("Predicate violation for:\n",u)
            assert False,"Predicate violation"

def forall_compile_and_deploy(users,
                              path,
                              contract_name,
                              value,
                              force_argument=None,
                              argument2=None,
                              compiler="solc",
                              debug=False):
    print("Compile and deploy started for {} users:".format(len(users)))
    for u in users:
        if force_argument is not None:
            print("*",end="")
            #print("Force argument: {}".format(force_argument))
            u_addr = force_argument
        else:
            u_addr = w3.to_checksum_address(u["account_address"])

        if argument2 is not None and argument2 is True:
            print("~",end="")
            #print("Double sha3 argument2: {}".format(argument2))
            tx_hash = compile_and_deploy_contract(path,
                                                   patch_api=False,
                                                   concise=True,
                                                   argument=u_addr,
                                                   argument2=w3.to_int(hexstr=w3.keccak(text=w3.keccak(text=u_addr).hex()).hex()),
                                                   wait=False,
                                                   value=value,
                                                   compiler=compiler,
                                                   debug=debug)
        elif argument2 is not None and isinstance(argument2,type(str())):
            print("+",end="")
            #print("Custom argument2: {}".format(argument2))
            tx_hash = compile_and_deploy_contract(path,
                                                   patch_api=False,
                                                   concise=True,
                                                   argument=u_addr,
                                                   argument2=argument2,
                                                   wait=False,
                                                   value=value,
                                                   compiler=compiler,
                                                   debug=debug)
        else:
            print(".",end="")
            tx_hash = compile_and_deploy_contract(path,
                                                   patch_api=False,
                                                   concise=True,
                                                   argument=u_addr,
                                                   wait=False,
                                                   value=value,
                                                   compiler=compiler,
                                                   debug=debug)
        # returns HexBytes
        # import hexbytes
        # help(hexbytes.main)
        u[contract_name + "_tx"] = tx_hash.hex()
        u[contract_name + "_seedvalue"] = value

    print("\nGetting tx receipts ...")
    time.sleep(17)
    for u in users:
        #print(u)
        tx_receipt = w3.eth.wait_for_transaction_receipt(u[contract_name + "_tx"])
        time.sleep(1)
        u[contract_name + "_addr"] = tx_receipt['contractAddress']
        print("-",end="")
    print()
    return users

def forall_check_contract(users,
                          c_path,
                          c_name,
                          predicate=(lambda a, b: a == b),
                          compiler="solc"):
    # Check for all users if the contract is initialized to the respective user
    # and that the balance is the seed value
    print("Check started for {} users:".format(len(users)))

    for u in users:
        c_abi = compile_contract_with_libs(compiler_path=compiler,src_path=c_path)["abi"]
        u_c_addr = u[c_name + "_addr"]
        u_c_instance = get_contract_instance(u_c_addr,c_abi,concise=False)

        # check owner
        #print(u_c_instance.functions.getStudent().call())
        #print(w3.toChecksumAddress(u["account"]))
        assert u_c_instance.functions.getStudent().call() == w3.to_checksum_address(u["account_address"])
        # check balance
        u_c_seedvalue = u[c_name + "_seedvalue"]
        u_c_balance = get_balance(u_c_addr,"wei")
        u[c_name + "_balance"] = u_c_balance
        if predicate(u_c_balance, u_c_seedvalue) == False:
            print("Predicate violation for:\n",u)
        print(".",end="")
    print()
    return users

# ---------------
# Helper scripts

def get_balance(address,unit="ether"):
    address = w3.to_checksum_address(address)
    if unit == "wei":
        return int(w3.eth.get_balance(address))
    else:
        return w3.from_wei(w3.eth.get_balance(address),unit)

def send_ether(_value,_to,_from=None):
    if _from is None:
        _from = w3.eth.default_account
    tx_hash = w3.eth.send_transaction({'from':_from,
                                      'to':_to,
                                      'value':w3.to_wei(_value,"ether")})
    return tx_hash

def write_keystore_file(path,account_json):
    current_time_utc = datetime.now(timezone.utc)
    formatted_timestamp = current_time_utc.strftime("UTC--%Y-%m-%dT%H-%M-%S.%fZ--")
    file_name = formatted_timestamp + account_json["address"]
    path += file_name
    print(f"writing to {file_name} ...")
    with open(path, 'w') as json_file:
        json.dump(account_json, json_file)
    return

def get_events(contract_instance, event_name):
    # eventFilter = contract.eventFilter(event_name, {"fromBlock": 0})
    eventFilter = contract_instance.events.__dict__[event_name].createFilter(fromBlock=0)
    return [e for e in eventFilter.get_all_entries() if e.address == contract_instance.address]

# -----------
# w3 helper

def mine_block():
    w3.providers[0].make_request('evm_mine', params='')


def mine_blocks_until(predicate):
    while not predicate():
        mine_block()

def getBalance(address):
    return w3.fromWei(w3.eth.getBalance(address),'ether')

# -----------

def flatten(list_of_lists):
    return [y for x in list_of_lists for y in x]


def wait_for(predicate, check_interval=1.0):
    while not predicate():
        time.sleep(check_interval)

# -----------

def run(func_or_funcs, args=()):
    """ executes the given functions in parallel and waits
        until all execution have finished
    """
    threads = []
    if isinstance(func_or_funcs, list):
        funcs = func_or_funcs
        for i, f in enumerate(funcs):
            arg = args[i] if isinstance(args, list) else args
            if (arg is not None) and (not isinstance(arg, tuple)):
                arg = (arg, )
            threads.append(threading.Thread(target=f, args=arg))
    else:
        func = func_or_funcs
        assert isinstance(args, list)
        for arg in args:
            xarg = arg if isinstance(arg, tuple) else (arg, )
            threads.append(threading.Thread(target=func, args=xarg))

    for t in threads:
        t.start()
    for t in threads:
        t.join()




