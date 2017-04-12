import xml.etree.ElementTree as ET 
import pprint 
import re 
import codecs 
import json 
import sys 
from collections import defaultdict


OSMFILE = 'southampton.osm'  

street_types = defaultdict(set)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"] 
 
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) # intersted in the last word of the string.
street_type_start = re.compile(r'^\d+\S', re.IGNORECASE) # intersted in the first word of the string.

expected =["Street", "Avenue","Drove", "Close","walk","Boulevard","access", "Hill","Drive", "Court", "Place", "Square", "Lane", "Road","Trail", "Parkway", "Commons", "Circle", "Way"]


mapping = { "Market Buildings": "High Road","Raod": "Road", "Rd": "Road", "road":"Road","Western Esplanade (corner of Fitzhugh Street)":"Fitzhugh Street","Royal Crescent Road student re":"Royal Crescent Road","Road Westal":"Road West","Bassett Green Road / Bassett Green Village":"Bassett Green Road", "Redhill":"Red Hill","Greenways": "Green Way"}
 
 
def shape_element(element): 
    node = {} 
     # you should process only 2 types of top level tags: "node" and "way" 
    if element.tag == "node" or element.tag == "way" : 
        #create the dictionary based on exaclty the value in element attribute.
        for key in element.attrib.keys(): 
            val = element.attrib[key] 
            node["type"] = element.tag 
            if key in CREATED: 
                if not "created" in node.keys(): 
                    node["created"] = {} 
                node["created"][key] = val 
            elif key == "lat" or key == "lon": 
                if not "pos" in node.keys(): 
                    node["pos"] = [0.0, 0.0] 
                old_pos = node["pos"] 
                if key == "lat": 
                    new_pos = [float(val), old_pos[1]] 
                else: 
                    new_pos = [old_pos[0], float(val)] 
                node["pos"] = new_pos 
            else: 
                node[key] = val 
            for tag in element.iter("tag"): 
                tag_key = tag.attrib['k'] 
                tag_val = tag.attrib['v'] 
                if problemchars.match(tag_key): 
                    continue 
                elif tag_key.startswith("addr:"): 
                    if not "address" in node.keys(): 
                        node["address"] = {} 
                    addr_key = tag.attrib['k'][len("addr:") : ] 
                    if lower_colon.match(addr_key): 
                        continue 
                    else: 
                        node["address"][addr_key] = tag_val 
                elif lower_colon.match(tag_key): 
                    node[tag_key] = tag_val 
                else: 
                    node[tag_key] = tag_val 
        for tag in element.iter("nd"): 
            if not "node_refs" in node.keys(): 
                node["node_refs"] = [] 
            node_refs = node["node_refs"] 
            node_refs.append(tag.attrib["ref"]) 
            node["node_refs"] = node_refs 
 
 
        return node 
    else: 
        return None 
 
 
 
 # Process the osm file to json file to be prepared for input file to monggo

def process_map(file_in, pretty = False): 
    # You do not need to change this file 
    file_out = "{0}.json".format(file_in) 
    data = [] 
    with codecs.open(file_out, "w") as fo: 
        for _, element in ET.iterparse(file_in): 
            el = shape_element(element) 
            if el: 
                data.append(el) 
                if pretty: 
                    fo.write(json.dumps(el, indent=2)+"\n") 
                else: 
                    fo.write(json.dumps(el) + "\n") 
    return data 



def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                    tag.attrib['v'] = update_name(tag.attrib['v'],mapping)

    osm_file.close()
    return street_types


def update_name(name, mapping):

    dictionary_map = sorted(mapping.keys(), key=len, reverse=True)
    for key in dictionary_map:
        
        if name.find(key) != -1:          
            name = name.replace(key,mapping[key])

    return name


def test():
    st_types = audit(OSMFILE)

    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            #print (name, "=>", better_name)		
    data = process_map(OSMFILE, False)
    #print (data[297241:297243]) # uncomment if you want to print your .json file
	          


if __name__ == '__main__':
    test()
		

    
    
#print (run(osm_file))    
#  if __name__ == "__main__": 
#     if not len(sys.argv) == 2: 
#          print "Usage: python maps/data.py input-file" 
#     else: 
#          run(sys.argv[1]) 
