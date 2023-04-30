# ELT_Python_Data_Warehouse
Python, SSMS, Data model, SQL, StarNet, SSAS, PowerBI, SSDT, Association Rule Mining, ARCGIS, JSON

A collection of crime data from the Atlanta Police Department's open data portal. This is an aggregation of city-wide data for every month between January 2009 and February 2017:
http://opendata.atlantapd.org/
The dataset includes 1/1/2009 - 2/28/2017. It is in csv format with 270688 rows.


Python was used to transform the orginal raw data into several dimension table, fact table , in order to build data warehouse for visualisation in Power BI.

Multiple JSON files were downloaded from interactive maps to pull beat, zone infomation.  
https://atlantapd.maps.arcgis.com/apps/webappviewer/index.html?id=e891b9b618a747a795d2f609a349ee7b

Some statistic data has also been added for extra demographic info for each NPU (Neighbourhood Planning Unit) https://opendata.atlantaregional.com/datasets/d6298dee8938464294d3f49d473bcf15_196/about

Load data into SSMS server, build MOLAP in SSAS, cube deployment, hierachy desgin.

Visualisation in PowerBI, association rule mining. Identify top rules.

