# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import requests
import json
from dash import dcc
from dash import html
from dash import dash_table as dt
import dash_bootstrap_components as dbc
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----MAIN FUNCTIONS-------

def render_network_options(hierarchical_enabled=False, direction='UD'):
    DEFAULT_OPTIONS = {
        'height': '700px',
        'width': '100%',
        'interaction': {'hover': True, 'hoverConnectedEdges': True, 'navigationButtons': True},
        'edges': {'arrows': {
            'to': {'enabled': True, 'scaleFactor': 1, 'type': "arrow"}
        }},
        'layout': {'hierarchical': {
            'enabled': hierarchical_enabled,
            'levelSeparation': 150,
            'nodeSpacing': 100,
            'treeSpacing': 200,
            'blockShifting': True,
            'edgeMinimization': True,
            'parentCentralization': True,
            'direction': direction,        # UD, DU, LR, RL
            'sortMethod': 'directed',  # hubsize, directed
            # 'shakeTowards': 'roots'  # roots, leaves
        }
        },
        # 'edges': {'scaling': {'min': 1, 'max': 5}},
        'physics': {'stabilization': {'iterations': 100}}
    }
    return DEFAULT_OPTIONS

def render_network_legend(colors_dict):
    c_list = []
    for key, value in colors_dict.items():
        c_list.append(dbc.Badge(key, color=value, className="me-1"))
    return ",".join(c_list)


def render_datatable(columns, data):
    return html.Div([dt.DataTable(
        columns=columns,
        data=data,
        sort_action="native",
        sort_mode="multi",
        filter_action='native',
        page_action="native",
        page_current=0,
        page_size=10,
        style_header={
            "backgroundColor": "rgb(2,21,70)", "color": "white", "textAlign": "center", },
        style_table={'overflowX': 'auto'},
        style_data={"whiteSpace": "normal"},
        style_cell={
            "padding": "5px",
            "midWidth": "0px",
            "width": "25%",
            "textAlign": "left",
            "border": "white",
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
    ),
    ]
    )

def get_nb_pub_by_struct(id):
    numfound = ""
    url = 'https://api.archives-ouvertes.fr/search/?wt=json&q=authStructId_i:{}&rows=1'.format(id)
    resp = requests.get(url).text
    if json.loads(resp)['response']:
        numfound = json.loads(resp)['response']['numFound']
    else:
        pass
    return numfound

def get_child_struct(id, result=None):
    """
    Function to recursivly get all the child structures of a structure in the Aurehal referential.
    Metadata are coming from a request on the parentDocid_id field to the ref/structure HAL API (param &q=parentDocid_i:).

    Args
    ----------
    id (str|int) : the docid HAL structure identifier
    result (list of dicts, default None) : the cumulative list of dictionaries in which the parsed data are incremented

    Return
    -------
    returns a list of dicts populated with HAL docid (of structures) and "from" and "to" keys
    Example : [{'from': 1039632, 'to': 520677}, {'from': 1039632, 'to': 537646},...] 

    Uses
    -------
    * get_childStruct(id,None)
    * Assign to a dataframe : df = pd.DataFrame(get_childStruct(id,None))
    """
    if result is None:  # create a new result if no intermediate was given
        result = []
    url = 'https://api.archives-ouvertes.fr/ref/structure/?wt=json&rows=10000&q=parentDocid_i:{}&fl=docid'.format(
        id)
    print(url)
    resp = requests.get(url).text
    if json.loads(resp)['response']['docs']:
        data = json.loads(resp)['response']['docs']
        for node in data:
            result.append({"from": id, 'to': node['docid']})
            get_child_struct(node['docid'], result)
    else:
        pass
    # dedup in case of duplicate relatioships
    output = [i for n, i in enumerate(result) if i not in result[n + 1:]]
    return output

def dict_populate(node,id=None,result=None):
    result.append({"from": node, 'to': id})
    return result



def get_parent_struct(id, result=None):
    """
    Function to recursivly get all the parent structures of a structure in the Aurehal referential.
    Metadata are coming from a request on the docid field to the ref/structure HAL API (param &q=docid:) and with the parentDocid_i in the result displayed fields (param &fl=parentDocid_i).

    Args
    ----------
    id (str|int) : the docid HAL structure identifier
    result (list of dicts, default None) : the cumulative list of dictionaries in which the parsed data are incremented

    Return
    -------
    returns a list of dicts populated with HAL docid (of structures) and "from" and "to" keys
    Example : [{'from': '409', 'to': 399760}, {'from': '117617', 'to': '409'}, {'from': '523042', 'to': '117617'}, {'from': '441569', 'to': '409'}, {'from': '1039632', 'to': '409'}]

    Uses
    -------
    * get_parentStruct(id,None)
    * Assign to a dataframe : df = pd.DataFrame(get_parentStruct(id,None))
    """
    if result is None:  # create a new result if no intermediate was given
        result = []
    url = 'https://api.archives-ouvertes.fr/ref/structure/?wt=json&rows=50&q=docid:"{}"&fl=parentDocid_i'.format(
        id)
    print(url)
    resp = requests.get(url).text
    if json.loads(resp)['response']['docs'][0]:
        data = json.loads(resp)['response']['docs'][0]['parentDocid_i']
        for node in data:
            result.append({"from": node, 'to': id})
            get_parent_struct(node, result)
    else:
        pass
    output = [i for n, i in enumerate(result) if i not in result[n + 1:]]
    return output


def get_struct_infos(id):
    """
    Function to get descriptive HAL metadata of a given structure.
    Metadata are coming from a request on the docid field to the ref/structure HAL API (&q=docid:)
    The choosen metadata for output are : acronym_s,label_s,valid_s,type_s,address_s,url_s

    Args
    ----------
    id (str|int) : the docid HAL structure identifier

    Return
    -------
    returns a dict populated with the HAL requested metadata
    Example : {'id': 1039632,'label_s': "Université Côte d'Azur [UCA]",'acronym_s': 'UCA','address_s': 'Parc Valrose, 28, avenue Valrose 06108 Nice Cedex 2','url_s': 'https://univ-cotedazur.fr','type_s': 'regroupinstitution','valid_s': 'VALID'}

    Uses
    -------
    * get_struct_infos(id)
    * used in the get_list_struct_infos function
    """
    result = {}
    url = 'https://api.archives-ouvertes.fr/ref/structure/?wt=json&q=docid:{}&fl=acronym_s,label_s,valid_s,type_s,address_s,url_s'.format(
        id)
    print(url)
    resp = requests.get(url).text
    data = json.loads(resp)['response']['docs']
    result["id"] = id
    result["nb_publis"] = get_nb_pub_by_struct(id)
    for item in data:
        for key, value in item.items():
            result[key] = value
    return result


def get_list_struct_infos(docid_list):
    """
    applies the get_struct_infos function to a list of structure's docid and compile the results in a dataframe.

    Args
    ----------
    docid_list (list) : a list of docid HAL structure's identifiers
    Example : ["1039632","399760","409"]

    Return
    -------
    returns a dataframe populated with all the results of teh get_struct_infos function

    Uses
    -------
    * get_list_struct_infos(docid_list)
    * assign to a new dataframe : df = get_list_struct_infos(docid_list)
    """
    processes = []
    df_collection = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        processes = {executor.submit(get_struct_infos, i): i for i in docid_list}
    for task in as_completed(processes):
        worker_result = task.result()
        df_collection.append(worker_result)
    results =  pd.DataFrame(df_collection)
    #results = pd.DataFrame()
    #for i in docid_list:
    #    df = pd.DataFrame(get_struct_infos(i), index=[i])
    #    results = pd.concat([results, df], axis=0).reset_index(drop=True)
    return results
