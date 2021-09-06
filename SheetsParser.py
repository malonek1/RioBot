#Google Sheets imports:
import gspread
import glicko2

#Creation of gspread object
client = gspread.service_account()
eloSheet = client.open('MSSB Elo').worksheet('Elo')
logSheet = client.open('MSSB Elo').worksheet('Logs')
calcSheet = client.open('MSSB Elo').worksheet('Calculations')

class EloSheetsParser:
    def __init__(self, name):
        self.name = name

    def next_available_row(self, worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list)+1)

    def confirmMatch(self, winnerName, loserName, winnerScore, loserScore):
        print('function: confirmMatch entered')
        #Calculate Glicko
        if calcSheet.find(winnerName):
            print(calcSheet.find(winnerName).row)
            print(calcSheet.cell(calcSheet.find(winnerName).row, 6).value)
            winner = glicko2.Player(float(calcSheet.cell(calcSheet.find(winnerName).row, 6).value), float(calcSheet.cell(calcSheet.find(winnerName).row, 7).value))
            print('Existing winner instantiated')
        else:
            winner = glicko2.Player(1500, 300)
            print('New winner instantiated')

        if calcSheet.find(loserName):
            loser = glicko2.Player(float(calcSheet.cell(calcSheet.find(loserName).row, 6).value), float(calcSheet.cell(calcSheet.find(loserName).row, 7).value))
            print('Existing loser instantiated')
        else: 
            loser = glicko2.Player(1500, 300)
            print('New loser instantiated')
        #loserElo = glicko2.Player()

        print("Old Rating Deviation: " + str(winner.rd))
        print("Old Volatility: " + str(winner.vol))

        #Initial values for winner and loser
        winnerRating = winner.rating
        winnerRd = winner.rd
        loserRating = loser.rating
        loserRd = loser.rd

        #Update Rating and Rd through glicko2 library
        winner.update_player([loserRating], [loserRd], [1])
        loser.update_player([winnerRating], [winnerRd], [0])

        print("New Rating: " + str(winner.rating))
        print("New Rating Deviation: " + str(winner.rd))
        print("New Volatility: " + str(winner.vol))

        #Enter data into sheets
        nextRow = self.next_available_row(logSheet)

        #Update winner info
        logSheet.update_acell("A{}".format(nextRow), winnerName)
        logSheet.update_acell("B{}".format(nextRow), winnerScore)
        logSheet.update_acell("C{}".format(nextRow), winner.rating)
        logSheet.update_acell("D{}".format(nextRow), winner.rd)

        #Update loser info
        logSheet.update_acell("E{}".format(nextRow), loserName)
        logSheet.update_acell("F{}".format(nextRow), loserScore)
        logSheet.update_acell("G{}".format(nextRow), loser.rating)
        logSheet.update_acell("H{}".format(nextRow), loser.rd)

        #Update index
        print('next row index: ' + f'{int(nextRow) - 1}')
        logSheet.update_acell("J{}".format(nextRow), f'{int(nextRow) - 1}')

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