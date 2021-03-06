from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests

# don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # do not change this

# insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content, "html.parser")

tbody = soup.find('table', attrs={
                  'class': 'table table-striped table-hover table-hover-solid-row table-simple history-data'})
tr = tbody.find_all('tr')
temp = []  # initiating a tuple

for i in range(1, len(tr)):
    # insert the scrapping process here
    row = tbody.find_all('tr')[i]
    if len(row) == 4:

        # get date
        date = row.find_all('td')[0].text
        date = date.strip()  # for removing the excess whitespace

        # get day
        day = row.find_all('td')[1].text
        day = day.strip()  # for removing the excess whitespace

        # get value
        idr = row.find_all('td')[2].text
        idr = idr.strip()  # for removing the excess whitespace

        # get note
        note = row.find_all('td')[3].text
        note = note.strip()  # for removing the excess whitespace
    temp.append((date, idr))

temp = temp[::-1]

# change into dataframe
df = pd.DataFrame(temp, columns=('date', 'idr'))

# insert data wrangling here

df['date'] = pd.to_datetime(df['date'], dayfirst = True)
# df['date'] = df['date'].astype('datetime64', dayfirst = True )
df['idr'] = df['idr'].str.replace(" IDR","")
df['idr'] = df['idr'].str.replace(",","")
df['idr'] = df['idr'].astype('float64')
df['idr'] = df['idr'].round()
df['day'] = df['date'].dt.day_name()
# cond = (df['day'] >= '2021-02-01')
# df = df[cond]


# end of data wranggling


@app.route("/")
def index():

    card_data = f'USD {df["idr"].mean()}'

    # generate plot
    # ax = df.plot(figsize=(20, 9))
    ax = df.plot(x='date', figsize=(20, 9))
    # Rendering plot
    # Do not change this
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png)[2:-1]

    # generate plot 2

    df['yearmonth'] = df['date'].dt.to_period('M')
    ax2 = df.groupby('yearmonth').mean().plot(figsize = (20,9))

    # Rendering plot
    # Do not change this
    figfile2 = BytesIO()
    plt.savefig(figfile2, format='png', transparent=True)
    figfile2.seek(0)
    figdata_png2 = base64.b64encode(figfile2.getvalue())
    plot_result2 = str(figdata_png2)[2:-1]

    # render to html
    return render_template('index.html',
                           card_data=card_data,
                           plot_result=plot_result,
                           plot_result2=plot_result2
                           )


if __name__ == "__main__":
    app.run(debug=True)
