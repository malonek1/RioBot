import datetime
import gspread
import glicko2

#Creation of gspread objects
client = gspread.service_account()
stars_off_calc_sheet = client.open('MSSB Elo').worksheet('Calculations-OFF')
stars_off_log_sheet = client.open('MSSB Elo').worksheet('Logs-OFF')

stars_on_calc_sheet = client.open('MSSB Elo').worksheet('Calculations-ON')
stars_on_log_sheet = client.open('MSSB Elo').worksheet('Logs-ON')

class EloSheetsParser:
    def __init__(self, name):
        self.name = name

    def next_available_row(self, worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list)+1)

    def confirmMatch(self, winner_name, loser_name, winner_id, loser_id, winner_score, loser_score, game_mode):
        print('\n' + str(datetime.datetime.now))
        print('function: confirmMatch entered')

        if game_mode == 'OFF':
            calc_sheet = stars_off_calc_sheet
            log_sheet = stars_off_log_sheet
        elif game_mode == 'ON':
            calc_sheet = stars_on_calc_sheet
            log_sheet = stars_on_log_sheet

        #Calculate Glicko
        if calc_sheet.find(winner_id):
            winner = glicko2.Player(float(calc_sheet.cell(calc_sheet.find(winner_id).row, 7).value), float(calc_sheet.cell(calc_sheet.find(winner_id).row, 9).value))
            print('Existing winner instantiated')
        else:
            winner = glicko2.Player(1500, 300)
            print('New winner instantiated')

        if calc_sheet.find(loser_id):
            loser = glicko2.Player(float(calc_sheet.cell(calc_sheet.find(loser_id).row, 7).value), float(calc_sheet.cell(calc_sheet.find(loser_id).row, 9).value))
            print('Existing loser instantiated')
        else: 
            loser = glicko2.Player(1500, 300)
            print('New loser instantiated')
            
        #loserElo = glicko2.Player()

        print("Old Rating Deviation: " + str(winner.rd))
        print("Old Volatility: " + str(winner.vol))

        #Initial values for winner and loser
        winner_rating = winner.rating
        winner_rd = winner.rd
        loser_rating = loser.rating
        loser_rd = loser.rd

        #Update Rating and Rd through glicko2 library
        winner.update_player([loser_rating], [loser_rd], [1])
        loser.update_player([winner_rating], [winner_rd], [0])

        print("New Rating: " + str(winner.rating))
        print("New Rating Deviation: " + str(winner.rd))
        print("New Volatility: " + str(winner.vol))
        print("---------------------------------------------\n")

        nextRow = self.next_available_row(log_sheet)

        #A list of all cells on the next row of the log_sheet
        cell_list = [log_sheet.acell("A{}".format(nextRow)), log_sheet.acell("B{}".format(nextRow)), log_sheet.acell("C{}".format(nextRow)), log_sheet.acell("D{}".format(nextRow)), log_sheet.acell("E{}".format(nextRow)), log_sheet.acell("F{}".format(nextRow)), log_sheet.acell("G{}".format(nextRow)), log_sheet.acell("H{}".format(nextRow)), log_sheet.acell("I{}".format(nextRow)), log_sheet.acell("J{}".format(nextRow)), log_sheet.acell("K{}".format(nextRow)), log_sheet.acell("L{}".format(nextRow))]
        
        #A list of all values to be added to the cells stored in cell_list
        value_list = [winner_id, winner_name, winner_score, winner.rating, winner.rd, loser_id, loser_name, loser_score, loser.rating, loser.rd, '{:%b/%d/%Y at %H:%M:%S}'.format(datetime.datetime.now()), int(f'{int(nextRow) - 1}')]

        for i, val in enumerate(value_list):
            cell_list[i].value = val

        #Add all gathered data to the next row of the log_sheet
        log_sheet.update_cells(cell_list)