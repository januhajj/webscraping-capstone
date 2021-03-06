from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

tbody = soup.find('table', attrs={'class':'table table-striped table-hover table-hover-solid-row table-simple history-data'})
tr = tbody.find_all('tr')

temp = [] #initiating a tuple

for i in range(1, len(tr)):
#insert the scrapping process here
    row = tbody.find_all('tr')[i]
    if len(row) == 4:

        #get date
        date = row.find_all('td')[0].text
        date = date.strip() #for removing the excess whitespace

        #get value
        kurs = row.find_all('td')[2].text
        kurs = kurs.strip() #for removing the excess whitespace
    
temp.append((date,kurs)) 

temp = temp[::-1]

#change into dataframe

data = pd.DataFrame(temp, columns = ('date','kurs'))

#insert data wrangling here
data['date'] = pd.to_datetime(data['date'], dayfirst = True)
data['kurs'] = data['kurs'].str.replace(" IDR","")
data['kurs'] = data['kurs'].str.replace(",","")
data['kurs'] = data['kurs'].astype('float64').round(2)
data['day'] = data['date'].dt.day_name()
#data = data.loc[(data['date'] >= '2021-02-01') & (data['date'] <= '2021-02-28')]

#end of data wranggling 

@app.route("/")
def index(): 

	card_data = f'USD {data["kurs"].mean()}'
	# generate plot
	ax = data.plot(x='date', figsize = (18,9))
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
