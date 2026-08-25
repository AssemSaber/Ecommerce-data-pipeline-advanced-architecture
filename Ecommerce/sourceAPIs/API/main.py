from fastapi import FastAPI
import sys
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.files import read_csv

# .\venv\Scripts\activate

# defualt port number 8000
# http://127.0.0.1:8000/payments
#  uvicorn API.main:app --reload >>> api(folder_name).file_name:appName --reload (for any updates restart)

app = FastAPI()

PAYMENTS_FILE = r"H:\Atos\Ecommerce Dataset\olist_order_payments_dataset.csv"
REVIEWS_FILE = r"H:\Atos\Ecommerce Dataset\olist_order_reviews_dataset.csv"


@app.get("/payments")
def get_payments():

    df = read_csv(PAYMENTS_FILE)

    return df.to_dict(orient="records")


@app.get("/order-reviews")
def get_order_reviews():

    print("REVIEWS FILE PATH:")
    print(REVIEWS_FILE)

    df = read_csv(REVIEWS_FILE)

    print("COLUMNS:")
    print(df.columns.tolist())

    print("FIRST ROWS:")
    print(df.head())

    df = df.astype(object).where(df.notna(), None)

    return df.to_dict(orient="records")