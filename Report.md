OpenStreetMap Sample Project Data Wrangling with MongoDB
===================

**Map area: Southampton, England, United Kingdom.**

OpenStreetMap is an open source project, contains many city maps where users can add, remove and edit local places and streets. It is directly connected with Google Maps which would help improving maps. The most challenge is to insure the correctness and constancy of the provided dataset. In this project, Southampton street map is analyzed which it's size is over 45 MB as requested. I have chosen this city because I have been there and I loved it. Southampton dataset is available to download from: 
https://mapzen.com/data/metro-extracts/metro/southampton_england/

Note: This report is documented using **StackEdit**[^stackedit]. Don't delete me, I'm very helpful! I can be recovered anyway in the **Utils** tab of the <i class="icon-cog"></i> **Settings** dialog.

----------
**Main steps to work with this project successfully:**

1- Select derived area from openmapstreet.org
2- Download OSM file.
3- Explore data.
4- Wrangling selected area file
5- Work with SQL or MongoDB ( I chose MongoDB in this report )
6- Clean our data.

Discovering Data:
-----------------

**Getting unique tags (mapparse.py):**

To start audit the .osm file, first we have to get an overview of the data by running it against mapparse.py to represent tags and count them by parsing Southampton xml file using ElementTree.

> Conut tags in southampton.osm:
> 	{'bounds': 1, 	 'member': 12072, 	 'nd': 375357, 	 'node': 272642, 	
> 'osm': 1, 	 'relation': 1175, 	 'tag': 204363, 	 'way': 51358}

when running users.py to find the total number of users:

> 497
		
So, moving to tags.py and running it to have a focus look at the tags key attributes format, we get a result:

> {'lower': 110892, 'lower_colon': 90941, 'other': 2528, 'problemchars': 2}

as lower, lower_colon, other and problemchars indicates  ....., ....., ..... and ........ .
shifting to tags value attributes to have a general look at any inappropriate typing style done by contributors.

    
	 if problemchars.search(element.attrib['v']):
	         keys['problemchars']+=1
	         print (element.attrib['v']) 
	
    
  I found really interested data to take into account and considered of next auditing like:
  
   > Mo-Fr 16:45; Sa 11:45 
   > St. Nicolas Church 
   > Southampton, Hampshire, England, UK 
   > en:Woolston, Hampshire 
   > cushion;choker 
   > Catholic Church of St. Boniface
   > Potlatch 0.10f
   > Thornhill, Southampton 
   > +44 2380 557943 

  From the above results sample, I can for sure say that Southampton open street map has a lot of inconsistence, invalid and dirty data which needs an extra effort to handle. 


1. Problems Encountered in the Map
-------------

After discovering .osm file and running it, I noticed problems in some fields that have to pay more attention:  

 * Street names are wrong which some were inserted as abbreviate name.
 
 > Bellevue Rd --> 'Bellevue Road

 * Wrong input in city value. 
 > Southampton' --> Southampton 
 
 * Column shift from house number to street name.

	>"street": "387"  -- > Hinkler Road
 - Inconsistent phone numbers. 
 
 > 02381247029 --> +44 23 8124 7029
    
### Over-Abbreviated Street Names (audit_street.py):

by running database against audit_street.py using the following regexes: 
1- To find a word at the end of string:

	street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

2- To find a word at the beginning of string:

	street_type_re = re.compile(r'^\d+\S', re.IGNORECASE)
and exclude the following street types:

	expected =["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road","Trail", "Parkway", "Commons", "Circle", "Way"]

and then, grouping all street types to identify any unacceptable types.
	
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
	

*Sample of values need more attention:*
	  
	'Buildings': {'Hanover Buildings', 'Gordon Buildings', 'Market Buildings'}, 

Not a street type here there is a mistake in filling the attribute of street. So, trying to predicate the correct name, I back to .osm file and searched for any information that help me.  
Italian Creams --- for 'Hanover Buildings'
	
	'Western Esplanade (corner of Fitzhugh Street)'
 In this case I will delete the section before brackets as Western Esplanade is an area beside the beach. the correct street is Fitzhugh Street.

	'S'

No idea about the meaning of S (street/south/written by mistake!) but when discovering the xml file S value mentioned Farah cafe which is located on Clifford Street after googling it but it is not existing  anymore. So, In this case I will ignore it.

>'136 Church Road'

I would prefer split it into 2 attributes street name and street number. 

> '387'

A contributor typed street number instead of street name.  

### 2- Develop plan for cleaning street names(improve_street.py):

sample of the mapping that I have applied :

> mapping = { "Market Buildings": "High Road",
            "Raod": "Road",
            "Rd": "Road",
            "road":"Road",
           "Western Esplanade (corner of Fitzhugh Street)":"Fitzhugh Street",
            "Royal Crescent Road student re":"Royal Crescent Road",
            "Road Westal":"Road West",
            "Bassett Green Road / Bassett Green Village":"Bassett Green Road",
                 
      } 
            
As a result, all street names will be improved in a correct and uniform manner.

### Over-Abbreviated Post Codes (audit_post.py):

by running database against post_street.py using the following regex: 


	POSTCODE_re = re.compile(r'[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}', re.IGNORECASE)



*Sample of values need more attention:*
	  
	'SO14 0AH': {'SO14 0AH'}
	'SO14 0AL': {'SO14 0AL'},
	'SO14 0EG': {'SO14 0EG'},
	'SO14 0GE': {'SO14 0GE'},


all post code values seem very clean and in a correct UK's format.
	
Preparing Southampton database:

In **data.py** the processed map has been saved and the result is southampton.osm.json. by using this line:
> data = process_map(OSM_FILE, False). 

A script will be loaded to insert our map into it. I print some values just to make sure everything is well formatted:

>from data import *
data = process_map(OSM_FILE, False) 
pprint.pprint(data[:2]) # checking data format before transfar it into MongoDB.

	[{'created': {'changeset': '8139974',
	              'timestamp': '2011-05-14T11:45:29Z',
	              'uid': '260682',
	              'user': 'monxton',
	              'version': '5'},
	  'id': '132707',
	  'pos': [50.9454657, -1.4775675],
	  'type': 'node'},
	 {'created': {'changeset': '153019',
	              'timestamp': '2006-11-11T17:58:16Z',
	              'uid': '2231',
	              'user': 'Deanna Earley',
	              'version': '1'},
	  'id': '132708',
	  'pos': [50.9474216, -1.4709162],
	  'type': 'node'}
	
	
## Connecting to MongoDB:

	"""""
	4- ACCESSING MongoDB
	1) cd c: //changes to C drive
	2) mkdir data //creates directory data
	3) cd data
	4) mkdir db //creates directory db 
	5) cd db //changes directory so that you are in c:/data/db
	6) run mongod -dbpath 
	7) close this terminal, open a new one and run mongod
	>> Point your command prompt to C:\Program Files\MongoDB\Server\3.4\bin
	>> mongod
	http://stackoverflow.com/questions/23726684/mongodb-on-a-windows-7-machine-no-connection-could-be-made
	"""""
	
	from pymongo import MongoClient
	
	client  = MongoClient('mongodb://localhost:27017')
	
	# Access Database Objects
	db = client.southampton
		
and then, inserting a document into a collection named 'southcol' in MongoDB.

	from pymongo import InsertOne
	[db.southcol.insert_one(e) for e in data]
		
***Playing with collection and getting some statistical value:***	

	def find():
	    count=0
	    x={"highway": "residential"}
	    resdient = db.southcol.find(x)
	    for r in resdient:
	        count +=1
	        #pprint.pprint(r)
	    return count    
	    
	if __name__ == '__main__':
	    count = find()
	    print ('Total of residential in Southampton: {}'.format(count))
	
Total of residential in Southampton: 6946

	def find():
	    count = 0
	    cafes = db.southcol.find({"amenity": "cafe"})
	    for cafe in cafes:
	        count +=1
	        #pprint.pprint(cafe)
	    return count
	        
	if __name__ == '__main__':
	    count=find()
	    print ('Total of cafes in Southampton: {}'.format(count)) 
		
Total of cafes in Southampton: 156
	
## Data Overview:

	"""
	FILE SIZE.
	
	"""
	
	import os
	print ("FILE SIZES: \n")
	s1=os.path.getsize('southampton.osm')
	s2=os.path.getsize('audit_street.py')
	s3=os.path.getsize('users.py')
	s4=os.path.getsize('tags.py')
	print ('southampton.osm ....{}'.format(s1))
	print ('audit_street.py ....{}'.format(s2))
	print ('users.py ...........{}'.format(s3))
	print ('tags.py ............{}'.format(s4))
	
	# OR:
	# statinfo = os.stat(OSM_FILE)
	# #print (statinfo)
	# statinfo.st_size
	




FILE SIZES: 

southampton.osm ....66903798
audit_street.py ....2131
users.py ...........783
tags.py ............2203	

	"""
	Number of documents
	
	"""
	
	# count() is equivalent to the db.collection.find(query).count() construct.
	x=db.southcol.find().count()  
	pprint.pprint(x)
	
= 648000
	
	"""
	Number of nodes
	
	"""
	
	db.southcol.find({"type":"node"}).count() 

= 545282

	"""
	Number of ways
	
	"""
	
	db.southcol.find({"type":"way"}).count() 		

= 102708
	
	"""
	1- Group posts by users
	2- Count posts of each user
	3- Sort posts into descending order
	4- Select user at top
	
	"""
	info = db.southcol.aggregate([
	        {"$group":{"_id":"$created.user",
	                   "count":{"$sum":1}}},
	        {"$sort":{"count":-1}},
	         {'$limit' : 1}]) 
	
	
	if __name__=='__main__':
	    #result  = top_user()
	    for doc in info:
	        print(doc)	

Top 1 contributing user:
{'_id': 'Chris Baines', 'count': 214502}

	info = db.southcol.aggregate([
	        {"$group":{"_id":"$created.user",
	                   "count":{"$sum":1}}},
	        {"$sort":{"count":1}},
	         {'$limit' : 1}]) 
	
	
	if __name__=='__main__':
	    #result  = top_user()
	    for doc in info:
	        print(doc)
	
	
Contributor has only one post:	
{'_id': 'hofoen', 'count': 2}

##Additional data exploration using MongoDB queries:

Get restaurants details that have Chinese, Indian or Italian cuisine

	count = 0
	info = db.southcol.find({"cuisine": {"$in": ["chinese","Indian","Italian"]}})
	
	for document in info:
	    count+=1
	    pprint.pprint(document)
	    print ('\n')
	print ('total places = {}'.format(count))
	#result  = db.southcol.aggregate(pipeline)['result']
	
	
Find places can be reached by wheelchair

	db.southcol.find({"wheelchair":{"$exists":1}}).count()
	

#Conclusion:
------

The Southampton OpenStreetMap dataset is not too large but a quite messy especially in street types and phone numbers. While the data is not 100% clean in these field more wrangling should be applied. To be honest, I discovered many places I have not visited yet by searching dataset. I found myself improved every time I trying my wrangling skills.

### Suggestions and ideas: 

-	It should be some rules that prevent users from entering wrong format especially in postcode and phone numbers.
-	Encourage tourists and residents to improve their city map that would make the life direction as a piece of cake. 
-	Add a column for additional info about address (optional to fill).
-	Prevent users from using ( - / \ | ), which might be reduced the number of entering mistake.f
-	Did not accept one letter or one number in any field. 
-	Regarding of duplicating values in all field like what I mentioned before in postcode as a user fill all fields with the same value, some verification rules might be applied.
-	In phone number field, some auditing can be applied:
o	Using regex re.compile(r'\+44\s\d{2}\s\d{4}\s\d{4}') as United Kingdom phone line format is: +44 XX XXXX XXXX and auditing the following.
o	Check for valid phone number format. 
o	Convert all dashes to spaces
o	Remove all brackets
o	Space out 10 straight numbers
o	Space out 11 straight numbers
o	Add full country code
o	Add + in country code
o	Ignore tag if no area code and local number (<10 digits)
collection_times element has many data for example (Mo-Fr 16:45; Sa 11:45), in my point of view it should split into 2 keys: collection_times_weekday and collection_times_weekend or collection_times_staurday as there are closed on Saturday. 
I would prefer split street name into 2 attributes street name and street number.


	> <i class="icon-pencil"> ***Note**:* I refer to http://pythonex.org/ to build my regular expression before applying it.
