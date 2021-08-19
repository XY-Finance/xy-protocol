from brownie import accounts, Swapper, TestERC20
from brownie.network.gas.strategies import GasNowScalingStrategy
from brownie.network import gas_price

from constants import XY_CONTRACT_ADDRESS, BRIDGE_ADDRESS
from utils.xy_optimizer_server import get_swap_input

def main():
    gas_strategy = GasNowScalingStrategy('fast', increment=1.2)
    gas_price(gas_strategy)
    swapper = Swapper.at(XY_CONTRACT_ADDRESS)

    account = accounts[0]

    # for example
    source_chain_id = 1
    from_token_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' # USDC
    amount = 100000000
    target_chain_id = 56
    to_token_address = '0x55d398326f99059fF775485246999027B3197955'
    from_account_address = '0x2A8AA72fC7B1EfB9b5a1B0Beb6b89A79AeA2e619'
    receiver = account

    token = TestERC20.at(from_token_address)
    token.approve(swapper, amount, {'from': account})

    amount, source_chain_swap, target_chain_swap = get_swap_input(
        source_chain_id,
        from_token_address,
        amount,
        target_chain_id,
        to_token_address,
        from_account_address,
        XY_CONTRACT_ADDRESS,
        BRIDGE_ADDRESS
    )

    swapper.swap(
        amount,
        source_chain_swap,
        target_chain_swap,
        receiver,
        {'from': account},
    )
