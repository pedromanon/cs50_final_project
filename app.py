import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
from dateutil.parser import parse
from fpdf import FPDF
# from pdf_calendar import createCalendar

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLite database
connection = sqlite3.connect('schedule.db', check_same_thread=False)
db = connection.cursor()

# Used to determine whether the charge day should change for option1
def change_charge(original, date, leap):
    month_last = "0"
    if int(original) == 31:
        if date == "04" or date == "06" or date == "09" or date == "11":
            month_last = "30"
        elif date == "02":
            month_last = str(28 + leap)
    elif int(original) > 28:
        if date == "02":
            month_last = str(28 + leap)
    return month_last

# Sets the fill color to a certain color
def appointment_color(pdf):
    return pdf.set_fill_color(253, 38, 38)

# Sets the fill color to a certain color
def draft_day_color(pdf, style):
    if style == "Classic":
        return pdf.set_fill_color(253, 39, 189)
    if style == "Hybrid":
        return pdf.set_fill_color(39, 253, 47)
    if style == "Volume":
        return pdf.set_fill_color(253, 253, 39)
    return None

# Sets the fill color to a certain color
def draft_and_appointment_day_color(pdf, style):
    if style == "Classic":
        return pdf.set_fill_color(160, 38, 253)
    if style == "Hybrid":
        return pdf.set_fill_color(38, 210, 253)
    if style == "Volume":
        return pdf.set_fill_color(253, 160, 38)
    return None
# Returns a specified string depending on what month is given as the parameter
def get_month(month):
    if month == "January":
        return "01"
    if month == "February":
        return "02"
    if month == "March":
        return "03"
    if month == "April":
        return "04"
    if month == "May":
        return "05"
    if month == "June":
        return "06"
    if month == "July":
        return "07"
    if month == "August":
        return "08"
    if month == "September":
        return "09"
    if month == "October":
        return "10"
    if month == "November":
        return "11"
    if month == "December":
        return "12"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Makes sure all tables in the database are clear
        db.execute("DELETE FROM option1")
        db.execute("DELETE FROM option2")
        connection.commit()
        
        # Sets variables equal to the values entered in the html form
        name = request.form.get("name")
        if name == None:
            name = ""
        date = request.form.get("date")
        membership_type = request.form.get("membership")
        if membership_type == None:
            return redirect("/")
        location = request.form.get("location")
        if location == None:
            location = ""
        weekends_only = request.form.get("weekend")

        # Sets the very first day in a variable
        start_date = datetime.datetime.today()
        while True:
            try:         
                start_date = parse(date)
                break
            except ValueError:
                return redirect("/")

        leap_year = 0
        i = 0
        # Creates a defualt set of dates starting on the date entered
        while i < (366 + leap_year):
            todays_date = (start_date + datetime.timedelta(days = i)).strftime('%Y-%m-%d')
            month = (start_date + datetime.timedelta(days = i)).strftime('%m')
            day = (start_date + datetime.timedelta(days = i)).strftime('%d')
            week_ahead = (start_date + datetime.timedelta(days = i + 7)).strftime('%m')
            week_before = (start_date + datetime.timedelta(days = i - 7)).strftime('%m')
            weekday = datetime.date.fromisoformat(todays_date).weekday()

            # Checks what day of the week the current day is and inserts the day into the schedule.db database
            if (weekday == 0):
                db.execute("INSERT INTO option1 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Monday', 1, 0, 0, 0)", (todays_date,))
                db.execute("INSERT INTO option2 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Monday', 1, 0, 0, 0)", (todays_date,))
            elif (weekday == 1):
                db.execute("INSERT INTO option1 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Tuesday', 1, 0, 0, 0)", (todays_date,))
                db.execute("INSERT INTO option2 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Tuesday', 1, 0, 0, 0)", (todays_date,))
            elif (weekday == 2):
                db.execute("INSERT INTO option1 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Wednesday', 1, 0, 0, 0)", (todays_date,))
                db.execute("INSERT INTO option2 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Wednesday', 1, 0, 0, 0)", (todays_date,))
            elif (weekday == 3):
                db.execute("INSERT INTO option1 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Thursday', 1, 0, 0, 0)", (todays_date,))
                db.execute("INSERT INTO option2 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Thursday', 1, 0, 0, 0)", (todays_date,))
            elif (weekday == 4):
                db.execute("INSERT INTO option1 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Friday', 1, 0, 0, 0)", (todays_date,))
                db.execute("INSERT INTO option2 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Friday', 1, 0, 0, 0)", (todays_date,))
            elif (weekday == 5):
                db.execute("INSERT INTO option1 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Saturday', 1, 0, 0, 0)", (todays_date,))
                db.execute("INSERT INTO option2 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Saturday', 1, 0, 0, 0)", (todays_date,))
            elif (weekday == 6):
                db.execute("INSERT INTO option1 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Sunday', 0, 0, 0, 0)", (todays_date,))
                db.execute("INSERT INTO option2 (date, weekday, can_schedule, appointment, charge, holliday) VALUES (?, 'Sunday', 0, 0, 0, 0)", (todays_date,))
            connection.commit()

            # Marks memorial day
            if (month == "05" and weekday == 0):
                if (week_ahead  == "06"):
                    temp = i + 1
                    db.execute("UPDATE option1 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                    db.execute("UPDATE option2 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                    connection.commit()
            # Marks labor day
            if (month == "09" and weekday == 0):
                if (week_before == "08"):
                    temp = i + 1
                    db.execute("UPDATE option1 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                    db.execute("UPDATE option2 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                    connection.commit()
            # Marks thanksgiving
            if (month == "11" and weekday == 3):
                if (week_ahead  == "12"):
                    temp = i + 1
                    db.execute("UPDATE option1 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                    db.execute("UPDATE option2 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                    connection.commit()
            # Marks new years
            if (month == "01" and day == "01"):
                temp = i + 1
                db.execute("UPDATE option1 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                db.execute("UPDATE option2 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                connection.commit()
            # Marks fourth of july
            if (month == "07" and day == "04"):
                temp = i + 1
                db.execute("UPDATE option1 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                db.execute("UPDATE option2 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                connection.commit()
            # Marks christmas
            if (month == "12" and day == "25"):
                temp = i + 1
                db.execute("UPDATE option1 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                db.execute("UPDATE option2 SET can_schedule = ?, appointment = ?, charge = ?, holliday = ? WHERE id = ?", (0, 0, 0, 1, temp))
                connection.commit()
            # Checks if it's leap year
            if (month == "02" and day == "29"):
                leap_year = 1
            i += 1


        # Creates the option 1 calendar
        count = 0
        first = None
        last = None
        middle = None
        for i in range(1,(367 + leap_year)):
            # These variables are used to figure out if a person can be scheduled depending on the day
            can_schedule = None
            day_before_can_schedule = None
            db.execute("SELECT * FROM option1 WHERE id = ?", (i,))
            value = db.fetchall()
            for x in value:
                can_schedule = x[3]
            db.execute("SELECT * FROM option1 WHERE id = ?", (i - 1,))
            value2 = db.fetchall()
            for x in value2:
                day_before_can_schedule = x[3]
            original_day = (start_date + datetime.timedelta(days = 0)).strftime('%d') 
            todays_date_day = (start_date + datetime.timedelta(days = i - 1)).strftime('%d')
            todays_date = (start_date + datetime.timedelta(days = i - 1)).strftime('%Y-%m-%d')
            weekday = datetime.date.fromisoformat(todays_date).weekday()
            todays_month = (start_date + datetime.timedelta(days = i - 1)).strftime('%m')

            # Executes a command to figure out when to schedule a client
            if todays_date_day == original_day or todays_date_day == change_charge(original_day, todays_month, leap_year):
                # first stores a day that can have an appointment and charge
                first = i
                last = None
                x = 0
                while last == None:
                    x += 1
                    target_date = (start_date + datetime.timedelta(days = i - 1 + x)).strftime('%d')
                    todays_new_month = (start_date + datetime.timedelta(days = i - 1 + x)).strftime('%m')
                    if target_date == original_day or target_date == change_charge(original_day, todays_new_month, leap_year):
                        last = i + x
                # middle stores a day that can have an appointment in between charges
                middle = int((first + last)/2)

            # This is run if the client chooses to be scheduled only on weekends
            if weekends_only == "yes":
                # The client gets charged on the first day of every month including the last day of the loop
                if i == first or i == 366 + leap_year:
                    db.execute("UPDATE option1 SET charge = ? WHERE id = ?", (True, i))
                    connection.commit()
                if i == middle or i == first or i == 366 + leap_year:
                    # This checks to see what day of the week the proposed appointment day is; if its not a saturday its rescheduled to the saturday closest to the current day
                    temp_num = 0
                    if weekday == 6:
                        temp_num = -1
                    elif weekday == 0:
                        temp_num = -2
                    elif weekday == 1:
                        temp_num = -3
                    elif weekday == 4:
                        temp_num = 1
                    elif weekday == 3:
                        temp_num = 2
                    elif weekday == 2:
                        temp_num = 3
                    
                    # This updates the option1 table so that it can denote an appointment
                    db.execute("SELECT * FROM option1 WHERE id = ?", (i + temp_num,))
                    value = db.fetchall()
                    for x in value:
                        can_schedule = x[3]
                    if can_schedule == 1:
                        db.execute("UPDATE option1 SET appointment = ? WHERE id = ?", (True, i + temp_num))
                    else:
                        can_schedule_tuple = db.execute("SELECT * FROM option1 WHERE id = ?", (i - 7 + temp_num,))
                        value = db.fetchall()
                        for x in value:
                            can_schedule = x[3]
                        if can_schedule == 1:
                            db.execute("UPDATE option1 SET appointment = ? WHERE id = ?", (True, i - 7 + temp_num))
                    connection.commit()
            else:
                # The client gets charged on the first day of every month including the last day of the loop
                if i == first or i == 366 + leap_year:
                    db.execute("UPDATE option1 SET charge = ? WHERE id = ?", (True, i))
                    connection.commit()
                # This updates the option1 table so that it can denote an appointment
                if i == middle or i == first or i == 366 + leap_year:
                    if can_schedule == 1:
                        db.execute("UPDATE option1 SET appointment = ? WHERE id = ?", (True, i))
                    elif day_before_can_schedule == 1:
                        db.execute("UPDATE option1 SET appointment = ? WHERE id = ?", (True, i - 1))
                    else:
                        db.execute("UPDATE option1 SET appointment = ? WHERE id = ?", (True, i - 2))
                    connection.commit()

        # Creates the option 2 calendar
        count = 0
        for i in range(1,(367 + leap_year), 14):
            # These variables are used to figure out if a person can be scheduled depending on the day
            count += 1
            can_schedule = None
            day_before_can_schedule = None
            db.execute("SELECT * FROM option2 WHERE id = ?", (i,))
            value = db.fetchall()
            for x in value:
                can_schedule = x[3]
            db.execute("SELECT * FROM option2 WHERE id = ?", (i - 1,))
            value2 = db.fetchall()
            for x in value2:
                day_before_can_schedule = x[3]

            # Checks to see whether or not it should charge the client and schedule them too
            if (count % 2 == 1 and (count < 13 or count > 26)) or (count % 2 == 0 and (count > 13 and count < 26)):
                db.execute("UPDATE option2 SET charge = ? WHERE id = ?", (True, i))
                # This adjusts the appointment to the nearest earliest available day if the store is closed
                if can_schedule == 1:
                    db.execute("UPDATE option2 SET appointment = ? WHERE id = ?", (True, i))
                elif day_before_can_schedule == 1:
                    db.execute("UPDATE option2 SET appointment = ? WHERE id = ?", (True, i - 1))
                else:
                    db.execute("UPDATE option2 SET appointment = ? WHERE id = ?", (True, i - 2))
                connection.commit()
            # This only schedules the client
            else:
                # This adjusts the appointment to the nearest earliest available day if the store is closed
                if can_schedule == 1:
                    db.execute("UPDATE option2 SET appointment = ? WHERE id = ?", (True, i))
                elif day_before_can_schedule == 1:
                    db.execute("UPDATE option2 SET appointment = ? WHERE id = ?", (True, i - 1))
                else:
                    db.execute("UPDATE option2 SET appointment = ? WHERE id = ?", (True, i - 2))
                connection.commit()

        
        # This list stores every day of the week in numerical order
        calendar_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        # This code goes through the first day of every month and stores its weekday in a list
        start_weekdays = []
        db.execute("SELECT weekday FROM option1 WHERE date LIKE '%01'")
        value = db.fetchall()
        for x in value:
            start_weekdays.append(x[0])
        start_day = str(start_date)[8:10]

        # If the day the client purchased their membership isn't the first day of the month this is run to figure
        #  out what day of the week the first day of the month in which the client bought the membership was
        if start_day != "01":
            last_day_year = None
            last_day_month = None
            last_day_day = None
            db.execute("SELECT date FROM option1 WHERE id = ?", (366 + leap_year,))
            value = db.fetchall()
            for x in value:
                last_day_year = str(x[0])[0:4]
                last_day_month = str(x[0])[5:7]
                last_day_day = str(x[0])[8:10]
            
            # This finds the weekday of the first day of the first month if there was a leap year
            if (int(last_day_year) % 4 == 0 and last_day_month != "01" and last_day_month != "02") or (last_day_month == "02" and last_day_day == "29"):
                # Since the year is a leapyear, the weekday of the first day of the first month should be two weekdays less than the last value on the weekday list we already have
                for j in range(7):
                    if calendar_week[j] == start_weekdays[len(start_weekdays) - 1]:
                        if j == 1:
                            start_weekdays.insert(0, "Saturday")
                        elif j == 0:
                            start_weekdays.insert(0, "Friday")
                        else:
                            start_weekdays.insert(0, calendar_week[j - 2])
            # This finds the weekday of the first day of the first month if there wasn't a leap year
            else:
                # Since the year is not a leapyear, the weekday of the first day of the first month should be a weekday less than the last value on the weekday list we already have
                for j in range(7):
                    if calendar_week[j] == start_weekdays[len(start_weekdays) - 1]:
                        if j == 0:
                            start_weekdays.insert(0, "Saturday")
                        else:
                            start_weekdays.insert(0, calendar_week[j - 1])

        # Creates a pdf page
        pdf = FPDF()
        pdf.add_page()

        # Initializes values 
        pdf.set_top_margin(.5)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Arial", size = 12)


  
        # Creates header of pdf
        pdf.cell(95, 8, txt = "Membership: " + membership_type, border = 1, align = 'C')
        pdf.cell(95, 8, txt = "Lash Lounge: " + location, ln = 1, border = 1, align = 'C')
        pdf.cell(95, 8, txt = "Client: " + name, border = 1, align = 'C')
        pdf.cell(95, 8, txt = "Signature: ", ln = 1, border = 1, align = 'L')

        # Skips a row of cell
        pdf.cell(0, 8, ln = 1)

        # Makes a list of months for a year in the order in which the month of purchase was
        months = []
        start_month = (start_date + datetime.timedelta(days = 0)).strftime('%m')
        if start_month == "01":
            months.extend(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January"])
        elif start_month == "02":
            months.extend(["February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February"])
        elif start_month == "03":
            months.extend(["March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March"])
        elif start_month == "04":
            months.extend(["April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March", "April"])
        elif start_month == "05":
            months.extend(["May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May"])
        elif start_month == "06":
            months.extend(["June", "July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June"])
        elif start_month == "07":
            months.extend(["July", "August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July"])
        elif start_month == "08":
            months.extend(["August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July", "August"])
        elif start_month == "9":
            months.extend(["September", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September"])
        elif start_month == "10":
            months.extend(["October", "November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "Ocotober"])
        elif start_month == "11":
            months.extend(["November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November"])
        elif start_month == "12":
            months.extend(["December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])


        # Creates the calendar headers of the pdf
        pdf.cell(95, 8, txt = "Option 1: Monthly", align = 'C')
        pdf.cell(95, 8, txt = "Option 2: Every Two Weeks", ln = 1, align = 'C')

        pdf.set_font("Arial", size = 8)

        total_day_count = 0
        total_count_flag = 0
        count_var = -1
        leap_year_flag = 0

        # This loop creates the calendar
        for i in range(7):
            # Figures out what month it is and prints it on the left side of the calendar
            count_var += 1
            month1 = months[count_var]
            pdf.cell(42, 6, txt = month1, align = 'C')
            pdf.cell(7, 6)

            # Figures out what month it is and prints it on the left side of the calendar
            count_var += 1
            month2 = None
            if count_var != 13:
                month2 = months[count_var]
                pdf.cell(42, 6, txt = month2, align = 'C')
            else:
                pdf.cell(42, 6)
            pdf.cell(8, 6)

            # Prints the month on the left side of the calendar again for the option 2 calendar
            count_var -= 1
            pdf.cell(42, 6, txt = month1, align = 'C')
            pdf.cell(7, 6)

            # Prints the month on the right side of the calendar again for the option 2 calendar
            count_var += 1
            if count_var != 13:
                pdf.cell(42, 6, txt = month2, ln = 1, align = 'C')
            else:
                pdf.cell(42, 6, ln = 1)
            
            # Creates count limits for each month which store the number of days per month and are eventually reset
            month1_count_limit = 0
            month2_count_limit = 0

            # Figures out how many days are in the current months and sets them to the count limit for the respective month
            if month1 == "January" or month1 == "March" or month1 == "May" or month1 == "July" or month1 == "August" or month1 == "October" or month1 == "December":
                month1_count_limit = 31
            elif month1 == "April" or month1 == "June" or month1 == "September" or month1 == "November":
                month1_count_limit = 30
            else:
                # Accomodates for a leap year
                if leap_year == 1:
                    if start_day == "29" and start_month == "02" and leap_year_flag == 0:
                        leap_year_flag = 1
                        month1_count_limit = 29
                    else:
                        month1_count_limit = 29 - leap_year_flag
                else:
                    month1_count_limit = 28
            if month2 == "January" or month2 == "March" or month2 == "May" or month2 == "July" or month2 == "August" or month2 == "October" or month2 == "December":
                month2_count_limit = 31
            elif month2 == "April" or month2 == "June" or month2 == "September" or month2 == "November":
                month2_count_limit = 30
            elif month2 != None:
                # Accomodates for a leap year
                month2_count_limit = 28 + leap_year

            month1_count = 0
            month2_count = 0
            month1_count_total = 0
            month2_count_total = 0

            # Loops through all of the rows in a single calendar month
            for x in range(7):
                # First row is reserved for printing the days of the week
                if x == 0:
                    pdf.cell(6, 3, txt = "Sun", align = 'C')
                    pdf.cell(6, 3, txt = "Mon", align = 'C')
                    pdf.cell(6, 3, txt = "Tue", align = 'C')
                    pdf.cell(6, 3, txt = "Wed", align = 'C')
                    pdf.cell(6, 3, txt = "Thu", align = 'C')
                    pdf.cell(6, 3, txt = "Fri", align = 'C')
                    pdf.cell(6, 3, txt = "Sat", align = 'C')

                    pdf.cell(7, 3)

                    if count_var != 13:
                        pdf.cell(6, 3, txt = "Sun", align = 'C')
                        pdf.cell(6, 3, txt = "Mon", align = 'C')
                        pdf.cell(6, 3, txt = "Tue", align = 'C')
                        pdf.cell(6, 3, txt = "Wed", align = 'C')
                        pdf.cell(6, 3, txt = "Thu", align = 'C')
                        pdf.cell(6, 3, txt = "Fri", align = 'C')
                        pdf.cell(6, 3, txt = "Sat", align = 'C')
                    else:
                        pdf.cell(42, 3)

                    pdf.cell(8, 3)

                    pdf.cell(6, 3, txt = "Sun", align = 'C')
                    pdf.cell(6, 3, txt = "Mon", align = 'C')
                    pdf.cell(6, 3, txt = "Tue", align = 'C')
                    pdf.cell(6, 3, txt = "Wed", align = 'C')
                    pdf.cell(6, 3, txt = "Thu", align = 'C')
                    pdf.cell(6, 3, txt = "Fri", align = 'C')
                    pdf.cell(6, 3, txt = "Sat", align = 'C')

                    pdf.cell(7, 3)

                    if count_var != 13:
                        pdf.cell(6, 3, txt = "Sun", align = 'C')
                        pdf.cell(6, 3, txt = "Mon", align = 'C')
                        pdf.cell(6, 3, txt = "Tue", align = 'C')
                        pdf.cell(6, 3, txt = "Wed", align = 'C')
                        pdf.cell(6, 3, txt = "Thu", align = 'C')
                        pdf.cell(6, 3, txt = "Fri", align = 'C')
                        pdf.cell(6, 3, txt = "Sat", ln = 1, align = 'C')
                    else:
                        pdf.cell(42, 3, ln = 1)
                # The rest of the rows will be used to print out the days of the month
                else:
                    # Runs if this isn't the last month on the calendar
                    if count_var != 13:
                        # Loops through the four months that will be printed on each row
                        for j in range(4):
                            # These variables keep track of how many days in the month have already been printed
                            flag1 = 0
                            flag2 = 0
                            month1_count = month1_count_total
                            month2_count = month2_count_total
                            # Loops through the 7 days in a week plus an empty cell to space out the calendars
                            for k in range(8):
                                # Checks to see that this cell isn't meant to be a space
                                if k != 7:
                                    # Checks to see that the next lines of code only apply to the left side of each calendar
                                    if j == 0 or j == 2:
                                        count_var -= 1
                                        # Applies code only to the days in the first week of the month
                                        if x == 1:
                                            # Only allows a day to be printed on the calendar if it is at the first day of the week of the month
                                            if start_weekdays[count_var] == calendar_week[k] or flag1 == 1:
                                                flag1 = 1
                                                month1_count += 1
                                                # Will print out the days of the month as long as the month count variable hasn't exceded the number of days in the month
                                                if month1_count <= month1_count_limit:
                                                    count_var += 1

                                                    # Formats the day of the month into something that can be used by a sql command
                                                    if (month1_count == int(start_day) and i == 0) or total_count_flag == 1:
                                                        string_length = len(str(month1_count))
                                                        if string_length == 1:
                                                            month_day = "%"+ get_month(month1) + "-0" + str(month1_count)
                                                        else:
                                                            month_day = "%"+ get_month(month1) + "-" + str(month1_count)
                                                        
                                                        # Code runs if it is a part of the calendar in option 1
                                                        if j == 0:
                                                            info = []
                                                            db.execute("SELECT appointment,charge FROM option1 WHERE date LIKE ?", (month_day,))
                                                            value = db.fetchall()
                                                            for m in value:
                                                                info.append(m[0])
                                                                info.append(m[1])
                                                                break

                                                            # Changes the color of the cell depending on the first table in schedule.db
                                                            if info[0] == 0 and info[1] == 0:
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                            elif info[0] == 1 and info[1] == 1:
                                                                draft_and_appointment_day_color(pdf, membership_type)
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                            elif info[0] == 1 and info[1] == 0:
                                                                appointment_color(pdf)
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                            elif info[0] == 0 and info[1] == 1:
                                                                draft_day_color(pdf, membership_type)
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                        # Code runs if it is a part of the calendar in option 2
                                                        elif j == 2:
                                                            info = []
                                                            db.execute("SELECT appointment,charge FROM option2 WHERE date LIKE ?", (month_day,))
                                                            value = db.fetchall()
                                                            for m in value:
                                                                info.append(m[0])
                                                                info.append(m[1])
                                                                break

                                                            # Changes the color of the cell depending on the second table in schedule.db
                                                            if info[0] == 0 and info[1] == 0:
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                            elif info[0] == 1 and info[1] == 1:
                                                                draft_and_appointment_day_color(pdf, membership_type)
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                            elif info[0] == 1 and info[1] == 0:
                                                                appointment_color(pdf)
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                            elif info[0] == 0 and info[1] == 1:
                                                                draft_day_color(pdf, membership_type)
                                                                pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                            total_count_flag = 1
                                                            total_day_count += 1
                                                    # Prints the day of the month
                                                    else:
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                # Prints empty cells
                                                else:
                                                    count_var += 1
                                                    pdf.cell(6, 3, border = 1)
                                            # Prints empty cells
                                            else:
                                                count_var += 1
                                                pdf.cell(6, 3, border = 1)
                                            # Sets the total count equal to the current count so that its not reset
                                            if j == 2:
                                                month1_count_total = month1_count
                                        # Applies code to the days after the first week of the month
                                        else:
                                            month1_count += 1
                                            # Will print out the days of the month as long as the month count variable hasn't exceded the number of days in the month
                                            if month1_count <= month1_count_limit:
                                                count_var += 1
                                                # Only allows a day to be printed on the calendar if it is at the first day of the week of the month
                                                if (month1_count == int(start_day) and i == 0) or total_count_flag == 1:

                                                    # Formats the day of the month into something that can be used by a sql command
                                                    string_length = len(str(month1_count))
                                                    if string_length == 1:
                                                        month_day = "%"+ get_month(month1) + "-0" + str(month1_count)
                                                    else:
                                                        month_day = "%"+ get_month(month1) + "-" + str(month1_count)
                                                        
                                                    # Code runs if it is a part of the calendar in option 1
                                                    if j == 0:
                                                        info = []
                                                        db.execute("SELECT appointment,charge FROM option1 WHERE date LIKE ?", (month_day,))
                                                        value = db.fetchall()
                                                        for m in value:
                                                            info.append(m[0])
                                                            info.append(m[1])
                                                            break

                                                        # Changes the color of the cell depending on the first table in schedule.db
                                                        if info[0] == 0 and info[1] == 0:
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                        elif info[0] == 1 and info[1] == 1:
                                                            draft_and_appointment_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 1 and info[1] == 0:
                                                            appointment_color(pdf)
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 0 and info[1] == 1:
                                                            draft_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                    # Code runs if it is a part of the calendar in option 1
                                                    elif j == 2:
                                                        info = []
                                                        db.execute("SELECT appointment,charge FROM option2 WHERE date LIKE ?", (month_day,))
                                                        value = db.fetchall()
                                                        for m in value:
                                                            info.append(m[0])
                                                            info.append(m[1])
                                                            break

                                                        # Changes the color of the cell depending on the second table in schedule.db
                                                        if info[0] == 0 and info[1] == 0:
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                        elif info[0] == 1 and info[1] == 1:
                                                            draft_and_appointment_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 1 and info[1] == 0:
                                                            appointment_color(pdf)
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 0 and info[1] == 1:
                                                            draft_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                        total_count_flag = 1
                                                        total_day_count += 1
                                                # Prints the day of the month
                                                else:
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                            # Prints empty cells
                                            else:
                                                count_var += 1
                                                pdf.cell(6, 3, border = 1)
                                            # Sets the total count equal to the current count so that its not reset
                                            if j == 2:
                                                month1_count_total = month1_count

                                    # Checks to see that the next lines of code only apply to the right side of each calendar
                                    else:
                                        # Applies code only to the days in the first week of the month
                                        if x == 1:
                                            # Only allows a day to be printed on the calendar if it is at the first day of the week of the month
                                            if start_weekdays[count_var] == calendar_week[k] or flag2 == 1:
                                                flag2 = 1
                                                month2_count += 1
                                                # Will print out the days of the month as long as the month count variable hasn't exceded the number of days in the month
                                                if month2_count <= month2_count_limit:

                                                    # Formats the day of the month into something that can be used by a sql command
                                                    string_length = len(str(month2_count))
                                                    if string_length == 1:
                                                        month_day = "%"+ get_month(month2) + "-0" + str(month2_count)
                                                    else:
                                                        month_day = "%"+ get_month(month2) + "-" + str(month2_count)
                                                    
                                                    # Code runs if it is a part of the calendar in option 1
                                                    if j == 1:
                                                        info = []
                                                        db.execute("SELECT appointment,charge FROM option1 WHERE date LIKE ?", (month_day,))
                                                        value = db.fetchall()
                                                        for m in value:
                                                            info.append(m[0])
                                                            info.append(m[1])
                                                            break

                                                        # Changes the color of the cell depending on the first table in schedule.db
                                                        if info[0] == 0 and info[1] == 0:
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1)
                                                        elif info[0] == 1 and info[1] == 1:
                                                            draft_and_appointment_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 1 and info[1] == 0:
                                                            appointment_color(pdf)
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 0 and info[1] == 1:
                                                            draft_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                    # Code runs if it is a part of the calendar in option 2
                                                    elif j == 3:
                                                        info = []
                                                        db.execute("SELECT appointment,charge FROM option2 WHERE date LIKE ?", (month_day,))
                                                        value = db.fetchall()
                                                        for m in value:
                                                            info.append(m[0])
                                                            info.append(m[1])
                                                            break

                                                        # Changes the color of the cell depending on the second table in schedule.db
                                                        if info[0] == 0 and info[1] == 0:
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1)
                                                        elif info[0] == 1 and info[1] == 1:
                                                            draft_and_appointment_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 1 and info[1] == 0:
                                                            appointment_color(pdf)
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                        elif info[0] == 0 and info[1] == 1:
                                                            draft_day_color(pdf, membership_type)
                                                            pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                        total_day_count += 1
                                                # Prints empty cells
                                                else:
                                                    pdf.cell(6, 3, border = 1)
                                            # Prints empty cells
                                            else:
                                                pdf.cell(6, 3, border = 1)
                                            # Sets the total count equal to the current count so that its not reset
                                            if j == 3:
                                                month2_count_total = month2_count
                                        else:
                                            month2_count += 1
                                            # Will print out the days of the month as long as the month count variable hasn't exceded the number of days in the month
                                            if month2_count <= month2_count_limit:

                                                # Formats the day of the month into something that can be used by a sql command
                                                string_length = len(str(month2_count))
                                                if string_length == 1:
                                                    month_day = "%"+ get_month(month2) + "-0" + str(month2_count)
                                                else:
                                                    month_day = "%"+ get_month(month2) + "-" + str(month2_count)
                                                    
                                                # Code runs if it is a part of the calendar in option 1
                                                if j == 1:
                                                    info = []
                                                    db.execute("SELECT appointment,charge FROM option1 WHERE date LIKE ?", (month_day,))
                                                    value = db.fetchall()
                                                    for m in value:
                                                        info.append(m[0])
                                                        info.append(m[1])
                                                        break

                                                    # Changes the color of the cell depending on the first table in schedule.db
                                                    if info[0] == 0 and info[1] == 0:
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1)
                                                    elif info[0] == 1 and info[1] == 1:
                                                        draft_and_appointment_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 1 and info[1] == 0:
                                                        appointment_color(pdf)
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 0 and info[1] == 1:
                                                        draft_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                # Code runs if it is a part of the calendar in option 2
                                                elif j == 3:
                                                    info = []
                                                    db.execute("SELECT appointment,charge FROM option2 WHERE date LIKE ?", (month_day,))
                                                    value = db.fetchall()
                                                    for m in value:
                                                        info.append(m[0])
                                                        info.append(m[1])
                                                        break

                                                    # Changes the color of the cell depending on the second table in schedule.db
                                                    if info[0] == 0 and info[1] == 0:
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1)
                                                    elif info[0] == 1 and info[1] == 1:
                                                        draft_and_appointment_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 1 and info[1] == 0:
                                                        appointment_color(pdf)
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 0 and info[1] == 1:
                                                        draft_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month2_count), align = 'C', border = 1, fill = True)
                                                    total_day_count += 1
                                            # Prints empty cells
                                            else:
                                                pdf.cell(6, 3, border = 1)
                                            # Sets the total count equal to the current count so that its not reset
                                            if j == 3:
                                                month2_count_total = month2_count

                                # These all print cells that are used for spaces
                                elif k == 7 and (j == 0 or j == 2):
                                    pdf.cell(7, 3)
                                elif k == 7 and j == 1:
                                    pdf.cell(8, 3)
                                else:
                                    pdf.cell(6, 3, ln = 1)

                    # This is the code run for the last month
                    else:
                        # Loops through the two months and empty spaces that will be printed on each row
                        for j in range(4):
                            # These variables keep track of how many days in the month have already been printed
                            flag1 = 0
                            month1_count = month1_count_total
                            temporary_var = 0
                            # Loops through the 7 days in a week plus an empty cell to space out the calendars
                            for k in range(8):
                                # Since this is the last month its printed on the left side of both calendars
                                if k != 7 and (j == 0 or j == 2):
                                    count_var -= 1
                                    # Applies code only to the days in the first week of the month
                                    if x == 1:
                                        # Only allows a day to be printed on the calendar if it is at the first day of the week of the month
                                        if start_weekdays[count_var] == calendar_week[k] or flag1 == 1:
                                            flag1 = 1
                                            month1_count += 1
                                            # Will print out the days of the month as long as the month count variable hasn't exceded the number of days in the month
                                            if month1_count <= month1_count_limit:
                                                # Code runs if it is a part of the calendar in option 1
                                                if j == 0:
                                                    temporary_var += 1
                                                    info = []
                                                    db.execute("SELECT appointment,charge FROM option1 WHERE id = ?", (total_day_count + temporary_var,))
                                                    value = db.fetchall()
                                                    for m in value:
                                                        info.append(m[0])
                                                        info.append(m[1])
                                                        break

                                                    # Changes the color of the cell depending on the first table in schedule.db
                                                    if len(info) < 2:
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                    elif info[0] == 0 and info[1] == 0:
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                    elif info[0] == 1 and info[1] == 1:
                                                        draft_and_appointment_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 1 and info[1] == 0:
                                                        appointment_color(pdf)
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 0 and info[1] == 1:
                                                        draft_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                # Code runs if it is a part of the calendar in option 2
                                                elif j == 2:
                                                    total_day_count += 1
                                                    info = []
                                                    db.execute("SELECT appointment,charge FROM option2 WHERE id = ?", (total_day_count,))
                                                    value = db.fetchall()
                                                    for m in value:
                                                        info.append(m[0])
                                                        info.append(m[1])
                                                        break

                                                    # Changes the color of the cell depending on the second table in schedule.db
                                                    if len(info) < 2:
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                    elif info[0] == 0 and info[1] == 0:
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                    elif info[0] == 1 and info[1] == 1:
                                                        draft_and_appointment_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 1 and info[1] == 0:
                                                        appointment_color(pdf)
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                    elif info[0] == 0 and info[1] == 1:
                                                        draft_day_color(pdf, membership_type)
                                                        pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                            # Prints empty cells
                                            else:
                                                pdf.cell(6, 3, border = 1)
                                        # Prints empty cells
                                        else:
                                            pdf.cell(6, 3, border = 1)
                                        # Sets the total count equal to the current count so that its not reset
                                        if j == 2:
                                                month1_count_total = month1_count
                                    else:
                                        month1_count += 1
                                        # Will print out the days of the month as long as the month count variable hasn't exceded the number of days in the month
                                        if month1_count <= month1_count_limit:
                                            # Code runs if it is a part of the calendar in option 1
                                            if j == 0:
                                                temporary_var += 1
                                                info = []
                                                db.execute("SELECT appointment,charge FROM option1 WHERE id = ?", (total_day_count + temporary_var,))
                                                value = db.fetchall()
                                                for m in value:
                                                    info.append(m[0])
                                                    info.append(m[1])
                                                    break

                                                # Changes the color of the cell depending on the first table in schedule.db
                                                if len(info) < 2:
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                elif info[0] == 0 and info[1] == 0:
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                elif info[0] == 1 and info[1] == 1:
                                                    draft_and_appointment_day_color(pdf, membership_type)
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                elif info[0] == 1 and info[1] == 0:
                                                    appointment_color(pdf)
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                elif info[0] == 0 and info[1] == 1:
                                                    draft_day_color(pdf, membership_type)
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                            # Code runs if it is a part of the calendar in option 2
                                            elif j == 2:
                                                total_day_count += 1
                                                info = []
                                                db.execute("SELECT appointment,charge FROM option2 WHERE id = ?", (total_day_count,))
                                                value = db.fetchall()
                                                for m in value:
                                                    info.append(m[0])
                                                    info.append(m[1])
                                                    break

                                                # Changes the color of the cell depending on the second table in schedule.db
                                                if len(info) < 2:
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                elif info[0] == 0 and info[1] == 0:
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1)
                                                elif info[0] == 1 and info[1] == 1:
                                                    draft_and_appointment_day_color(pdf, membership_type)
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                elif info[0] == 1 and info[1] == 0:
                                                    appointment_color(pdf)
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                                elif info[0] == 0 and info[1] == 1:
                                                    draft_day_color(pdf, membership_type)
                                                    pdf.cell(6, 3, txt = str(month1_count), align = 'C', border = 1, fill = True)
                                        # Prints empty cells
                                        else:
                                            pdf.cell(6, 3, border = 1)
                                        # Sets the total count equal to the current count so that its not reset
                                        if j == 2:
                                                month1_count_total = month1_count
                                    count_var += 1

                                # This prints cells that are used as spaces
                                elif k != 7 and (j == 1 or j == 3):
                                    pdf.cell(6, 3)
                                elif k == 7 and (j == 0 or j == 2):
                                    pdf.cell(7, 3)
                                elif k == 7 and j == 1:
                                    pdf.cell(8, 3)
                                else:
                                    pdf.cell(6, 3, ln = 1)

        # Skips a row of cell
        pdf.cell(0, 8, ln = 1)
        
        # This creates the color key
        appointment_color(pdf)
        pdf.cell(20, 3)
        pdf.cell(5, 3, border = 1, fill = True)
        pdf.cell(58, 3, txt = "Appointment", align = 'L')

        if membership_type == "Classic":

            draft_day_color(pdf, "Classic")
            pdf.cell(5, 3, border = 1, fill = True)
            pdf.cell(58, 3, txt = "Draft Day: $109", align = 'L')

            draft_and_appointment_day_color(pdf, "Classic")
            pdf.cell(5, 3, border = 1, fill = True)
            pdf.cell(58, 3, txt = "Appt/Draft: $109", align = 'L', ln = 1)
        elif membership_type == "Hybrid":

            draft_day_color(pdf, "Hybrid")
            pdf.cell(5, 3, border = 1, fill = True)
            pdf.cell(58, 3, txt = "Draft Day: $139", align = 'L')

            draft_and_appointment_day_color(pdf, "Hybrid")
            pdf.cell(5, 3, border = 1, fill = True)
            pdf.cell(58, 3, txt = "Appt/Draft: $139", align = 'L', ln = 1)
        elif membership_type == "Volume":

            draft_day_color(pdf, "Volume")
            pdf.cell(5, 3, border = 1, fill = True)
            pdf.cell(58, 3, txt = "Draft Day: $159", align = 'L')

            draft_and_appointment_day_color(pdf, "Volume")
            pdf.cell(5, 3, border = 1, fill = True)
            pdf.cell(58, 3, txt = "Appt/Draft: $159", align = 'L', ln = 1)

        # This stores the pdf in the static file
        pdf.output("./static/schedule.pdf")

        return render_template("index.html")
    else:
        # Makes sure all tables in the database are clear
        db.execute("DELETE FROM option1")
        db.execute("DELETE FROM option2")
        connection.commit()

        return render_template("layout.html")