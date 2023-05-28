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

![Screenshot 2023-05-28 121024](https://github.com/coffeemartin/ELT_Python_Data_Warehouse/assets/73702415/b3d3d50e-2914-4107-a4ca-96b60945bd33)
![Screenshot 2023-05-28 123716](https://github.com/coffeemartin/ELT_Python_Data_Warehouse/assets/73702415/4677bb7e-8a23-488b-93bb-dbd4423a4bc2)
![Screenshot 2023-05-28 123727](https://github.com/coffeemartin/ELT_Python_Data_Warehouse/assets/73702415/23079fbc-d59a-4e17-9685-fab9942f32fe)
![Screenshot 2023-05-28 123755](https://github.com/coffeemartin/ELT_Python_Data_Warehouse/assets/73702415/2122bff5-4346-4515-b8c3-3825b74c0c43)
![Screenshot 2023-05-28 123808](https://github.com/coffeemartin/ELT_Python_Data_Warehouse/assets/73702415/d0008a12-17ed-4625-827c-6a528c1330bb)
