import gspread
from discord.ext import tasks
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
client = gspread.authorize(creds)

# Access spreadsheet and store data
stars_off_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("STARS-OFF")
stars_on_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("STARS-ON")
off_log_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("Logs-OFF")
on_log_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("Logs-ON")
# Create a list of all player ratings (to be used for defining percentile search ranges)
off_rating_list = sorted(list(map(int, stars_off_sheet.col_values(5)[1:])), reverse=True)
on_rating_list = sorted(list(map(int, stars_on_sheet.col_values(5)[1:])), reverse=True)


# update spreadsheet API data once per minute
@tasks.loop(minutes=1)
async def refresh_api_data():
    global stars_off_sheet, stars_on_sheet, off_log_sheet, on_log_sheet, off_rating_list, on_rating_list
    stars_off_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("STARS-OFF")
    stars_on_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("STARS-ON")
    off_log_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("Logs-OFF")
    on_log_sheet = client.open_by_key("1B03IEnfOo3pAG7wBIjDW6jIHP0CTzn7jQJuxlNJebgc").worksheet("Logs-ON")
    off_rating_list = sorted(list(map(int, stars_off_sheet.col_values(5)[1:])), reverse=True)
    on_rating_list = sorted(list(map(int, stars_on_sheet.col_values(5)[1:])), reverse=True)
