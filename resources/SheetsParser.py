import datetime
import resources.gspread_client as gs
import glicko2

ELO_SHEET_NAME = "Elo Test"

# Creation of gspread objects
stars_off_calc_sheet = gs.client.open(ELO_SHEET_NAME).worksheet('Calculations-OFF')
stars_off_log_sheet = gs.client.open(ELO_SHEET_NAME).worksheet('Logs-OFF')

stars_on_calc_sheet = gs.client.open(ELO_SHEET_NAME).worksheet('Calculations-ON')
stars_on_log_sheet = gs.client.open(ELO_SHEET_NAME).worksheet('Logs-ON')


def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)


def confirm_match(winner_name, loser_name, winner_id, loser_id, winner_score, loser_score, game_mode):
    print('\n' + str(datetime.datetime.now()))
    print('function: confirmMatch entered')

    calc_sheet = stars_off_calc_sheet
    log_sheet = stars_off_log_sheet
    if game_mode == 'ON':
        calc_sheet = stars_on_calc_sheet
        log_sheet = stars_on_log_sheet

    # Calculate Glicko
    if calc_sheet.find(winner_id):
        winner = glicko2.Player(float(calc_sheet.cell(calc_sheet.find(winner_id).row, 7).value),
                                float(calc_sheet.cell(calc_sheet.find(winner_id).row, 9).value))
        print('Existing winner instantiated')
    else:
        winner = glicko2.Player(1500, 300)
        print('New winner instantiated')

    if calc_sheet.find(loser_id):
        loser = glicko2.Player(float(calc_sheet.cell(calc_sheet.find(loser_id).row, 7).value),
                               float(calc_sheet.cell(calc_sheet.find(loser_id).row, 9).value))
        print('Existing loser instantiated')
    else:
        loser = glicko2.Player(1500, 300)
        print('New loser instantiated')

    # loserElo = glicko2.Player()

    print("Old Rating Deviation: " + str(winner.rd))
    print("Old Volatility: " + str(winner.vol))

    # Initial values for winner and loser
    winner_rating = winner.rating
    winner_rd = winner.rd
    loser_rating = loser.rating
    loser_rd = loser.rd

    # Update Rating and Rd through glicko2 library
    winner.update_player([loser_rating], [loser_rd], [1])
    loser.update_player([winner_rating], [winner_rd], [0])

    print("New Rating: " + str(winner.rating))
    print("New Rating Deviation: " + str(winner.rd))
    print("New Volatility: " + str(winner.vol))
    print("---------------------------------------------\n")

    next_row = next_available_row(log_sheet)

    # A list of all values to be added to the log
    value_list = [winner_id, winner_name, winner_score, winner.rating, winner.rd, loser_id, loser_name, loser_score,
                  loser.rating, loser.rd, '{:%b/%d/%Y at %H:%M:%S}'.format(datetime.datetime.now()),
                  int(f'{int(next_row) - 1}')]

    # Add all gathered data to the next row of the log_sheet
    log_sheet.append_row(value_list)
