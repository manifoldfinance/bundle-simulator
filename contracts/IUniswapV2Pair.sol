/// SPDX-License-Identifier: MPL-2.0
// Creator: Manifold Finance
// PackageName: @securerpc/simulate-bundle
// PackageOriginator: ManifoldFinance
// PackageHomePage: https://github.com/manifoldfinance/securerpc-simulate-bundle

pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

interface IUniswapV2Pair is IERC20Metadata {
    function factory() external view returns (address);

    function token0() external view returns (address);

    function token1() external view returns (address);

    function getReserves()
        external
        view
        returns (
            uint112,
            uint112,
            uint32
        );
}
