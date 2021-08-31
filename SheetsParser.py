#Google Sheets imports:
import gspread

#Creation of gspread object
client = gspread.service_account()
sheet = client.open('MSSB Elo').sheet1

class SheetsParser:
    def __init__(self, name):
        self.name = name

    def confirmMatch(self, winnerName, loserName, winnerScore, loserScore):
        print('function: confirmMatch entered')
        #Update Winner
        sheet.update_cell(2, 4, winnerName)
        sheet.update_cell(2, 5, '1')

        #Update Loser
        sheet.update_cell(3, 4, loserName)
        sheet.update_cell(3, 6, '1')
