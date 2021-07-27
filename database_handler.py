import sys
sys.path.insert(0, sys.path[0]+'/Modules')
import pymysql


def makeConnection():
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
        return conn
   
    except:
        return "Connection Fail"
        #print("connection fail")

def add_increment_userDB(event):
    #add or increment user
    #if the user doesn't exist, add the user to the database with a session count of 1
    #if the user already exists, add 1 to the session count of the user
    #should be added to the beginning of every session in spelling_main.
    conn = makeConnection()

    userID = event['session']['user']['userId']
    getUserSQL = "SELECT UserID, SessionCount FROM spelling.Users WHERE UserID = '" + userID + "'"
    newUserSQL = "INSERT INTO spelling.Users(UserID, SessionCount) VALUES('"+userID+"',1)"
    #userID = 'testuser123'
    
    with conn.cursor() as cur:
        cur.execute(getUserSQL)
        result = cur.fetchall()  #returns ['{UserIDKey':18, 'SessionCount': 3}]
        conn.commit()
        if len(result) == 0:
            cur.execute(newUserSQL)
            conn.commit()
            userAdded = 1
        else:
            currentSessionCount = result[0]["SessionCount"]
            #existingUserSQL = "UPDATE spelling.Users SET SessionCount = "+ str(currentSessionCount + 1) + " WHERE UserID = '" + userID + "'"
            existingUserSQL = """Update spelling.Users
                                 SET SessionCount = %s, LastDate = NOW()
                                 WHERE UserID = '%s'""" %(currentSessionCount+1, userID)
            cur.execute(existingUserSQL)
            conn.commit()
            userAdded = 0
        #cur.close()
    cur.close()
    conn.commit()
    conn.close()
    #del cur
    return userAdded
#userAdded

def check_userSessionsDB(session):
    #find out how many lists the user has
    userID = session['user']['userId']
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    getUserIDKeySQL = """SELECT SessionCount
                         FROM spelling.Users WHERE UserID = '%s'""" %(userID)
    with conn.cursor() as cur:
        cur.execute(getUserIDKeySQL)
        sessionCount = cur.fetchall()[0]['SessionCount']
        
        conn.commit()
        
    cur.close()
    conn.commit()
    conn.close()
    
    return sessionCount

def check_listDB(session):
    #find out how many lists the user has
    userID = session['user']['userId']
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    
    getUserIDKeySQL = """SELECT UserIDKey
                         FROM spelling.Users WHERE UserID = '%s'""" %(userID)
    with conn.cursor() as cur:
        cur.execute(getUserIDKeySQL)
        userIDKey = cur.fetchall()[0]['UserIDKey']
        checkListSQL = """SELECT DISTINCT(List) FROM spelling.Lists WHERE UserIDKey = %s"""%(userIDKey)
        cur.execute(checkListSQL)
        allLists = cur.fetchall()
        #this is the output of a fetchall
        #         [
        #   {
        #     "List": 1
        #   },
        #   {
        #     "List": 2
        #   }
        # ]
        #get all the lists being used. put them in a "list"
        allListNums = []
        for row in allLists:
            allListNums.append(row["List"])
        
        conn.commit()
            
    cur.close()
    conn.commit()
    conn.close()
    return allListNums
    
    
def add_wordsDB(session, wordList, listNum):
    #add words to the database
    numMap = {"one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eight":8, "nine":9, "ten":10}
    listNum = numMap[listNum]
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    
    userID = session['user']['userId'] 
    getUserIDKeySQL = """SELECT UserIDKey
                         FROM spelling.Users WHERE UserID = '%s'""" %(userID)
    with conn.cursor() as cur:
        cur.execute(getUserIDKeySQL)
        userIDKey = cur.fetchall()[0]['UserIDKey']
        for word in wordList:
            #implement later?
            checkWordExistsSQL = """SELECT Word FROM spelling.Lists
                                    WHERE UserIDKey = %s
                                    AND Word = %s""" %(userIDKey, word) 
            insertWordSQL = """INSERT INTO spelling.Lists (UserIDKey, List, Word)
                               VALUES (%s, %s, '%s')""" %(userIDKey, listNum, word)
            cur.execute(insertWordSQL)
            conn.commit()
            
    cur.close()
    conn.commit()
    conn.close()

def get_wordsDB(session, listNum):
    numMap = {"one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eight":8, "nine":9, "ten":10}
    listNum = numMap[listNum]
    
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    
    userID = session['user']['userId'] 
    getUserIDKeySQL = """SELECT UserIDKey 
                         FROM spelling.Users 
                         WHERE UserID = '%s'""" %(userID)
    with conn.cursor() as cur:
        cur.execute(getUserIDKeySQL)
        userIDKey = cur.fetchall()[0]['UserIDKey']
        getWordsSQL = """SELECT Word
                         FROM spelling.Lists
                         WHERE UserIDKey = %s AND List = %s""" %(userIDKey, listNum)
        cur.execute(getWordsSQL)
        wordsResult = cur.fetchall()
        wordList = []
        for row in wordsResult:
            wordList.append(row['Word'])
        return(wordList)
    conn.close()
    
    
def get_paidDB(session):
    #find out if the user is paid
    #returns 1 or 0
    userID = session['user']['userId']
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    getPaidSQL = """SELECT Paid
                         FROM spelling.Users WHERE UserID = '%s'""" %(userID)
    with conn.cursor() as cur:
        cur.execute(getPaidSQL)
        paid = cur.fetchall()[0]['Paid']
        
        conn.commit()
        
    cur.close()
    conn.commit()
    conn.close()
    
    return paid

def set_paidDB(session, paid):
    userID = session['user']['userId']
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    setPaidSQL = """UPDATE spelling.Users SET Paid = %s WHERE UserID = '%s'""" %(paid, userID)
    with conn.cursor() as cur:
        cur.execute(setPaidSQL)
        conn.commit()
        
    cur.close()
    conn.commit()
    conn.close()

def set_gradeDB(session, grade):
    numMap = {"one":1, "two":2, "three":3, "four":4, "five":5, "six":6, "seven":7, "eight":8, "nine":9, "ten":10, "eleven": 11, "twelve":12}
    gradeNum = numMap[grade]
    userID = session['user']['userId']
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    setGradeSQL = """UPDATE spelling.Users SET Grade = %s WHERE UserID = '%s'""" %(gradeNum, userID)
    with conn.cursor() as cur:
        cur.execute(setGradeSQL)
        conn.commit()
        
    cur.close()
    conn.commit()
    conn.close()
    
def get_GradewordsDB(session):
    userID = session['user']['userId']
    try:
        conn = pymysql.connect('jeffdb.c8gaccabupfm.us-east-1.rds.amazonaws.com', user='lambdauser', passwd='dRt4#98Uknd', db='spelling', connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
    except:
        return "Connection Fail"
    getGradeSQL = """SELECT Grade FROM spelling.Users WHERE UserID = '%s'""" %(userID)
    getWordsSQL = """SELECT Word
                    FROM spelling.GradeLists
                    WHERE GradeLevel = %s
                    ORDER BY RAND()
                    LIMIT 10"""%(grade)
    with conn.cursor() as cur:
        cur.execute(getGradeSQL)
        grade = cur.fetchall()[0]['Grade']
        conn.commit()
        cur.execute(getWordsSQL)
        wordList = cur.fetchall[0]['Word']
        conn.commit()
        
    print(wordList)
        
    cur.close()
    conn.commit()
    conn.close()
