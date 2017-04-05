#%load mapparser.py
"""""
1- find documentatin of osm xml format in wiki
    https://wiki.openstreetmap.org/wiki/Main_Page
    http://wiki.openstreetmap.org/wiki/OSM_XML
"""""
import xml.etree.ElementTree as ET
import pprint

OSM_FILE='southampton.osm'

def count_tags(filename):
    tag_count = {}
    for _, element in ET.iterparse(filename, events=("start",)):
        add_tag(element.tag, tag_count)
    return tag_count

def add_tag(tag, tag_count):
    if tag in tag_count:
        tag_count[tag] += 1
    else:
        tag_count[tag] = 1

def test():

    tags = count_tags(OSM_FILE)
    pprint.pprint(tags)
    """
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}

    """

if __name__ == "__main__":
    print ("Conut tags in southampton.osm")
    test()