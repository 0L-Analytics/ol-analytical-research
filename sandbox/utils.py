import requests
import csv
from typing import List, AnyStr, Dict
import json
import networkx as nx


def build_graph(G, node, data, gen_depth=0, parent=None, epoch=0):
    """Recursive function to build the graph of a hierarchy"""
    # Add the node to the graph
    G.add_node(node, epoch_onboarded=epoch, generation=gen_depth)
    
    # If the node has a parent, add an edge between the node and its parent
    if parent:
        G.add_edge(node, parent)
    
    # If the node has children, call the build_graph function for each child
    children = data.get(node, {}).get("children", [])
    for child in children:
        build_graph(G, child['address'], data, gen_depth + 1, node, child['epoch_onboarded'])


def depth_of_hierarchy(data: Dict, parent:AnyStr=None, depth:int=0) -> int:
    """
    A recursive function that calculates the depth of the hierarchical data.
    """
    if not data:
        return 0
    
    max_depth = depth

    if not parent:
        # top level recursion loop
        for current_validator_address in data:
            child_depth = depth_of_hierarchy(data, data[current_validator_address]['parent'], depth + 1)
            max_depth = max(max_depth, child_depth)
    elif parent == '00000000000000000000000000000000':
        max_depth = max(max_depth, depth)
    else:
        child_depth = depth_of_hierarchy(data, data[parent]['parent'], depth + 1)
        max_depth = max(max_depth, child_depth)
    
    return max_depth


def load_addresses_list(path) -> list:
    """
    Read in csv of address keys
    Output a list, ready for querying API of explorer
    """
    all_addresses = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            all_addresses.append(row[0])
    return all_addresses


def get_validator_addresses(in_active_set: bool=False) -> List:
    active_set_list = []

    try:
        if in_active_set:
            api_url = "https://0lexplorer.io/api/webmonitor/vitals"
            result = requests.get(api_url, timeout=10).json()
            active_set_list = [validator['account_address'] for validator in result['chain_view']['validator_view']]
        else:
            api_url = "https://0lexplorer.io:444/balances?account_type=validator"
            result = requests.get(api_url, timeout=300).json()
            active_set_list = [validator['address'] for validator in result]

    except Exception as e:
        print(f"{e}")
    
    return active_set_list


def get_permission_tree(account_list):
    """
    Input a list of address keys
    Queries API for permission tree of validator
    Returns a dictionary for that address list 
    """
    web_address = "https://0l.interblockcha.in:444/permission-tree/validator/"
    genesis_dict = {}
    for account in account_list:
        # print(web_address+account)
        response = requests.get(web_address+account)
        genesis_dict[str(account)] = response.json()
        # print(response.json())

    return genesis_dict


def get_epoch():
    """
    get current epoch
    """
    web_address = "https://0l.interblockcha.in:444/epochs"

    response = requests.get(web_address)
    epochs = response.json()

    return epochs



if __name__ == "__main__":

    path = 'assets/generated/full_genesis_tree.json'

    genesis_tree = []
    with open(path, 'r') as infile:
        genesis_tree = json.load(infile)
        
    # print number of validator addresses in the list
    # print(len(genesis_tree))

    max_depth = depth_of_hierarchy(genesis_tree)

    print(max_depth)

    # print("########################### Active set ###########################################")
    # vals = get_validator_addresses(True)
    # print(f"vals count = {len(vals)}\nvals = {vals}")
    
    # print("##################################################################################")
    # print("##################################################################################")
    # print("########################## All validators ########################################")
    
    # vals = get_validator_addresses(False)
    # print(f"vals count = {len(vals)}\nvals = {vals}")
    # print("##################################################################################")

