import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import random
import time
from coinGeckoPrices import *
from contract_addresses import *
from tokenInfo import *

from urllib.error import URLError

st.title('FLI Risk Automation')
ethFLISafeLR = 2.3 
tradeSizeScale = 1
fees = 0.03
timeBetweenTrades = 120

productSelection = st.selectbox('Select', ["ETH2x-FLI","BTC2x-FLI"])

if productSelection == "ETH2x-FLI":
    collateral = "ETH"
    borrowed = "USDC"
    # ------ Current Data and Prices -------
    ethFliPrice = coinGeckoPriceData(ETHFLI_COINGECKO_ID)
    ethPrice = coinGeckoPriceData(ETH)
    ethFliCurrentSupply = getTotalSupply(ETHFLI_TOKEN_ADDRESS)
    sc = getSupplyCap(ETHFLI_SUPPLY_CAP_ISSUANCE_ADDRESS)
    ethFliCurrentLeverageRatio = getCurrentLeverageRatio(ETHFLI_STRATEGY_ADAPTER_ADDRESS)
    
    
    st.header('Current Data')
    left_column, right_column = st.columns(2)
    
    left_column.write("Coingecko ETH FLI Price is:")
    left_column.write(ethFliPrice)
    
    right_column.write("Coingecko ETH Price is:")
    right_column.write(ethPrice)

    left_column.write("ETH FLI Current Supply is:")
    left_column.write(ethFliCurrentSupply)

    right_column.write("ETH FLI Supply Cap is:")
    right_column.write(sc)

    left_column.write("ETH FLI Current Leverage Ratio is:")
    left_column.write(ethFliCurrentLeverageRatio)

    # ------ Side Bar -------

    priceChange = st.sidebar.number_input('Enter Price Change in %',min_value=-50,max_value=150,value=0,step=10)
    userInputEthPrice = (1+(priceChange/100))*ethPrice
    userInput_eth_max_trade_size_slider = st.sidebar.slider('ETH Max Trade Size', min_value=400, max_value=10000, value=800, step=100)
    userInput_supply = st.sidebar.slider('ETH FLI Supply', min_value=(sc-10000), max_value=(sc+100000), value=sc, step=100)
    userDexSupplyDepth = st.sidebar.slider('1% Dex Supply Depth', min_value=(1000), max_value=(10000), value=3000, step=100)
    
    # ------ Calculations -------
    collateralNotaionalUnits = ethFliPrice*ethFliCurrentLeverageRatio/userInputEthPrice*ethFliCurrentSupply
    collateralNotionalPrice = collateralNotaionalUnits*ethPrice
    borrowNotionalPrice = collateralNotionalPrice-ethFliPrice*ethFliCurrentSupply
    aum = collateralNotionalPrice-borrowNotionalPrice
    
    ## NEED TO REVISIT HERE current equation is giving too high of a tolerable price drop
    endLR = 2.9
    diff = endLR - ethFliCurrentLeverageRatio
    drop = (diff/2)*100
    tempDrop = -0.22
    
    newCollateralAssetPrice = userInputEthPrice * (1+tempDrop)
    newCollateralNotionalValue = newCollateralAssetPrice *collateralNotaionalUnits
    # below is equal to itself because 1$ = 1$
    newBorrowNotionalValue = borrowNotionalPrice
    newAUM = newCollateralNotionalValue - newBorrowNotionalValue
    newLR = newCollateralNotionalValue/newAUM
    lRDifference = newLR-ethFliCurrentLeverageRatio
    distanceToSafeLR = ethFLISafeLR-newLR
    
    
    # ------ UI -------
    st.header('Calculations Based on Inputs from left bar')
    
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander(f"New {collateral} Price"):
                st.caption(f"Current {collateral} Price \* Percent Change")
        con_right_column.write(userInputEthPrice)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander(f"Current Collateral Notaional Units in {collateral}"):
            st.caption(f"Current Collateral Notaional units = {collateral} FLI Price \* Current Leverage Ratio / New {collateral} Price \* Current Supply")
        con_right_column.write(collateralNotaionalUnits)
    
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Current Collateral Notaional Price:"):
            st.caption(f'Current Collateral Notaional Price = Collateral Notaional Units x {collateral} Price')
        con_right_column.write(collateralNotionalPrice)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Current Borrowed Asset Notional Price:"):
            st.caption(f'Current Borrowed Asset Notional Price = collateralNotionalPrice - {collateral} FLI Price \* CurrentSupply')
        con_right_column.write(borrowNotionalPrice)
    
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("AUM"):
            st.caption('AUM = collateralNotionalPrice-borrowNotionalPrice')
        con_right_column.write(aum)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Percent Price Drop to Liquidation from current LR (currently fixed  to 22%)"):
            st.caption('Max LR of 2.9 - current LR) / 2')
        con_right_column.write(tempDrop)

    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("new Collateral Asset Price"):
            st.caption('ethPrice * (1-drop)')
        con_right_column.write(newCollateralAssetPrice)

    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("new Collateral Notional Value"):
            st.caption('newCollateralAssetPrice *collateralNotaionalUnits')
        con_right_column.write(newCollateralNotionalValue)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("new Borrow Notional Value"):
            st.caption('newBorrowNotionalValue = borrowNotionalPrice')
        con_right_column.write(newBorrowNotionalValue)
    
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("newAUM"):
            st.caption('newCollateralNotionalValue - newBorrowNotionalValue')
        con_right_column.write(newAUM)

    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("New Leverage Ratio"):
            st.caption('newCollateralNotionalValue/newAUM')
        con_right_column.write(newLR)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Difference From Pervious leverage ratio"):
            st.caption('New Leverage Ratio - old leverage ratio')
        con_right_column.write(lRDifference)

    # ----- safe LR -----
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Safe LR"):
            st.caption('This is the max LR set by configurations, currenlty hard coded')
        con_right_column.write(ethFLISafeLR)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Distance to safe LR"):
            st.caption('newLR-ethFLISafeLR')
        con_right_column.write(distanceToSafeLR)
    
    
    # ------ Collateral Calculations -------

    
    rebalanceSizeInCollateralAsset = (distanceToSafeLR/newLR)*collateralNotaionalUnits
    rebalanceSizeInDollars = rebalanceSizeInCollateralAsset*newCollateralAssetPrice
    tradesRequired = rebalanceSizeInCollateralAsset/userInput_eth_max_trade_size_slider
    tradeSlippage = (userInput_eth_max_trade_size_slider/userDexSupplyDepth*0.01/tradeSizeScale)*100
    debtDeleveredPerTrade = min(userInput_eth_max_trade_size_slider*tradeSizeScale,rebalanceSizeInCollateralAsset)*((1-(fees+tradeSlippage))*newCollateralAssetPrice)
    debtNotionalDelevered = rebalanceSizeInCollateralAsset * (1-tradeSlippage) * newCollateralAssetPrice

    

    # ------ Collateral UI -------
    st.header('Collateral Calculataions')
    
    option = st.selectbox(
    'View In',
    ('Collateral/ETH', 'USDC')) 
    
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Total Rebalance Size"):
            st.caption('Total Rebalance Size in Collateral Asset= (distanceToSafeLR/newLR)*collateralNotaionalUnits')
        if option == 'Collateral/ETH':
            con_right_column.write(rebalanceSizeInCollateralAsset)
        else:
            con_right_column.write(f'${rebalanceSizeInDollars}')
            
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Number of Trades Required For Rebalance Based on  user input max trade size"):
            st.caption('Trades Required For Rebalance = Total Rebalance Size in Collateral Asset/ max trade size')
            con_right_column.write(tradesRequired)

    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Trade Slippage based on 1% Dex supply"):
            st.caption('Trade Slippage based on 1% Dex supply = userInput Max Trade Size / 1% liquidity depth * 0.01 / Trade Size Scale')
            con_right_column.write(fees+tradeSlippage)
            con_right_column.caption(f'Trade slippage of {tradeSlippage} plus fees of {fees}')
            
    with st.container():
        con_left_column, con_right_column = st.columns(2)
    with con_left_column.expander("Debt Delevered Per trade"):
        st.caption('min(userInput_eth_max_trade_size_slider/tradeSizeScale,rebalanceSizeInCollateralAsset)*(1-slippage and fees)*new collateral asset price')
        con_right_column.write(debtDeleveredPerTrade)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
    with con_left_column.expander("Debt notional delevered"):
        st.caption('Debt notional delevered = total rebalance size in collateral asset * (1-slppage) * new collateral asset price')
        con_right_column.write(debtNotionalDelevered)
    
    
     # ------ Post Rebalance -------
    st.header("Post Rebalance")
    
    postRebalanceCollateralNotionalUnits = collateralNotaionalUnits - rebalanceSizeInCollateralAsset
    postRebalanceCollateralNotionalValue = postRebalanceCollateralNotionalUnits* newCollateralAssetPrice
    postRebalanceBorrowedNotionalValue = newBorrowNotionalValue - debtNotionalDelevered
    postRebalanceAUM = postRebalanceCollateralNotionalValue - postRebalanceBorrowedNotionalValue
    endingLeverageRatio = postRebalanceCollateralNotionalUnits/postRebalanceAUM
    minutesToCompleteRebalance = tradesRequired*timeBetweenTrades/60
    
    with st.container():
        con_left_column, con_right_column = st.columns(2)
        with con_left_column.expander("Post Rebalance Collateral notaial units"):
            st.caption('Post Rebalance Collateral notaial units = pre collateral - rebalance size')
        if option == 'Collateral/ETH':
            con_right_column.write(postRebalanceCollateralNotionalUnits)
        else:
            con_right_column.write(f'${postRebalanceCollateralNotionalValue}')
    
    with st.container():
        con_left_column, con_right_column = st.columns(2)
    with con_left_column.expander("Post Rebalance Borrow notaial value"):
        st.caption('Post Rebalance Borrow notaial value  = new borrow notiaonl value - debt notional delevered')
        con_right_column.write(postRebalanceBorrowedNotionalValue)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
    with con_left_column.expander("Post Rebalance AUM"):
        st.caption('Post Rebalance AUM  = Collateral notional value - Borrow notional value')
        con_right_column.write(postRebalanceAUM)
        
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
    with con_left_column.expander("Ending Leverage Ratio"):
        st.caption('Ending Leverage Ratio = Post Collateral notional value / Post AUM')
        con_right_column.write(endingLeverageRatio)
        
    with st.container():
        con_left_column, con_right_column = st.columns(2)
    with con_left_column.expander("Minutes to Complete Rebalance"):
        st.caption('Minutes to Complete Rebalance = trade size required for rebalance * time between trades/60')
        con_right_column.write(minutesToCompleteRebalance)

    
if productSelection == "BTC2x-FLI":
    
    st.write("Coingecko BTC FLI Price is")
    st.write(coinGeckoPriceData(BTCFLI_COINGECKO_ID))

    st.write("Coingecko BTC Price is")
    st.write(coinGeckoPriceData(BTC))

    st.write("BTC FLI Current Supply is:")
    st.write(getTotalSupply(BTCFLI_TOKEN_ADDRESS))

    st.write("BTC FLI Current Leverage Ratio is:")
    st.write(getCurrentLeverageRatio(BTCFLI_STRATEGY_ADAPTER_ADDRESS))

    st.write("BTC FLI Supply Cap is:")
    st.write(getSupplyCap(BTCFLI_SUPPLY_CAP_ISSUANCE_ADDRESS))
    
    
    btc_max_trade_size_slider = st.slider('BTC Max Trade Size', min_value=0, max_value=10, step=100)



# st.button('Optimize')
