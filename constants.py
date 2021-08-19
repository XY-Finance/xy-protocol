from collections import namedtuple

ProcessConfigProd = namedtuple('ProcessConfigProd', ['XY_SERVER_URL', 'XY_CONTRACT_ADDRESS', 'BRIDGE_ADDRESS_DICT'])
ProcessConfigDev = namedtuple('ProcessConfigProd', ['XY_SERVER_URL', 'XY_CONTRACT_ADDRESS', 'BRIDGE_ADDRESS_DICT'])

PROCESS_CONFIG_PROD = ProcessConfigProd(
    'https://api.xy.finance/',
    '0xE1e853C58280F1e6ed9155CB06066e74B9102761',
    {
        1: '0xEb81D0236862Ec982d5f5fb169493b874D28A811',
        56: '0xa3bce6276C7348E9325B94a5ff8dd905Dcd6E3e8',
        137: '0x556319DC0f40414E41324078aFE1eB4D5e3fa511',
    }
)

PROCESS_CONFIG_DEV = ProcessConfigDev(
    'https://api-dev.xy.finance/',
    '0xb26A06E82843c2651a467990dd794953116Dd60a',
    {
        1: '0xd57d31adc3168A24A32AdA4B34db4194Fb0764DF',
        56: '0x7C7ebF444A83aed4CCe8a4e43C5EFc39D4b09624',
        137: '0x46bc90FEb2057889C34a0E564f8F64548C405Ca5',
    }
)

TestConfig = namedtuple('TestConfig', ['source_chain_id', 'target_chain_id', 'from_token_address', 'to_token_address', 'amount'])
ETHEREUM_TO_BSC_CONFIG = TestConfig(
    1,
    56,
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', # USDC(eth)
    '0x55d398326f99059fF775485246999027B3197955', # USDT(bsc)
    int(100 * 10**6),
)

BSC_TO_ETHEREUM_CONFIG = TestConfig(
    56,
    1,
    '0x55d398326f99059fF775485246999027B3197955', # USDT(bsc)
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', # USDC(eth)
    int(150 * 10**18),
)

BSC_TO_POLYGON_CONFIG = TestConfig(
    56,
    137,
    '0x55d398326f99059fF775485246999027B3197955', # USDT(bsc)
    '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', # USDT(polygon)
    int(150 * 10**18),
)

POLYGON_TO_BSC_CONFIG = TestConfig(
    137,
    56,
    '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', # USDT(polygon)
    '0x55d398326f99059fF775485246999027B3197955', # USDT(bsc)
    int(150 * 10**6),
)
