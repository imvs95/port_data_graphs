"""
Created on: 7-12-2023 10:52

@author: IvS
"""
import pandas as pd
import json
import copy

def check_optional_location(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            # If the value is a nested dictionary, recursively check it
            if check_optional_location(value):
                return True
        elif isinstance(value, str) and "OPTIONAL LOCATION" in value:
            # If the value is a string and contains "OPTIONAL LOCATION"
            return True
    return False

if __name__ == "__main__":
    # Import all
    df_all = pd.read_csv("data_av/20231206_combined_cnhk-us/extra_cnhk-us-ports.csv")

    # Filter on dates
    # df_all = df_all[
    #     (df_all['ScrapingDate'].str.contains('2023-11')) | (df_all['ScrapingDate'].str.contains('2023-12')) |
    #     (df_all['ScrapingDate'].str.contains('2023-01')) | (
    #         df_all['ScrapingDate'].str.contains('2023-02'))].reset_index(drop=True)

    #(df_all['ScrapingDate'].str.contains('2023-09')) | (df_all['ScrapingDate'].str.contains('2023-10')) |

    f = open("./data_av/port_codes_new.json")
    ports_av = json.load(f)

    def find_port_code_with_name(name):
        portcode = None
        for port in ports_av["Ports"]:
            name_port = port["LocationName"]
            if name in name_port or name_port in name:
                portcode = port["LocationCode"]
                # print(f"Found overlapping name: {name_port} and {name} with Portcode {portcode}")
        if portcode is None:
            if "OPTIONAL LOCATION" in name:
                return name
            else:
                print(f"Did not find overlapping name for: {name}")
        else:
            return portcode


    print(f"Total connections is {len(df_all)}")
    count_2m = 0
    count_other = 0

    df_all_new = copy.deepcopy(df_all)

    for index, row in df_all_new.iterrows():
        scrapingsite = row["ScrapingSite"]
        if (scrapingsite == "Maersk") or (scrapingsite == "MSC"):
            count_2m += 1
            continue

        elif (scrapingsite == "HMM") or (scrapingsite == "Evergreen"):
            count_other += 1
            num_legs = row["NumberOfLegs"]
            route_legs = eval(row["Legs"])
            route_legs_2 = route_legs.copy()
            for num, legs in route_legs.items():
                other_modalities = ["RAIL", "TRUCK"]
                # add the other modality if applicable
                if legs["vessel"]["vessel_name"] in other_modalities:
                    route_legs_2[num]["other_modality"] = legs["vessel"]["vessel_name"]

                elif legs["vessel"]["service"] == "Intermodal":
                    route_legs_2[num]["other_modality"] = "INTERMODAL"

                # when first leg
                if num == "1":
                    route_legs_2[num]["OriginPortCode"] = row["Origin"]

                    name_destination = legs["DestinationName"].split(", ")[0]
                    port_code_destination = find_port_code_with_name(name_destination)
                    route_legs_2[num]["DestinationPortCode"] = port_code_destination

                # when last leg
                elif num == str(num_legs):
                    name_origin = legs["OriginName"].split(", ")[0]
                    port_code_origin = find_port_code_with_name(name_origin)
                    route_legs_2[num]["OriginPortCode"] = port_code_origin

                    route_legs_2[num]["DestinationPortCode"] = row["Destination"]

                else:
                    name_origin = legs["OriginName"].split(", ")[0]
                    port_code_origin = find_port_code_with_name(name_origin)
                    route_legs_2[num]["OriginPortCode"] = port_code_origin

                    name_destination = legs["DestinationName"].split(", ")[0]
                    port_code_destination = find_port_code_with_name(name_destination)
                    route_legs_2[num]["DestinationPortCode"] = port_code_destination

            if check_optional_location(route_legs_2):
                filters_routes = {k: v for k, v in route_legs_2.items()
                                  if "OPTIONAL LOCATION" not in v["OriginName"] or
                                  "OPTIONAL LOCATION" not in v["DestinationName"]}
                sorted_routes = {str(i + 1): v for i, (k, v) in enumerate(filters_routes.items())}

                # reformat it for optional locations
                for key in sorted_routes:
                    current_entry = sorted_routes[key]
                    destination_name = current_entry['DestinationName']
                    # Check if 'OPTIONAL LOCATION' is present in the DestinationName
                    if 'OPTIONAL LOCATION' in destination_name:
                        next_key = str(int(key) + 1)
                        # Check if the next key exists in the dictionary
                        if next_key in sorted_routes:
                            next_entry = sorted_routes[next_key]
                            # Update the current entry with data from the next entry
                            current_entry['DestinationName'] = next_entry['OriginName']
                            current_entry['DestinationPortCode'] = next_entry['OriginPortCode']
                            current_entry['EstimatedArrivalTime'] = next_entry['EstimatedDepartureTime']

                df_all_new.at[index, "Legs"] = str(sorted_routes)

            else:
                df_all_new.at[index, "Legs"] = str(route_legs_2)
        else:
            print("No scraping site")
    print(f"Total with no changes is {count_2m}, total changes with {count_other}")

    df_all_new.to_csv("data_av/20231206_combined_cnhk-us/extra_cnhk-us-ports_new.csv")









