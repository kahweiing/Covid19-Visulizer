import numpy as np

import database
import plotchart
from flask import Flask, render_template, request, jsonify, send_file
import vt, hashlib
from io import BytesIO, StringIO
import time
import os
import virustotal
import sqlalchemy
from pandas.io import sql
import pandas as pd

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

frame = ""
finalname = ""
full_path = ""
file_extension = ""


@app.route("/")
def default():
    global frame
    global finalname
    if finalname != "":
        database.execute_drop(finalname)
    return render_template('index.html')


@app.route("/index.html")
def home():
    global finalname
    if finalname != "":
        database.execute_drop(finalname)
    return render_template('index.html')


@app.route("/upload.html")
def upload():
    return render_template('upload.html')


@app.route("/selectData.html", methods=['POST'])
def upload_file():
    global finalname
    global full_path
    global file_extension

    uploaded_file = request.files['dataupload']
    if uploaded_file.filename != '':
        uploaded_file.save("saved/" + uploaded_file.filename)
    full_path = "saved/" + uploaded_file.filename
    file_extension = os.path.splitext(uploaded_file.filename)
    size = os.path.getsize(full_path)
    if size >= 1048576:  # 10mb
        return render_template("danger.html")
    if file_extension[1] == ".csv":
        raw_data = pd.read_csv(full_path)  # Read data from csv spreadsheet
    else:
        raw_data = pd.read_excel(request.files.get("dataupload"))  # Read data from excel spreadsheet
    filename = request.files["dataupload"].filename
    purename = filename.split(".")
    finalname = purename[0].replace("-", "_")
    finalname = finalname.replace(" ", "")

    raw_data.head()

    print(filename)
    print(finalname)

    # Call virustotal module and return the value from virustotal
    resultDict = virustotal.scan(full_path)
    if resultDict.get("malicious") != 0:
        return render_template("danger.html")
    # If virustotal has already check before and check whether is it malicious
    elif resultDict.get("times_submitted") == 0:
        if resultDict.get("malicious") != 0:
            return render_template("danger.html")
    else:
        raw_data.to_sql(finalname, database.init_engine(), index=False, if_exists="replace")  # Insert database

        # Get the column names from the database that we just inserted and populate list with it
        df = database.execute_select(finalname)
        columnlist = df['COLUMN_NAME'].tolist()

        return render_template("selectData.html", items=columnlist)


@app.route('/uploaded.html', methods=['POST'])
def select():
    global frame
    global finalname
    global full_path
    global file_extension
    Datalist = request.form.getlist("Data")
    x_axistitle = request.form.get("xaxis")

    # Database Function
    statement = ""
    for i in Datalist:
        statement += "`" + i + "`,"
        # Get the colums that the user just requested
    db_engine = database.init_engine()
    frame = pd.read_sql("SELECT " + statement[:-1] + " FROM ict1002." + finalname, db_engine.connect())
    frame.index += 1

    # Plot table
    html = frame.to_html(escape=False, table_id="dataTable", justify="center")

    # Reading csv/xlxs file
    if file_extension[1] == ".csv":
        df = pd.read_csv(full_path)
    elif file_extension[1] == ".xlsx":
        df = pd.read_excel(full_path)

    # Plotting graph
    tempBranches = getattr(df, x_axistitle)
    mainBranches = []
    statementlist = statement[:-1].replace("`", '')
    titlelist = statementlist
    titlelist = titlelist.split(',')
    statementlist = statementlist.split(',')
    for x in tempBranches:
        mainBranches.append(x)

    # Plot Bar Chart
    bar = plotchart.plotBarChart(statementlist, mainBranches, df, titlelist, x_axistitle)

    # Plot Line Chart
    line = plotchart.plotLineChart(statementlist, mainBranches, df, titlelist, x_axistitle)

    # Plot Stack Chart
    stack = plotchart.plotStackChart(statementlist, mainBranches, df, titlelist, x_axistitle)

    return render_template("uploaded.html", content=html, chart=bar, line=line, stack=stack)


@app.route('/Worldmap.html')
def display():
    return plotchart.plotWorldMap()

@app.route('/MoreInfo.html', methods=['GET', 'POST'])
def detailedInfo():
    df_confirm = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    # df_confirm = pd.read_csv("csv/time_series_covid19_confirmed_global.csv")
    df_confirmCountry = df_confirm.drop(columns=['Province/State', 'Lat', 'Long'])
    # Province/State, Lat and Long are redundant data, therefore it should be dropped

    df_confirmCountry = df_confirmCountry.groupby('Country/Region').agg('sum')
    # Group all the duplicate Country names due to the present of Province/State previously

    totalCasesCount = df_confirmCountry[df_confirmCountry.columns[-1]].sum()
    # New daily update of data will always be at the last column
    # Sum up the whole of last column for the total count

    averageConfirm = totalCasesCount / len(df_confirmCountry.columns[:])
    # Sum of total cases up to data / The total number of days up till date

    # Retrieve additonal information to populate total active, recovered and death
    df_info = pd.read_csv("./csv/covid-19-dataset-2.csv")

    #group by active cases
    df_active = df_info.groupby('Country_Region').sum()[['Active']]

    #group by recovered cases
    df_recovered = df_info.groupby('Country_Region').sum()[['Recovered']]

    #group by death cases
    df_death = df_info.groupby('Country_Region').sum()[['Deaths']]

    #total sum of active cases
    totalactivecount = round(df_info[df_active.columns[-1]].sum())

    # total sum of recovered cases
    totalrecovercount = round(df_recovered[df_recovered.columns[-1]].sum())

    # total sum of death cases
    totaldeathcount = round(df_death[df_death.columns[-1]].sum())


    countryNames = df_confirmCountry.index
    dropDownCountry = request.form.getlist("country")
    if dropDownCountry == []:
        selectedCountry = countryNames[-1]
    else:
        selectedCountry = dropDownCountry[0]

    radioOption = request.form.getlist("typeofdata")
    selectedResult = df_confirmCountry.loc[[selectedCountry], :]
    selectedResult = selectedResult.iloc[0, -1]
    if radioOption == [] or radioOption[0] == "totalCountryCases":
        selectedOption = "Total number of cases as of Today for " + selectedCountry + ": "
    else:
        selectedOption = "Average number of cases per day for " + selectedCountry + ": "
        selectedResult = round(selectedResult / len(df_confirmCountry.columns[:]))


    #Drop all other column to populate date for dropdownlist
    df_confirmDate = df_confirm.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
    ListofDate = df_confirmDate.columns
    dropDownDate = request.form.getlist("date")

    #get selected date value
    if dropDownDate == []:
        selecteddate = ListofDate[-1]
    else:
        selecteddate = dropDownDate[0]

    #Get the index of selected date
    dateindex = df_confirmDate.columns.get_loc(selecteddate)

    #If index is 0 add up the sum of column normally
    if dateindex == 0:
        virusselectedDate = df_confirmDate[selecteddate].sum(axis=0)

    #if index is not 0, subtract the sum of previous column to get the amount of cases per day
    else:
        virusindex = dateindex -1
        virusselectedDate = df_confirmDate[selecteddate].sum(axis=0) - df_confirmDate[ListofDate[virusindex]].sum(axis=0)

    virustotalbydate = "Total number of covid cases on " + selecteddate + ": "

    return render_template("MoreInfo.html", totalcases=totalCasesCount, average=round(averageConfirm), country=countryNames
                           , countryGroup=selectedOption, selectedResult=selectedResult, date=ListofDate, dateGroup=virustotalbydate
                           ,selectedResult1=virusselectedDate, totalactive=totalactivecount, totalrecovered=totalrecovercount
                           ,totaldeath=totaldeathcount)

@app.route('/download')
def exporttoexcel():
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    frame.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    output.seek(0)

    return send_file(output, attachment_filename="COVID19_" + time.strftime("%Y%m%d%H%M%S") + ".xlsx",
                     as_attachment=True)

@app.route('/downloadcsv')
def exporttocsv():
    proxy = StringIO()
    frame.to_csv(proxy)
    mem = BytesIO()
    mem.write(proxy.getvalue().encode('utf-8'))
    mem.seek(0)
    proxy.close()
    return send_file(mem, attachment_filename="COVID19" + time.strftime("%Y%m%d%H%M%S") + ".csv",
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")
