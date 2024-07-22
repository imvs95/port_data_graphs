Generating Graphs based on Real-World Port Data
==========================================================================================================
This repository is used to generate a graph of open-source sea and airport data. For this, open-source data of the shipping schedules given by MSC, Maersk, HMM, and Evergreen is used.
The data is collected from the websites of the shipping companies (see also https://github.com/EwoutH/shipping-data). The data is then processed to generate a graph of the shipping schedules, including the distributions of the shipping schedules. The graph is used to analyze the shipping schedules and to identify the most important ports in the network.
Airport data is collected from the open-source `OpenFlights <https://www.kaggle.com/datasets/open-flights/flight-route-database/>`_ database.

As case study, we collect data on CN-HK to main ports in the USA, and mostly MSC data on South America to NL-BE.

This repository is also part of the Ph.D. thesis of  `Isabelle M. van Schilt <https://www.tudelft.nl/staff/i.m.vanschilt/?cHash=74e749835b2a89c6c76b804683ffbbcf>`_, Delft University of Technology. The version of the code used in the Ph.D. thesis is available at doi: `10.4121/72e97df0-147c-4228-a1b4-8bb8e8461317.v1<https://doi.org/10.4121/72e97df0-147c-4228-a1b4-8bb8e8461317.v1>`_.
This repository is used for developing various graphs on open-source data and automatically running it as a simulation model in the repository: `complex_stylized_supply_chain_model_generator <https://github.com/imvs95/complex_stylized_supply_chain_model_generator>`_.

Content
=====================================================
This repository contains the following folders:

* *data_av*: Contains the data of the shipping schedules from August 2023 to February 2024, and the modified open-source data set of airports in 2017 (added Haversine distance between airports).
* *figures*: Contains the figures created for analysis of the graphs.

This repository contains the following files:

* *graph_networkx_CNHK_USA_FINAL_route.pkl*: Networkx graph of the shipping schedules of CN-HK to USA.
* *graph_networkx_CNHK_USA_FINAL_route_with_sea.pkl*: Networkx graph of the shipping schedules of CN-HK to USA, including the travel time distributions and air/sea data.
* *graph_networkx_SOUTHAMERICA_msc_route.pkl*: Networkx graph of the shipping schedules of MSC of South America to NL-BE. Graph upon request (Large File).
* *graph_networkx_SOUTHAMERICA_msc_route_with_distributions.pkl*: Networkx graph of the shipping schedules of MSC of South America to NL-BE, including the travel time distributions. Graph upon request (Large File).
* *list_destination_cnhk_us_final.pkl*: List of the destinations of the shipping schedules of CN-HK to USA.
* *list_origin_cnhk_us_final.pkl*: List of the origins of the shipping schedules of MSC of CN-HK to USA.

This repository contains the following scripts:

* *data_to_graph_networkx.py*: Script to generate a networkx graph of the data on shipping schedules and airports.
* *preprocessing_data.py*: Script to preprocess the data of the shipping schedules before generating a networkx graph.

This repository contains the following notebooks:

* *add_missing_port_locations.ipynb*: Manually adding the latitude and longitude of some ports.
* *combine_sea_air_CNHK_USA.ipynb*: Combining the sea graphs and air data of CN-HK to USA.
* *fit_distributions_traveltimes_and_add_air_CNHK_USA.ipynb*: Fitting the distributions of the travel times of the shipping data and adding the air data of CN-HK to USA.
* *fit_distributions_traveltimes_SOUTHAMERICA.ipynb*: Fitting the distributions of the travel times of the shipping data of South America to NL-BE.
* *network_analysis_visualize_data_CNHKUSA.ipynb*: Network analysis and visualization of the data of CN-HK to USA.
* *network_analysis_visualize_data_SOUTHAMERICA.ipynb*: Network analysis and visualization of the data of South America to NL-BE.
* *network_analysis_visualize_data_SOUTHAMERICA_Subset.ipynb*: Network analysis and visualization of the data of some port in South America (mainly Colombia) to NL-BE.
