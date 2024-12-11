// Svicoins ICO

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract svicoin_ico {

    // Introducing the total count of Svicoins available for sale
    uint public max_svicoins = 1000000;

    // Introducing the USD to Svicoins convertion rate
    uint public usd_to_svicoins = 1000;

    // Introducing the total number of SVicoins that have been bought by investors
    uint public total_svicoins_bought = 0;

    // Mapping from the investor address to its equity in Svicoins and USD
    mapping(address => uint) equity_svicoins;
    mapping(address => uint) equity_usd;

    // Checking if an investor cat buy/sell Svicoins, using modifier
    modifier can_buy_svicoins(uint usd_invested) {
        require(usd_invested * usd_to_svicoins + total_svicoins_bought <= max_svicoins);
        _;
    }

    // Getting the equity in Svicoins of an investor
    function equity_in_svicoins(address investor) external view returns (uint) {
        return equity_svicoins[investor];
    }

    // Getting the equity in USD of an investor
    function equity_in_usd(address investor) external view returns (uint) {
        return equity_usd[investor];
    }

    // Buying Svicoins
    function buy_svicoins(address investor, uint usd_invested) external
    can_buy_svicoins(usd_invested) {
        uint svicoins_bought = usd_invested * usd_to_svicoins;
        equity_svicoins[investor] += svicoins_bought;
        equity_usd[investor] = equity_svicoins[investor] / 1000;
        total_svicoins_bought += svicoins_bought;
    }

    // Selling Svicoins
    function sell_svicoins(address investor, uint svicoins_to_sell) external {
        equity_svicoins[investor] -= svicoins_to_sell;
        equity_usd[investor] = equity_svicoins[investor] / 1000;
        total_svicoins_bought -= svicoins_to_sell;
    }

}

