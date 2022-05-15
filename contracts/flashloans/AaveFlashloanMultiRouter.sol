/// SPDX-License-Identifier: MPL-2.0
// Creator: Manifold Finance
// PackageName: @securerpc/simulate-bundle
// PackageOriginator: ManifoldFinance
// PackageHomePage: https://github.com/manifoldfinance/securerpc-simulate-bundle

pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./aave/interfaces/ILendingPool.sol";
import { IUniswapV2Router02 } from "../IUniswapV2Router.sol";

contract AaveFlashloanMultiRouter is AccessControl {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    bytes32 public constant EXECUTOR_ROLE = keccak256("EXECUTOR_ROLE");

    address public constant LENDING_POOL_ADDRESS = 0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9;

    constructor(address[] memory admins, address[] memory executors) {
        _grantAdminRole(admins);
        _grantExecutorRole(executors);
    }

    function call(
        address[] calldata routers,
        address[] calldata tokens,
        uint256 amount,
        uint256 deadline
    ) external onlyRole(EXECUTOR_ROLE) {
        require(tokens.length > 1, "AaveFlashloanMultiRouter: tokens.length <= 1");
        require(
            routers.length == tokens.length - 1,
            "AaveFlashloanMultiRouter: routers.length != tokens.length - 1"
        );
        require(amount > 0, "AaveFlashloanMultiRouter: amount == 0");
        require(deadline >= block.timestamp, "AaveFlashloanMultiRouter: Expired deadline");

        // address of the contract receiving the funds
        address receiverAddress = address(this);

        // addresses of the reserves to flashloan
        address[] memory assets = new address[](1);
        assets[0] = tokens[0];

        // amounts of assets to flashloan.
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = amount;

        // 0 = no debt (just revert), 1 = stable, 2 = variable
        uint256[] memory modes = new uint256[](1);
        modes[0] = 0;

        // if the associated mode is not 0 then the incurred debt will be applied to the onBehalfOf address
        address onBehalfOf = receiverAddress;

        // encode our extra params to struct Args
        bytes memory params = abi.encode(routers, tokens, deadline, msg.sender);

        // referral to nobody
        uint16 referralCode = 0;

        ILendingPool(LENDING_POOL_ADDRESS).flashLoan(
            receiverAddress,
            assets,
            amounts,
            modes,
            onBehalfOf,
            params,
            referralCode
        );
    }

    // Called after your contract has received the flash loaned amount
    // Interface: @aave/protocol-v2/contracts/flashloan/interfaces/IFlashLoanReceiver.sol
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        require(
            msg.sender == LENDING_POOL_ADDRESS,
            "AaveFlashloanMultiRouter: msg.sender != lendingPoolAddress"
        );

        (address[] memory routers, address[] memory tokens, uint256 deadline, address sender) = abi
            .decode(params, (address[], address[], uint256, address));

        // approve & swap
        _swapExactTokensForTokens(routers, tokens, amounts[0], initiator, deadline);

        // Approve the LendingPool contract allowance to *pull* the owed amount
        for (uint256 i = 0; i < assets.length; i++) {
            address asset = assets[i];
            uint256 amountOwing = amounts[i] + premiums[i];

            // approve loan re-payment and transfer amount left over back to sender
            uint256 amountOver = IERC20(asset).balanceOf(initiator);
            require(
                amountOver > amountOwing,
                "AaveFlashloanMultiRouter: Not enough to re-pay loan"
            );

            IERC20(asset).safeApprove(LENDING_POOL_ADDRESS, amountOwing);

            // transfer remainder if any
            amountOver = amountOver - amountOwing;
            if (amountOver > 0) {
                IERC20(asset).safeTransfer(sender, amountOver);
            }
        }

        return true;
    }

    function withdraw(address payable to) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(to != address(0), "AaveFlashloanMultiRouter: to == address(0)");
        uint256 amount = address(this).balance;
        (bool success, ) = to.call{ value: amount }("");
        require(success, "AaveFlashloanMultiRouter: Failed to send Ether");
    }

    function withdrawERC20(address token, address recipient) public onlyRole(DEFAULT_ADMIN_ROLE) {
        require(token != address(0), "AaveFlashloanMultiRouter: token address == invalid");
        uint256 amount = IERC20(token).balanceOf(address(this));
        IERC20(token).safeTransfer(recipient, amount);
    }

    function withdrawERC20s(address[] calldata tokens, address recipient)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        require(tokens.length > 0, "AaveFlashloanMultiRouter: tokens.length > 0");
        for (uint256 i = 0; i < tokens.length; i++) {
            withdrawERC20(tokens[i], recipient);
        }
    }

    function destroy(address payable recipient) external onlyRole(DEFAULT_ADMIN_ROLE) {
        selfdestruct(recipient);
    }

    function _swapExactTokensForTokens(
        address[] memory routers,
        address[] memory tokens,
        uint256 amount,
        address to,
        uint256 deadline
    ) internal {
        uint256[] memory amounts = new uint256[](routers.length + 1);
        amounts[0] = amount;

        address[] memory path = new address[](2);

        for (uint256 i = 0; i < routers.length; i++) {
            require(amounts[i] > 0, "AaveFlashloanMultiRouter: No token balance");
            IERC20(tokens[i]).safeApprove(routers[i], amounts[i]);

            uint256 allowance = IERC20(tokens[i]).allowance(to, routers[i]);
            require(
                allowance >= amounts[i],
                "AaveFlashloanMultiRouter: Not enough token allowance"
            );

            path[0] = tokens[i];
            path[1] = tokens[i + 1];
            uint256[] memory amts = IUniswapV2Router02(routers[i]).swapExactTokensForTokens(
                amounts[i],
                0,
                path,
                to,
                deadline
            );
            amounts[i + 1] = amts[amts.length - 1];
        }
    }

    function _grantAdminRole(address[] memory allowed) internal {
        _grantRole(allowed, DEFAULT_ADMIN_ROLE);
    }

    function _grantExecutorRole(address[] memory allowed) internal {
        _grantRole(allowed, EXECUTOR_ROLE);
    }

    function _grantRole(address[] memory allowed, bytes32 role) internal {
        require(
            allowed.length > 0,
            "AaveFlashloanMultiRouter: At least one address needs to be present to grant a role"
        );
        for (uint256 i = 0; i < allowed.length; i++) {
            address a = allowed[i];
            require(
                a != address(0),
                "AaveFlashloanMultiRouter: Empty address is invalid as to designate a role"
            );
            _setupRole(role, a);
        }
    }
}
