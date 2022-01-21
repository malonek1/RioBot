import csv

# returns row index of character in csv
def findCharacter(characterArg):
    for character in charNameDict.keys():
        if character == characterArg:
            return charNameDict[character] + 1 # add 1 for csv format stuff
    return -1 # invalid number, if returned, character not found


# returns row index of stat in csv
def findStat(statArg):
    if 'chem' in statArg:
        chemStr = statArg.replace('chem', '', 1) # remove first instance of 'chem'
        return findCharacter(chemStr) + 22
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
    for i in range(0, len(charNameList)):
        for name in charNameList[i]:
            charNameDict[name] = i
    for i in range(0, len(statsNameList)):
        for stat in statsNameList[i]:
            statNameDict[stat] = i

# end