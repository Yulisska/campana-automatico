import urequests
import json

def read_sheet(sheet_id, sheet_name, range_name, callback, online):
    # Replace with your own values
    SPREADSHEET_ID = sheet_id
    SHEET_NAME = sheet_name
    RANGE_NAME = f'{SHEET_NAME}!{range_name}'
    GOOGLE_API_KEY= "AIzaSyBo96F7mKwXFEMpeI1QNI9TeoNu-vp4XdU"

    # Use the Google Sheets API to get the data
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}?key={GOOGLE_API_KEY}'
    if online:
        response = urequests.get(url)
        json_string = response.text
    else:
        json_string = r'{"values": []}'

    # Parse the JSON response
    data = json.loads(json_string)

    # Print the values in the spreadsheet
    values = data['values']
    print("Google: ", online, ", ", values)
    if callback:
        return callback(values)
    return None