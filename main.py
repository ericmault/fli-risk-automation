import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import random
import time
from coinGeckoPrices import *
from contract_addresses import *
from tokenInfo import *

from urllib.error import URLError

#ideas - make a radio button to see prices in collateral asset or in USD$
# put values/results from calculations next to text as string rather than have seperate lines. Benefits to separate lines is the coloring and easy to copy
#need some sort of control on if trade size is too big to the point where slippage is 1% that messes up the debt delever per trade
# put button on side bar that says reset to current prices and then we can take away the current data from the top.
#need way to make sure price impact liquidity is correct, because right now if you go to the max 
    # tradesize on the spreadsheet (2200) where the current 1% depth is listed at 3000, the 2200 trade say it's 1% on the top chart
#could put some of this data in tables rather than having it all one after the other


st.title('FLI Risk Automation')
ethFLISafeLR = 2.3 
tradeSizeScale = 1
fees = 0.03
timeBetweenTrades = 120

productSelection = st.selectbox('Select', ["ETH2x-FLI","BTC2x-FLI"])

if productSelection == "ETH2x-FLI":
    
    # ------ Current Data -------
    
    st.header('Current Data')
    left_column, right_column = st.columns(2)
    # ## Left Column is ETH info ##
    # # left_column.write(f"Coingecko ETH FLI Price is: "+str(coinGeckoPriceData(ETHFLI_COINGECKO_ID)))
    # left_column.write("Coingecko ETH FLI Price is:")
    # left_column.write(coinGeckoPriceData(ETHFLI_COINGECKO_ID))

    # # left_column.write(f"Coingecko ETH Price is: "+str(coinGeckoPriceData(ETH)))
    # left_column.write("Coingecko ETH Price is:")
    # left_column.write(coinGeckoPriceData(ETH))

    # # left_column.write(f"ETH FLI current supply is: "+str(getTotalSupply(ETHFLI_TOKEN_ADDRESS)))
    # left_column.write("ETH FLI Current Supply is:")
    # left_column.write(getTotalSupply(ETHFLI_TOKEN_ADDRESS))

    # left_column.write("ETH FLI Current Leverage Ratio is:")
    # left_column.write(getCurrentLeverageRatio(ETHFLI_STRATEGY_ADAPTER_ADDRESS))

    # left_column.write("ETH FLI Supply Cap is:")
    # left_column.write(getSupplyCap(ETHFLI_SUPPLY_CAP_ISSUANCE_ADDRESS))
    
    
    
    # def writeAbstracted(value,string,value):
    #     st.sidebar.write(string)
    #     st.sidebar.write(value)
        
    # def Writecoingetckoprice(value,string,value):
    #     st.sidebar.write(string)
    #     st.sidebar.write(value)
    
    
    #original
    left_column.write("Coingecko ETH FLI Price is:")
    ethFliPrice = coinGeckoPriceData(ETHFLI_COINGECKO_ID)
    left_column.write(ethFliPrice)
    
    
    # #second
    # ethFliPrice = coinGeckoPriceData(ETHFLI_COINGECKO_ID)
    # writeAbstracted("Coingecko ETH FLI Price is:",ethFliPrice)
    
    # #thrid
    # writeAbstracted("Coingecko ETH FLI Price is:",coinGeckoPriceData(ETHFLI_COINGECKO_ID))
    
    right_column.write("Coingecko ETH Price is:")
    ethPrice = coinGeckoPriceData(ETH)
    right_column.write(ethPrice)

    left_column.write("ETH FLI Current Supply is:")
    ethFliCurrentSupply = getTotalSupply(ETHFLI_TOKEN_ADDRESS)
    left_column.write(ethFliCurrentSupply)

    right_column.write("ETH FLI Supply Cap is:")
    sc = getSupplyCap(ETHFLI_SUPPLY_CAP_ISSUANCE_ADDRESS)
    right_column.write(sc)

    left_column.write("ETH FLI Current Leverage Ratio is:")
    ethFliCurrentLeverageRatio = getCurrentLeverageRatio(ETHFLI_STRATEGY_ADAPTER_ADDRESS)
    left_column.write(ethFliCurrentLeverageRatio)



    # ------ Side Bar -------

    priceChange = st.sidebar.number_input('Enter Price Change in %',min_value=-50,max_value=150,value=0,step=10)
    userInputEthPrice = (1+(priceChange/100))*ethPrice
    userInput_eth_max_trade_size_slider = st.sidebar.slider('ETH Max Trade Size', min_value=400, max_value=2000, value=800, step=100)
    userInput_supply = st.sidebar.slider('ETH FLI Supply', min_value=(sc-10000), max_value=(sc+100000), value=sc, step=100)
    userDexSupplyDepth = st.sidebar.slider('1% Dex Supply Depth', min_value=(1000), max_value=(10000), value=2000, step=100)
    
    
    # ------ Calculations -------
    st.header('Calculations Based on Inputs from leftt bar')
    

    
    st.write("post eth price percent change")
    st.write(userInputEthPrice)
    
    st.write("current Collateral Notaional units:")
    collateralNotaionalUnits = ethFliPrice*ethFliCurrentLeverageRatio/userInputEthPrice*ethFliCurrentSupply
    st.caption('current Collateral Notaional units = ethFliPrice x ethFliCurrentLeverageRatio/userInputEthPrice x ethFliCurrentSupply')
    st.write(collateralNotaionalUnits)
    
    st.write("current Collateral Notaional Price:")
    st.caption('current Collateral Notaional Price = collateralNotaionalUnits*ethPrice')
    collateralNotionalPrice = collateralNotaionalUnits*ethPrice
    st.write(collateralNotionalPrice)
    
    st.write("current borrowed asset Notional Price:")
    st.caption('current borrowed asset Notional Price = collateralNotionalPrice-ethFliPrice*ethFliCurrentSupply')
    borrowNotionalPrice = collateralNotionalPrice-ethFliPrice*ethFliCurrentSupply
    st.write(borrowNotionalPrice)
    
    st.write("AUM")
    st.caption('AUM = collateralNotionalPrice-borrowNotionalPrice')
    aum = collateralNotionalPrice-borrowNotionalPrice
    st.write(aum)
    
    st.write("Price Drop to Liquidation from current LR")
    
    endLR = 2.9
    diff = endLR - ethFliCurrentLeverageRatio
    drop = diff/2
    st.caption('(Max LR of 2.9 - current LR) / 2')
    st.write(drop*100)
    
    newCollateralAssetPrice = ethPrice * (1-drop)
    st.write("new Collateral Asset Price")
    st.caption('ethPrice * (1-drop)')
    st.write(newCollateralAssetPrice)


    newCollateralNotionalValue = newCollateralAssetPrice *collateralNotaionalUnits
    st.caption('newCollateralAssetPrice *collateralNotaionalUnits')
    st.write(newCollateralNotionalValue)
    
    newBorrowNotionalValue = borrowNotionalPrice
    st.caption('newBorrowNotionalValue = borrowNotionalPrice')
    st.write(newBorrowNotionalValue)
    
    newAUM = newCollateralNotionalValue - newBorrowNotionalValue
    st.caption('newCollateralNotionalValue - newBorrowNotionalValue')
    st.write(newAUM)
    
    newLR = newCollateralNotionalValue/newAUM
    st.write("New Leverage Ratio")
    st.caption('newCollateralNotionalValue/newAUM')
    st.write(newLR)
    
    lRDifference = newLR-ethFliCurrentLeverageRatio
    st.write("Difference From Pervious leverage ratio")
    st.caption('New Leverage Ratio - old leverage ratio')
    st.write(lRDifference)
    
    # ----- safe LR -----
    st.write("Safe LR")
    st.write(ethFLISafeLR)
    
    distanceToSafeLR = newLR-ethFLISafeLR
    st.write("Distance to safe LR")
    st.caption('newLR-ethFLISafeLR')
    st.write(distanceToSafeLR)
    
    # ------ Collateral Calculations -------
    st.header('Collateral Calculataions')
    
    rebalanceSizeInCollateralAsset = (distanceToSafeLR/newLR)*collateralNotaionalUnits
    st.write("Total Rebalance Size in Collateral Asset")
    st.caption('Total Rebalance Size in Collateral Asset= (distanceToSafeLR/newLR)*collateralNotaionalUnits')
    st.write(rebalanceSizeInCollateralAsset)
    rebalanceSizeInDollars = rebalanceSizeInCollateralAsset*newCollateralAssetPrice
    st.caption(f'in dollars ${rebalanceSizeInDollars}')
    
    
    st.write("Number of Trades Required For Rebalance Based on  user input max trade size")
    st.caption('Trades Required For Rebalance = Total Rebalance Size in Collateral Asset/ max trade size')
    tradesRequired = rebalanceSizeInCollateralAsset/userInput_eth_max_trade_size_slider
    st.write(tradesRequired)
    
    st.write("Trade Slippage based on 1% Dex supply")
    st.caption('Trade Slippage based on 1% Dex supply = userInput Max Trade Size / 1% liquidity depth * 0.01 / Trade Size Scale')
    tradeSlippage = (userInput_eth_max_trade_size_slider/userDexSupplyDepth*0.01/tradeSizeScale)*100
    st.write(tradeSlippage)
    
    st.caption(f'plus fees of {fees} for a total of {fees+tradeSlippage}')
    
    
    st.write("Debt Delevered Per trade")
    st.caption('min(userInput_eth_max_trade_size_slider/tradeSizeScale,rebalanceSizeInCollateralAsset)*(1-slippage and fees)*new collateral asset price')
    debtDeleveredPerTrade = min(userInput_eth_max_trade_size_slider*tradeSizeScale,rebalanceSizeInCollateralAsset)*((1-(fees+tradeSlippage))*newCollateralAssetPrice)
    st.write(debtDeleveredPerTrade)
    
    st.write("Debt notional delevered")
    st.caption('Debt notional delevered = total rebalance size in collateral asset * (1-slppage) * new collateral asset price')
    debtNotionalDelevered = rebalanceSizeInCollateralAsset * (1-tradeSlippage) * newCollateralAssetPrice
    st.write(debtNotionalDelevered)
    
    
    st.header("Post Rebalance")
    
    st.write("Post Rebalance Collateral notaial units ")
    st.caption('Post Rebalance Collateral notaial units = pre collateral - rebalance size')
    postRebalanceCollateralNotionalUnits = collateralNotaionalUnits - rebalanceSizeInCollateralAsset
    st.write(postRebalanceCollateralNotionalUnits)
    
    postRebalanceCollateralNotionalValue = postRebalanceCollateralNotionalUnits* newCollateralAssetPrice
    st.caption(f'in dollars{postRebalanceCollateralNotionalValue}')
    
    
    st.write("Post Rebalance Borrow notaial value ")
    st.caption('Post Rebalance Borrow notaial value  = new borrow notiaonl value - debt notional delevered')
    postRebalanceBorrowedNotionalValue = newBorrowNotionalValue - debtNotionalDelevered
    st.write(postRebalanceBorrowedNotionalValue)
    
    
    st.write("Post Rebalance AUM")
    st.caption('Post Rebalance AUM  = Collateral notional value - Borrow notional value')
    postRebalanceAUM = postRebalanceCollateralNotionalValue - postRebalanceBorrowedNotionalValue
    st.write(postRebalanceAUM)
    
    st.write("Ending Leverage Ratio")
    st.caption('Ending Leverage Ratio = Post Collateral notional value / Post AUM')
    endingLeverageRatio = postRebalanceCollateralNotionalUnits/postRebalanceAUM
    st.write(endingLeverageRatio)
    
    st.write("Minutes to Complete Rebalance")
    st.caption('Minutes to Complete Rebalance = trade size required for rebalance * time between trades/60')
    minutesToCompleteRebalance = tradesRequired*timeBetweenTrades/60
    st.write(minutesToCompleteRebalance)

    
    
    

if productSelection == "BTC2x-FLI":
# ## Right Column is BTC info
# # right_column.write(f"Coingecko BTC FLI Price is: "+str(coinGeckoPriceData(BTCFLI_COINGECKO_ID)))
#     right_column.write("Coingecko BTC FLI Price is")
#     right_column.write(coinGeckoPriceData(BTCFLI_COINGECKO_ID))

#     # right_column.write(f"Coingecko BTC Price is: "+str(coinGeckoPriceData(BTC)))
#     right_column.write("Coingecko BTC Price is")
#     right_column.write(coinGeckoPriceData(BTC))

#     # right_column.write(f"BTC FLI current supply is: "+str(getTotalSupply(BTCFLI_TOKEN_ADDRESS)))
#     right_column.write("BTC FLI Current Supply is:")
#     right_column.write(getTotalSupply(BTCFLI_TOKEN_ADDRESS))

#     right_column.write("BTC FLI Current Leverage Ratio is:")
#     right_column.write(getCurrentLeverageRatio(BTCFLI_STRATEGY_ADAPTER_ADDRESS))

#     right_column.write("BTC FLI Supply Cap is:")
#     right_column.write(getSupplyCap(BTCFLI_SUPPLY_CAP_ISSUANCE_ADDRESS))
    
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
# st.checkbox('Check me out')
# st.radio('Radio', [1,2,3])
