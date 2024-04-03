import json
from datetime import datetime, timedelta


def get_chart_similar_coins(coin, start_date):
    if start_date is not None:
        start_date = datetime.fromisoformat(start_date)
        end_date = min(start_date + timedelta(days=30), datetime.now())
    else:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

    similar_coins = []

    return json.dumps({
        "type": "similar_coins",
        "coin": coin,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "data": similar_coins,
    })
