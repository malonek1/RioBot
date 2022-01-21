# returns row index of character in csv
def findCharacter(characterArg):
    for i in range(0, len(characterNameList)):
        for character in characterNameList[i]:
            if character == characterArg:
                return i + 1 # add 1 for csv format stuff
    return -1 # invalid number, if returned, character not found


# returns row index of stat in csv
def findStat(statArg):
    for i in range(0, len(statsNameList)):
        for stat in statsNameList[i]:
            if stat == statArg:
                return i + 1 # add 1 for csv format stuff
    return -1 # invalid number, if returned, stat not found


def testMatchingChemCharacter(iRow):
    outList = []
    for character in characterNameList[iRow]:
        outList.append(character + 'chem')
        outList.append(character + '-chem')
        outList.append(character + '_chem')
        outList.append(character + 'chemistry')
        outList.append(character + '-chemistry')
        outList.append(character + '_chemistry')
    return outList


# used for sorting list of dicts in highest and lowest commands
def sortStats(d):
  return d["value"]


# List of possible spellings of each character
characterNameList = [
    ['m', 'mario'], # 0
    ['l', 'luigi'], # 1
    ['dk', 'donkeykong', 'donkey-kong', 'donkey_kong'], # 2
    ['dy', 'diddy'], # 3
    ['p', 'peach'], # 4
    ['d', 'daisy'], # 5
    ['y', 'yoshi'], # 6
    ['bym', 'babymario','baby-mario', 'baby_mario'], # 7
    ['byl', 'babyluigi', 'baby-luigi', 'baby_luigi'], # 8
    ['bw', 'bowser'], # 9
    ['w', 'wario'], # 10
    ['wl', 'waluigi'], # 11
    ['rk', 'rkt', 'koopa(r)', 'r!koopa', 'redkoopa', 'red-koopa', 'red_koopa'], # 12
    ['rt', 'toad(r)', 'r!toad', 'redtoad', 'red-toad', 'red_toad'], # 13
    ['b', 'boo'], # 14
    ['te', 'toadette'], # 15
    ['rsg', 'shyguy(r)', 'shy-guy(r)', 'shy_guy(r)', 'r!shyguy', 'r!shy-guy', 'r!shy_guy', 'redshyguy', 'red-shy-guy', 'red_shy_guy'], # 16
    ['bi', 'bo', 'bd', 'birdo'], # 17
    ['my', 'mn', 'monty'], # 18
    ['bj', 'bowserjr', 'bowser-jr', 'bowser_jr'], # 19
    ['rpt', 'paratroopa(r)', 'para(r)', 'r!paratroopa', 'r!para', 'redpara', 'red-para', 'red_para', 'redparatroopa', 'red-paratroopa', 'red_paratroopa'], # 20
    ['bp', 'pianta(b)', 'b!pianta', 'bluepianta', 'blue-pianta', 'blue_pianta'], # 21
    ['pm', 'rp', 'pianta(r)', 'r!pianta', 'redpianta', 'red-pianta', 'red_pianta'], # 22
    ['yp', 'pianta(y)', 'y!pianta', 'yellowpianta', 'yellow-pianta', 'yellow_pianta'], # 23
    ['bn', 'noki(b)', 'b!noki', 'bluenoki', 'blue-noki', 'blue_noki'], # 24
    ['rn', 'noki(r)', 'r!noki', 'rednoki', 'red-noki', 'red_noki'], # 25
    ['gn', 'noki(g)', 'g!noki', 'greennoki', 'green-noki', 'green_noki'], # 26
    ['bro', 'hb', 'bro(h)', 'h!bro', 'hammerbro', 'hammer-bro', 'hammer_bro'], # 27
    ['tw', 'toadsworth'], # 28
    ['bt', 'toad(b)', 'b!toad', 'bluetoad', 'blue-toad', 'blue_toad'], # 29
    ['yt', 'toad(y)', 'y!toad', 'yellowtoad', 'yellow-toad', 'yellow_toad'], # 30
    ['gt', 'toad(g)', 'g!toad', 'greentoad', 'green-toad', 'green_toad'], # 31
    ['pt', 'toad(p)', 'p!toad', 'purpletoad', 'purple-toad', 'purple_toad'], # 32
    ['bm', 'mag(b)', 'magikoopa(b)', 'b!magikoopa', 'b!mag', 'bluemagikoopa', 'bluemag', 'blue-magikoopa', 'blue-mag', 'blue_magikoopa', 'blue_mag'], # 33
    ['rm', 'mag(r)', 'magikoopa(r)', 'r!magikoopa', 'r!mag', 'redmagikoopa', 'redmag', 'red-magikoopa', 'red-mag', 'red_magikoopa', 'red_mag'], # 34
    ['gm', 'mag(g)', 'magikoopa(g)', 'g!magikoopa', 'g!mag', 'greenmagikoopa', 'greenmag', 'green-magikoopa', 'green-mag', 'green_magikoopa', 'green_mag'], # 35
    ['ym', 'mag(y)', 'magikoopa(y)', 'y!magikoopa', 'y!mag', 'yellowmagikoopa', 'yellowmag', 'yellow-magikoopa', 'yellow-mag', 'yellow_magikoopa', 'yellow_mag'], # 36
    ['kb', 'kingboo', 'king-boo', 'king_boo'], # 37
    ['py', 'petey'], # 38
    ['dx', 'dix', 'dixie'], # 39
    ['g', 'goomba'], # 40
    ['pg', 'paragoomba'], # 41
    ['gk', 'koopa(g)', 'g!koopa', 'greenkoopa', 'green-koopa', 'green_koopa'], # 42
    ['gpt', 'paratroopa(g)', 'para(g)', 'g!paratroopa', 'g!para', 'greenpara', 'green-para', 'green_para', 'greenparatroopa', 'green-paratroopa', 'green_paratroopa'], # 43
    ['bsg', 'shyguy(b)', 'shy-guy(b)', 'shy_guy(b)', 'b!shyguy', 'b!shy-guy', 'b!shy_guy', 'blueshyguy', 'blue-shy-guy', 'blue_shy_guy'], # 44
    ['ysg', 'shyguy(y)', 'shy-guy(y)', 'shy_guy(y)', 'y!shyguy', 'y!shy-guy', 'y!shy_guy', 'yellowshyguy', 'yellow-shy-guy', 'yellow_shy_guy'], # 45
    ['gsg', 'shyguy(g)', 'shy-guy(g)', 'shy_guy(g)', 'g!shyguy', 'g!shy-guy', 'g!shy_guy', 'greenshyguy', 'green-shy-guy', 'green_shy_guy'], # 46
    ['bksg', 'shyguy(bk)', 'shy-guy(bk)', 'shy_guy(bk)', 'bk!shyguy', 'bk!shy-guy', 'bk!shy_guy', 'blackshyguy', 'black-shy-guy', 'black_shy_guy'], # 47
    ['gydb', 'drybones(gy)', 'dry-bones(gy)', 'dry_bones(gy)', 'bones(gy)', 'bones'], # 48
    ['gdb', 'drybones(g)', 'dry-bones(g)', 'dry_bones(g)', 'bones(g)', 'g!bones', 'greenbones', 'green-bones', 'green_bones', 'g!drybones', 'g!dry-bones', 'g!dry_bones', 'greendrybones', 'green-dry-bones', 'green_dry_bones'], # 49
    ['rdb', 'drybones(r)' 'dry-bones(r)', 'dry_bones(r)', 'bones(r)', 'r!bones', 'redbones', 'red-bones', 'red_bones', 'r!drybones', 'r!dry-bones', 'r!dry_bones', 'reddrybones', 'red-dry-bones', 'red_dry_bones'], # 50
    ['bdb', 'drybones(b)' 'dry-bones(b)', 'dry_bones(b)', 'bones(b)', 'b!bones', 'bluebones', 'blue-bones', 'blue_bones', 'b!drybones', 'b!dry-bones', 'b!dry_bones', 'bluedrybones', 'blue-dry-bones', 'blue_dry_bones'], # 51
    ['fb', 'firebro', 'fire-bro', 'fire_bro', 'bro(f)', 'f!bro'], # 52
    ['bb', 'boomer', 'boomerangbro', 'boomerang-bro', 'boomberang_bro', 'bro(b)', 'b!bro'] # 53
]

# List of possible spellings of each stat
statsNameList = [
    ['cb', 'cbs', 'curvespeed', 'curve-speed', 'curve_speed', 'curveball', 'curve-ball', 'curve_ball', 'curveballpower', 'curve-ball-power', 'curve_ball_power', 'curveballspeed', 'curve-ball-speed', 'curve_ball_speed'], # 0
    ['fb', 'fbs', 'fastball', 'fast-ball', 'fast_ball', 'fastballpower', 'fast-ball-power', 'fast_ball_power', 'fastballspeed', 'fast-ball-speed', 'fast_ball_speed'], # 1
    ['0x2'], # 2
    ['curve'], # 3
    ['0x4'], # 4
    ['ability', 'abilities'], # 5
    ['nice', 'nicecontactsize', 'nice-contact-size', 'nice_contact_size', 'nicecontact', 'nice-contact', 'nice_contact'], # 6
    ['perfect', 'perfectcontactsize', 'perfect-contact-size', 'perfect_contact_size', 'perfectcontact', 'perfect-contact', 'perfect_contact'], # 7
    ['slap', 'contact', 'slappower', 'slap-power', 'slap_power', 'slaphitpower', 'slap-hit-power', 'slap_hit_power'], # 8
    ['charge', 'power', 'chargepower', 'charge-power', 'charge_power', 'chargehitpower', 'charge-hit-power', 'charge_hit_power'], # 9
    ['bunt', 'buntpower', 'bunt-power', 'bunt_power', 'bunting'], # 10
    ['traj', 'trajectory'], # 11
    ['speed'], # 12
    ['throw', 'arm', 'throwing', 'throwingpower', 'throwing-power', 'throwing_power', 'throwingarm', 'throwing-arm', 'throwing_arm'], # 13
    ['class', 'type', 'characterclass', 'character-class', 'character_class', 'charactertype', 'character-type', 'character_type'], # 14
    ['weight'], # 15
    ['starswing', 'star-swing', 'star_swing'], # 16
    ['starpitch', 'star-pitch', 'star_pitch'], # 17
    ['cb', 'cssbat', 'css-bat', 'css_bat', 'cssbatting', 'css-batting', 'css_batting'], # 18
    ['cp', 'csspitch', 'css-pitch', 'css_pitch', 'csspitching', 'css-pitching', 'css_pitching'], # 19
    ['cf', 'cssfield', 'css-field', 'css_field', 'cssfielding', 'css-fielding', 'css_fielding'], # 20
    ['cs', 'cssspeed', 'css-speed', 'css_speed'], # 21
    testMatchingChemCharacter(0), # mario chem, 22 
    testMatchingChemCharacter(1), # luigi chem, 23
    testMatchingChemCharacter(2), # dk chem, 24
    testMatchingChemCharacter(3), # diddy chem, 25
    testMatchingChemCharacter(4), # peach chem, 26
    testMatchingChemCharacter(5), # daisy chem, 27
    testMatchingChemCharacter(6), # yoshi chem, 28
    testMatchingChemCharacter(7), # baby mario chem, 29
    testMatchingChemCharacter(8), # baby luigi chem, 30
    testMatchingChemCharacter(9), # bowser chem, 31
    testMatchingChemCharacter(10), # wario chem, 32
    testMatchingChemCharacter(11), # waluigi chem, 33
    testMatchingChemCharacter(12), # r!koopa chem, 34
    testMatchingChemCharacter(13), # r!toad chem, 35
    testMatchingChemCharacter(14), # boo chem, 36
    testMatchingChemCharacter(15), # toadette chem, 37
    testMatchingChemCharacter(16), # rsg chem, 38
    testMatchingChemCharacter(17), # birdo chem, 39
    testMatchingChemCharacter(18), # monty chem, 40
    testMatchingChemCharacter(19), # bj chem, 41
    testMatchingChemCharacter(20), # rpt chem, 42
    testMatchingChemCharacter(21), # bp chem, 43
    testMatchingChemCharacter(22), # pm chem, 44
    testMatchingChemCharacter(23), # yp chem, 45
    testMatchingChemCharacter(24), # b!noki chem, 46
    testMatchingChemCharacter(25), # r!noki chem, 47
    testMatchingChemCharacter(26), # g!noki, 48
    testMatchingChemCharacter(27), # h!bro chem, 49
    testMatchingChemCharacter(28), # tw chem, 50
    testMatchingChemCharacter(29), # b!toad chem, 51
    testMatchingChemCharacter(30), # y!toad, 52
    testMatchingChemCharacter(31), # g!toad chem, 53
    testMatchingChemCharacter(32), # p!toad chem, 54
    testMatchingChemCharacter(33), # b!mag chem, 55
    testMatchingChemCharacter(34), # r!mag chem, 56
    testMatchingChemCharacter(35), # g!mag chem, 57
    testMatchingChemCharacter(36), # y!mag chem, 58
    testMatchingChemCharacter(37), # kb chem, 59
    testMatchingChemCharacter(38), # petey chem, 60
    testMatchingChemCharacter(39), # dixie chem, 61
    testMatchingChemCharacter(40), # goomba chem, 62
    testMatchingChemCharacter(41), # paragoomba chem, 63
    testMatchingChemCharacter(42), # g!koopa chem, 64
    testMatchingChemCharacter(43), # g!para chem, 65
    testMatchingChemCharacter(44), # bsg chem, 66
    testMatchingChemCharacter(45), # ysg chem, 67
    testMatchingChemCharacter(46), # gsg chem, 68
    testMatchingChemCharacter(47), # bksg chem, 69
    testMatchingChemCharacter(48), # bones chem, 70
    testMatchingChemCharacter(49), # gdb chem, 71
    testMatchingChemCharacter(50), # rdb chem, 72
    testMatchingChemCharacter(51), # bdb chem, 73
    testMatchingChemCharacter(52), # f!bro chem, 74
    testMatchingChemCharacter(53) # b!bro chem, 75
]


# formatted from csv; need to manually convert int stuff when doing calculations with them
statsLoL = [
    ['Name', 'Curve Ball Speed', 'Fast Ball Speed', '0x2', 'Curve', '0x4', 'Ability', 'Nice Contact Size', 'Perfect Contact Size', 'Slap Hit Power', 'Charge Hit Power', 'Bunting', 'Trajectory', 'Speed', 'Throwing Arm', 'Character Class', 'Weight', 'Star Swing', 'Star Pitch', 'CSS Batting', 'CSS Pitching', 'CSS Fielding', 'CSS Speed', 'Mario Chem', 'Luigi Chem', 'DK Chem', 'Diddy Chem', 'Peach Chem', 'Daisy Chem', 'Yoshi Chem', 'Baby Mario Chem', 'Baby Luigi Chem', 'Bowser Chem', 'Wario Chem', 'Waluigi Chem', 'Red Koopa Chem', 'Red Toad Chem', 'Boo Chem', 'Toadette Chem', 'Red Shy Guy Chem', 'Birdo Chem', 'Monty Chem', 'Bowser Jr Chem', 'Red Paratroopa Chem', 'Blue Pianta Chem', 'Red Pianta Chem', 'Yellow Pianta Chem', 'Blue Noki Chem', 'Red Noki Chem', 'Green Noki Chem', 'Hammer Bro Chem', 'Toadsworth Chem', 'Blue Toad Chem', 'Yellow Toad Chem', 'Green Toad Chem', 'Purple Toad Chem', 'Blue Magikoopa Chem', 'Red Magikoopa Chem', 'Green Magikoopa Chem', 'Yellow Magikoopa Chem', 'King Boo Chem', 'Petey Chem', 'Dixie Chem', 'Goomba Chem', 'Paragoomba Chem', 'Green Koopa Chem', 'Green Paratroopa Chem', 'Blue Shy Guy Chem', 'Yellow Shy Guy Chem', 'Green Shy Guy Chem', 'Black Shy Guy Chem', 'Gray Dry Bones Chem', 'Green Dry Bones Chem', 'Red Dry Bones Chem', 'Blue Dry Bones Chem', 'Fire Bro Chem', 'Boomerang Bro Chem'],
    ['Mario', '130', '168', '60', '53', '50', 'Wall Jump & Sliding Catch', '65', '35', '50', '64', '35', 'Mid / Mid', '50', '60', 'Balance', '2', 'Fireball (Pop-Fly)', 'Fireball (Fastball)', '6', '6', '5', '6', '50', '99', '30', '59', '95', '88', '90', '87', '89', '15', '10', '20', '65', '82', '50', '81', '48', '63', '71', '25', '62', '86', '86', '86', '85', '85', '85', '38', '76', '82', '82', '82', '82', '40', '40', '40', '40', '49', '35', '55', '42', '43', '65', '62', '48', '48', '48', '48', '32', '32', '32', '32', '38', '38'],
    ['Luigi', '125', '165', '55', '56', '50', 'Wall Jump & Super Jump', '70', '40', '48', '59', '40', 'Mid / Mid', '60', '50', 'Balance', '2', 'Green Fireball (Grounder)', 'Green Fireball (Fastball)', '5', '6', '6', '6', '99', '50', '35', '55', '90', '95', '86', '89', '87', '25', '20', '10', '62', '81', '15', '82', '47', '60', '72', '30', '65', '83', '83', '83', '80', '80', '80', '39', '75', '81', '81', '81', '81', '51', '51', '51', '51', '11', '34', '57', '40', '41', '62', '65', '47', '47', '47', '47', '28', '28', '28', '28', '39', '39'],
    ['DK', '130', '165', '70', '35', '50', 'Clamber & Laser', '30', '15', '60', '80', '20', 'Pull / High', '40', '70', 'Power', '4', 'Banana Ball (Pop-Fly)', 'Banana Ball (Breaking Ball)', '8', '7', '4', '4', '30', '35', '50', '99', '22', '24', '77', '58', '57', '41', '59', '34', '67', '65', '68', '61', '50', '40', '83', '69', '72', '55', '55', '55', '45', '45', '45', '75', '63', '65', '65', '65', '65', '29', '29', '29', '29', '81', '91', '90', '80', '79', '67', '72', '50', '50', '50', '50', '43', '43', '43', '43', '75', '75'],
    ['Diddy', '115', '155', '45', '80', '50', 'Clamber & Super Catch', '45', '15', '45', '30', '20', 'Mid / Low', '70', '60', 'Speed', '1', 'Boomerang Ball (Grounder)', 'Boomerang Ball (Breaking Ball)', '3', '6', '7', '7', '59', '55', '99', '50', '64', '68', '72', '79', '78', '34', '33', '32', '75', '67', '60', '65', '66', '45', '77', '71', '70', '46', '46', '46', '56', '56', '56', '58', '62', '67', '67', '67', '67', '57', '57', '57', '57', '48', '52', '95', '91', '80', '75', '70', '66', '66', '66', '66', '44', '44', '44', '44', '58', '58'],
    ['Peach', '125', '165', '50', '70', '90', 'Quick Throw & Super Catch', '80', '45', '46', '45', '45', 'Push / Low', '50', '40', 'Technique', '2', 'Heart Ball (Grounder)', 'Heart Ball (Change-Up)', '4', '8', '5', '7', '95', '90', '22', '64', '50', '97', '83', '85', '80', '9', '14', '25', '60', '93', '31', '94', '58', '84', '45', '82', '57', '87', '87', '87', '88', '88', '88', '32', '96', '93', '93', '93', '93', '43', '43', '43', '43', '41', '5', '70', '44', '40', '60', '57', '58', '58', '58', '58', '35', '35', '35', '35', '32', '32'],
    ['Daisy', '120', '160', '55', '60', '55', 'Quick Throw & Sliding Catch', '70', '40', '49', '60', '55', 'Mid / Mid', '40', '40', 'Balance', '2', 'Flower Ball (Pop-Fly)', 'Flower Ball (Change-Up)', '6', '7', '4', '5', '88', '95', '24', '68', '97', '50', '80', '82', '85', '11', '25', '15', '57', '86', '34', '87', '55', '81', '43', '45', '60', '77', '77', '77', '83', '83', '83', '33', '79', '86', '86', '86', '86', '41', '41', '41', '41', '40', '6', '72', '46', '47', '57', '60', '55', '55', '55', '55', '30', '30', '30', '30', '33', '33'],
    ['Yoshi', '120', '155', '50', '51', '50', 'Tongue Catch & Clamber', '50', '30', '50', '45', '25', 'Mid / Mid', '90', '40', 'Speed', '2', 'Egg Ball (Grounder)', 'Egg Ball (Change-Up)', '5', '4', '9', '6', '90', '86', '77', '72', '83', '80', '50', '95', '94', '37', '50', '54', '78', '76', '53', '75', '45', '97', '73', '48', '74', '89', '89', '89', '82', '82', '82', '40', '71', '76', '76', '76', '76', '49', '49', '49', '49', '66', '42', '60', '67', '68', '78', '74', '45', '45', '45', '45', '46', '46', '46', '46', '40', '40'],
    ['Baby Mario', '115', '150', '50', '50', '50', 'Wall Jump', '50', '25', '44', '30', '25', 'Mid / Low', '70', '30', 'Speed', '0', 'Grounder', 'Breaking Ball', '3', '5', '7', '3', '87', '89', '58', '79', '85', '82', '95', '50', '99', '19', '12', '22', '66', '84', '14', '86', '10', '75', '60', '35', '61', '76', '76', '76', '77', '77', '77', '28', '88', '84', '84', '84', '84', '34', '34', '34', '34', '21', '24', '71', '45', '42', '66', '61', '10', '10', '10', '10', '33', '33', '33', '33', '28', '28'],
    ['Baby Luigi', '115', '150', '40', '50', '50', 'Wall Jump', '45', '25', '42', '20', '25', 'Mid / Low', '80', '30', 'Speed', '0', 'Grounder', 'Breaking Ball', '2', '5', '8', '3', '89', '87', '57', '78', '80', '85', '94', '99', '50', '18', '22', '12', '64', '83', '13', '84', '15', '70', '56', '41', '77', '79', '79', '79', '81', '81', '81', '27', '86', '83', '83', '83', '83', '33', '33', '33', '33', '10', '23', '73', '47', '44', '64', '77', '15', '15', '15', '15', '34', '34', '34', '34', '27', '27'],
    ['Bowser', '120', '175', '90', '35', '50', 'Laser, Body Check, & Wall Splat', '40', '15', '60', '95', '20', 'Pull / High', '10', '70', 'Power', '4', 'Killer Ball (Pop-Fly)', 'Killer Ball (Fastball)', '9', '9', '1', '1', '15', '25', '41', '34', '9', '11', '37', '19', '18', '50', '65', '60', '91', '10', '80', '5', '85', '71', '59', '99', '90', '30', '30', '30', '35', '35', '35', '95', '13', '10', '10', '10', '10', '88', '88', '88', '88', '75', '66', '33', '73', '72', '91', '90', '85', '85', '85', '85', '92', '92', '92', '92', '95', '95'],
    ['Wario', '125', '165', '80', '30', '50', 'Sliding Catch, Body Check, & Wall Splat', '50', '25', '55', '80', '25', 'Mid / Mid', '30', '60', 'Power', '3', 'Phony Ball (Pop-Fly)', 'Phony Ball (Fastball)', '8', '3', '3', '4', '10', '20', '59', '33', '14', '25', '50', '12', '22', '65', '50', '99', '58', '15', '90', '16', '80', '30', '70', '81', '55', '39', '39', '39', '48', '48', '48', '84', '24', '15', '15', '15', '15', '71', '71', '71', '71', '82', '63', '21', '62', '61', '58', '55', '80', '80', '80', '80', '42', '42', '42', '42', '84', '84'],
    ['Waluigi', '110', '169', '50', '70', '60', 'Laser & Super Jump', '90', '40', '50', '1', '45', 'Push / Low', '40', '40', 'Technique', '3', 'Liar Ball (Line Drive)', 'Liar Ball (Breaking Ball)', '4', '9', '4', '4', '20', '10', '34', '32', '25', '15', '54', '22', '12', '60', '99', '50', '55', '16', '88', '17', '78', '35', '67', '77', '58', '42', '42', '42', '47', '47', '47', '86', '23', '16', '16', '16', '16', '91', '91', '91', '91', '80', '51', '24', '61', '63', '55', '58', '78', '78', '78', '78', '48', '48', '48', '48', '86', '86'],
    ['Green Koopa', '120', '160', '50', '50', '50', 'Sliding Catch', '70', '30', '40', '50', '30', 'Mid / Mid', '40', '50', 'Balance', '1', 'Grounder', 'Breaking Ball', '5', '4', '4', '5', '65', '62', '67', '75', '60', '57', '78', '66', '64', '91', '58', '55', '50', '39', '84', '36', '70', '68', '80', '87', '99', '53', '53', '53', '71', '71', '71', '85', '31', '39', '39', '39', '39', '81', '81', '81', '81', '69', '44', '63', '88', '86', '50', '99', '70', '70', '70', '70', '90', '90', '90', '90', '85', '85'],
    ['Red Toad', '115', '155', '50', '50', '50', 'Body Check', '50', '30', '45', '70', '25', 'Mid / Mid', '60', '50', 'Balance', '0', 'Pop-Fly', 'Fastball', '5', '3', '6', '3', '82', '81', '65', '67', '93', '86', '76', '84', '83', '10', '15', '16', '39', '50', '25', '99', '53', '74', '52', '46', '38', '85', '85', '85', '78', '78', '78', '35', '92', '50', '50', '50', '50', '36', '36', '36', '36', '37', '31', '64', '66', '60', '39', '38', '53', '53', '53', '53', '29', '29', '29', '29', '35', '35'],
    ['Boo', '120', '160', '50', '90', '60', 'Super Jump & Curved Hits', '85', '45', '40', '30', '50', 'Mid / Mid', '40', '40', 'Technique', '1', 'Grounder', 'Breaking Ball', '3', '8', '4', '2', '50', '15', '68', '60', '31', '34', '53', '14', '13', '80', '90', '88', '84', '25', '50', '23', '86', '83', '55', '70', '89', '49', '49', '49', '65', '65', '65', '71', '27', '25', '25', '25', '25', '95', '95', '95', '95', '98', '64', '51', '82', '87', '84', '89', '86', '86', '86', '86', '85', '85', '85', '85', '71', '71'],
    ['Toadette', '115', '150', '50', '50', '50', 'Wall Jump & Sliding Catch', '50', '30', '44', '20', '25', 'Mid / Low', '90', '40', 'Speed', '0', 'Grounder', 'Breaking Ball', '2', '3', '9', '4', '81', '82', '61', '65', '94', '87', '75', '86', '84', '5', '16', '17', '36', '99', '23', '50', '51', '80', '49', '47', '35', '78', '78', '78', '74', '74', '74', '34', '91', '99', '99', '99', '99', '31', '31', '31', '31', '32', '30', '62', '64', '59', '36', '35', '51', '51', '51', '51', '27', '27', '27', '27', '34', '34'],
    ['Red Shy Guy', '120', '160', '50', '50', '50', 'Sliding Catch', '50', '30', '46', '55', '25', 'Mid / Mid', '40', '40', 'Balance', '1', 'Pop-Fly', 'Change-Up', '5', '3', '4', '5', '48', '47', '50', '66', '58', '55', '45', '10', '15', '85', '80', '78', '70', '53', '86', '51', '50', '90', '91', '83', '75', '60', '60', '60', '62', '62', '62', '72', '46', '53', '53', '53', '53', '84', '84', '84', '84', '65', '33', '67', '52', '54', '70', '75', '50', '50', '50', '50', '68', '68', '68', '68', '72', '72'],
    ['Birdo', '125', '165', '60', '40', '50', 'Suction, Body Check, & Wall Splat', '45', '30', '55', '67', '20', 'Mid / Mid', '40', '60', 'Balance', '3', 'Weird ball (Pop-Fly)', 'Weird Ball (Fastball)', '6', '4', '4', '4', '63', '60', '40', '45', '84', '81', '97', '75', '70', '71', '30', '35', '68', '74', '83', '80', '90', '50', '42', '38', '64', '51', '51', '51', '67', '67', '67', '73', '69', '74', '74', '74', '74', '37', '37', '37', '37', '79', '92', '89', '54', '55', '68', '64', '90', '90', '90', '90', '56', '56', '56', '56', '73', '73'],
    ['Monty', '120', '155', '50', '50', '50', 'Ball Dash & Wall Splat', '40', '30', '45', '30', '20', 'Mid / Low', '60', '30', 'Speed', '1', 'Grounder', 'Change-Up', '3', '3', '7', '5', '71', '72', '83', '77', '45', '43', '73', '60', '56', '59', '70', '67', '80', '52', '55', '49', '91', '42', '50', '76', '82', '68', '68', '68', '40', '40', '40', '25', '51', '52', '52', '52', '52', '39', '39', '39', '39', '47', '37', '74', '95', '90', '80', '82', '91', '91', '91', '91', '81', '81', '81', '81', '25', '25'],
    ['Bowser Jr', '125', '166', '50', '40', '50', 'Wall Jump & Body Check', '35', '20', '55', '75', '30', 'Mid / High', '40', '50', 'Power', '2', 'Killer Jr. Ball (Pop-Fly)', 'Killer Jr. Ball (Fastball)', '8', '5', '4', '3', '25', '30', '69', '71', '82', '45', '48', '35', '41', '99', '81', '77', '87', '46', '70', '47', '83', '38', '76', '50', '80', '20', '20', '20', '24', '24', '24', '91', '52', '46', '46', '46', '46', '90', '90', '90', '90', '58', '68', '66', '55', '51', '87', '80', '83', '83', '83', '83', '84', '84', '84', '84', '91', '91'],
    ['Red Paratroopa', '115', '155', '50', '60', '50', 'Super Jump', '55', '30', '48', '35', '20', 'Mid / Low', '60', '60', 'Technique', '1', 'Grounder', 'Breaking Ball', '3', '3', '6', '4', '62', '65', '72', '70', '57', '60', '74', '61', '77', '90', '55', '58', '99', '38', '89', '35', '75', '64', '82', '80', '50', '50', '50', '50', '68', '68', '68', '83', '30', '38', '38', '38', '38', '79', '79', '79', '79', '73', '43', '59', '85', '91', '99', '50', '75', '75', '75', '75', '88', '88', '88', '88', '83', '83'],
    ['Blue Pianta', '125', '160', '50', '30', '50', 'Laser & Wall Splat', '35', '15', '51', '65', '20', 'Pull / Low', '20', '80', 'Power', '3', 'Grounder', 'Change-Up', '6', '3', '2', '5', '86', '83', '55', '46', '87', '77', '89', '76', '79', '30', '39', '42', '53', '85', '49', '78', '60', '51', '68', '20', '50', '50', '50', '50', '98', '98', '98', '69', '72', '85', '85', '85', '85', '61', '61', '61', '61', '54', '15', '44', '38', '36', '53', '50', '60', '60', '60', '60', '58', '58', '58', '58', '69', '69'],
    ['Red Pianta', '125', '160', '50', '30', '50', 'Laser & Wall Splat', '35', '15', '51', '70', '20', 'Pull / Low', '10', '80', 'Power', '3', 'Pop-Fly', 'Fastball', '7', '3', '1', '5', '86', '83', '55', '46', '87', '77', '89', '76', '79', '30', '39', '42', '53', '85', '49', '78', '60', '51', '68', '20', '50', '50', '50', '50', '98', '98', '98', '69', '72', '85', '85', '85', '85', '61', '61', '61', '61', '54', '15', '44', '38', '36', '53', '50', '60', '60', '60', '60', '58', '58', '58', '58', '69', '69'],
    ['YellowPianta', '125', '165', '50', '40', '50', 'Laser & Wall Splat', '35', '15', '51', '65', '20', 'Pull / Low', '10', '80', 'Power', '3', 'Grounder', 'Breaking Ball', '6', '4', '1', '5', '86', '83', '55', '46', '87', '77', '89', '76', '79', '30', '39', '42', '53', '85', '49', '78', '60', '51', '68', '20', '50', '50', '50', '50', '98', '98', '98', '69', '72', '85', '85', '85', '85', '61', '61', '61', '61', '54', '15', '44', '38', '36', '53', '50', '60', '60', '60', '60', '58', '58', '58', '58', '69', '69'],
    ['Blue Noki', '115', '155', '50', '50', '50', 'Sliding Catch', '40', '15', '43', '30', '20', 'Mid / Low', '70', '60', 'Speed', '1', 'Grounder', 'Change-Up', '3', '3', '7', '4', '85', '80', '45', '56', '88', '83', '82', '77', '81', '35', '48', '47', '71', '78', '65', '74', '62', '67', '40', '24', '68', '98', '98', '98', '50', '50', '50', '42', '73', '78', '78', '78', '78', '54', '54', '54', '54', '38', '10', '75', '70', '69', '71', '68', '62', '62', '62', '62', '55', '55', '55', '55', '42', '42'],
    ['Red Noki', '115', '155', '50', '50', '50', 'Sliding Catch', '40', '15', '45', '40', '20', 'Mid / Low', '60', '60', 'Speed', '1', 'Pop-Fly', 'Fastball', '4', '3', '6', '4', '85', '80', '45', '56', '88', '83', '82', '77', '81', '35', '48', '47', '71', '78', '65', '74', '62', '67', '40', '24', '68', '98', '98', '98', '50', '50', '50', '42', '73', '78', '78', '78', '78', '54', '54', '54', '54', '38', '10', '75', '70', '69', '71', '68', '62', '62', '62', '62', '55', '55', '55', '55', '42', '42'],
    ['Green Noki', '115', '155', '50', '60', '50', 'Sliding Catch', '45', '13', '43', '30', '25', 'Mid / Low', '60', '60', 'Speed', '1', 'Line Drive', 'Breaking Ball', '3', '4', '6', '4', '85', '80', '45', '56', '88', '83', '82', '77', '81', '35', '48', '47', '71', '78', '65', '74', '62', '67', '40', '24', '68', '98', '98', '98', '50', '50', '50', '42', '73', '78', '78', '78', '78', '54', '54', '54', '54', '38', '10', '75', '70', '69', '71', '68', '62', '62', '62', '62', '55', '55', '55', '55', '42', '42'],
    ['Hammer Bro', '125', '165', '50', '40', '50', 'Body Check & Wall Splat', '30', '20', '10', '85', '15', 'Pull / High', '30', '60', 'Power', '3', 'Pop-Fly', 'Fastball', '8', '3', '3', '3', '38', '39', '75', '58', '32', '33', '40', '28', '27', '95', '84', '86', '85', '35', '71', '34', '72', '73', '25', '91', '83', '69', '69', '69', '42', '42', '42', '50', '36', '35', '35', '35', '35', '87', '87', '87', '87', '76', '81', '54', '78', '77', '85', '83', '72', '72', '72', '72', '82', '82', '82', '82', '50', '50'],
    ['Toadsworth', '120', '155', '50', '50', '50', 'Super Catch & Wall Splat', '85', '40', '45', '40', '45', 'Mid / Mid', '40', '30', 'Technique', '0', 'Line Drive', 'Change-Up', '4', '4', '4', '6', '76', '75', '63', '62', '96', '79', '71', '88', '86', '13', '24', '23', '31', '92', '27', '91', '46', '69', '51', '52', '30', '72', '72', '72', '73', '73', '73', '36', '50', '92', '92', '92', '92', '25', '25', '25', '25', '39', '28', '61', '60', '58', '31', '30', '46', '46', '46', '46', '38', '38', '38', '38', '36', '36'],
    ['Blue Toad', '115', '155', '50', '50', '50', 'Body Check', '50', '30', '40', '60', '25', 'Mid / Mid', '70', '50', 'Balance', '0', 'Grounder', 'Change-Up', '4', '3', '7', '3', '82', '81', '65', '67', '93', '86', '76', '84', '83', '10', '15', '16', '39', '50', '25', '99', '53', '74', '52', '46', '38', '85', '85', '85', '78', '78', '78', '35', '92', '50', '50', '50', '50', '36', '36', '36', '36', '37', '31', '64', '66', '60', '39', '38', '53', '53', '53', '53', '29', '29', '29', '29', '35', '35'],
    ['Yellow Toad', '120', '160', '50', '55', '50', 'Body Check', '50', '30', '40', '60', '25', 'Mid / Mid', '60', '50', 'Balance', '0', 'Grounder', 'Breaking Ball', '4', '4', '6', '3', '82', '81', '65', '67', '93', '86', '76', '84', '83', '10', '15', '16', '39', '50', '25', '99', '53', '74', '52', '46', '38', '85', '85', '85', '78', '78', '78', '35', '92', '50', '50', '50', '50', '36', '36', '36', '36', '37', '31', '64', '66', '60', '39', '38', '53', '53', '53', '53', '29', '29', '29', '29', '35', '35'],
    ['Green Toad', '115', '155', '50', '50', '50', 'Body Check', '55', '35', '45', '65', '35', 'Mid / Mid', '60', '50', 'Balance', '0', 'Grounder', 'Change-Up', '5', '3', '6', '3', '82', '81', '65', '67', '93', '86', '76', '84', '83', '10', '15', '16', '39', '50', '25', '99', '53', '74', '52', '46', '38', '85', '85', '85', '78', '78', '78', '35', '92', '50', '50', '50', '50', '36', '36', '36', '36', '37', '31', '64', '66', '60', '39', '38', '53', '53', '53', '53', '29', '29', '29', '29', '35', '35'],
    ['Purple Toad', '115', '155', '50', '50', '50', 'Body Check', '50', '30', '45', '70', '25', 'Mid / Mid', '50', '60', 'Balance', '0', 'Pop-Fly', 'Fastball', '5', '3', '5', '4', '82', '81', '65', '67', '93', '86', '76', '84', '83', '10', '15', '16', '39', '50', '25', '99', '53', '74', '52', '46', '38', '85', '85', '85', '78', '78', '78', '35', '92', '50', '50', '50', '50', '36', '36', '36', '36', '37', '31', '64', '66', '60', '39', '38', '53', '53', '53', '53', '29', '29', '29', '29', '35', '35'],
    ['Blue Magikoopa', '120', '150', '50', '50', '40', 'Magical Catch', '65', '35', '48', '40', '40', 'Push / Low', '20', '40', 'Technique', '2', 'Line Drive', 'Breaking Ball', '4', '2', '2', '8', '40', '51', '29', '57', '43', '41', '49', '34', '33', '88', '71', '91', '81', '36', '95', '31', '84', '37', '39', '90', '79', '61', '61', '61', '54', '54', '54', '87', '25', '36', '36', '36', '36', '50', '50', '50', '50', '44', '38', '35', '65', '67', '81', '79', '84', '84', '84', '84', '86', '86', '86', '86', '87', '87'],
    ['Red Magikoopa', '120', '155', '50', '50', '40', 'Magical Catch', '65', '35', '50', '45', '40', 'Push / Low', '10', '40', 'Technique', '2', 'Line Drive', 'Breaking Ball', '5', '2', '1', '8', '40', '51', '29', '57', '43', '41', '49', '34', '33', '88', '71', '91', '81', '36', '95', '31', '84', '37', '39', '90', '79', '61', '61', '61', '54', '54', '54', '87', '25', '36', '36', '36', '36', '50', '50', '50', '50', '44', '38', '35', '65', '67', '81', '79', '84', '84', '84', '84', '86', '86', '86', '86', '87', '87'],
    ['Green Magikoopa', '120', '150', '50', '60', '50', 'Magical Catch', '65', '35', '48', '40', '40', 'Push / Low', '10', '40', 'Technique', '2', 'Line Drive', 'Breaking Ball', '4', '3', '1', '8', '40', '51', '29', '57', '43', '41', '49', '34', '33', '88', '71', '91', '81', '36', '95', '31', '84', '37', '39', '90', '79', '61', '61', '61', '54', '54', '54', '87', '25', '36', '36', '36', '36', '50', '50', '50', '50', '44', '38', '35', '65', '67', '81', '79', '84', '84', '84', '84', '86', '86', '86', '86', '87', '87'],
    ['Yellow Magikoopa', '120', '150', '50', '70', '50', 'Magical Catch', '65', '35', '40', '30', '40', 'Push / Low', '10', '40', 'Technique', '2', 'Line Drive', 'Breaking Ball', '3', '4', '1', '8', '40', '51', '29', '57', '43', '41', '49', '34', '33', '88', '71', '91', '81', '36', '95', '31', '84', '37', '39', '90', '79', '61', '61', '61', '54', '54', '54', '87', '25', '36', '36', '36', '36', '50', '50', '50', '50', '44', '38', '35', '65', '67', '81', '79', '84', '84', '84', '84', '86', '86', '86', '86', '87', '87'],
    ['King Boo', '125', '165', '50', '60', '50', 'Super Jump & Curved Hits', '50', '15', '55', '75', '20', 'Mid / Mid', '30', '70', 'Power', '4', 'Pop-Fly', 'Fastball', '7', '5', '3', '4', '49', '11', '81', '48', '41', '40', '66', '21', '10', '75', '82', '80', '69', '37', '98', '32', '65', '79', '47', '58', '73', '54', '54', '54', '38', '38', '38', '76', '39', '37', '37', '37', '37', '44', '44', '44', '44', '50', '95', '42', '71', '70', '69', '73', '65', '65', '65', '65', '77', '77', '77', '77', '76', '76'],
    ['Petey', '130', '170', '50', '30', '50', 'Body Check & Wall Splat', '30', '10', '60', '95', '10', 'Pull / High', '10', '100', 'Power', '4', 'Pop-Fly', 'Change-Up', '9', '4', '1', '3', '35', '34', '91', '52', '5', '6', '42', '24', '23', '66', '63', '51', '44', '31', '64', '30', '33', '92', '37', '68', '43', '15', '15', '15', '10', '10', '10', '81', '28', '31', '31', '31', '31', '38', '38', '38', '38', '95', '50', '56', '74', '73', '44', '43', '33', '33', '33', '33', '41', '41', '41', '41', '81', '81'],
    ['Dixie', '115', '155', '50', '70', '50', 'Clamber', '60', '25', '42', '25', '30', 'Push / Low', '60', '70', 'Technique', '1', 'Grounder', 'Breaking Ball', '2', '5', '6', '6', '55', '57', '90', '95', '70', '72', '60', '71', '73', '33', '21', '24', '63', '64', '51', '62', '67', '89', '74', '66', '59', '44', '44', '44', '75', '75', '75', '54', '61', '64', '64', '64', '64', '35', '35', '35', '35', '42', '56', '50', '77', '88', '63', '59', '67', '67', '67', '67', '37', '37', '37', '37', '54', '54'],
    ['Goomba', '115', '155', '50', '50', '50', 'Ball Dash', '40', '15', '45', '40', '80', 'Mid / Mid', '50', '30', 'Balance', '0', 'Grounder', 'Fastball', '4', '3', '5', '4', '42', '40', '80', '91', '44', '46', '67', '45', '47', '73', '62', '61', '88', '66', '82', '64', '52', '54', '95', '55', '85', '38', '38', '38', '70', '70', '70', '78', '60', '66', '66', '66', '66', '65', '65', '65', '65', '71', '74', '77', '50', '97', '88', '85', '52', '52', '52', '52', '63', '63', '63', '63', '78', '78'],
    ['Paragoomba', '115', '154', '50', '50', '50', 'Super Jump', '30', '15', '45', '30', '80', 'Mid / Low', '70', '60', 'Speed', '0', 'Grounder', 'Fastball', '3', '2', '7', '5', '43', '41', '79', '80', '40', '47', '68', '42', '44', '72', '61', '63', '86', '60', '87', '59', '54', '55', '90', '51', '91', '36', '36', '36', '69', '69', '69', '77', '58', '60', '60', '60', '60', '67', '67', '67', '67', '70', '73', '88', '97', '50', '86', '91', '54', '54', '54', '54', '62', '62', '62', '62', '77', '77'],
    ['Red Koopa', '120', '165', '50', '50', '50', 'Sliding Catch', '70', '30', '40', '60', '30', 'Mid / Mid', '30', '50', 'Balance', '1', 'Pop-Fly', 'Breaking Ball', '6', '4', '3', '5', '65', '62', '67', '75', '60', '57', '78', '66', '64', '91', '58', '55', '50', '39', '84', '36', '70', '68', '80', '87', '99', '53', '53', '53', '71', '71', '71', '85', '31', '39', '39', '39', '39', '81', '81', '81', '81', '69', '44', '63', '88', '86', '50', '99', '70', '70', '70', '70', '90', '90', '90', '90', '85', '85'],
    ['Green Paratroopa', '115', '155', '50', '60', '50', 'Super Jump', '60', '35', '40', '30', '20', 'Mid / Low', '60', '60', 'Technique', '1', 'Line Drive', 'Breaking Ball', '2', '3', '6', '4', '62', '65', '72', '70', '57', '60', '74', '61', '77', '90', '55', '58', '99', '38', '89', '35', '75', '64', '82', '80', '50', '50', '50', '50', '68', '68', '68', '83', '30', '38', '38', '38', '38', '79', '79', '79', '79', '73', '43', '59', '85', '91', '99', '50', '75', '75', '75', '75', '88', '88', '88', '88', '83', '83'],
    ['Blue Shy Guy', '120', '160', '50', '50', '50', 'Sliding Catch', '50', '30', '42', '50', '25', 'Mid / Mid', '50', '40', 'Balance', '1', 'Grounder', 'Change-Up', '4', '3', '5', '5', '48', '47', '50', '66', '58', '55', '45', '10', '15', '85', '80', '78', '70', '53', '86', '51', '50', '90', '91', '83', '75', '60', '60', '60', '62', '62', '62', '72', '46', '53', '53', '53', '53', '84', '84', '84', '84', '65', '33', '67', '52', '54', '70', '75', '50', '50', '50', '50', '68', '68', '68', '68', '72', '72'],
    ['Yellow Shy Guy', '130', '165', '50', '55', '50', 'Sliding Catch', '50', '30', '42', '50', '25', 'Mid / Mid', '40', '40', 'Balance', '1', 'Grounder', 'Breaking Ball', '4', '4', '4', '5', '48', '47', '50', '66', '58', '55', '45', '10', '15', '85', '80', '78', '70', '53', '86', '51', '50', '90', '91', '83', '75', '60', '60', '60', '62', '62', '62', '72', '46', '53', '53', '53', '53', '84', '84', '84', '84', '65', '33', '67', '52', '54', '70', '75', '50', '50', '50', '50', '68', '68', '68', '68', '72', '72'],
    ['Green Shy Guy', '125', '160', '50', '60', '60', 'Sliding Catch', '50', '30', '42', '50', '25', 'Mid / Mid', '40', '40', 'Balance', '1', 'Grounder', 'Change-Up', '4', '4', '4', '5', '48', '47', '50', '66', '58', '55', '45', '10', '15', '85', '80', '78', '70', '53', '86', '51', '50', '90', '91', '83', '75', '60', '60', '60', '62', '62', '62', '72', '46', '53', '53', '53', '53', '84', '84', '84', '84', '65', '33', '67', '52', '54', '70', '75', '50', '50', '50', '50', '68', '68', '68', '68', '72', '72'],
    ['Black Shy Guy', '120', '160', '50', '50', '50', 'Sliding Catch', '50', '30', '42', '50', '25', 'Mid / Mid', '40', '50', 'Balance', '1', 'Pop-Fly', 'Fastball', '4', '4', '4', '6', '48', '47', '50', '66', '58', '55', '45', '10', '15', '85', '80', '78', '70', '53', '86', '51', '50', '90', '91', '83', '75', '60', '60', '60', '62', '62', '62', '72', '46', '53', '53', '53', '53', '84', '84', '84', '84', '65', '33', '67', '52', '54', '70', '75', '50', '50', '50', '50', '68', '68', '68', '68', '72', '72'],
    ['Gray Dry Bones', '120', '150', '90', '50', '50', 'Sliding Catch & Wall Splat', '65', '25', '40', '55', '30', 'Mid / Mid', '40', '50', 'Technique', '1', 'Grounder', 'Breaking Ball', '5', '4', '4', '3', '32', '28', '43', '44', '35', '30', '46', '33', '34', '92', '42', '48', '90', '29', '85', '27', '68', '56', '81', '84', '88', '58', '58', '58', '55', '55', '55', '82', '38', '29', '29', '29', '29', '86', '86', '86', '86', '77', '41', '37', '63', '62', '90', '88', '68', '68', '68', '68', '50', '50', '50', '50', '82', '82'],
    ['Green Dry Bones', '120', '150', '90', '50', '50', 'Sliding Catch & Wall Splat', '70', '25', '40', '55', '30', 'Mid / Mid', '30', '50', 'Technique', '1', 'Line Drive', 'Breaking Ball', '6', '4', '3', '3', '32', '28', '43', '44', '35', '30', '46', '33', '34', '92', '42', '48', '90', '29', '85', '27', '68', '56', '81', '84', '88', '58', '58', '58', '55', '55', '55', '82', '38', '29', '29', '29', '29', '86', '86', '86', '86', '77', '41', '37', '63', '62', '90', '88', '68', '68', '68', '68', '50', '50', '50', '50', '82', '82'],
    ['Red Dry Bones', '125', '155', '90', '50', '50', 'Sliding Catch & Wall Splat', '65', '25', '44', '60', '30', 'Mid / Mid', '30', '50', 'Technique', '1', 'Pop-Fly', 'Fastball', '6', '4', '3', '3', '32', '28', '43', '44', '35', '30', '46', '33', '34', '92', '42', '48', '90', '29', '85', '27', '68', '56', '81', '84', '88', '58', '58', '58', '55', '55', '55', '82', '38', '29', '29', '29', '29', '86', '86', '86', '86', '77', '41', '37', '63', '62', '90', '88', '68', '68', '68', '68', '50', '50', '50', '50', '82', '82'],
    ['Blue Dry Bones', '120', '150', '90', '50', '50', 'Sliding Catch & Wall Splat', '65', '25', '40', '55', '30', 'Mid / Mid', '30', '60', 'Technique', '1', 'Grounder', 'Change-Up', '5', '4', '3', '4', '32', '28', '43', '44', '35', '30', '46', '33', '34', '92', '42', '48', '90', '29', '85', '27', '68', '56', '81', '84', '88', '58', '58', '58', '55', '55', '55', '82', '38', '29', '29', '29', '29', '86', '86', '86', '86', '77', '41', '37', '63', '62', '90', '88', '68', '68', '68', '68', '50', '50', '50', '50', '82', '82'],
    ['Fire Bro', '125', '165', '50', '40', '50', 'Body Check', '30', '20', '5', '90', '15', 'Pull / Low', '20', '60', 'Power', '3', 'Grounder', 'Fastball', '8', '3', '2', '3', '38', '39', '75', '58', '32', '33', '40', '28', '27', '95', '84', '86', '85', '35', '71', '34', '72', '73', '25', '91', '83', '69', '69', '69', '42', '42', '42', '50', '36', '35', '35', '35', '35', '87', '87', '87', '87', '76', '81', '54', '78', '77', '85', '83', '72', '72', '72', '72', '82', '82', '82', '82', '50', '50'],
    ['Boomerang Bro', '125', '165', '50', '40', '50', 'Body Check, Curved Hits, & Wall Splat', '30', '20', '20', '80', '15', 'Mid / Mid', '30', '60', 'Power', '3', 'Line Drive', 'Breaking Ball', '8', '3', '3', '3', '38', '39', '75', '58', '32', '33', '40', '28', '27', '95', '84', '86', '85', '35', '71', '34', '72', '73', '25', '91', '83', '69', '69', '69', '42', '42', '42', '50', '36', '35', '35', '35', '35', '87', '87', '87', '87', '76', '81', '54', '78', '77', '85', '83', '72', '72', '72', '72', '82', '82', '82', '82', '50', '50']
]
# end