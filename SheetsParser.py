#Google eloSheets imports:
import gspread

#Creation of gspread object
client = gspread.service_account()
eloSheet = client.open('MSSB Elo').worksheet('Elo')
logSheet = client.open('MSSB Elo').worksheet('Logs')

class EloSheetsParser:
    def __init__(self, name):
        self.name = name

    def next_available_row(self, worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list)+1)

    def confirmMatch(self, winnerName, loserName, winnerScore, loserScore):
        print('function: confirmMatch entered')
        nextRow = self.next_available_row(logSheet)
        print('next row index: ' + f'{int(nextRow) - 1}')

        logSheet.update_acell("A{}".format(nextRow), f'{int(nextRow) - 1}')
        logSheet.update_acell("C{}".format(nextRow), winnerName)
        logSheet.update_acell("D{}".format(nextRow), winnerScore)
        logSheet.update_acell("F{}".format(nextRow), loserName)
        logSheet.update_acell("G{}".format(nextRow), loserScore)

    def playerStats(self, winnerName, loserName):
        winnerCell = eloSheet.find(winnerName)
        loserCell = eloSheet.find(loserName)       
        #Update Winner
        if winnerCell:
            print('--------------')
            print('Winner exists!')
            print('Row: ' + f'{winnerCell.row}')
            print('Column: ' + f'{winnerCell.col}')
            print('Value: ' + f'{winnerCell.value}')
            print('Player Wins: ' + f'{eloSheet.cell(winnerCell.row, winnerCell.col + 1).value}')

            playerWins = eloSheet.cell(winnerCell.row, winnerCell.col + 1).value
            eloSheet.update_cell(winnerCell.row, winnerCell.col + 1, int(playerWins) + 1)

        #Update Loser
        if loserCell:
            print('-------------')
            print('Loser exists!')
            print('Row: ' + f'{loserCell.row}')
            print('Column: ' + f'{loserCell.col}')
            print('Value: ' + f'{loserCell.value}')
            print('Player Losses: ' + f'{eloSheet.cell(loserCell.row, loserCell.col + 2).value}')

            playerLosses = eloSheet.cell(loserCell.row, loserCell.col + 2).value
            eloSheet.update_cell(loserCell.row, loserCell.col + 2, int(playerLosses) + 1)