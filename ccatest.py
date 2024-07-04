MERCHANT_CODE = "2998921"
ACCESS_CODE = ""
order_id = "7BE8E7551D62C750A223D3D0E951F286"
amount = "1000.00"
currency = "INR"
REDIRECT_URL = "rizad.me"
import requests

access_code = ACCESS_CODE
currency = "INR"
amount = "10.00"

url = f'https://test.ccavenue.com/transaction/transaction.do?command=getJsonData&access_code={access_code}&currency={currency}&amount={amount}'

try:
    response = requests.get(url)
    response.raise_for_status()
    jsonData = response.json()
    print(jsonData)

except Exception as e:
    print(f"An error occurred: {e}")
