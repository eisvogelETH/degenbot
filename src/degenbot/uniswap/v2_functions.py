import itertools
from collections.abc import Iterable
from fractions import Fraction
from typing import TYPE_CHECKING

import eth_abi.packed
from eth_typing import ChecksumAddress
from eth_utils.crypto import keccak
from hexbytes import HexBytes

from degenbot.functions import create2_address

if TYPE_CHECKING:
    from degenbot.uniswap.managers import UniswapV2PoolManager
    from degenbot.uniswap.v2_liquidity_pool import UniswapV2Pool


def generate_v2_pool_address(
    deployer_address: str | bytes,
    token_addresses: Iterable[str | bytes],
    init_hash: str | bytes,
) -> ChecksumAddress:
    """
    Get the deterministic V2 pool address generated by CREATE2. Uses the token address to generate
    the salt. The token addresses can be passed in any order.

    Adapted from https://github.com/Uniswap/universal-router/blob/59f1291d3760d2537a7bd1cbf37317922a49efb0/contracts/modules/uniswap/v2/UniswapV2Library.sol#L50
    """

    sorted_token_addresses = sorted([HexBytes(address) for address in token_addresses])

    salt = keccak(
        eth_abi.packed.encode_packed(
            ("address", "address"),
            sorted_token_addresses,
        )
    )

    return create2_address(
        deployer=deployer_address,
        salt=salt,
        init_code_hash=init_hash,
    )


def get_v2_pools_from_token_path(
    tx_path: Iterable[ChecksumAddress | str],
    pool_manager: "UniswapV2PoolManager",
) -> list["UniswapV2Pool"]:
    result: list[UniswapV2Pool] = []
    for token_addresses in itertools.pairwise(tx_path):
        pool = pool_manager.get_pool_from_tokens(
            token_addresses=token_addresses,
            silent=True,
        )
        if TYPE_CHECKING:
            assert isinstance(pool, UniswapV2Pool)
        result.append(pool)
    return result


def constant_product_calc_exact_in(
    amount_in: int,
    reserves_in: int,
    reserves_out: int,
    fee: Fraction,
) -> int:
    """
    Calculate the amount out for an exact input from a constant product (x*y=k) invariant pool.
    """

    return (amount_in * (fee.denominator - fee.numerator) * reserves_out) // (
        reserves_in * fee.denominator + amount_in * (fee.denominator - fee.numerator)
    )


def constant_product_calc_exact_out(
    amount_out: int,
    reserves_in: int,
    reserves_out: int,
    fee: Fraction,
) -> int:
    """
    Calculate the amount in necessary for an exact output swap through a constant product (x*y=k)
    invariant pool.
    """

    return 1 + (reserves_in * amount_out * fee.denominator) // (
        (reserves_out - amount_out) * (fee.denominator - fee.numerator)
    )
