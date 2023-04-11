#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pathlib import Path
import csv
import pandas as pd
import geopandas as gpd
import glob
#from shapely.geometry import Polygon, mapping
from shapely.geometry import Point
import numpy as np
#from shapely.geometry.polygon import Polygon


# In[2]:


parent_path = Path.cwd().parent


# In[3]:


CRIME_DATA = "crime.CSV"


# In[4]:


#parse_dates=['date']
with open (parent_path/CRIME_DATA, newline = '') as file:
    crime_df = pd.read_csv(file, skipinitialspace=True)
    
crime_df.tail(10)


# In[5]:


crime_df.dtypes
# dtype = {'beat': int}


# In[6]:


#chop off the rows without being enriched
crime_df_final = crime_df.loc[~crime_df['state'].isnull(), ]


# In[7]:


#drop the unnamed row
crime_df_final = crime_df_final.drop('Unnamed: 0', axis=1)


# In[9]:


#locate other files
extra_csv_files = glob.glob( str(parent_path) + '/**/*.csv')
extra_csv_files


# In[10]:


#combined all the other files
extra_csv_concat = pd.concat([pd.read_csv(file,skipinitialspace=True) for file in extra_csv_files ], ignore_index=True)
extra_csv_concat.tail()


# In[11]:


#one of csv file: 50000-75000 has extra columns
sum(~extra_csv_concat.iloc[:,-1].isnull())


# In[12]:


extra_csv_concat.loc[~extra_csv_concat.iloc[:,-1].isnull(), : ]


# In[13]:


#drop index number columns
extra_csv_concat = extra_csv_concat.drop('Unnamed: 0', axis=1)
extra_csv_concat = extra_csv_concat.drop('Unnamed: 0.1', axis=1)
extra_csv_concat


# In[14]:


crime_df_final = pd.concat([crime_df_final, extra_csv_concat])


# In[15]:


#combine all the file - 225001 rows × 17 columns in total
crime_df_final


# In[ ]:





# In[16]:


#read in JSON file for the zone alignment
zone_df = gpd.read_file('https://services3.arcgis.com/Et5Qfajgiyosiw4d/arcgis/rest/services/2019_Zone_Alignment/FeatureServer/0/query?where=1=1&outFields=*&f=geojson')


# In[17]:


#check dataframe
zone_df[['ZONE','geometry']]


# In[18]:


#create the point object for the data set, then populating the matched the zone info from JSON file
crime_df_final['coordinates'] = [Point(xy) for xy in zip(crime_df_final.long, crime_df_final.lat)] 

for i in range (len(zone_df.index)) :
    zone_mask = (zone_df['geometry'][i].contains(crime_df_final['coordinates']))
    crime_df_final.loc[zone_mask,['Zone']] = zone_df['ZONE'][i]



crime_df_final


# In[19]:


#check geometry boundary
zone_df.geometry[0].boundary


# In[20]:


#check geometry
zone_df['geometry'][3]


# In[21]:


#read in JSON file for the beat alignment
beat_df = gpd.read_file('https://services3.arcgis.com/Et5Qfajgiyosiw4d/arcgis/rest/services/2019_Beat_Alignment/FeatureServer/0/query?where=1=1&outFields=*&f=geojson')


# In[22]:


# populating the matched beat info from JSON file
for i in range (len(beat_df.index)) :
    beat_mask = (beat_df['geometry'][i].contains(crime_df_final['coordinates']))
    crime_df_final.loc[beat_mask,['Beat_2']] = beat_df['BEAT'][i]

crime_df_final


# In[23]:


#read in JSON file for the airport beat alignment
airport_beat_df = gpd.read_file('https://services3.arcgis.com/Et5Qfajgiyosiw4d/ArcGIS/rest/services/Airport_Beats/FeatureServer/0/query?where=1=1&outFields=*&f=geojson')
airport_beat_df


# In[24]:


# populating the matched airport beat info from JSON file
for i in range (len(airport_beat_df.index)) :
    beat_mask = (airport_beat_df['geometry'][i].contains(crime_df_final['coordinates']))
    crime_df_final.loc[beat_mask,['Beat_2']] = airport_beat_df['NAME'][i]

crime_df_final


# In[25]:


#example of all the discrepency in location columns
example = crime_df_final.loc[(crime_df_final["lat"]==33.62522)&(crime_df_final["long"]==-84.43082)]

example


# In[26]:


#convert to appropriate type for processing 
#crime_df_final["beat"].str.strip()
#crime_df_final ["beat"] = crime_df_final ["beat"].replace (" " , "")
crime_df_final ["beat"] = crime_df_final["beat"].fillna(0)
crime_df_final = crime_df_final.astype({"beat":'int'})
crime_df_final ["Beat_2"] = crime_df_final["Beat_2"].fillna(0)
crime_df_final = crime_df_final.astype({"Beat_2":'int'})


# In[27]:


#only 74 rows of data's beat info haven't been enriched by JSON file, however they all have orginal beat data, except for 1 row
crime_df_final [crime_df_final["Beat_2"] == 0] 


# In[ ]:


crime_df_final.dtypes


# In[28]:


#upon checking ,orginal beat data has a lot less accuracy comparing with the new beat data enriched from JSON file. also lots of comfusion between beat 50 / beat 700s
difference_mask = crime_df_final["beat"] != crime_df_final["Beat_2"]
sum(difference_mask)


# In[29]:


crime_df_final[difference_mask]


# In[30]:


#74 entries of data without newly enriched beat info from JSON file
crime_df_final [crime_df_final["Beat_2"] == 0]["Beat_2"] 


# In[31]:


#populated all these empty entry with orginal beat info. 
crime_df_final["Beat_2"] = np.where(crime_df_final["Beat_2"] == 0, crime_df_final["beat"], crime_df_final["Beat_2"])


# In[32]:


#only one row has no beat file in both beat columns, out of 225001 rows, 
crime_df_final [crime_df_final["Beat_2"] == 0]


# In[33]:


crime_df_final = crime_df_final[crime_df_final.Beat_2 != 0]


# In[34]:


crime_df_final


# In[35]:


# 125 rows has no zone info . 
crime_df_final ["Zone"] = crime_df_final["Zone"].fillna(0)
crime_df_final = crime_df_final.astype({"Zone":'int'})
crime_df_final [crime_df_final["Zone"] == 0]


# In[36]:


## fill in missing zone data based on beat info from beat_2 column, floor division. for example. beat 201 --- zone 2. 
## Lots of them due to boarder classification issue
crime_df_final["Zone"] = np.where(crime_df_final["Zone"] == 0, crime_df_final["Beat_2"]//100, crime_df_final["Zone"])


# In[37]:


crime_df_final[crime_df_final["number"] == 130460779]


# In[38]:


#checking both zone and beat_2 columns have info in every row
crime_df_final.loc[(crime_df_final["Zone"] == 0) | (crime_df_final["Beat_2"] == 0 )]


# In[39]:


#drop the original beat column
crime_df_final = crime_df_final.drop('beat', axis=1,errors='ignore')


# In[40]:


crime_df_final.head()


# In[41]:


# factorise, assign surrogate key to coordinates tuple 
crime_df_final['coordinate_ID'] = pd.factorize(list(zip(crime_df_final.lat.values, crime_df_final.long.values)))[0]+1
crime_df_final

#checking how many unique coordinates tuples locations
crime_df_final['coordinate_ID'].nunique()
crime_df_final['coordinates'].nunique()
#samples of factorize and group by syntax in python
#df['ID']=pd.factorize(df['Name'])[0]+1
#df
#codes,unique = pd.factorize(df['Name'])
#x = df.groupby["Name","Phone"]
#unique
#sql1=df[['ID','S1','S2','S3']]
#sql2=df[['ID','Name','Phone']].drop_duplicates()
#sql1


# In[42]:


crime_df_final.head()


# In[43]:


#checking npu column info
len(crime_df_final[crime_df_final['npu'].isnull()])    


# In[44]:


crime_df_final['npu'].unique()


# In[45]:


crime_df_final['type'].unique()


# In[46]:


#2039 rows has no city info
sum(crime_df_final['city'].isnull())


# In[47]:


#checking the city info, only 1 entry is "Snady Springs", the rest are Atlanta or Null
crime_df_final[(crime_df_final['city'] != "Atlanta") & (crime_df_final['city'].notnull())]


# In[48]:


#made decision to assign Atlanta to all the empty city cell, they are all from 700 airport zone 7, technically they don't belong to Atlanta city from the map, however a lot more other airport zone location has been assigned 
#with Atlanta info already. plus the data set description demonstrated it is crime data from Atlanta city.  
crime_df_final['city'] = np.where((crime_df_final['city'] != "Atlanta") | (crime_df_final['city'].isnull()), "Atlanta", crime_df_final['city'])


# In[49]:


crime_df_final[(crime_df_final['city'] != "Atlanta") | (crime_df_final['city'].isnull())]


# In[ ]:





# In[ ]:


#address_dim = crime_df_final[["coordinate_ID","Beat_2","Zone","city","county","state"]].drop_duplicates()


# In[ ]:


#sql2=df[['ID','Name','Phone']].drop_duplicates()


# In[50]:


#assign address info to address_dimension table, however not all these will be in the address dimension table, just to 
#clean the data a bit more, as one single coordinate_ID should only have one NPU, TYPE, BEAT, ROAD, ZONE info etc....
address_dim = crime_df_final[["coordinate_ID","lat","long","npu","type","Beat_2","road","Zone","city","county","state"]].drop_duplicates()
address_dim


# In[51]:


#103 pairs of duplicates, out of 63699 difference location, has discrepency info under same corodinates, pretty clean already. 
address_dim[address_dim.duplicated(subset=['coordinate_ID'])]


# In[52]:


# to demostrate 103x2 = 206 rows of info discrepancy , same coordinates, but various different info 
ids = address_dim["coordinate_ID"]
duplicates = address_dim[ids.isin(ids[ids.duplicated()])].sort_values("coordinate_ID")
duplicates


# In[ ]:


"""#crime_df_final[crime_df_final["coordinate_ID"] == 28794]
#crime_df_final["Beat_2"] = np.where(crime_df_final["coordinate_ID"] == 28794, 612, crime_df_final["Beat_2"])
#address_dim = crime_df_final[["coordinate_ID","lat","long","npu","type","type_ID","Beat_2","road","Zone","city","county","state"]].drop_duplicates()
#address_dim"""


# In[ ]:


"""ids = address_dim["coordinate_ID"]
duplicates = address_dim[ids.isin(ids[ids.duplicated()])].sort_values("coordinate_ID")
duplicates
#~ids.duplicated()"""


# In[53]:


#made decision to delete descrepency rows, as that is only 0.3% of all the coordinates has some sort of confilct location info. 
address_dim = address_dim[~ids.duplicated()]


# In[54]:


#63699 clean unique rows of different lat,long tuple. with respective info.
address_dim


# In[ ]:


"""#creating final house_type_dim table
house_type_dim = address_dim[["type_ID","type"]].drop_duplicates()
house_type_dim"""
"""address_dim = address_dim.drop('type', axis=1)"""
"""address_dim = address_dim.drop('type_ID', axis=1)"""


# In[55]:


address_dim


# In[56]:


address_dim["road"].isnull().values.any()


# In[57]:


date = crime_df_final["date"].unique()


# In[58]:


len(date)


# In[59]:


date[:5]


# In[60]:


date_dataframe = pd.to_datetime(date)
date_dataframe
date_dataframe.sort_values()


# In[67]:


#Define a date function to create date dimension table
def create_date_table2(start='2009-01-01', end='2017-12-31'):
    df = pd.DataFrame({"Date": pd.date_range(start, end)})
    df["Day_of_week"] = df.Date.dt.dayofweek
    df["Day"] = df.Date.dt.day_name()
    df['Weekday_Weekend'] = np.where((df['Day_of_week']) < 5,"Weekday","Weekend")
    df["Week"] = df.Date.dt.isocalendar().week
    df["Month"] = df.Date.dt.month_name().str.slice(stop=3)
    df["Quarter"] = df.Date.dt.quarter
    df["Year"] = df.Date.dt.year
    #df["Is Weekend"] = df.Date.dt.dayofweek > 4
    return df


# In[68]:


date_dim = create_date_table2()
date_dim["Date_id"] =date_dim['Date'].dt.strftime('%Y%m%d')
date_dim_1 = date_dim.reindex(columns=['Date_id', 'Date', 'Day','Weekday_Weekend','Week','Month','Quarter','Year'])


# In[69]:


date_dim_1


# In[70]:


#Found neiboughood JSON file too, use this formal Json file to update the neiboughood column as lots of info were missing
neighborhood_df = gpd.read_file('https://gis.atlantaga.gov/dpcd/rest/services/OpenDataService/FeatureServer/3/query?where=1=1&outFields=*&f=geojson')
neighborhood_df


# In[71]:


neighborhood_df.geometry[3]


# In[72]:


address_dim['point_obj'] = [Point(xy) for xy in zip(address_dim.long, address_dim.lat)] 

for i in range (len(neighborhood_df.index)) :
    neighborhood_mask = (neighborhood_df['geometry'][i].contains(address_dim['point_obj']))
    address_dim.loc[neighborhood_mask,['Neighborhood']] = neighborhood_df['NAME'][i]


address_dim


# In[74]:


address_dim_final = address_dim [["coordinate_ID","lat","long","type","road","Beat_2","Zone","Neighborhood","npu","city","county","state"]]
address_dim_final


# In[75]:


crime_df_final["crime"].unique()


# In[76]:


sum(address_dim_final["Neighborhood"].isnull())


# In[77]:


address_dim_final["Neighborhood"].nunique()


# In[78]:


sum(address_dim_final["npu"].isnull())


# In[79]:


sum(address_dim_final["Beat_2"].isnull())


# In[80]:


sum(address_dim_final["Zone"].isnull())


# In[81]:


sum(address_dim_final["road"].isnull())


# In[85]:


# use stats data downloaded from Georgia Gov to add in a bit more info regarding the NPU demographic. 
STATS_DATA = "City_of_Atlanta_Neighborhood_Statistical_Areas.csv" 


# In[86]:


with open (parent_path/STATS_DATA, newline = '') as file:
    stats_df = pd.read_csv(file, skipinitialspace=True)
    
stats_df.head(10)


# In[ ]:


"""demo_df = pd.pivot_table(stats_df,
                         index=['NPU'],
                         aggfunc={'pop': np.sum, 'white': np.sum, 'black': np.sum,'asian': np.sum,'other': np.sum,'hispanic': np.sum, 'STATISTICA': len}).rename(columns={'STATISTICA': 'count'})
"""


# In[88]:


# as below shows, the data divided the NPU into smaller suburb groups. So just need to convert each small group
# percentage into population, then recaculate the demographic info for each suburb 
stats_df ["white"] = stats_df ["white"]/100*stats_df["pop"]
stats_df ["black"] = stats_df ["black"]/100*stats_df["pop"]
stats_df ["asian"] = stats_df ["asian"]/100*stats_df["pop"]
stats_df ["other"] = stats_df ["other"]/100*stats_df["pop"]
stats_df ["hispanic"] = stats_df ["white"]/100*stats_df["pop"]

stats_df


# In[89]:


#group each smaller suburbs, which belongs to the same NPU, in order to recaculate the percentage for each NUP
demo_df = pd.pivot_table(stats_df,
                         index=['NPU'],
                         aggfunc={'pop': np.sum, 'white': np.sum, 'black': np.sum,'asian': np.sum,'other': np.sum,'hispanic': np.sum, 'STATISTICA': len}).rename(columns={'STATISTICA': 'count'})

demo_df.iloc[:, 1:] = demo_df.iloc[:, 1:].div(demo_df['pop'], axis=0).mul(100).round(2)
demo_df


# In[90]:


# simple classfication to check the people of colour (POC) percentage in each NPU
def demo_filter(x):
    if x > 75:
        return "(0%...25%]"
    elif x > 50:
        return "(25%...50%]"
    elif x > 25:
        return "(50%...70%]"
    else:
        return "(75%...100%]"
    


# In[91]:


demo_df["NPU_POC_Pop_Pct"] = demo_df["white"].apply(demo_filter)


# In[92]:


demo_df=demo_df.reset_index()


# In[93]:


demo_df


# In[94]:


demo_df_final = demo_df[["NPU","NPU_POC_Pop_Pct"]]


# In[95]:


demo_df_final["NPU"] = demo_df_final["NPU"].str[-1:]


# In[96]:


demo_df_final


# In[97]:


#merge this info into address dimention table , by using left join. 
address_dim_final_1 = pd.merge(left=address_dim_final, right=demo_df_final, how='left', left_on='npu', right_on='NPU')


# In[98]:


address_dim_final_1.drop('NPU', axis=1, inplace=True)


# In[99]:


address_dim_final_1.rename(columns={'Beat_2':'beat', "Zone":"zone", "Neighborhood":"neighborhood","NPU_POC_Pop_Pct":"npu_poc_pop_pct"}, inplace=True)


# In[100]:


address_dim_final_1


# In[101]:


#export address dimension table
address_dim_final_1.to_csv('coordinate_dim.csv',index=False,header=False, sep='|')


# In[102]:


#export date dimension table
date_dim_1.to_csv('date_dim.csv',index=False,header=False,sep='|')


# In[103]:


#convert date column into datetime object
crime_df_final['date'] = crime_df_final['date'].astype('datetime64[ns]')


# In[104]:


#create a datekey for fact table, same formate with date dimension table
crime_df_final['date_ID'] = crime_df_final['date'].dt.strftime('%Y%m%d')
crime_df_final


# In[105]:


#factorize crime type
crime_df_final['crime_ID'] = pd.factorize(crime_df_final["crime"])[0]+1
crime_df_final


# In[106]:


# create crime type dimension table
crime_type_dim_1 = crime_df_final[['crime_ID','crime']].drop_duplicates()
crime_type_dim_1.crime = crime_type_dim_1.crime.str.title()


# In[107]:


crime_type_dim_1


# In[108]:


#adding another column to better classfy crime type
crime_type_dim_1["crime_against"] = ["Property","Persons","Property","Persons","Property","Persons","Property","Property","Persons","Persons","Persons",]


# In[109]:


crime_type_dim_1


# In[110]:


#export crime type dimension table to csv file
crime_type_dim_1.to_csv("crime_type_dim.csv",index=False,header=False,sep='|')


# In[ ]:


#df['ID']=pd.factorize(df['Name'])[0]+1
#df
#codes,unique = pd.factorize(df['Name'])

#x = df.groupby["Name","Phone"]
#unique
#sql1=df[['ID','S1','S2','S3']]
#sql2=df[['ID','Name','Phone']].drop_duplicates()
#sql1


# In[ ]:





# In[111]:


#finally create crime fact table
crime_fact = crime_df_final.reindex(columns=['Blank','date_ID', 'coordinate_ID','crime_ID'])


# In[112]:


crime_fact


# In[113]:


crime_fact.dtypes


# In[114]:


crime_fact.isnull().sum()


# In[115]:


crime_type_dim_1.dtypes


# In[116]:


crime_type_dim_1.isnull().sum()


# In[117]:


address_dim_final_1.dtypes


# In[118]:


address_dim_final_1.isnull().sum()


# In[119]:


date_dim_1.dtypes


# In[120]:


date_dim_1.isnull().sum()


# In[121]:


crime_fact.to_csv("crime_fact.csv",index=False,header=False,sep='|')


# In[ ]:





# In[ ]:





# In[ ]:


#ignore below


# In[ ]:


"""point = Point([-84.38895, 33.77101])
count = 0
for i in range(len(zone_df.index)):
    if zone_df['geometry'][i].contains(point):
        count += 1            
for i in range(len(beat_df.index)):
    if  beat_df['geometry'][i].contains(point):
        count += 1 
        
count"""


# In[ ]:


#crime_df['coordinates'] = list(zip(crime_df["long"], crime_df["lat"]))
#crime_df

#zone_1 = (df['geometry'][1].contains(Point((-84.45058, 33.76722))))
#zone_1


# In[ ]:


#rating = []
#for row in crime_df['cord']:
#    for i in range(len(df.index)):
#        if df['geometry'][i].contains(crime_df['cord']):
#            rating.append(df['ZONE'][i])
#rating


# In[ ]:


#crime_data.loc[:,"crime"]


# In[ ]:


#import requests
#from bs4 import BeautifulSoup


# In[ ]:


#url = "https://atlantapd.maps.arcgis.com/apps/webappviewer/index.html?id=e891b9b618a747a795d2f609a349ee7b"
#response = requests.get(url)


# In[ ]:


#soup = BeautifulSoup (response.text, 'html.parser')


# In[ ]:


#soup


# In[ ]:


#url = 'https://atlantapd.maps.arcgis.com/apps/webappviewer/index.html?id=e891b9b618a747a795d2f609a349ee7b'
#headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
#response = requests.get(url, headers=headers)
#soup = BeautifulSoup(response.text, 'html.parser')
#soup

#scripts = soup.find_all('script')
#scripts


# In[ ]:


#beat_data = pd.read_json("https://services3.arcgis.com/Et5Qfajgiyosiw4d/arcgis/rest/services/2019_Zone_Alignment/FeatureServer/0/query?where=1=1&outFields=*&f=geojson")


# In[ ]:


#df.head()


# In[ ]:


#xx,yy = zone_df.loc[0,"geometry"].exterior.coords.xy
#list(xx)
#list(yy)


# In[ ]:


#zone_df[['ZONE','geometry']]


# In[ ]:


#mapping(zone_df.geometry[1])["coordinates"]


# In[ ]:


#zone_df.geometry


# In[ ]:


#a = []
#for i in zone_df['geometry']:
#    a.append(list([i.exterior.coords]))
    
#a


# In[ ]:


#list(zone_df['geometry'][1].exterior.coords)


# In[ ]:


#lon = [ round(i[0],5) for i in list(df['geometry'][1].exterior.coords)]
#lat = [ round(i[1],5) for i in list(df['geometry'][1].exterior.coords)]
#lon
#lat


# In[ ]:





# In[ ]:


"""point = Point([-84.44773, 33.62875])
for i in range(len(airport_beat_df.index)):
    print(airport_beat_df['geometry'][i].contains(point))"""


# In[ ]:


"""list(zone_df ['ZONE'])"""


# In[ ]:


"""beat_df['geometry'][7]"""


# In[ ]:


"""beat_df.loc[beat_df['BEAT']==50]"""


# In[ ]:


"""zone_df['geometry'][5]"""


# In[ ]:


#crime_df_final.to_csv('crime_df_final.csv')


# In[ ]:


'''with open (parent_path/CRIME_DATA, newline = '') as csvfile:
    reader = csv.reader(csvfile)
    for (index, row) in enumerate(reader):
        if index < 4:
            print(row)'''

