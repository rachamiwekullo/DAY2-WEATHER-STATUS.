import urllib.request
import json

try:
    # API URL endpoint
    url = "https://open.er-api.com/v6/latest/USD"
    
    # Send request and parse JSON response
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        
        # Check if request was successful
        if data.get("result") == "success":
            # Extract USD to KES rate
            kes_rate = data["rates"]["KES"]
            print(f"Current USD to KES Exchange Rate: 1 USD = {kes_rate:,.4f} KES\n")
            
            # Values to convert from KES to USD
            amounts_kes = [10000, 50000, 100000]
            
            print("Converted Values:")
            for amount in amounts_kes:
                amount_usd = amount / kes_rate
                print(f"KES {amount:,.2f} = USD ${amount_usd:,.2f}")
        else:
            print("Error: Failed to retrieve valid data from the exchange rate API.")

except Exception as e:
    print(f"An error occurred during the API request or calculation: {e}")