emas_guide_prompt = """

Below is guide of Emas strategy from EmperorBTC.

########################
Beginners are obsessed with complicated strategies. Simple methods work wonders in the long run. I
will show you an EMA strategy to make big money without any leverage. Simple doesn't mean low
profit. 

TOOLS:
- 13,21 EMA on Daily
- 200 EMA on 4 hourly
- Volume confirmation

PREMISE:
1. Bullish crossover on the daily chart for 13 and 21 EMA.
2. 200 EMA on the 4 hourly chart acting as support.
3. All breakouts confirmed by volume. (13,21 EMA sloping upwards)
On the daily chart, 13 and 21 EMAs, should form a bullish Cross over.
1. The 13 EMA should be over the 21 EMA after a contraction.
2. Both EMAs should be upward sloping.
3. The price should be above the EMAs.


On the 4 hour chart, the 200 EMA should act as a support and entry should be made upon
confirmation by volume.


Here is a chart explaining a trade of 40% Profit.
1. 200 EMA Support
2. Entry on volume confirmation.
3. Addition to position upon accumulation confirmation.
The 200 EMA is powerful enough, that after the confirmations on the daily charts, high probability
trades can be made without any other tools. Here is a trade with 1. Entry on support by volume
confirmation. 2. Addition upon retest.

Here I've explained an entry and addition with the help of just volume expansion.
It's simple, easy to understand, it works and gives a high probability trade. I will be posting a 3 EMA
strategy in future. Please share it. It Might help a confused beginner. Study it and practice!
########################

Considering the above guide and calculated results of current charts of {coin_name} tell us your thoughts. 

Chart results below:
########################
{chart_results} 
########################

Don't write recommendations, just your concernts, possible circumstances, what does those chart results mean and so on. 

Don't make any assumptions or make up any information. Just use the information provided and your knowledge.

Your thoughts:
"""
