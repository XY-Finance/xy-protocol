import os
import sys

sys.path.append(os.getcwd())

import requests

def convert_to_tuple(swap_infos):
    converted_swap_infos = []
    for swap_info in swap_infos:
        converted_swap_infos.append(tuple(swap_info))
    return converted_swap_infos

def get_swap_input(
    base_endpoint,
    source_chain_id,
    from_token_address,
    amount,
    target_chain_id,
    to_token_address,
    from_account_address,
    xy_contract_address,
    bridge_address,
):
    payload = {
        'sourceChainId': source_chain_id,
        'fromTokenAddress': from_token_address,
        'amount': amount,
        'targetChainId': target_chain_id,
        'toTokenAddress': to_token_address,
        'fromAccountAddress': from_account_address,
        'xyContractAddress': xy_contract_address,
        'bridgeAddress': bridge_address,
    }
    response_json = requests.get(f'{base_endpoint}swap', params=payload).json()
    print('response_json:', response_json)
    calldata = response_json['calldata']
    if not calldata:
        return
    amount = calldata['amount']
    source_chain_swap = convert_to_tuple(calldata['sourceChainSwaps'])
    target_chain_swap = convert_to_tuple(calldata['targetChainSwaps'])
    return amount, source_chain_swap, target_chain_swap
