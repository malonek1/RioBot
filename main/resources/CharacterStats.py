import csv


# returns row index of character in csv
# arg1: >= 0 is index of character, -1 = character DNE, -2 = 'highest', -3 = 'lowest', -4 = 'average'
def find_character(character_arg):
    character_arg = character_arg.replace("_", "").replace("-", "")
    if character_arg == 'highest' or character_arg == 'best':
        return -2
    elif character_arg == 'lowest' or character_arg == 'worst':
        return -3
    elif character_arg == 'average' or character_arg == 'avg':
        return -4
    else:
        for character in charNameDict.keys():
            if character == character_arg:
                return charNameDict[character] + 1  # add 1 for csv format stuff
    return -1  # invalid number, if returned, character not found


# returns row index of stat in csv
def find_stat(stat_arg):
    stat_arg = stat_arg.replace("_", "").replace("-", "")
    if 'chem' in stat_arg:
        chem_str = stat_arg.replace('chem', '', 1)  # remove first instance of 'chem'
        return find_character(chem_str) + 26
    else:
        for stat in statNameDict.keys():
            if stat == stat_arg:
                return statNameDict[stat] + 1  # add 1 for csv format stuff
    return -1  # invalid number, if returned, stat not found


# used for sorting list of dicts in highest and lowest commands
def sort_stats(d):
    return d["value"]


charNameDict = {}
statNameDict = {}


# converts characterNameList and statNameList to dicts
# format {<name>: <csv Index>}
def build_stat_objs():
    # make LoL's
    char_name_list = []
    stats_name_list = []
    with open('resources/CharNames.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            char_name_list.append(row)
    with open('resources/StatNames.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            stats_name_list.append(row)

    # convert list of lists to kv objects
    for i in range(0, len(char_name_list)):  # use enumerate
        for name in char_name_list[i]:
            charNameDict[name] = i
    for i in range(0, len(stats_name_list)):
        for stat in stats_name_list[i]:
            statNameDict[stat] = i


def build_stats_lol(lolref):
    with open('resources/Stats.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            lolref.append(row)


# performs logic for processing the stat command
def stat_logic(arg1, arg2, stat_name, stats_lol):
    stat_list = []  # list of dicts; {'name': <str>, 'value': <int>}
    type_of_sort = ''
    for iRow in range(1, len(stats_lol)):  # skip first row; labels
        stat_val = stats_lol[iRow][arg2]
        try:
            float(stat_val)
        except ValueError:
            return 'That operation is not possible with this stat.'
        stat_list.append({'name': stats_lol[iRow][0], 'value': float(stat_val)})

    if arg1 == -4:  # average
        sum_vals = 0
        n_vals = len(stat_list)
        for info in stat_list:
            sum_vals += info['value']
        avg_stat = str(round(sum_vals / n_vals, 2))
        return f'The average {stat_name} is {avg_stat}'

    if arg1 == -2:  # highest of a stat
        stat_list.sort(key=sort_stats, reverse=True)
        type_of_sort = 'highest'

    if arg1 == -3:  # lowest of a stat
        stat_list.sort(key=sort_stats)
        type_of_sort = 'lowest'

    # generate message for high and low
    char_grammar_check = 'characters'
    target_stat = stat_list[0]['value']
    target_chars = []
    for character in stat_list:
        if character['value'] == target_stat:
            target_chars.append(character['name'])
    character_string = 'are '
    num_of_chars = len(target_chars)
    for iChar in range(0, num_of_chars):
        if num_of_chars == 1:
            character_string = 'is '
            character_string += target_chars[iChar]
            char_grammar_check = 'character'
        if num_of_chars == 2:
            if iChar == 0:
                character_string += target_chars[iChar] + " & "
            else:
                character_string += target_chars[iChar]
        if num_of_chars > 2:
            if iChar < num_of_chars - 1:
                character_string += target_chars[iChar] + ", "
            else:
                character_string += "& " + target_chars[iChar]
    return_stat_val = str(stat_list[0]['value'])
    return f'The {type_of_sort} {stat_name} is {return_stat_val}\nThe {char_grammar_check} with the {type_of_sort} {stat_name} {character_string}'
