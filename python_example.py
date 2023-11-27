#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
#set==0無狀態 set==1新增 set==2刪除 set==3 送出跳轉
from unittest import result
from flask import Flask, request
import MySQLdb
import updateDB as DB
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

app = Flask(__name__)
'''
    form = """
    <form method="post" action="/action" >
        文字輸出欄位：<input name="my_head">
        <input type="submit" value="送出">
    </form>
    <button >
    
    <form method="post" action="/action2">
        <button type="submit" name="AllCourse" value="CourseID, CourseName">Click Me 2</button>
        登入帳號：<input type="text" name="user">
        密碼：<input type="password" name="passwd">
        <input type="submit" name="submit" value="送出">
    </form>
    """
'''
#<form method="post" action="/printOwnCourse">
 #       <p>登入帳號：<p><input type="text" name="user">
  #      <p>密碼：<p><input type="password" name="passwd">
   #     <p><button type="submit" value="*">送出</button>
    #</from>
#
 #   <form method="post" action="/index2" >
  #      <button type="submit" value="*">新增使用者</button>
   # </form>


@app.route('/')
def index():
    form = f"""
    <form method="post" action="/index2">
        <button type="submit" value="*">新增使用者</button>
    </form>
    <form method="post" action="/printAllCourse" >
        <button type="submit" name="AllCourse" value="*">顯示所有課程</button>
    </form>
    <form method="post" action="/printOwnCourse">
        <p>登入帳號：</p><input type="text" name="user">
        <p>密碼：</p><input type="password" name="passwd">
        <p><button type="submit" name="set"value="1">送出</button>
    </from>
    """
    return form

@app.route('/printOwnCourse', methods=['POST'])
def printOwnCourse():
    truth = {0:"否", 1:"是"}
    results=""
    username = request.form.get("user")
    passwd = request.form.get("passwd")
    yourname = DB.showName(username,conn)
    if username == "" or passwd == "":
        results = "<h1>帳號密碼不能為空</h1>"
        results += """<p><a href="/">Back to Query Interface</a></p>"""
        return results
    elif (DB.isUser(username, passwd, conn)== False):
        results = "<h1>帳號或密碼錯誤</h1>"
        results += """<p><a href="/">Back to Query Interface</a></p>"""
        results += """ <form method="post" action="/index2" >
                            <button type="submit" value="*">新增使用者</button>
                        </form>
                    """
        return results
    else:
        global StudentID
        StudentID= username
        cursor.execute(DB.listChosenList(StudentID))
        Set = request.form.get("set")
        if (Set=="2"):
            CourseID = request.form.get("courseID")
            #results +=f"{CourseID}"
            results += DB.deleteCourse(StudentID,CourseID,conn)
        results += """
    <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }
        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }
        tr:nth-child(even) {
        background-color: #dddddd;
        }
    </style>
    <p><a href="/">Back to Query Interface</a></p>
    """
    results +=  f"<h1>Welcome, 你的學號:{username}, 你的名字:{yourname}</h1>"
    results +=  f"""<form method="post" action="/AddCourse" >
                        <button type="submit" name="set" value="0">去選課!</button>
                    </form>"""
                
    results += f"<h2>已選課表 當前學分: {DB.currentPoint(StudentID, conn)}</h2>"
    results += """<p><font color="#ff0000">提示：若該課程是你的必修課程，退選按鈕將是紅色</font></p>"""
    results += "<table>"
    # 取得並列出所有查詢結果
    #CourseID,CourseName,Dept,PeopleLimit,Points,Teacher,Grade,MustHave
    results += "<tr>"
    results += "<th>課程ID</th> <th>課程名稱</th> <th>科系</th> <th>人數</th> <th>學分</th> <th>教授</th> <th>年級</th> <th>必修</th><th>時間地點</th><th>退選</th>"
    results += "</tr>"
    for (CourseID,CourseName,Dept,HowManyPeople, PeopleLimit,Points,Teacher,Grade,MustHav) in cursor.fetchall():
        #stringCourse = str(CourseID)
        results += "<tr>"
        results += "<td>{}</td> <td>{}</td> <td>{}</td> <td>{}/{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td><td>{}</td>".format(str(CourseID).zfill(4),CourseName,Dept,HowManyPeople,PeopleLimit,Points,Teacher,Grade,truth[MustHav],DB.courseTimeString(CourseID,conn))
        results += f"""<td>
                            <form method="post" action="" >
                            <input type="hidden"  name="courseID" value={CourseID}>
                            <input type="hidden"  name="user" value={username}>
                            <input type="hidden"  name="passwd" value={passwd}>
                            <button type="submit" name="set" value="2">"""
        if (DB.isMustHaveCourse(StudentID, CourseID, conn) == True):
            results += """<font color="#ff0000">退選</font>"""
        else:
            results += """退選"""
        results +=  """</button>
                            </form>
                        </td>
                    """
        results += "</tr>"            
    results += "</table>"
    results += f"""<form method="post" action="/personalTime" >
                        <button type="submit">查看個人課表</button>
                    </form>
                """
    return results




@app.route('/printAllCourse', methods=['POST'])
def printAllCourse():
    truth = {0:"否", 1:"是"}
    # 取得輸入的文字
    my_head = request.form.get("AllCourse")
    # 建立資料庫連線
    
    # 欲查詢的 query 指令
    #query1 = "SELECT * FROM AllCourse;"
    query1 = "SELECT {} FROM AllCourse;".format(my_head)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query1)

    results = """
    <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }
        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }
        tr:nth-child(even) {
        background-color: #dddddd;
        }
    </style>
    <p><a href="/">Back to Query Interface</a></p>
    """
    results += "<table>"
    # 取得並列出所有查詢結果
    #CourseID,CourseName,Dept,PeopleLimit,Points,Teacher,Grade,MustHave
    results += "<tr>"
    results += "<th>課程ID</th> <th>課程名稱</th> <th>科系</th> <th>人數</th> <th>學分</th> <th>教授</th> <th>年級</th> <th>必修</th> <th>時間地點</th>"
    results += "</tr>"
    for (CourseID,CourseName,Dept,HowManyPeople, PeopleLimit,Points,Teacher,Grade,MustHav) in cursor.fetchall():
        results += "<tr>"
        results += "<td>{}</td> <td>{}</td> <td>{}</td> <td>{}/{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>".format(str(CourseID).zfill(4),CourseName,Dept,HowManyPeople,PeopleLimit,Points,Teacher,Grade,truth[MustHav], DB.courseTimeString(CourseID,conn))
        results += "</tr>"
    results += "</table>"
    #results += "<h1>Welcome</h1>"
    return results

#login fill in form
@app.route('/index2', methods=['POST'])
def index2():
    form = """
    <form method="post" action="/AddUsers">
        <p>帳號：<p><input type="text" name="user">
        <p>密碼：<p><input type="password" name="passwd">
        <p>你的資料:
        <p>名字<input type="text" name="name">
        <p>系所<input type="text" name="dept">
        <p>年級<input type="text" name="grade">
        <p><button type="submit" value="*">送出</button>
    </from>
    """
    return form 

@app.route('/AddUsers', methods=['POST'])
def AddUsers():
    NID = request.form.get("user")
    UserPassword = request.form.get("passwd")
    UserName = request.form.get("name")
    Dept = request.form.get("dept")
    Grade = request.form.get("grade")
    if (isInt(Grade) == False):
        return """<script>alert("年級必須為數字")</script>""" + index2()
    if (DB.addUser(NID, UserName, UserPassword, Dept, Grade, conn) == False):
        return """<script>alert("用戶已存在")</script>""" + index2()
    DB.autoChooseMustHaveList(NID,conn)
    results = "<h1>新增成功，已將必選課程列入課表</h1>"
    results += """<p><a href="/">Back to Query Interface</a></p>"""
    return results

@app.route('/AddCourse',methods=['POST'])
def AddCourse():
    results =""
    truth = {0:"否", 1:"是"}
    Set = request.form.get("set")
    if (Set=="1"):
        CourseID = request.form.get("courseID")
        if (isInt(CourseID) == False):
            results += """<script>alert("請輸入課程ID(數字)")</script>"""
        elif (DB.addInWishList(StudentID,int(CourseID),conn) == False):
            results += """<script>alert("無此課程或該課程已選")</script>"""
        else:
            results += """<script>alert("成功加入願望清單")</script>"""
    if (Set=="2"):#deleteWishList
        CourseID = request.form.get("courseID")
        #results +=f"""{CourseID}"""
        if (DB.deleteFromWishList(StudentID,CourseID,conn) == True):
            results += """<script>alert("退出願望清單成功")</script>"""
        else:
            results += """<script>alert("退出失敗")</script>"""
    if (Set=="3"):
        #results += Set
        #results += DB.chooseCourse(StudentID,conn)
        results +=  f"""<script>
                            alert("{DB.chooseCourse(StudentID,conn)}")
                        </script>
                    """
    cursor.execute(DB.showWishList(StudentID))
    results += """
        <style>
            table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }
            td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            tr:nth-child(even) {
                background-color: #dddddd;
            }
        </style>
        <p><a href="/">Back to Query Interface</a></p>"""
    results +=  f"<h1>Welcome, 你的學號:{StudentID}, 你的名字:{DB.showName(StudentID,conn)} </h1>"
    results +=   f"""<form method="post" action="" >
                        輸入要加入願望清單的課程ID:<p><input type="text" name="courseID">
                        <button type="submit" name="set" value="1">加入願望清單</button>
                    </form>
                """
    results += """<p><font color="#ff0000">提示：修習學分數不可高於30分或低於9分</font></p>"""
    results += f"<h2>願望清單 | 願望清單學分數: {DB.wishListPoint(StudentID, conn)}</h2>"
    results += "<table>"
    # 取得並列出所有查詢結果
    #CourseID,CourseName,Dept,PeopleLimit,Points,Teacher,Grade,MustHave
    results += "<tr>"
    results += "<th>課程ID</th> <th>課程名稱</th> <th>科系</th> <th>人數</th> <th>學分</th> <th>教授</th> <th>年級</th> <th>必修</th> <th>時間地點</th> <th>取消關注</th>"
    results += "</tr>"
    
    for (CourseID,CourseName,Dept,HowManyPeople, PeopleLimit,Points,Teacher,Grade,MustHav) in cursor.fetchall():
        str(CourseID)
        results += "<tr>"

        results += "<td>{}</td> <td>{}</td> <td>{}</td> <td>{}/{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>".format(str(CourseID).zfill(4),CourseName,Dept,HowManyPeople,PeopleLimit,Points,Teacher,Grade,truth[MustHav],DB.courseTimeString(CourseID,conn))
        results += f"""<td>
                            <form method="post" action="" >
                            <input type="hidden"  name="courseID" value={CourseID}>
                            <button type="submit" name="set" value="2" >取消關注</button>
                            </form>
                        </td>
                    """
        results += "</tr>"
    results += "</table>"
    results += f"""<form method="post" action="" >
                        <button type="submit" name="set" value="3">將願望清單加入已選課表</button>
                    </form>
                """

    results += "<table>"
    # 取得並列出所有查詢結果
    #CourseID,CourseName,Dept,PeopleLimit,Points,Teacher,Grade,MustHave

    results += "<h2>可選課表</h2>"
    results += "<tr>"
    results += "<th>課程ID</th> <th>課程名稱</th> <th>學分</th> <th>人數</th> <th>學分</th> <th>教授</th> <th>年級</th> <th>必修</th> <th>時間地點</th>"
    results += "</tr>"
    choosableList = DB.ListChoosableCourse(StudentID, conn)
    for (CourseID,CourseName,Dept,HowManyPeople, PeopleLimit,Points,Teacher,Grade,MustHav) in choosableList:
        str(CourseID)
        results += "<tr>"
        results += "<td>{}</td> <td>{}</td> <td>{}</td> <td>{}/{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>".format(str(CourseID).zfill(4),CourseName,Dept,HowManyPeople,PeopleLimit,Points,Teacher,Grade,truth[MustHav],DB.courseTimeString(CourseID,conn))
        results += "</tr>"
    results += "</table>"
    return results

@app.route('/personalTime', methods=['POST'])
def pCourseTime():
    personalList = DB.personalCourseTime(StudentID, conn)
    results = """
    <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }
        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }
        tr:nth-child(even) {
        background-color: #dddddd;
        }
    </style>
    <p><a href="/">Back to Query Interface</a></p>
    """
    results += "<table>"
    results += "<tr>"
    results += "<th>課程名稱</th> <th>時間</th> <th>地點</th>"
    results += "</tr>"
    for a in personalList:
        results += "<tr>"
        for b in a:
            results += f" <td>{b}</td> "
        results += "</tr>"
    results += "</table>"
    return results