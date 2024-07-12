import pandas as pd
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import json
import time
import pickle


def string_to_datetime(str_time):
    try:
        date = datetime.strptime(str_time, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        try:
            date = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            date = datetime.strptime(str_time, '%Y-%m-%dT%H:%M:%SZ')
    return date


def construct_nodes(data, G):
    for index, row in data.iterrows():
        unique_name = row["Origin"] + row["EstimatedDepartureTime"] + row["Destination"] + row[
            "EstimatedArrivalTime"]

        prev_leg = None
        scrapingsite = row["ScrapingSite"]

        rows_legs = eval(row["Legs"])
        for num, leg in rows_legs.items():
            leg_attributes = leg
            leg_attributes["ScrapingSite"] = scrapingsite
            if (scrapingsite == "Maersk") or (scrapingsite == "MSC"):
                origin = leg["OriginName"].split("(")[-1][:-1]
                destination = leg["DestinationName"].split("(")[-1][:-1]
            elif (scrapingsite == "HMM") or (scrapingsite == "Evergreen"):
                origin = leg["OriginPortCode"]
                destination = leg["DestinationPortCode"]

            try:
                # this is possible because same time zone
                eta = string_to_datetime(prev_leg["EstimatedArrivalTime"][:19])
                etd = string_to_datetime(leg["EstimatedDepartureTime"][:19])
                processing_time = (etd - eta).total_seconds() / 60
                leg_attributes["ProcessingTimeMinutes"] = processing_time

            except TypeError:
                pass

            prev_leg = leg

            if origin not in G.nodes():
                multiple_routes = {unique_name: leg_attributes}
                G.add_node(origin, **multiple_routes)
                G.nodes[origin]["modality"] = "sea"
            else:
                G.nodes[origin][unique_name] = leg_attributes

            if destination not in G.nodes():
                G.add_node(destination)
                G.nodes[destination]["modality"] = "sea"

def construct_edges(G):
    # Add egdes
    node_list = []
    for node_r, attributes_r in G.nodes(data=True):
        for k_r, v_r in attributes_r.items():
            try:
                scrapingsite = v_r["ScrapingSite"]
                if (scrapingsite == "Maersk") or (scrapingsite == "MSC"):
                    edge = [(node_r, node, {"time_minutes": [(string_to_datetime(
                        v_r["EstimatedArrivalTime"]) - string_to_datetime(
                        v_r["EstimatedDepartureTime"])).total_seconds() / 60],
                                            "eta_destination": [string_to_datetime(v_r["EstimatedArrivalTime"])],
                                            "etd_origin": [string_to_datetime(v_r["EstimatedDepartureTime"])]})
                            for node, attributes in G.nodes(data=True) if
                            v_r["DestinationName"].split("(")[-1][:-1] == str(node)]

                elif (scrapingsite == "HMM") or (scrapingsite == "Evergreen"):
                    if "other_modality" in v_r:
                        edge = [(node_r, node, {"time_minutes": [(string_to_datetime(
                            v_r["EstimatedArrivalTime"]) - string_to_datetime(
                            v_r["EstimatedDepartureTime"])).total_seconds() / 60],
                                                "eta_destination": [string_to_datetime(v_r["EstimatedArrivalTime"])],
                                                "etd_origin": [string_to_datetime(v_r["EstimatedDepartureTime"])],
                                                "other_modality": [v_r["other_modality"]]})
                                for node, attributes in G.nodes(data=True) if
                                v_r["DestinationPortCode"] == str(node)]
                    else:
                        edge = [(node_r, node, {"time_minutes": [(string_to_datetime(
                            v_r["EstimatedArrivalTime"]) - string_to_datetime(
                            v_r["EstimatedDepartureTime"])).total_seconds() / 60],
                                                "eta_destination": [string_to_datetime(v_r["EstimatedArrivalTime"])],
                                                "etd_origin": [string_to_datetime(v_r["EstimatedDepartureTime"])]})
                                for node, attributes in G.nodes(data=True) if
                                v_r["DestinationPortCode"] == str(node)]

            except (KeyError, TypeError):
                pass

            if len(edge) > 0:
                node_list.append(edge[0])

    # Combine node in list for the edges
    unique_edges = list(set([(i[0], i[1]) for i in node_list]))

    edge_list = []
    for u in unique_edges:
        u_leg = [l for l in node_list if u == l[:2]]

        if len(u_leg) == 1:
            edge_list.append(u_leg[0])

        if len(u_leg) > 1:
            base_edge = u_leg[0]
            # Add others to the base edge
            new_u_leg = u_leg[1:]
            for route in new_u_leg:
                for k, v in base_edge[2].items():
                    v.append(route[2][k][0])
                    base_edge[2][k] = v

            edge_list.append(base_edge)
    G.add_edges_from(edge_list)


def set_port_locations(ports, G):
    # Plot nodes based on location
    for node, attributes in G.nodes(data=True):
        try:
            attributes["latitude"] = ports[node]["LocationLatitude"]
            attributes["longitude"] = ports[node]["LocationLongitude"]
        except KeyError:
            raise Warning("Port {0} cannot be found".format(node))

    position_ports = {k: (attr["longitude"], attr["latitude"]) for k, attr in G.nodes(data=True)}
    return position_ports

def create_list_origin_destination(df_all, name_list):
    list_origin = list(df_all["Origin"].unique())
    list_destination = list(df_all["Destination"].unique())

    lists_od = {"origin": list_origin,
                "destination": list_destination}  # Replace list_origin and list_destination with your actual lists

    for name, mylist in lists_od.items():
        filename = f"list_{name}_{name_list}.pkl"

        with open(filename, 'wb') as f:
            pickle.dump(mylist, f)


if __name__ == "__main__":
    # Import data and combine

    df_data = pd.read_csv("data_av/20231206_combined_cnhk-us/combined_cnhk-us_new.csv")
    # create_list_origin_destination(df_data, "cnhk_us_final")

    df_extra = pd.read_csv("data_av/20231206_combined_cnhk-us/extra_cnhk-us-ports_new.csv")
    df_data = pd.concat([df_data, df_extra]).reset_index(drop=True)

    start_time = time.time()
    # #Create graph
    G = nx.DiGraph()
    construct_nodes(df_data, G)
    time_nodes = time.time()
    print("Constructing nodes takes {0:.1f} seconds".format(time_nodes - start_time))
    construct_edges(G)
    print("Constructing edges takes {0:.1f} seconds".format(time.time() - time_nodes))

    # Import ports data
    f = open("data_av/msc_route_country_port_codes.json")
    port_locs = json.load(f)

    position_ports = set_port_locations(port_locs, G)

    # check which ports still need to be found: [name for name in list(G.nodes()) if name not in list(position_ports.keys())]

    with open("./graph_networkx_CNHK_USA_FINAL_route.pkl", "wb") as f:
        pickle.dump(G, f)

    start_time_plot = time.time()
    # Plot network
    plt.figure(figsize=(20, 10))
    nx.draw_networkx(G, pos=position_ports)
    plt.show()
