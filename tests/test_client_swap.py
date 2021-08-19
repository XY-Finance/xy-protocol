from brownie import accounts, Swapper, TestERC20

from constants import XY_CONTRACT_ADDRESS, BRIDGE_ADDRESS_DICT
from utils.xy_optimizer_server import get_swap_input

def test_source_chain_swap():
    swapper = Swapper.at(XY_CONTRACT_ADDRESS)

    # for example
    source_chain_id = 1
    from_token_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' # USDC
    amount = 100000000
    target_chain_id = 56
    to_token_address = '0x55d398326f99059fF775485246999027B3197955' # binance USDT

    # The account must have USDC
    user_account =  accounts.at('0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503', force=True)
    from_account_address = user_account.address

    token = TestERC20.at(from_token_address)

    assert token.balanceOf(user_account) >= amount

    bridge_account = accounts.at(BRIDGE_ADDRESS_DICT[source_chain_id][target_chain_id], force=True)
    receiver = user_account

    token.approve(swapper, amount, {'from':user_account})

    amount, source_chain_swap, target_chain_swap = get_swap_input(
        source_chain_id,
        from_token_address,
        amount,
        target_chain_id,
        to_token_address,
        from_account_address,
        XY_CONTRACT_ADDRESS,
        bridge_account
    )

    assert int(amount) > 0

    if source_chain_swap[0][3].lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
        before_bridge_balance = bridge_account.balance()
    else:
        bridge_token = token = TestERC20.at(source_chain_swap[0][3])
        before_bridge_balance = bridge_token.balanceOf(bridge_account)

    swapper.swap(
        amount,
        source_chain_swap,
        target_chain_swap,
        receiver,
        {'from': user_account},
    )

    if source_chain_swap[0][3].lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
        after_bridge_balance = bridge_account.balance()
    else:
        bridge_token = token = TestERC20.at(source_chain_swap[0][3])
        after_bridge_balance = bridge_token.balanceOf(bridge_account)

    assert after_bridge_balance > before_bridge_balance
