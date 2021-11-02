## fli-risk-automation

## TO-DO

make a radio button to see prices in collateral asset or in USD$


put values/results from calculations next to text as string rather than have seperate lines. Benefits to separate lines is the coloring and easy to copy


need some sort of control on if trade size is too big to the point where slippage is 1% that messes up the debt delever per trade

put button on side bar that says reset to current prices and then we can take away the current data from the top.


need way to make sure price impact liquidity is correct, because right now if you go to the max tradesize on the spreadsheet (2200) where the current 1% depth is listed at 3000, the 2200 trade say it's 1% on the top chart

could put some of this data in tables rather than having it all one after the other


can add formatting like  borrowNotionalPrice = "{:,}".format(collateralNotionalPrice-ethFliPrice*ethFliCurrentSupply) if needed, but then need to make seperate var so we don't cause errors in further calcualtions down the line because this changes it to str