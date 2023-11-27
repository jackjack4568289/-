# updateDB.py testing place

import updateDB as udb
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="testdb")
cursor = conn.cursor()
def isInt(a):
    try:
        int(a)
    except:
        return False
    return True
NID = "aaa"
userName = "紀彥廷"
userDept = "資訊系"
userPasswd = "aaa"
userGrade = 2
#udb.addUser('421324', userName, userPasswd, userDept, userGrade, conn)
#udb.addUser(NID, userName, userPasswd, userDept, userGrade, conn)
#udb.autoChooseMustHaveList(NID, conn)
#udb.deleteCourse(NID, 9487, conn)
if (udb.isMustHaveCourse(NID, 859, conn) == True):
    print("aaa")
else:
    print("bbb")
#print(udb.isUser(NID, "IWasTestins", conn))
#cursor.execute()
#print(udb.chooseCourse(NID, conn))
#print(udb.timeCollision(NID,770,conn))
#print(udb.personalCourseTime(NID, conn))
#print(udb.addInWishList(NID, 5477, conn))
