from app.community.plugins.coin_price_chart_similarity_search.utilities import CoinPriceChartSimilaritySearchUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class CoinPriceChartSimilaritySearchToolInput(BaseToolInput):
    coin_name = str
    start_date = str


CoinPriceChartSimilaritySearchTool = BaseTool(
    name="coin-price-chart-similarity-search",
    description="A tool that allows you to search for similar coins by price chart of the given time range",
    args_schema=CoinPriceChartSimilaritySearchToolInput,
    utility=CoinPriceChartSimilaritySearchUtility()
)


TOOLS = [CoinPriceChartSimilaritySearchTool]
