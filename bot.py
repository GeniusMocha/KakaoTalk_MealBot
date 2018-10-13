# -*- coding: utf-8 -*-

import os, datetime, requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import re
from urllib2 import urlopen

app = Flask(__name__)

def get_diet(code, ymd, weekday):
    schMmealScCode = code # 항상 중식이라.. 2로 Default. 
    schYmd = str(ymd) # 요청할 날짜 YYYY.MM.DD
    if weekday == 5 or weekday == 6: #토요일, 일요일은..
        Meal_rep = "\nNull\n" # 급식 없어!
    else:
        URL = (
                "http://stu.ice.go.kr/sts_sci_md01_001.do?"
                "schulCode=E100002026"
                "&schulCrseScCode=3"
                "&schulKndScCode=03"
                "&schMmealScCode=%d&schYmd=%s" %(schMmealScCode, schYmd)
            )
        #schulCode= 학교코드
        #schulCrseScCode= 1 / 유치원, 2 / 초등학교, 3 / 중학교, 4 / 고등학교
        #schulKndScCode= 01 / 유치원, 02 / 초등학교, 03 / 중학교, 04 / 고등학교

        html = urlopen(URL)
        Meal = html.read()
        html.close()
        soup = BeautifulSoup(Meal, "lxml")

        Meal_data = soup.find("table", {"class" :"tbl_type3"}).find_all("tr")
        tmp0 = Meal_data[2]
    
        tdtmp = tmp0.find_all("td", {"class": "textC"})
        # 요일 처리.
        mon = tdtmp[1]
        tue = tdtmp[2]
        wed = tdtmp[3]
        thu = tdtmp[4]
        fri = tdtmp[5]
        if (weekday == 0 or weekday == 7):
            tmp1 = str(mon)
        elif (weekday == 1):
            tmp1 = str(tue)
        elif (weekday == 2):
            tmp1 = str(wed)
        elif (weekday == 3):
            tmp1 = str(thu)
        else:
            tmp1 = str(fri)
        
        # 잡것들 제거.
        Meal_rep = tmp1.replace('<br/>', '\n')
        Meal_rep = Meal_rep.replace('<td class="textC">', '')
        Meal_rep = Meal_rep.replace('<td class="textC last">', '')
        Meal_rep = Meal_rep.replace('<td>', '')
        Meal_rep = Meal_rep.replace('</td>', '')
        Meal_rep = Meal_rep.replace('</th>', '')
        Meal_rep = Meal_rep.replace('<th>', '')
        Meal_rep = Meal_rep.replace('<tr>', '')
        Meal_rep = Meal_rep.replace('</tr>', '')
        Meal_rep = Meal_rep.replace('<th scope="row">', '')
        Meal_rep = Meal_rep.replace('<tbody>', '')
        Meal_rep = Meal_rep.replace('<th scope="col">', '')
        Meal_rep = Meal_rep.replace('</tbody>', '')
        Meal_rep = Meal_rep.replace('<th class="last" scope="row">', '')
        Meal_rep = Meal_rep.replace('&amp;', ' ')

    return Meal_rep

def timetable(day):
    mon = "\n도덕,\n가정,\n과학,\n음악,\n체육,\n중국어 "
    tue = "\n국어,\n영어,\n스포츠,\n역사,\n기술,\n과학,\n수학 "
    wed = "\n영어,\n수학,\n체육,\n기술,\n과학,\n국어\n "
    thu = "\n역사(1),과학,\n국어,\n수학,\n영어,\n도덕 "
    fri = "\n수학,\n체육,\n가정,\n국어,\n역사(2),\n중국어 "

    if day == 5 or day == 6 :
        return "\nNull\n"

    elif day == 0 :
        return mon
    
    elif day == 1 :
        return tue
    
    elif day == 2 :
        return wed
    
    elif day == 3 :
        return thu
    
    elif day == 4 :
        return fri

@app.route('/keyboard')
def Keyboard():
 
    dataSend = {
        'type': 'buttons',
        'buttons': ['오늘의 급식은 무엇인가요?' , '내일의 급식은 무엇인가요?', '시간표 (아직 2-6반만 지원합니다.)']
    }
    return jsonify(dataSend)
 
 
 
@app.route('/message', methods=['POST'])
def Message():
    // JSON 반환..
    dataReceive = request.get_json()
    content = dataReceive['content']
 
    if content == u"오늘의 급식은 무엇인가요?":
        dataSend = {
            'message': {
                'text': "오늘의 급식은, " + get_diet(2, datetime.date.today().strftime("20%y.%m.%d"), datetime.datetime.now().weekday()) + "입니다."
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['오늘의 급식은 무엇인가요?' , '내일의 급식은 무엇인가요?', '시간표 (아직 2-6반만 지원합니다.)']
            }
        }

    elif content == u"내일의 급식은 무엇인가요?":
        dataSend = {
            'message': {
                'text': "내일의 급식은, " + get_diet(2, datetime.date.today().strftime("20%y.%m.%d"), datetime.datetime.now().weekday() + 1) + "입니다."
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['오늘의 급식은 무엇인가요?' , '내일의 급식은 무엇인가요?', '시간표 (아직 2-6반만 지원합니다.)']
            }
        }

    elif content == u"시간표 (아직 2-6반만 지원합니다.)":
        dataSend = {
            'message': {
                'text': "오늘의 시간표는, " + timetable(datetime.datetime.now().weekday()) + "입니다."
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['오늘의 급식은 무엇인가요?' , '내일의 급식은 무엇인가요?', '시간표 (아직 2-6반만 지원합니다.)']
            }
        }
 
    return jsonify(dataSend)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 5000)
