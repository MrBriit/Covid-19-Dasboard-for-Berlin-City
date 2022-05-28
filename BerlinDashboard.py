import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mplcyberpunk
from PIL import Image

# Title - The title and introductory text and images are all written in Markdown format here, using st.write()


def run():

    img = Image.open('logo 1.jpeg')
    # img = img.resize((1000,1000))
    st.image(img)
    st.title('Covid-19 Report Dashboard for Berlin City')

    link = '[©Developed by Dr,Briit](https://www.linkedin.com/in/mrbriit/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)

run()




st.write("""



------------

This dashboard provides daily updates of the 7-day-incidence (number of cases per 100,000 inhabitants), the rolling 7-day-average number of new cases and the raw number of new reported Covid-19 cases. You may select the districts to view and compare.

The data are the latest official figures provided by the Berlin government, sourced from [berlin.de](https://www.berlin.de/lageso/gesundheit/infektionsepidemiologie-infektionsschutz/corona/tabelle-bezirke-gesamtuebersicht/).

If you are viewing this on a mobile device, tap **>** in the top left corner to select district and timescale.
""")
st.write("---")

####################################
# Getting Data

def get_data():
    historic_district_cases_url = 'https://www.berlin.de/lageso/_assets/gesundheit/publikationen/corona/meldedatum_bezirk.csv'
    historic_district_cases = pd.read_csv(historic_district_cases_url, sep=';', encoding = 'unicode_escape')

    return historic_district_cases

historic_district_cases_df = get_data()
print(historic_district_cases_df)

# Adding a Total column for all Berlin
historic_district_cases_df['All Berlin'] = historic_district_cases_df.sum(axis=1)
print(historic_district_cases_df)

# Convert 'Datum' Column to datetime pandas format
historic_district_cases_df['Datum'] = pd.to_datetime(historic_district_cases_df['Datum'])

# Defining a list with the districts of Berlin, ensuring consistency of ordering and spelling, and a list with the corresponding populations
districts = ['Lichtenberg', 'All Berlin', 'Mitte', 'Charlottenburg-Wilmersdorf', 'Friedrichshain-Kreuzberg', 'Neukoelln', 'Tempelhof-Schoeneberg', 'Pankow', 'Reinickendorf', 'Steglitz-Zehlendorf', 'Spandau', 'Marzahn-Hellersdorf', 'Treptow-Koepenick']
populations = [2.91452, 37.54418, 3.84172, 3.42332, 2.89762, 3.29691, 3.51644, 4.07765, 2.65225, 3.08697, 2.43977, 2.68548, 2.71153]

# Creating a pandas DataFrame with the populations of the districts
pop_dict = {'Bezirk': districts, 
            'Population': populations}
pop_df = pd.DataFrame(data=pop_dict)
print(pop_df)


####################################
# Sidebar for User Input

# Creating a multi-select box to allow multiple districts to be compared
selected_districts = st.sidebar.multiselect(
    'Select District(s):',
    districts,
    default=['Lichtenberg']   # setting Lichtenberg as the default district as it's the one I'm most interested in seeing
)

if selected_districts == []:
    selected_districts = ['All Berlin'] # if all selected districts are x'd out, display data for 'All Berlin'

# Creating a slider on the sidebar to adjust dates
days_to_show = st.sidebar.slider(
    'Number of days to display:',
    0, 365, 30
)

# Creating a Checkbox in the sidebar to turn off the mplcyberpunk style
st.sidebar.write('---')
st.sidebar.write('Chart Presentation Settings:')
nocyber = st.sidebar.checkbox('Light Style')


####################################
# Manipulating Data based on User Input

# This is the simple metric of new reported cases on each day
new_reported_cases = historic_district_cases_df['Datum']

# Adding a new column for each district selected by the user
for i in selected_districts:
    new_reported_cases = pd.concat([new_reported_cases, historic_district_cases_df[i]], axis = 1)


# Adding a  7-day-average column for the selected district to the existing dataframe ( moving average or rolling mean is simply a way to smooth out data fluctuations to help you distinguish between typical “noise” in data and the actual trend direction)
data_to_plot = historic_district_cases_df['Datum']

for i in selected_districts:
    seven_day_average = historic_district_cases_df.rolling(window=7)[i].mean()
    new_col_name = ('7 Day Average for %s' % i)
    historic_cases = historic_district_cases_df
    historic_cases[new_col_name] = seven_day_average
    data_to_plot = pd.concat([data_to_plot, historic_cases[new_col_name]], axis = 1)


# Creating a 7 day rolling sum of cases per district
for i in selected_districts:
    new_reported_cases['Seven Day Sum for %s' % i] = new_reported_cases[i].rolling(7).sum()

# Getting the population for the selected districts, using that to calculate the 7-day-incidence
for i in selected_districts:
    poppo = pop_df.loc[pop_df['Bezirk'] == i]
    popn = float(poppo['Population'])
    new_reported_cases['Seven Day Incidence for %s' % i] = new_reported_cases['Seven Day Sum for %s' % i] / popn


# Creating a DataFrame containing only the 7-day-incidence data
incidence = new_reported_cases['Datum']

for i in selected_districts:
    incidence = pd.concat([incidence, new_reported_cases['Seven Day Incidence for %s' % i]], axis = 1)


####################################
# Output - Producing the plots


# Selecting the style for the plots
if nocyber == False:
    plt.style.use('cyberpunk')
else:
    plt.style.use('ggplot')


# Plotting the 7 day incidence
st.write('## 7 Day Incidence')
st.write('This chart shows the 7 day incidence (# of cases per 100,000 inhabitants) for the selected district(s)')

incidence_data = incidence.iloc[-days_to_show:,:]

# Defining the 7-day incidence figure 
fig, ax = plt.subplots()

for i in selected_districts: # looping to plot each district
    plt.plot(incidence_data['Datum'], incidence_data['Seven Day Incidence for %s' % i])

ax.legend(selected_districts)
plt.xticks(rotation=45,
    horizontalalignment='right',
    fontweight='normal',
    fontsize='small',
    color= '1')
plt.yticks(color = '1')
plt.ylim((0))
plt.title('Seven Day Incidence - Last ' + str(days_to_show) + ' Days', color = '1')

# Removing the mplcyberpunk glow effects if checkbox selected
if nocyber == False:
    mplcyberpunk.add_glow_effects()
else:
    # fig.patch.set_facecolor('gray')
    legend = plt.legend(selected_districts)
    plt.setp(legend.get_texts(), color='k')

# Displaying the plot and the last 3 days' values
st.pyplot(fig)
st.table(incidence.iloc[-3:,:])

st.write('---')


# Plotting the 7 day average

#CYBERPUNK

st.write('## New reported cases - Rolling 7 Day Average')
st.write('This chart shows a [rolling 7-day-average](https://en.wikipedia.org/wiki/Moving_average) of newly reported cases for the selected district(s).')
st.write('This smoothes out the spikes somewhat and makes it easier to identify the real trend in cases.')

data = data_to_plot.iloc[-days_to_show:,:]

# Defining the figure 
fig, ax = plt.subplots()

for i in selected_districts: # looping to plot each district
    plt.plot(data['Datum'], data['7 Day Average for %s' % i])

ax.legend(selected_districts)
plt.xticks(rotation=45,
    horizontalalignment='right',
    fontweight='light',
    fontsize='small',
    color= '1')
plt.yticks(color = '1')
plt.title('Rolling 7-day-average - Last ' + str(days_to_show) + ' Days', color = '1')

#GGPLOT

# Removing the mplcyberpunk glow effects if checkbox selected
if nocyber == False:
    mplcyberpunk.add_glow_effects()
else:
    legend = plt.legend(selected_districts)
    plt.setp(legend.get_texts(), color='k')

# Displaying the plot and the last 3 days' values
st.pyplot(fig)
st.table(data_to_plot.iloc[-10:,:])

st.write('---')


# Plotting the new cases

st.write('## Newly Reported Cases')
st.write('This chart shows the raw number of new reported cases in the selected district(s).')
st.write("This will show larger variance and generally be 'noisier' than the 7-day-average chart.")
st.write('Notice that the numbers tend to dip to near zero on weekends and spike on Mondays. This is an artifact of the data collection process and not a real trend - new cases are generally not recorded / reported over weekends.')

new_cases = new_reported_cases.iloc[-days_to_show:,:]

# Defining the figure 
fig, ax = plt.subplots()

for i in selected_districts:
    plt.plot(new_cases['Datum'], new_cases[i])

ax.legend(selected_districts)
plt.xticks(rotation=45, 
    horizontalalignment='right',
    fontweight='light',
    fontsize='small',
    color= '1')
plt.yticks(color = '1')
plt.title('New Reported Cases - Last ' + str(days_to_show) + ' Days', color='1')

# Removing the mplcyberpunk glow effects if checkbox selected
if nocyber == False:
    mplcyberpunk.add_glow_effects()
else:
    legend = plt.legend(selected_districts)
    plt.setp(legend.get_texts(), color='k')

# Displaying the plot and the last 3 days' values
st.pyplot(fig)
number_to_limit_table = len(selected_districts) + 1 # This is just a hack to display the figures I want
st.table(new_reported_cases.iloc[-3:,:number_to_limit_table])

st.write('---')

st.write('''
    Dashboard created by [Dr Briit](https://linkedin.com/in/mrbriit), with [Streamlit](https://www.streamlit.io).
    See the code on [GitHub](https://github.com/MrBriit/Covid-19-Dasboard-for-Berlin-City).

    Disclaimer: I have made every effort to ensure the accuracy and reliability of the information on this dashboard. However, the information is provided "as is" without warranty of any kind.
''')

