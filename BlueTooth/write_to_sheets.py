import gspread
#from oauth2client.service_account import ServiceAccountCredentials

# define the scope
#scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
#creds = ServiceAccountCredentials.from_json_keyfile_name('api_key.json', scope)

client = gspread.service_account()

sheet = client.open('Remote Temperature')

sheet_instance = sheet.get_worksheet(0)

sheet_instance.append_row(['2020-09-05','13:54:20',16.3,55,18,30])
#sheet_instance.insert_row(['2020-09-05','13:54:20',16.3,55,18,30], 998)
print('nrows = ',sheet_instance.row_count)
#sheet_instance.delete_row(2)
print('nrows = ',sheet_instance.row_count)
