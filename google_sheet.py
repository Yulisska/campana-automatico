import urequests
import json

def read_sheet(sheet_id, sheet_name, range_name, callback):
    # Replace with your own values
    SPREADSHEET_ID = sheet_id
    SHEET_NAME = sheet_name
    RANGE_NAME = f'{SHEET_NAME}!{range_name}'
    GOOGLE_API_KEY= "AIzaSyBo96F7mKwXFEMpeI1QNI9TeoNu-vp4XdU"

    # Use the Google Sheets API to get the data
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}?key={GOOGLE_API_KEY}'
    response = urequests.get(url)

    # Parse the JSON response
    data = json.loads(response.text)

    # Print the values in the spreadsheet
    values = data['values']
    if callback:
        callback(values)