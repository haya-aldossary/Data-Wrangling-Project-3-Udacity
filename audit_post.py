#%load audit_post.py

import xml.etree.cElementTree as ET
from collections import defaultdict
# python regular expression module
import re 
import pprint
OSM_FILE = open("southampton.osm", "r")

POSTCODE_re = re.compile(r'[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}', re.IGNORECASE) #http://en.wikipedia.orgwikiUK_postcodes#Validation
POSTCODE_types = defaultdict(set)

def audit_POSTCODE_type(POSTCODE_types, POSTCODE):
    m = POSTCODE_re.search(POSTCODE)
    if m:
        POSTCODE_type = m.group()
        if POSTCODE_type:
            POSTCODE_types[POSTCODE_type].add(POSTCODE)
            return True

def is_POSTCODE(elem,x):
    return (elem.attrib['k'] == x) 
	
def audit():
    for event, elem in ET.iterparse(OSM_FILE, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_POSTCODE(tag, "addr:postcode"):
                    audit_POSTCODE_type(POSTCODE_types, tag.attrib['v'])    
    pprint.pprint(dict(POSTCODE_types))

if __name__ == '__main__':
    audit()