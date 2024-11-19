# Name: Derek Greene
# OSU Email: greenede@oregonstate.edu
# Course: CS361 - Software Engineering I
# Description: Financial report microservice that provides endpoints for curreny conversion,
#              financial summary, and ranked list of expenses and income by category. 


from flask import Flask, request, jsonify
from collections import defaultdict
import freecurrencyapi

app = Flask(__name__)

@app.route('/convert', methods=['GET'])
def convert():
    """
    Endpoint to convert currency. 
    Example request: curl "http://127.0.0.1:5000/convert?amount=20&fromCurrency=USD&toCurrency=CAD"
    Notes: fromCurrency and toCurrency should be 3 letter ISO 4217 currency codes. See supported currencies & codes at (https://freecurrencyapi.com/docs/currency-list)
    """
    
    amount = request.args.get('amount', type=float)
    fromCurrency = request.args.get('fromCurrency', type=str)
    toCurrency = request.args.get('toCurrency', type=str)
    
    # if missing parameters in request, return error message
    if not amount or not fromCurrency or not toCurrency:
        return 'Error: Missing parameters', 400
    
    # call conversion method
    result = convertCurrency(amount, fromCurrency, toCurrency)
    
    # return result as a string
    return str(result)


@app.route('/totals', methods=['POST'])
def totals():
    """ 
    Endpoint to generate financial summary (total expenses and income).
    Example request: curl -X POST http://127.0.0.1:5000/totals -H "Content-Type: application/json" -d '[{"category": "income", "amount": 100}, {"category": "expenses", "amount": 50}, {"category": "income", "amount": 200}]'
    Notes: JSON data needs to be categorized as 'income' or 'expense' and contain an 'amount' value.
    """
    
    # get JSON data from request
    data = request.get_json()
        
    # initialize totals
    income = 0
    expense = 0
        
    # iterate through JSON data to calculate totals
    for item in data:
        category = item.get('category')
        amount = item.get('amount')
            
        if category.lower() == 'income':
            income += amount
        elif category.lower() == 'expense':
            expense += amount
    
    # return totals as JSON            
    return jsonify({'income': income, 'expenses': expense})


@app.route('/rank', methods=['POST'])
def rank():
    """ 
    Endpoint to calculate ranked list of expenses and income by category.
    Example request: curl -X POST http://127.0.0.1:5000/rank -H "Content-Type: application/json" -d '[{"category": "food", "amount": 50}, {"category": "entertainment", "amount": 100}, {"category": "food", "amount": 25}]'
    Notes: JSON data needs to contain a 'category' and an 'amount' value.
    """
    
    # get JSON data from request
    data = request.get_json()
    
    # initialize dictionary to store ranked data
    rankedData = defaultdict(float)
    
    # iterate through JSON data to rank values
    for item in data:
        category = item.get('category')
        amount = item.get('amount')
        rankedData[category] += amount
    
    # sort ranked data in descending order based on total ampount     
    rankedFinal = sorted(rankedData.items(), key=lambda x: x[1], reverse=True)

    # return ranked data as JSON
    return jsonify(rankedFinal)


def convertCurrency(amount, fromCurrency, toCurrency):
    """ 
    Method to get currency conversion rate from API and perform conversion. Returns none if unsupported currency type.
    Parameters: amount: value of currency to convert from. This should be a number and contain a decimal place.
                fromCurrency: the currency you want to convert. This should be a 3 letter ISO 4217 currency code. 
                toCurrency: the currency you want to convert the amount to. This should be a 3 letter currrency code.
    Returns: result: the converted amount in the desired currency. This will be a float.
    """
    # add your own API key here (see https://app.freecurrencyapi.com/)
    client = freecurrencyapi.Client('fca_live_t0nABF1liMfGuUsbE6KboSFOB9QyQGqWJ8yp8Sv1')
    
    # call API to get conversion rate
    convertFactor = client.latest(fromCurrency, [toCurrency])
    
    # extract conversion rate from API JSON response
    convertRate = convertFactor['data'].get(toCurrency)
       
    # if not converted currency type, return None
    if convertRate is None:
        return "Error: Unsupported currency type", 400
    
    # currency conversion (rate * amount)
    result = convertRate * amount
    return result


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)