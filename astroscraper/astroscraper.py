import sqlite3

from bs4 import BeautifulSoup
import urllib.request
import datetime
import googlemaps
import pyodbc
import lxml

gmaps = googlemaps.Client(key='AIzaSyBK-qaY0zVUQX6CCHursfLJGSF-aysxw-8')

def get_launches(url):
    x = urllib.request.urlopen(url)
    soup = BeautifulSoup(x.read(), "html.parser")
    dates = soup.find_all(class_ = "datename")
    data = soup.find_all(class_= "missiondata")
    description = soup.find_all(class_= "missdescrip")
    list = []
    for x in range(0,len(dates)):
        contents = ((data[x].contents))
        info = []
        date_list = dates[x].find(class_="launchdate")
        mission = dates[x].find(class_="mission").contents[0].split("•")
        date = date_list.contents[len(date_list)-1]
        for y in date_list.contents:
            if str(y).count(",")==1:
               date = y
        if(len(contents)==1):
            lsunch_time = " ".join(contents[0].contents[0].split(" ")[2:])
        else:
            launch_time = contents[1]
        rocket = mission[0]
        payload = mission[1]
        launch_site = contents[len(contents)-1]
        my_description = description[x].contents[0]
        info.append(format_date(date,launch_time))
        #geocode_result = gmaps.geocode(launch_site)[0]
        #lat = geocode_result.get('geometry').get('location').get('lat')
        #long = geocode_result.get('geometry').get('location').get('lng')
        #info.append(lat)
        #info.append(long)
        info.append(launch_site)
        info.append(rocket)
        info.append(payload)
        info.append(my_description)
        list.append(info)
    return list




def format_date(day, time):
    correct_day = "   "
    day_vector = day.split(" ")
    #if split across month
    if(day_vector.count('')>0):
       day_vector = day_vector[:3]
    if (len(day_vector)==3):
        first_month = day_vector[0]
        second_month = first_month
        first_day = day_vector[1].split("/")[0][:2]
        if(len(day_vector[1].split("/"))==2):
            second_day = day_vector[1].split("/")[1][:2]
        else:
            second_day = first_day
        year = day_vector[2]
    elif (len(day_vector)==2):
        first_month = day_vector[0]
        second_month = first_month
        first_day = day_vector[1].split("/")[0][:2]
        if (len(day_vector[1].split("/"))==2):
            second_day = day_vector[1].split("/")[1][:2]
        else:
            second_day = first_day
    elif (len(day_vector)==4):
        first_month = day_vector[0]
        first_day = day_vector[1].split("/")[0][:2]
        second_month = day_vector[1].split("/")[1]
        second_day = day_vector[2][:2]
        year = day_vector[3]
    time_vector = time.split(" ")
    passer = True
    the_time=""
    for x in range(1,len(time_vector)):
        if time_vector[x].count("GMT")==1:
            the_time = time_vector[x-1]
        if time_vector[x].count("(")==1 and passer and time_vector[x-1].count("GMT")==0:
            correct_day = time_vector[x-1].strip("th").strip("st").strip("nd").strip("rd")
            passer = False
    if the_time=="":
       the_time=time_vector[1]
    correct_day = correct_day[0:2].strip("(")
    first_day = first_day.strip(",")
    second_day = second_day.strip(",")
    if (first_day==second_day and first_month==second_month):
        month = first_month
        the_day = first_day
    else:
        if(first_day==correct_day):
            the_day = first_day
            month = first_month
        elif(second_day==correct_day):
            the_day = second_day
            month = second_month
        else:
            the_day = first_day
            month = first_month
    monthDict = {'Jan.':1, 'Feb.':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'Aug.':8, 'Sept.':9,
                     'Oct.':10, 'Nov.':11, 'Dec.':12}
    monthDig = monthDict[month]
    if(the_time.isdigit()):
        if(the_time.count(":")==1):
            my_result = datetime.datetime(int(year),monthDig,int(the_day),int(the_time[:2]),int(the_time[2:4]),the_time[5:7])
        else:
            my_result = datetime.datetime(int(year), monthDig, int(the_day), int(the_time[:2]), int(the_time[2:4]))
    else:
        my_result = datetime.datetime(int(year), monthDig, int(the_day))
    return (my_result)


def main():
    connection = sqlite3.connect("myTable.db")
    crsr = connection.cursor()



    if input("Would you like to setup the table? y/n: ")=='y':
        sql = """CREATE table if not exists my_table (
                id INT PRIMARY KEY,
                [date] DATE,
                site TEXT,
                rocket TEXT,
                payload TEXT,
                description TEXT
                );"""
        crsr.execute(sql)
        list = get_launches('https://spaceflightnow.com/launch-log-2004-2008/')+ get_launches('https://spaceflightnow.com/launch-log-2009-2011/')+ get_launches('https://spaceflightnow.com/launch-log-2012-2014/')+get_launches('https://spaceflightnow.com/launch-log/')
        i=0
        for x in list:
            sql = """INSERT INTO my_table (ID,[DATE], SITE, ROCKET, PAYLOAD, DESCRIPTION) VALUES ( """""+ str(i) + """, '%s' , '%s' , '%s' , '%s' , '%s' );""" % (str(x[0]),x[1],x[2],x[3],x[4])
            print(sql)
            i=i+1
            crsr.execute(sql)
    sql = """SELECT COUNT(rocket) FROM my_table where rocket='Falcon 9 '"""
    crsr.execute(sql)
    for x in crsr:
        print (x)
    connection.commit()
    connection.close()

if __name__ == '__main__':
   main()