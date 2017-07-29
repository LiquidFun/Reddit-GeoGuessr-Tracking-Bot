import sqlite3
import operator

def getRankingsFromDatabase(databaseName, seriesTitle):
    
    #Connect to database
    database = sqlite3.connect(databaseName)
    cursor = database.cursor()

    nameSet = set()
    for row in cursor.execute('SELECT Place1, Place2, Place3 FROM ChallengeRankings WHERE SeriesTitle = \'' + seriesTitle + '\''):
        for val in row:
            if val is not '':
                #if '|' in val:
                    #print(val)
                for author in val.split('|'):
                    nameSet.add(author)
                #nameSet.add(author for author in val.split('|'))
                
    nameList = [name for name in nameSet]

    table = [[name, 0, 0, 0] for name in nameList]

    for i in range(1, 4):
        for row in cursor.execute('SELECT Place' + str(i) + ' FROM ChallengeRankings WHERE SeriesTitle = \'' + seriesTitle + '\''):
            for val in row:
                if val is not '':
                    for author in val.split('|'):
                        table[nameList.index(author)][i] += 1

    table.sort(reverse = True, key = operator.itemgetter(1, 2, 3))

    #print(table)
    return table

if __name__ == '__main__':
    getRankingsFromDatabase('database.db', 'dailychallenge')