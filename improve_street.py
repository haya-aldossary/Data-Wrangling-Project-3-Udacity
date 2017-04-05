"""""
4- Improving Street Names
"""""
import xml.etree.cElementTree as ET
from collections import defaultdict
from __future__ import division, absolute_import, print_function, unicode_literals
import re
import pprint

OSMFILE = "southampton.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

mapping = { "2HW": "HighRoad",
            "Raod": "Road",
            "Rd": "Road",
            "Street)":"Street",
            "road":"Road",
            "Road Westal":"Road West"
          }


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
    #assert len(st_types) == 6
    #pprint.pprint(dict(st_types))
    # in python 3: iteritems =>>> items 
    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print (name, "=>", better_name)
            if name == "Bluebell Raod":
                assert better_name == "Bluebell Road"
            if name == "Hythe Rd":
                assert better_name == "Hythe Road"


if __name__ == '__main__':
    test()