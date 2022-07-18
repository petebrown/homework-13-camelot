#!/usr/bin/env python
# coding: utf-8

# # Parsing PDFs Homework
# 
# With the power of pdfminer, pytesseract, Camelot, and Tika, let's analyze some documents!
# 
# > If at any point you think, **"I'm close enough, I'd just edit the rest of it in Excel"**: that's fine! Just make a note of it.
# 
# ## A trick to use again and again
# 
# ### Approach 1
# 
# Before we get started: when you want to take the first row of your data and set it as the header, use this trick.

# In[5]:


import pandas as pd


# In[6]:


df = pd.DataFrame([
    [ 'fruit name', 'likes' ],
    [ 'apple', 15 ],
    [ 'carrot', 3 ],
    [ 'sweet potato', 45 ],
    [ 'peach', 12 ],
])
df


# In[7]:


# Set the first column as the columns
df.columns = df.loc[0]

# Drop the first row
df = df.drop(0)

df


# 🚀 Done!
# 
# ### Approach 2
# 
# Another alternative is to use `.rename` on your columns and just filter out the columns you aren't interested in. This can be useful if the column name shows up multiple times in your data for some reason or another.

# In[5]:


# Starting with the same-ish data...
df = pd.DataFrame([
    [ 'fruit name', 'likes' ],
    [ 'apple', 15 ],
    [ 'carrot', 3 ],
    [ 'fruit name', 'likes' ],
    [ 'sweet potato', 45 ],
    [ 'peach', 12 ],
])
df


# In[4]:


df = df.rename(columns={
    0: 'fruit name',
    1: 'likes'
})
df = df[df['fruit name'] != 'fruit name']
df


# 🚀 Done!
# 
# ### Useful tips about coordinates
# 
# If you want to grab only a section of the page [Kull](https://jsoma.github.io/kull/#/) might be helpful in finding the coordinates.
# 
# > **Alternatively** run `%matplotlib notebook` in a cell. Afterwards, every time you use something like `camelot.plot(tables[0]).show()` it will get you nice zoomable, hoverable versions that include `x` and `y` coordinates as you move your mouse.
# 
# Coordinates are given as `"left_x,top_y,right_x,bottom_y"` with `(0,0)` being in the bottom left-hand corner.
# 
# Note that all coordinates are strings, for some reason. It won't be `[1, 2, 3, 4]` it will be `['1,2,3,4']`
# 
# # Camelot questions
# 
# The largest part of this assignment is **mostly Camelot work**. As tabular data is usually the most typical data you'll be working with, it's what I'm giving you!
# 
# It will probably be helpful to read through [Camelot's advanced usage tips](https://camelot-py.readthedocs.io/en/master/user/advanced.html), along with the notebook I posted in the homework assignment.
# 
# ## Prison Inmates
# 
# Working from [InmateList.pdf](InmateList.pdf), save a CSV file that includes every inmate.
# 
# * Make sure your rows are *all data*, and you don't have any people named "Inmate Name."
# 

# In[70]:


import camelot
import pandas as pd

get_ipython().run_line_magic('matplotlib', 'notebook')

# Read every page of PDF in camelot
tables = camelot.read_pdf('InmateList.pdf', flavor="stream", pages="all")


# In[71]:


# Get coordinates (top left x, top left y, bottom right x, bottom right y)
camelot.plot(tables[0]).show()


# In[74]:


# Read all pages of PDF into camelot with x, y coordinates in table_areas
tables = camelot.read_pdf('InmateList.pdf', pages= 'all', flavor= 'stream', table_areas=['18, 714, 373, 60'])

# Convert each page into a dataframe. Returns a list of dataframes, one per page
dfs = [table.df for table in tables]

# Concatenate all dataframes from dfs into one df
df = pd.concat(dfs, ignore_index=True)

# Rename the columns
df = df.rename(columns={
    0: 'icn',
    1: 'inmate_name',
    2: 'facility',
    3: 'booking date'
})

df.head()


# In[76]:


df.info()


# In[77]:


df[df.inmate_name == 'Inmate Name']


# In[78]:


df.to_csv('inmates.csv', index=False)


# ## WHO resolutions
# 
# Using [A74_R13-en.pdf](A74_R13-en.pdf), what ten member countries are given the highest assessments?
# 
# * You might need to have two separate queries, and combine the results: that last page is pretty awful!
# * Always rename your columns
# * Double-check that your sorting looks right......
# * You can still get the answer even without perfectly clean data

# In[80]:


tables = camelot.read_pdf('A74_R13-en.pdf', flavor="stream", pages="all")


# In[83]:


camelot.plot(tables[5]).show()


# In[84]:


# Extract the row 3 onwards from first five pages
part_1 = [table.df.iloc[3: , :] for table in tables[0:5]]

# Concatenate first five pages
part_1 = pd.concat(part_1, ignore_index=True)

# Rename columns
part_1 = part_1.rename(columns = 
                       {0: 'members_and_associate_members',
                        1: 'who_scale_2223'})


# In[85]:


# Page 6 is a mess
# Extract rows 4 and 5, and columns 1-3
# Then limit to columns 1 and 3
part_2 = tables[5].df.iloc[4:6 , 1:4][[1, 3]]

# Rename columns to watch dfs
part_2 = part_2.rename(columns = {1: 'members_and_associate_members',
                          3: 'who_scale_2223'})


# In[86]:


# Concatenate dfs and p6
df = pd.concat([part_1, part_2])

df.who_scale_2223 = pd.to_numeric(df.who_scale_2223, errors = 'coerce')


# Answering the question: **what ten member countries are given the highest assessments?**

# In[87]:


df.sort_values('who_scale_2223', ascending=False).head(10)


# ## The Avengers
# 
# Using [THE_AVENGERS.pdf](THE_AVENGERS.pdf), approximately how many lines does Captain America have as compared to Thor and Iron Man?
# 
# * Character names only: we're only counting `IRON MAN` as Iron Man, not `TONY`.
# * Your new best friend might be `\n`
# * Look up `.count` for strings

# N.B. I originally attempted this question with Camelot, but found PDF Miner much more straightforward!

# In[97]:


from pdfminer.high_level import extract_text

text = extract_text('THE_AVENGERS.pdf')

avengers = pd.Series(text)

captain_america_count = avengers.str.count(r'\nCAPTAIN\sAMERICA?(\s\(V.O\))?\n').sum()

iron_man_count = avengers.str.count(r'\nIRON\sMAN?(\s\(V.O\))?\n').sum()

thor_count = avengers.str.count(r'\nTHOR?(\s\(V.O\))?\n').sum()

print(f'Captain America has {captain_america_count} lines including voiceovers.')
print(f'Thor has {thor_count} lines including voiceovers.')
print(f'Iron Man has {iron_man_count} lines including voiceovers.')


# ## COVID data
# 
# Using [covidweekly2721.pdf](covidweekly2721.pdf), what's the total number of tests performed in Minnesota? Use the Laboratory Test Rates by County of Residence chart.
# 
# * You COULD pull both tables separately OR you could pull them both at once and split them in pandas.
# * Remember you can do things like `df[['name','age']]` to ask for multiple columns

# In[98]:


tables = camelot.read_pdf('covidweekly2721.pdf', flavor="stream", pages="6")

camelot.plot(tables[0]).show()


# In[99]:


table_coords = '459.4, 576.2, 785, 24'

tables = camelot.read_pdf('covidweekly2721.pdf', pages= '6', flavor= 'stream', table_areas=[table_coords])


# In[103]:


part_1 = tables[0].df[[0, 1, 2]]

part_1.columns = part_1.loc[0]

part_1 = part_1.drop(0)

# Drop the empty row
part_1 = part_1.drop(6)

# Manually fill in a missing value
part_1.iloc[4, 2] = '19,574'

part_1.head()


# In[107]:


part_2 = tables[0].df[[3, 4, 5]]

part_2.columns = part_2.loc[0]

part_2 = part_2.drop(0)

# Drop the empty row
part_2 = part_2.drop(6)

part_2.head()


# In[108]:


df = pd.concat([part_1, part_2], ignore_index=True)

df['Number of Tests'] = df['Number of Tests'].str.replace(',', '')

total_tests = df['Number of Tests'].astype('int').sum()

print(f'The total number of tests performed in Minnesota is {total_tests:,}')


# ## Theme Parks
# 
# Using [2019-Theme-Index-web-1.pdf](2019-Theme-Index-web-1.pdf), save a CSV of the top 10 theme park groups worldwide.
# 
# * You can clean the results or you can restrict the area the table is pulled from, up to you

# In[111]:


tables = camelot.read_pdf('2019-Theme-Index-web-1.pdf', flavor="stream", pages="11")

camelot.plot(tables[0]).show()


# In[112]:


table_coords = '37.7, 460.6, 400.1, 295.6'

tables = camelot.read_pdf('2019-Theme-Index-web-1.pdf', pages= '11', flavor= 'stream', table_areas=[table_coords])


# In[113]:


theme_parks = tables[0].df
theme_parks


# In[114]:


theme_parks = theme_parks.rename(columns = {
    0: 'rank',
    1: 'group_name',
    2: 'pc_change',
    3: 'attendance_2019',
    4: 'attendance_2018'
})

theme_parks.attendance_2019 = theme_parks.attendance_2019.str.replace(',', '').astype('int')
theme_parks.attendance_2018 = theme_parks.attendance_2018.str.replace('\*|\,', '', regex=True).astype('int')

theme_parks['pc_change'] = ((theme_parks.attendance_2019 - theme_parks.attendance_2018) / theme_parks.attendance_2018) * 100

theme_parks


# In[115]:


theme_parks.to_csv('theme_parks.csv', index=False)


# ## Hunting licenses
# 
# Using [US_Fish_and_Wildlife_Service_2021.pdf](US_Fish_and_Wildlife_Service_2021.pdf) and [a CSV of state populations](http://goodcsv.com/geography/us-states-territories/), find the states with the highest per-capita hunting license holders.

# In[117]:


tables = camelot.read_pdf('US_Fish_and_Wildlife_Service_2021.pdf', flavor="stream")

df = tables[0].df

df = df.copy().loc[5:60, 0:1]

df = df.rename(columns = {0: 'state',
                          1: 'license_holders'})

df.license_holders = df.license_holders.replace('\,', '', regex=True).astype('int')

df.head()


# In[118]:


get_ipython().system("wget 'http://goodcsv.com/wp-content/uploads/2020/08/us-states-territories.csv'")


# In[152]:


states = pd.read_csv('us-states-territories.csv', encoding = 'unicode_escape')

states = states.rename(columns = {'Abbreviation': 'state',
                                  'Population (2019)': 'population'})

states = states[['state', 'population']]

states.state = states.state.str.replace(" ", "")

states = states[(states.state.isin(df.state)) & states.population.notnull()]

states.population = states.population.str.replace(',', '').astype('int')

states.head()


# In[155]:


merged = df.merge(states, on='state', how='left')

merged['licenses_per_capita'] = merged.license_holders / merged.population

merged.sort_values('licenses_per_capita', ascending=False).head(10)


# # Not-Camelot questions
# 
# You can answer these without using Camelot.

# ## Federal rules on assault weapons
# 
# Download all of the PDFs from the Bureau of Alcohol, Tobacco, Firearms and Explosives's [Rules and Regulations Library](https://www.atf.gov/rules-and-regulations/rules-and-regulations-library). Filter for a list of all PDFs that contain the word `assault weapon` or `assault rifle`.
# 
# > If you're having trouble scraping, maybe someone will be kind enough to drop a list of PDF urls in Slack?

# In[157]:


### Part 1: Scrape the URLs of PDFs


# In[156]:


from bs4 import BeautifulSoup
import requests

url = 'https://www.atf.gov/rules-and-regulations/rules-and-regulations-library'

r = requests.get(url)

bs = BeautifulSoup(r.text)

# Find the number of the last page for use in a while loop
last_page = bs.select_one('.pager-last a')['href']
last_page = int(last_page.split('page=')[1])

# Empty list for dictionary of pdf urls
pdfs = []

page_no = 0

while page_no <= last_page:
    
    url = f'https://www.atf.gov/rules-and-regulations/rules-and-regulations-library?page={page_no}'
    
    r = requests.get(url)

    bs = BeautifulSoup(r.text)

    links = bs.select('.views-field-name a')

    for link in links[1:]:
        pdf_name = link.text.strip()
        pdf_url = 'https://www.atf.gov' + link['href']
        
        pdf = {'name': pdf_name,
               'url': pdf_url
        }
        pdfs.append(pdf)
    
    print(f'Scraped {url}')
            
    page_no += 1


# In[159]:


import re

counter = 1

for pdf in pdfs:
    pdf_url = pdf['url']
    file_no = re.findall('file/(.*)/download', pdf_url)[0]
    file_name = f'{file_no}.pdf'
    file_dir = 'pdfs/'
    
    with open(f'{file_dir}/{file_name}', 'wb') as file:
        data = requests.get(pdf_url)
        file.write(data.content)
        
        print(f'{counter}. {file_name} SAVED!')
        counter += 1


# In[ ]:


import os
from pdfminer.high_level import extract_text

path = 'pdfs/'
files = os.listdir(path)

df_list = []

for file in files:   
    if file.endswith('.pdf'):
        text = extract_text(f'{path}{file}')
        
        df_dict = {
            'filename': file,
            'text': text
        }
        
        df_list.append(df_dict)
    
df = pd.DataFrame(df_list)


# In[162]:


df[df.text.str.contains('assault weapon|assault rifle', case=False)]


# ## New immigration judge training materials
# 
# Extract the text from [this 2020 guide for new immigration judges](2020-training-materials-2a-201-300.pdf) and save it as a file called `training-material.txt`.
# 
# > I took this PDF from [a FOIA request](https://www.muckrock.com/foi/united-states-of-america-10/most-recent-new-immigration-judge-training-materials-120125/#comms) – but the unfortunate thing is *I actually had to remove the OCR layer to make it part of this assignment*. By default everything that goes through Muckrock gets all of the text detected!

# In[163]:


import tika
from tika import parser

headers = {
            "X-Tika-PDFextractInlineImages": "true",
        }
parsed = parser.from_file('2020-training-materials-2a-201-300.pdf', xmlContent=False, requestOptions={'headers': headers, 'timeout': 300})

data = parsed['content']

white_space = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
data = data.replace(white_space, '').strip()

with open('training-material.txt', 'w') as f:
    f.write(data)


# In[ ]:




