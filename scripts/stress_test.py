import time

from brownie import accounts, Swapper, TestERC20, network, web3
from brownie.network.gas.strategies import GasNowScalingStrategy
from brownie.network import gas_price

from constants import (
    ETHEREUM_TO_BSC_CONFIG,
    BSC_TO_ETHEREUM_CONFIG,
    POLYGON_TO_BSC_CONFIG,
    PROCESS_CONFIG_PROD,
    PROCESS_CONFIG_DEV,
)
from utils.xy_optimizer_server import get_swap_input
from collections import namedtuple
from web3.middleware import geth_poa_middleware

Input = namedtuple('Input', ['amount', 'source_chain_swap', 'target_chain_swap', 'account', 'source_chain_id'])

use_dev_env = True
if use_dev_env:
    process_config = PROCESS_CONFIG_DEV
else:
    process_config = PROCESS_CONFIG_PROD

def is_polygon_mainnet():
    active_network = network.show_active()
    if active_network == 'polygon':
        return True
    return False

def batch_send_swap(swapper, inputs):
    if is_polygon_mainnet():
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    for input in inputs:
        print('send account:', input.account)
        swapper.swap(
           input.amount,
           input.source_chain_swap,
           input.target_chain_swap,
           input.account,
           {'from': input.account, 'required_confs': 1},
        )

def make_inputs(source_chain_id, target_chain_id, from_token_address, to_token_address, amount, accounts):
    bridge_address = process_config.BRIDGE_ADDRESS_DICT[source_chain_id]
    inputs = []
    for account in accounts:
        amount, source_chain_swap, target_chain_swap = get_swap_input(
            process_config.XY_SERVER_URL,
            source_chain_id,
            from_token_address,
            amount,
            target_chain_id,
            to_token_address,
            account,
            process_config.XY_CONTRACT_ADDRESS,
            bridge_address
        )
        input = Input(amount, source_chain_swap, target_chain_swap, account, source_chain_id)
        inputs.append(input)
    return inputs

def approve(swapper, from_token_address, use_accounts):
    token = TestERC20.at(from_token_address)
    decimal = token.decimals()
    approve_amount = (10**5) * (10**decimal)
    min_approve_amount = (10**3) * (10**decimal)
    for account in use_accounts:
        allowance = token.allowance(account, swapper)
        if allowance < min_approve_amount:
            print('not approved.')
            token.approve(swapper, approve_amount, {'from': account, 'required_confs': 1})
        else:
            print('already approved.')

def test(swapper, use_accounts, config):
    inputs = make_inputs(
        config.source_chain_id,
        config.target_chain_id,
        config.from_token_address,
        config.to_token_address,
        config.amount,
        use_accounts
    )
    batch_send_swap(swapper, inputs)

def check_balance(use_accounts, from_token_address, need_amount):
    token = TestERC20.at(from_token_address)
    for account in use_accounts:
        if token.balanceOf(account) < need_amount:
            print(f'{account} balance not enough.')
            return False
    return True

def detect_receive(use_accounts, from_token_address):
    token = TestERC20.at(from_token_address)
    while True:
        try:
            for account in use_accounts:
                print(f'{account} balance: {token.balanceOf(account)}')
            print('-----------')
            time.sleep(2.5)
        except KeyboardInterrupt:
            break

def main():
    # set accounts
    use_accounts = accounts

    swapper = Swapper.at(process_config.XY_CONTRACT_ADDRESS)

    active_network = network.show_active()
    print('network:', active_network)

    if active_network == 'mainnet':
        gas_strategy = GasNowScalingStrategy("rapid", increment=1.2)
        gas_price(gas_strategy)

    if active_network == 'mainnet' or active_network == 'mainnet-fork':
        approve(swapper, ETHEREUM_TO_BSC_CONFIG.from_token_address, use_accounts)
        if check_balance(use_accounts, ETHEREUM_TO_BSC_CONFIG.from_token_address, ETHEREUM_TO_BSC_CONFIG.amount):
            test(swapper, use_accounts, ETHEREUM_TO_BSC_CONFIG)
    elif active_network == 'bsc' or active_network == 'bsc-fork':
        approve(swapper, BSC_TO_ETHEREUM_CONFIG.from_token_address, use_accounts)
        if check_balance(use_accounts, BSC_TO_ETHEREUM_CONFIG.from_token_address, BSC_TO_ETHEREUM_CONFIG.amount):
            test(swapper, use_accounts, BSC_TO_ETHEREUM_CONFIG)
    elif active_network == 'polygon' or active_network == 'polygon-fork':
        approve(swapper, POLYGON_TO_BSC_CONFIG.from_token_address, use_accounts)
        if check_balance(use_accounts, POLYGON_TO_BSC_CONFIG.from_token_address, POLYGON_TO_BSC_CONFIG.amount):
            test(swapper, use_accounts, POLYGON_TO_BSC_CONFIG)

    while True:
        try:
            print('sleep')
            time.sleep(5)
        except KeyboardInterrupt:
            break

    # detect_receive(use_accounts, BSC_TO_ETHEREUM_CONFIG.to_token_address)
    # detect_receive(use_accounts, ETHEREUM_TO_BSC_CONFIG.to_token_address)
