from hashlib import sha256
import MySQLdb

def tsuSHA256(aString):
    return str(sha256(aString.encode("utf-8")).hexdigest())

def haveSameNID(NID, conn):
    cursor = conn.cursor()
    cursor.execute(f"select count(*) from Users where NID = \'{NID}\';")
    results = 0
    for (a,) in cursor.fetchall():
        results = a
    if (results == 1):
        return True
    return False

# tested: ABLE TO USE
#add user with password using SHA256 hash function
def addUser(NID, UserName, UserPassword, Dept, Grade, conn):
    if (haveSameNID(NID, conn)):
        return False
    cursor = conn.cursor()
    passwd = tsuSHA256(UserPassword)
    results = f"insert into Users values(\'{NID}\', \'{UserName}\', \'{passwd}\', \'{Dept}\', {Grade});"
    cursor.execute(results)
    conn.commit()
    return True

# tested: ABLE TO USE
def listChosenListID(NID):
    results = f"select CourseID from AllCourse where CourseID in (select CourseID from Chosen where NID = \'{NID}\');"
    return results


def pyChosenList(NID, conn):
    cursor = conn.cursor()
    cursor.execute(listChosenListID(NID))
    finalList = []
    '''
    for (CourseID, CourseName, Dept, HowManyPeople, PeopleLimit, Points, Teacher, Grade, MustHave) in cursor.fetchall():
        temp = classroomAndCourseTime(CourseID, conn)
        finalList.append(CourseID, CourseName, Dept, HowManyPeople, PeopleLimit, Points, Teacher, Grade, MustHave, temp)
    '''
    for (a,) in cursor.fetchall():
        finalList.append(a)

    return finalList

# tested: ABLE TO USE
def showWishListID(NID):
    return f"select CourseID from AllCourse where CourseID in (select CourseID from WishList where NID = \'{NID}\');"

def pyWishList(NID, conn):
    cursor = conn.cursor()
    cursor.execute(showWishListID(NID))
    finalList = []
    for (a,) in cursor.fetchall():
        finalList.append(a)
    return finalList

# tested: ABLE TO USE
#list all Courses that a user must have
def mustHaveList(NID, conn):
    cursor = conn.cursor()
    cursor.execute(f"select Grade from Users where NID = \'{NID}\';")
    grade = 0
    for (a,) in cursor.fetchall():
        grade = a
    return f"select CourseID from AllCourse where MustHave = true and Dept in (select Dept from Users where NID = \'{NID}\') and Grade = {grade};"


'''
def isMustHaveCourse(Dept,CourseID, conn):
    cursor = conn.cursor()
    results =  f"SELECT MustHave, Dept FROM AllCourse WHERE CourseID = {CourseID};"
    cursor.execute(results)
    tempA = cursor.fetchall()
    
    #source: python_example.py
    if (tempA[0] == True) and (tempA[1] == Dept) :
        return True
    return False

'''
#tested: ABLE TO USE
def timeCollision(NID, CourseID, conn):
    cursor = conn.cursor()
    exxe = f"select count(*) from CourseTime where TimeID in "
    exxe += f"(select TimeID from CourseTime where CourseID in (select CourseID from Chosen where NID = \'{NID}\')) and "
    exxe += f"TimeID in (select TimeID from CourseTime where CourseID = {CourseID});"
    cursor.execute(exxe)
    results = 0
    for (a,) in cursor.fetchall():
        results = a
    if (results == 0):
        return False
    return True
    
'''
#not include time collision 未完成
def chooseCourse(NID, CourseID):
    
    timeTable = timeCollision(NID, CourseID)
    currentTimeOfCourse = f"SELECT TimeID FROM CourseTime WHERE CourseID = {CourseID}"
    result = f"IF (NOT EXISTS(SELECT TimeID FROM {currentTimeOfCourse} INNER JOIN {timeTable} ON {currentTimeOfCourse}.TimeID = {timeTable}.TimeID))"
    if 
    
    results = f"update AllCourse set HowManyPeople = HowManyPeople + 1 where CourseID = {CourseID};"
    results += f"insert into Chosen values(\'{NID}\', {CourseID});"
    return results
'''
# tested: ABLE TO USE
# 調用此函式需把回傳值results放入html裡呈現結果
def deleteCourse(NID, CourseID, conn):
    results = ""
    cursor = conn.cursor()
    if CourseIDIsChosenByNID(NID, CourseID, conn) == False:
        results += f"""  <script>
                            alert("你已經退選過 {CourseID} 了!!")
                        </script>
                    """
        return results
    cursor.execute(f"SELECT Points FROM AllCourse WHERE CourseID = {CourseID}")
    pointOfCourse = cursor.fetchone()
    pointOfresult = currentPoint(NID, conn) - pointOfCourse[0]
    if pointOfresult < 9:
        results += """  <script>
                            alert("不能退選, 退選當前課程會低於學分下限!!")
                        </script>
                    """
        return results
    results1 =  f"delete from Chosen where CourseID = {CourseID} and NID = \'{NID}\';\n"
    cursor.execute(results1)
    conn.commit()
    results2 = f"update AllCourse set HowManyPeople = HowManyPeople - 1 where CourseID = {CourseID};"
    cursor.execute(results2)
    conn.commit()
    if isMustHaveCourse(NID, CourseID, conn) == True:
        results += """  <script>
                            alert("你已退選您的 必選課程 !!")
                        </script>
                   """
        return results
    results +=  """ <script>
                        alert("你已退選成功!!")
                    </script>
                """
    return results

def isSameNameCourse(NID, CourseID, conn):
    chosenCourseName = f"select CourseName from AllCourse where CourseID in (select CourseID from Chosen where NID = \'{NID}\');"
    cursor = conn.cursor()
    cursor.execute(chosenCourseName)
    chosenCourseNameList = cursor.fetchall()
    cursor.execute(f"select CourseName from AllCourse where CourseID = {CourseID};")
    thisCourseName = cursor.fetchall()[0][0]
    for (coursename,) in chosenCourseNameList:
        if (coursename == None):
            return False
        if (coursename == thisCourseName):
            return True
    return False

def isCourse(CourseID, conn):
    cursor = conn.cursor()
    cursor.execute(f"select count(*) from AllCourse where CourseID = {CourseID};")
    results = 0
    for (a,) in cursor.fetchall():
        results = a
    if (results == 1):
        return True
    return False

def addInWishList(NID, CourseID, conn):
    cursor = conn.cursor()
    if (isCourse(CourseID, conn) == False):
        return False
    #cursor.execute(f"select CourseID from AllCourse where CourseID in (select CourseID from Chosen where NID = \'{NID}\');")
    #for (cID,) in cursor.fetchall():
    #    if CourseID == cID:
    #        return False
    if CourseID in pyChosenList(NID, conn):
        return False
    #cursor.execute(f"select CourseID from AllCourse where CourseID in (select CourseID from WishList where NID = \'{NID}\');")
    #for (cID,) in cursor.fetchall():
    #    if CourseID == cID:
    #        return False
    if CourseID in pyWishList(NID, conn):
        return False
    results = f"insert into WishList values(\'{NID}\', {CourseID});"
    cursor.execute(results)
    conn.commit()
    return True

def isExceedLimitOfStudent(CourseID, cursor):
    results = f"SELECT HowManyPeople,PeopleLimit FROM AllCourse WHERE CourseID = {CourseID};"
    cursor.execute(results)
    tempA = cursor.fetchall()
    #return tempA
    return tempA[0][0]>=tempA[0][1]#true or false


# tested: ABLE TO USE
#automate the "choose MustHave" process
def autoChooseMustHaveList(NID, conn):
    cursor = conn.cursor()
    cursor.execute(mustHaveList(NID,conn))
    for (CourseID,) in cursor.fetchall():
        if (isExceedLimitOfStudent(CourseID,cursor) == True):
            cursor.execute(f"insert into WishList values(\'{NID}\', {CourseID});")
            conn.commit()
            continue
        addAllCoursePeople = f"update AllCourse set HowManyPeople = HowManyPeople + 1 where CourseID = {CourseID};"
        addChosen = f"insert into Chosen values(\'{NID}\', {CourseID});"
        #print(addAllCoursePeople)
        #print(addChosen)
        cursor.execute(addAllCoursePeople)
        conn.commit()
        cursor.execute(addChosen)
        conn.commit()

#lists all CourseName, CourseID, Point that don't exceed limit of Point
#results is tuple list
def ListChoosableCourse(NID, conn):
    #source: python_example.py
    #cursor.execute(f"SELECT sum(Points) FROM AllCourse WHERE CourseID in (SELECT CourseID FROM Chosen WHERE NID = \'{NID}\');")
    currentTotalPointsOfStudent = currentPoint(NID, conn)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM AllCourse WHERE CourseID NOT IN (SELECT CourseID FROM Chosen where NID = \'{NID}\');")
    notChosenList = cursor.fetchall()
    results = []
    for (CourseID, CourseName, Dept, HowManyPeople, PeopleLimit, Points, Teacher, Grade, MustHave) in notChosenList:
        sum = currentTotalPointsOfStudent + Points
        if (9 <= sum and sum <= 30) and (isExceedLimitOfStudent(CourseID, cursor) == False):
            results.append((CourseID, CourseName, Dept, HowManyPeople, PeopleLimit, Points, Teacher, Grade, MustHave)) 
    return results


def isLessThanPointUpperLimit(NID, cursor):
    results = f"SELECT sum(Points) FROM AllCourse WHERE CourseID in (SELECT CourseID FROM Chosen WHERE NID = \'{NID}\');"
    #source: python_example.py
    cursor.execute(results)
    temp = cursor.fetchone()
    if temp[0] <= 30:
        return True
    return False


def isGreaterThanPointLowerLimit(NID, cursor):
    results = f"SELECT sum(Points) FROM AllCourse WHERE CourseID in (SELECT CourseID FROM Chosen WHERE NID = \'{NID}\');"
    #source: python_example.py
    cursor.execute(results)
    temp = cursor.fetchone()
    if temp[0] >= 9:
        return True
    return False

def isMustHaveCourse(NID, CourseID, conn):
    cursor = conn.cursor()
    results =  f"SELECT Dept, Grade, MustHave FROM AllCourse WHERE CourseID = {CourseID};"
    results2 = f"select Dept, Grade from Users where NID = \'{NID}\';"
    #source: python_example.py
    cursor.execute(results)
    temp = cursor.fetchall()
    cursor.execute(results2)
    temp2 = cursor.fetchall()
    for (dept, grade, musthave) in temp:
        if (dept == temp2[0][0]) and (grade == temp2[0][1]) and (musthave == 1):
            return True
    return False

# tested: ABLE TO USE
# if current point = 0, then return None
def currentPoint(NID, conn):
    cursor = conn.cursor()   
    results = f"select sum(Points) as CurrentPoint from AllCourse where CourseID in (select CourseID from Chosen where NID = \'{NID}\');"
    cursor.execute(results)
    CurrentPoints = 0
    for (a,) in cursor.fetchall():
        CurrentPoints = a
        if CurrentPoints == None:
            CurrentPoints = 0
    return CurrentPoints

#return [星期幾(string), 第幾節課(int)]
def TimeIDToTime(TimeID):
    weekRef = {1 :"一", 2: "二", 3: "三", 4: "四",
               5: "五", 6: "六", 7: "日"}
    week = (int)(TimeID/100)
    #print(week)
    theClass = TimeID % 100
    return [weekRef[week], theClass]

# tested: ABLE TO USE
def isUser(NID, passwd, conn):
    cursor = conn.cursor()
    userPassWd = tsuSHA256(passwd)
    searchsql = f"select count(*) from Users where NID = \'{NID}\' and UserPassword = \'{userPassWd}\';"
    cursor.execute(searchsql)
    results = 0
    for (amount,) in cursor.fetchall():
        results += amount
    if results == 1:
        return True
    return False

# tested: ABLE TO USE
def listChosenList(NID):
    results = f"select * from AllCourse where CourseID in (select CourseID from Chosen where NID = \'{NID}\');"
    return results

# tested: ABLE TO USE
def wishListPoint(NID, conn):
    cursor = conn.cursor()   
    results = f"select sum(Points) as CurrentPoint from AllCourse where CourseID in (select CourseID from WishList where NID = \'{NID}\');"
    cursor.execute(results)
    CurrentPoints = 0
    for (a,) in cursor.fetchall():
        CurrentPoints = a
        if CurrentPoints == None:
            CurrentPoints = 0
    return CurrentPoints

# tested: ABLE TO USE
def wishListPointAddChosenPoint(NID, conn):
    return currentPoint(NID, conn) + wishListPoint(NID, conn)

# tested: ABLE TO USE
def showWishList(NID):
    return f"select * from AllCourse where CourseID in (select CourseID from WishList where NID = \'{NID}\');"


# tested: ABLE TO USE

def chooseCourse(NID,conn):
    wishList = f"select CourseID from WishList where NID = \'{NID}\';"
    cursor = conn.cursor()
    cursor.execute(wishList)
    results = ""
    if (wishListPointAddChosenPoint(NID, conn) > 30):
        results += f"超出學分上限,"
        return results
    for (CourseID,) in cursor.fetchall():
        if (isExceedLimitOfStudent(CourseID, cursor) == True):
            #print(f"{CourseID} Exceed People Limit\n")
            results += f"超出人數上限：{CourseID},"
            continue
        if (timeCollision(NID, CourseID, conn) == True):
            results += f"{CourseID} 與已選課程衝堂,"
            continue
        if (isSameNameCourse(NID, CourseID, conn) == True):
            results += f"{CourseID} 與已選課程同名"
            continue
        results += f"{CourseID} 成功加選,"
        cursor.execute(f"insert into Chosen values(\'{NID}\', {CourseID});")
        conn.commit()
        cursor.execute(f"update AllCourse set HowManyPeople = HowManyPeople + 1 where CourseID = {CourseID};")
        conn.commit()
        cursor.execute(f"delete from WishList where CourseID = {CourseID} and NID = \'{NID}\';")
        conn.commit()
    if results == "":
        results = "願望清單為空"
    return results


#True when success
def deleteFromWishList(NID, CourseID, conn):

    inWishList = f"select count(*) from WishList where CourseID = {CourseID} and NID = \'{NID}\';"
    cursor = conn.cursor()
    cursor.execute(inWishList)
    wishCount = 0
    for (a,) in cursor.fetchall():
        wishCount = a
    if (wishCount != 1):
        return False
    cursor.execute(f"delete from WishList where CourseID = {CourseID} and NID = \'{NID}\';")
    conn.commit()
    return True
  

def classroomAndCourseTime(CourseID, conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT TimeID, Classroom FROM CourseTime WHERE CourseID = {CourseID};")
    return cursor.fetchall()


#（星期幾）第？節，在哪裡\n
def courseTimeString(CourseID, conn):
    finalResults = "｜"
    for (a,b) in classroomAndCourseTime(CourseID, conn):
        coursetime = TimeIDToTime(a)
        finalResults += f"（{coursetime[0]}）第{coursetime[1]}節，{b}｜"
    return finalResults

def personalCourseTime(NID, conn):
    cursor = conn.cursor()
    searchcoursetime = f"select * from CourseTime where CourseID in (select CourseID from Chosen where NID = \'{NID}\') order by TimeID;"
    cursor.execute(searchcoursetime)
    idlist = []
    for (CourseID, TimeID, Place) in cursor.fetchall():
        coursetime = TimeIDToTime(TimeID)
        idlist.append([CourseID, f"（{coursetime[0]}）第{coursetime[1]}節", Place])
    #return idlist
    for a in idlist:
        cursor.execute(f"select CourseName from AllCourse where CourseID = {a[0]};")
        for (b,) in cursor.fetchall():
            a[0] = b
    return idlist


def showLimit():
    return """<script>
                function(){
                    alert("提醒: 學分最高不能超過30，最低不能低於9")
                }
            </script>"""

def CourseIDIsChosenByNID(NID, CourseID, conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT count(*) FROM Chosen WHERE NID = \'{NID}\' AND CourseID = {CourseID};")
    temp = cursor.fetchall()
    if temp[0][0] == 0:
        return False
    return True

def showName(NID, conn):
    cursor = conn.cursor()
    results = f"SELECT Username FROM Users WHERE NID = \'{NID}\';"
    cursor.execute(results)
    for (a,) in cursor.fetchall():
        return a
