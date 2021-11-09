import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

start = time.time()

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
data_csv = pd.read_csv('https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv')
    
def setSelectorsToDropDown(data_csv):
    countries_all = []
    for x in data_csv['Country/Region']:
        countries_all.append(x)
    countries_all = list(dict.fromkeys(countries_all)) 
    countries = []
    for x in countries_all:
        countries.append({'label': x, 'value': x})
    return countries

def selectAllCountriesToList(data_csv):
    countries_all = []
    for x in data_csv['Country/Region']:
        countries_all.append(x)
    countries_all = list(dict.fromkeys(countries_all)) 
    countries = []
    for x in countries_all:
        countries.append(x)
    return countries

def countAllCasesForCountries(countries):
    sum = {}
    for x in countries:
        index = np.where(data_csv == x)
        tup  = index[0]
        all = 0
        for y in tup:
            all += data_csv.iloc[y,-1]
        sum[x] = all
    sum = sorted(sum.items(), key=lambda x: x[1], reverse=True)
    sum = np.array(sum)
    return sum

def countAllCasesForOneCountry(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]
    ret = []
    for x in dates[3:]:
        dd = country
        cc = country.value.loc[dd.variable == x]
        all = 0
        for y in cc:
            all += y
        ret.append(all)  
    return ret

def selectDates(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]
    ret = []
    for x in dates[3:]:
        split = (x.split("/"))
        dd = datetime(int("20"+split[2]),int(split[0]),int(split[1]))
        ret.append(dd)
    return ret

def countAllCasesPerDayForOneCountry(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]
    yesterday = 0
    ret = []
    for x in dates[3:]:
        dd = country
        cc = country.value.loc[dd.variable == x]
        all = 0
        for y in cc:
            all += y
        ret.append(all - yesterday)
        yesterday = all  
    return ret

def countLastCasesPerDayForOneCountry(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]
    yesterday = 0
    ret = []
    
    f = dates[len(dates)-2:len(dates)-1]
    f = list(f.items())[0][1]
    dd = country
    cc = country.value.loc[dd.variable == f]
    all = 0
    for y in cc:
        all += y
    yesterday = all

    f = dates[len(dates)-1:len(dates)]
    f = list(f.items())[0][1]
    dd = country
    cc = country.value.loc[dd.variable == f]
    all = 0
    for y in cc:
        all += y
        ret.append(all - yesterday)
    today = all

    return today - yesterday

countries = selectAllCountriesToList(data_csv)
total_rank = countAllCasesForCountries(countries)

dic = {}
for cc in countries:
    ff = countLastCasesPerDayForOneCountry(cc)
    dic[cc] = ff

countedCasesAllCountries = sorted(dic.items(), key=lambda x: x[1], reverse=True)
countedCasesAllCountriesPerDay = sorted(dic.items(), key=lambda x: x[1])

leastCasesPerDay = {}
countriesWithoutDisease = 0
for d in countedCasesAllCountriesPerDay:
    
    if(d[1] > 0):
        leastCasesPerDay[d[0]] = d[1]
        break
    countriesWithoutDisease+=1

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(children=[
    html.H1("COVID-19 DASHBOARD - Python version", style={'textAlign': 'center'}),
    html.Div([
        "Dane pobrano z dnia: ", 
        html.B("ładowanie aktualnych danych...  ",id = 'liveUpdate'),
        html.A(html.Button("Odśwież dane",n_clicks=0),id='button')],
        id = 'testup',
        style={'textAlign':'center'}),
    html.Div([
        "W dniu dzisiejszym odnotowano najwięcej przypadków zakażeń w kraju: " ,
        html.B("{}".format(countedCasesAllCountries[0][0])), 
        " z liczbą ",
        html.B("{}".format(countedCasesAllCountries[0][1])), 
        " przypdaków"
        ], style={'textAlign':'center'}),
    html.Div([
        "W dniu dzisiejszym odnotowano najmniej przypadków zakażeń w kraju: " ,
        html.B("{}".format(list(leastCasesPerDay.items())[0][0])),
        " z liczbą ",
        html.B("{}".format(list(leastCasesPerDay.items())[0][1])),
        " przypdaków"
        ], style={'textAlign':'center'}),
    html.Div([
        "W dniu dzisiejszym nie odnotowano nowych przypadków w ",
        html.B("{}".format(countriesWithoutDisease)),
        " krajach"
        ], style={'textAlign':'center', 'paddingBottom':'3%'}),
    dcc.Graph(
        id='example-graphhe',
        figure={
            'data': [
                {'x': total_rank[:5,0], 'y': total_rank[:5,1], 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Kraje z największą ilością przypadków zakażeń',
                'yaxis': {
                    'categoryorder': 'array',
                    'categoryarray': [x for _, x in sorted(zip(total_rank[:,0], total_rank[:,1]))]      
                    }
            },
        }
    ),
    html.Div("Wybierz Kraj:", style={'paddingBottom':'1%','paddingLeft':'5%'}),
    dcc.Dropdown(
        id='dropp',
        options=setSelectorsToDropDown(data_csv),
        value=['Poland'],
        style={'width':'40%'},
        multi=True
        
    ),
    dcc.Graph(
        id='example-graph',
    
    ),
    dcc.Graph(
        id='example-graphh',
     
    ),
])

@app.callback(
    [dash.dependencies.Output('liveUpdate', 'children')],
    [dash.dependencies.Input('button', 'n_clicks')])

def update_outputt(n_clicks):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    data_csv = pd.read_csv('https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv')

    return [str(dt_string)+" "]
@app.callback(
    [dash.dependencies.Output('testup', 'children')],
    [dash.dependencies.Input('button', 'n_clicks')])
def update_outputt(n_clicks):
    return [html.Div([
    "Dane pobrano: ", 
    html.B("ładowanie aktualnych danych...  ",id = "liveUpdate"),
    html.A(html.Button("Odśwież dane",n_clicks=0,id="button"))],
    style={'textAlign':'center'})]

@app.callback(
    [dash.dependencies.Output('dropp', 'value')],
    [dash.dependencies.Input('liveUpdate', 'children')])
def update_outputt(n_clicks):
    return [['Poland']]
 
@app.callback(
    [dash.dependencies.Output('example-graph', 'figure'),
    dash.dependencies.Output('example-graphh', 'figure')],
    [dash.dependencies.Input('dropp', 'value')])

def update_output(value):

    plot_x = selectDates('Poland')
    selectedCountries = ""
    figure = go.Figure()
    for country in value:
        selectedCountries += ", " + str(country).strip("['']") 
        plo =  countAllCasesForOneCountry(str(country).strip("['']"))
        figure.add_trace(go.Scatter(x=plot_x,y= plo,name = str(country).strip("['']")))
    

    figure1 = go.Figure()
    for country in value:
        plo = countAllCasesPerDayForOneCountry(str(country).strip("['']"))
        figure1.add_trace(go.Bar(x=plot_x,y= plo,name = str(country).strip("['']")))

    figure.update_layout(title =  {'text':'Wszystkie przypadki dla' + selectedCountries.lstrip(','),'x':0.5})
    figure1.update_layout(barmode='stack',title = {'text' : 'Dobowy przyrost dla' + selectedCountries.lstrip(','),'x':0.5})


    return figure,figure1

end = time.time()
print(end - start)

if __name__ == '__main__':
    app.run_server(debug=True)
