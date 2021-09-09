import datetime
import gspread
import glicko2

#Creation of gspread objects
client = gspread.service_account()
calcSheet = client.open('MSSB Elo').worksheet('Calculations')
logSheet = client.open('MSSB Elo').worksheet('Logs')

#Creation of pygsheet objects
#pyg = pygsheets.authorize(service_file='mssb-elo-ac8af23a81f5.json')
#pygLogSheet = pyg.open('MSSB').worksheet('Logs')

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
            winner = glicko2.Player(float(calcSheet.cell(calcSheet.find(winnerName).row, 6).value), float(calcSheet.cell(calcSheet.find(winnerName).row, 8).value))
            print('Existing winner instantiated')
        else:
            winner = glicko2.Player(1500, 300)
            print('New winner instantiated')

        if calcSheet.find(loserName):
            loser = glicko2.Player(float(calcSheet.cell(calcSheet.find(loserName).row, 6).value), float(calcSheet.cell(calcSheet.find(loserName).row, 8).value))
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

        nextRow = self.next_available_row(logSheet)

        #A list of all cells on the next row of the logSheet
        cell_list = [logSheet.acell("A{}".format(nextRow)), logSheet.acell("B{}".format(nextRow)), logSheet.acell("C{}".format(nextRow)), logSheet.acell("D{}".format(nextRow)), logSheet.acell("E{}".format(nextRow)), logSheet.acell("F{}".format(nextRow)), logSheet.acell("G{}".format(nextRow)), logSheet.acell("H{}".format(nextRow)), logSheet.acell("I{}".format(nextRow)), logSheet.acell("J{}".format(nextRow))]
        
        #A list of all values to be added to the cells stored in cell_list
        value_list = [winnerName, winnerScore, winner.rating, winner.rd, loserName, loserScore, loser.rating, loser.rd, '{:%b/%d/%Y at %H:%M:%S}'.format(datetime.datetime.now()), f'{int(nextRow) - 1}']

        for i, val in enumerate(value_list):
            cell_list[i].value = val

        #Add all gathered data to the next row of the logSheet
        logSheet.update_cells(cell_list)

    def playerStats(self, winnerName, loserName):
        winnerCell = calcSheet.find(winnerName)
        loserCell = calcSheet.find(loserName)       
        #Update Winner
        if winnerCell:
            print('--------------')
            print('Winner exists!')
            print('Row: ' + f'{winnerCell.row}')
            print('Column: ' + f'{winnerCell.col}')
            print('Value: ' + f'{winnerCell.value}')
            print('Player Wins: ' + f'{calcSheet.cell(winnerCell.row, winnerCell.col + 1).value}')

            playerWins = calcSheet.cell(winnerCell.row, winnerCell.col + 1).value
            calcSheet.update_cell(winnerCell.row, winnerCell.col + 1, int(playerWins) + 1)

        #Update Loser
        if loserCell:
            print('-------------')
            print('Loser exists!')
            print('Row: ' + f'{loserCell.row}')
            print('Column: ' + f'{loserCell.col}')
            print('Value: ' + f'{loserCell.value}')
            print('Player Losses: ' + f'{calcSheet.cell(loserCell.row, loserCell.col + 2).value}')

            playerLosses = calcSheet.cell(loserCell.row, loserCell.col + 2).value
            calcSheet.update_cell(loserCell.row, loserCell.col + 2, int(playerLosses) + 1)