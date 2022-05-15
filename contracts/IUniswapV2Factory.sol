/// SPDX-License-Identifier: MPL-2.0
// Creator: Manifold Finance
// PackageName: @securerpc/simulate-bundle
// PackageOriginator: ManifoldFinance
// PackageHomePage: https://github.com/manifoldfinance/securerpc-simulate-bundle

pragma solidity >=0.8.0 <0.9.0;

interface IUniswapV2Factory {
    function allPairsLength() external view returns (uint256);

    function allPairs(uint256 i) external view returns (address);

    function getPair(address token0, address token1) external view returns (address);
}
