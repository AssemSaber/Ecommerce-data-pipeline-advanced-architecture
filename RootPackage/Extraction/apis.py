import requests
import pandas as pd
def getFromAPI(name):

    response = requests.get(
        f"http://127.0.0.1:8000/{name}"
    )

    response.raise_for_status()

    data = response.json()

    return pd.DataFrame(data)