from app.community.plugins.coin_technical_analyzer.utilities import CoinTechnicalAnalyzerUtility


class CoinTechnicalAnalyzerToolInput:
    coin = str
    start_date = str


class CoinTechnicalAnalyzerTool:
    name = "coin_price_chart_similarity_search"
    description = "A tool that allows you to search for similar coins by price chart of the given time range"

    args_schema = CoinTechnicalAnalyzerToolInput
    utility = CoinTechnicalAnalyzerUtility()


TOOLS = [CoinTechnicalAnalyzerTool]

