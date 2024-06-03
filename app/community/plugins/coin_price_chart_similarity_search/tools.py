from app.community.plugins.coin_price_chart_similarity_search.utilities import CoinPriceChartSimilaritySearchUtility


class CoinPriceChartSimilaritySearchToolInput:
    coin = str
    start_date = str


class CoinPriceChartSimilaritySearchTool:
    name = "coin_price_chart_similarity_search"
    description = "A tool that allows you to search for similar coins by price chart of the given time range"

    args_schema = CoinPriceChartSimilaritySearchToolInput
    utility = CoinPriceChartSimilaritySearchUtility()


TOOLS = [CoinPriceChartSimilaritySearchTool]
