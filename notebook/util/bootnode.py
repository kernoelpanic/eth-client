#!/usr/bin/env python3
"""Mimics: bootnode -nodekeyhex <key> -writeaddress"""
import argparse
from eth_keys import keys  # pip install eth-keys

def enode_address_eth_keys(nodekeyhex: str) -> str:
    nodekeyhex = nodekeyhex.removeprefix("0x")
    priv = keys.PrivateKey(bytes.fromhex(nodekeyhex))
    # .to_hex() already returns the 64-byte pubkey (no 0x04 prefix), with a 0x
    return priv.public_key.to_hex().removeprefix("0x")

from coincurve import PrivateKey  # pip install coincurve

def enode_address_coincurve(nodekeyhex: str) -> str:
    priv = PrivateKey(bytes.fromhex(nodekeyhex.removeprefix("0x")))
    pub = priv.public_key.format(compressed=False)  # 65 bytes: 0x04 || X || Y
    return pub[1:].hex()                             # drop the 0x04 → 64 bytes

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-nodekeyhex", required=True)
    p.add_argument("-writeaddress", action="store_true")
    args = p.parse_args()
    enode_1 = enode_address_eth_keys(args.nodekeyhex)
    enode_2 = enode_address_coincurve(args.nodekeyhex)
    assert enode_1 == enode_2
    print(f"enode://{enode_1}@<IP>:<PORT>")
