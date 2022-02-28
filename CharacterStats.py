import csv

# returns row index of character in csv
# arg1: >= 0 is index of character, -1 = charcter DNE, -2 = 'highest', -3 = 'lowest', -4 = 'average'
def findCharacter(characterArg):
    characterArg = characterArg.replace("_","").replace("-","")
    if characterArg == 'highest' or characterArg == 'best':
        return -2
    elif characterArg == 'lowest' or characterArg == 'worst':
        return -3
    elif characterArg == 'average' or characterArg == 'avg':
        return -4
    else:
        for character in charNameDict.keys():
            if character == characterArg:
                return charNameDict[character] + 1 # add 1 for csv format stuff
    return -1 # invalid number, if returned, character not found


# returns row index of stat in csv
def findStat(statArg):
    statArg = statArg.replace("_","").replace("-","")
    if 'chem' in statArg:
        chemStr = statArg.replace('chem', '', 1) # remove first instance of 'chem'
        return findCharacter(chemStr) + 26
    else:
        for stat in statNameDict.keys():
            if stat == statArg:
                return statNameDict[stat] + 1 # add 1 for csv format stuff
    return -1 # invalid number, if returned, stat not found


# used for sorting list of dicts in highest and lowest commands
def sortStats(d):
  return d["value"]


charNameDict = {}
statNameDict = {}
# converts characterNameList and statNameList to dicts
# format {<name>: <csv Index>}
def buildStatObjs():
    # make LoL's
    charNameList = []
    statsNameList = []
    with open('CharNames.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            charNameList.append(row)
    with open('StatNames.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            statsNameList.append(row)

    # convert list of lists to kv objects
    for i in range(0, len(charNameList)): # use ennumerate
        for name in charNameList[i]:
            charNameDict[name] = i
    for i in range(0, len(statsNameList)):
        for stat in statsNameList[i]:
            statNameDict[stat] = i


def buildStatsLoL(lolref):
    with open('Stats.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            lolref.append(row)


# performs logic for processing the stat command
def statLogic(arg1, arg2, statName, statsLoL):
    statList = [] # list of dicts; {'name': <str>, 'value': <int>}
    typeOfSort = ''
    for iRow in range(1, len(statsLoL)): # skip first row; labels
        statVal = statsLoL[iRow][arg2]
        try:
            float(statVal)
        except ValueError:
            return 'That operation is not possible with this stat.'
        statList.append({'name':statsLoL[iRow][0], 'value':float(statVal)})

    if arg1 == -4: # average
        sumVals = 0
        nVals = len(statList)
        for info in statList:
            sumVals += info['value']
        avgStat = str(round(sumVals/nVals, 2))
        return f'The average {statName} is {avgStat}'
        
    if arg1 == -2: # highest of a stat
        statList.sort(key = sortStats, reverse=True)
        typeOfSort = 'highest'
    
    if arg1 == -3: # lowest of a stat
        statList.sort(key = sortStats)
        typeOfSort = 'lowest'
    
    # generate message for high and low
    charGrammarCheck = 'characters'
    targetStat = statList[0]['value']
    targetChars = []
    for character in statList:
        if character['value'] == targetStat:
            targetChars.append(character['name'])
    characterString = 'are '
    numOfChars = len(targetChars)
    for iChar in range(0, numOfChars):
        if numOfChars == 1:
            characterString = 'is '
            characterString += targetChars[iChar]
            charGrammarCheck = 'character'
        if numOfChars == 2:
            if iChar == 0:
                characterString += targetChars[iChar] + " & "
            else:
                characterString += targetChars[iChar]
        if numOfChars > 2:
            if iChar < numOfChars - 1:
                characterString += targetChars[iChar] + ", "
            else:
                characterString += "& " + targetChars[iChar]
    returnStatVal = str(statList[0]['value'])
    return f'The {typeOfSort} {statName} is {returnStatVal}\nThe {charGrammarCheck} with the {typeOfSort} {statName} {characterString}'