"""
2- AUDIT DATA - Street names

"""	

import xml.etree.cElementTree as ET
from collections import defaultdict
# python regular expression module
import re 
import pprint
OSM_FILE = open("southampton.osm", "r")

# \S: matches any non-whitespace character
# \.: matches any character except a newline
# $: Occur at the end of string.

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)

expected =["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road","Trail", "Parkway", "Commons", "Circle", "Way"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        #street_types[street_type] += 1
        if street_type not in expected:
            #tracking unusual street type
            street_types[street_type].add(street_name)
            #return True if need to be updated
            return True
def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print ("%s: %d" % (k, v) )
# checking k attribute in same tag.
def is_street_name(elem):
    #return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")
    return (elem.attrib['k'] == "addr:street") or (elem.attrib['k'] == "addr:full")

#create a records of all street types that we find in .osm dataset
def audit():
    # start means start tag. so generate next tag (elem "object type")
    for event, elem in ET.iterparse(OSM_FILE, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            #return iteration all of sub tags ( nested in elem object) named tag only.
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                # v is an attribute in tag
                    audit_street_type(street_types, tag.attrib['v'])    
    #print_sorted_dict(street_types) # uncomment if wanted to count the frequancey of each name.   
    pprint.pprint(dict(street_types))
	
if __name__ == '__main__':
    audit()
	 
