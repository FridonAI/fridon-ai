import json
from datetime import datetime, timedelta

from app.utils.birdeye import convert_history_to_tensor, BirdEyeApiClient
from app.utils.timeseries import TimeSeriesVectorStore, TimeSeriesEmbeddings
from app.utils.timeseries.index.pgvector import PgVectorTimeSeriesIndex

embeddings = TimeSeriesEmbeddings("amazon/chronos-t5-tiny")
index = PgVectorTimeSeriesIndex()
vector_store = TimeSeriesVectorStore(embeddings, index)
token_list = json.load(open("data/coins-list.json", "r"))


def get_chart_similar_coins(coin, start_date):
    # convert iso date to timestamp
    if start_date is not None:
        start_date = datetime.fromisoformat(start_date)
        end_date = min(start_date + timedelta(days=30), datetime.now())
    else:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

    birdeye_api = BirdEyeApiClient(base_url="https://public-api.birdeye.so/defi",
                                   api_key="9f0fc8d9eb0f42758e36ea3f71bec8d6")

    similar_coins = []
    for token in token_list:
        if token['symbol'] == coin:
            tensor = convert_history_to_tensor(birdeye_api.get_history(token["address"], int(start_date.timestamp()), int(end_date.timestamp()), "1H"))

            results = vector_store.search(vector_store.embed(tensor), top_k=5)

            for result in results:
                if result[0] != coin:
                    similar_coins.append({
                        "score": result[1],
                        "coin": result[0],
                        "address": token["address"]
                    })
            break

    return json.dumps({
        "type": "similar_coins",
        "coin": coin,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "data": similar_coins,
    })
