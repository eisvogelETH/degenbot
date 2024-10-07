from ..uniswap.v2_liquidity_pool import UniswapV2Pool
from ..uniswap.v3_liquidity_pool import UniswapV3Pool


class PancakeV2Pool(UniswapV2Pool): ...


class PancakeV3Pool(UniswapV3Pool):
    SLOT0_STRUCT_TYPES = [
        "uint160",
        "int24",
        "uint16",
        "uint16",
        "uint16",
        "uint32",
        "bool",
    ]