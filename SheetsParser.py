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

        winnerCell = sheet.find(winnerName)
        loserCell = sheet.find(loserName)

        #Update Winner
        if winnerCell:
            print('--------------')
            print('Winner exists!')
            print('Row: ' + f'{winnerCell.row}')
            print('Column: ' + f'{winnerCell.col}')
            print('Value: ' + f'{winnerCell.value}')
            print('Player Wins: ' + f'{sheet.cell(winnerCell.row, winnerCell.col + 1).value}')
            print('Total Games: ' + f'{sheet.cell(winnerCell.row, winnerCell.col + 4).value}')

            playerWins = sheet.cell(winnerCell.row, winnerCell.col + 1).value
            totalGames = sheet.cell(winnerCell.row, winnerCell.col + 4).value
            sheet.update_cell(winnerCell.row, winnerCell.col + 1, int(playerWins) + 1)
            sheet.update_cell(winnerCell.row, winnerCell.col + 4, int(totalGames) + 1)

        #Update Loser
        if loserCell:
            print('-------------')
            print('Loser exists!')
            print('Row: ' + f'{loserCell.row}')
            print('Column: ' + f'{loserCell.col}')
            print('Value: ' + f'{loserCell.value}')
            print('Player Losses: ' + f'{sheet.cell(loserCell.row, loserCell.col + 2).value}')
            print('Total Games: ' + f'{sheet.cell(loserCell.row, loserCell.col + 4).value}')

            playerLosses = sheet.cell(loserCell.row, loserCell.col + 2).value
            totalGames = sheet.cell(loserCell.row, loserCell.col + 4).value
            sheet.update_cell(loserCell.row, loserCell.col + 2, int(playerLosses) + 1)
            sheet.update_cell(loserCell.row, loserCell.col + 4, int(totalGames) + 1)
