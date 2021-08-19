from brownie import accounts, Swapper, TestERC20, network
from brownie.network.gas.strategies import GasNowScalingStrategy
from brownie.network import gas_price

from constants import XY_CONTRACT_ADDRESS, ETHEREUM_TO_BSC_CONFIG, BSC_TO_ETHEREUM_CONFIG


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

def balance_tokens(use_accounts, from_token_address, amount):
    token = TestERC20.at(from_token_address)
    decimal = token.decimals()
    is_balanced = False
    while not is_balanced:
        min_less_account = None
        min_balance = 10**10 * (10**decimal)
        max_enough_account = None
        max_balance = 0
        is_balanced = True
        for account in use_accounts:
            balance = token.balanceOf(account)
            if balance < amount:
                is_balanced = False
                if balance < min_balance:
                    min_less_account = account
                    min_balance = balance
            elif balance > max_balance and balance >= amount:
                max_enough_account = account
                max_balance = balance
        print('min balance:', min_less_account, min_balance)
        print('max balance:', max_enough_account, max_balance)
        if not is_balanced:
            if max_balance - amount < amount - min_balance:
                print(f'balance not enough')
                break
            send_amount = amount - min_balance
            if send_amount > 0:
                print(f'transfer {send_amount} {token.symbol()} from {max_enough_account} to {min_less_account}')
                token.transfer(min_less_account, send_amount, {'from': max_enough_account, 'required_confs': 1})

def main():
    # set accounts
    use_accounts = accounts

    swapper = Swapper.at(XY_CONTRACT_ADDRESS)

    active_network = network.show_active()
    print('network:', active_network)

    if active_network == 'mainnet':
        gas_strategy = GasNowScalingStrategy("rapid", increment=1.2)
        gas_price(gas_strategy)
    
    if active_network == 'mainnet' or active_network == 'mainnet-fork':
        approve(swapper, ETHEREUM_TO_BSC_CONFIG.from_token_address, use_accounts)
        balance_tokens(use_accounts, ETHEREUM_TO_BSC_CONFIG.from_token_address, ETHEREUM_TO_BSC_CONFIG.amount)
    elif active_network == 'bsc' or active_network == 'bsc-fork':
        approve(swapper, BSC_TO_ETHEREUM_CONFIG.from_token_address, use_accounts)
        balance_tokens(use_accounts, BSC_TO_ETHEREUM_CONFIG.from_token_address, BSC_TO_ETHEREUM_CONFIG.amount)
