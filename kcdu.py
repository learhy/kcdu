#!/usr/bin/env python
import sys
import argparse
import requests
import json
from os.path import expanduser
import os.path
from jinja2 import Template
import csv
from time import sleep

## Future-- add ncurses support to evenly space columns

def get_creds():
	# TODO: check permisions on file and fail if not set to 600
	homeDir = expanduser("~")
	credsFile = ".kauth"
	credsFile = homeDir + "/" + credsFile
	if os.path.isfile(credsFile):
		with open(credsFile) as f:
			content = f.read()
		creds = json.loads(content)
		return(creds)
	else:
		pass


def create_cd(col_name, type, display_name):
	url = 'https://api.kentik.com/api/v5/customdimension'
	json_template = '''
	{
		"name": "{{ column }}",
		"type": "{{ data_type }}",
		"display_name": "{{ pretty_name }}"
	}
	'''
	t = Template(json_template)
	data = json.loads(t.render(column = col_name, data_type = type, pretty_name = display_name))	
	response = requests.post(url, headers=headers, data=data)
	if response.status_code != 201:
# 		if (response.json()['error'] == "name: Column name already in use"):
# 			response = raw_input("Selected column name is already in use. Would you like to update the existing column? [Y/N] ").lower()
# 			if response == 'y':
# 				cd_dict = get_cds()
# 				for id, (column, display) in cd_dict.iteritems():
# 					if 'Source Continent' in display:
# 						print("Found the following custom dimensions {}").format(id)
# 					else:
# 						continue
		print("Unable to create custom dimension column. Exiting.")
		print("Status code: {}").format(response.status_code)
		print("Error message: {}").format(response.json()['error'])
		exit()
	else:
		print("Custom dimension \"{}\" created as id: {}").format(display_name, \
			response.json()['customDimension']['id'])
		return(response.json()['customDimension']['id'])


def get_cds():
	url = 'https://api.kentik.com/api/v5/customdimensions/'
	response = requests.get(url,headers=headers)
	response_dict = response.json()
	mydict = {n['id']: (n['name'], n['display_name']) for n in response_dict["customDimensions"]}
	return(mydict)

def read_csv(filen):
	with open(filen, mode='r') as infile:
		count = 0
		print("Reading input file.")
		reader = csv.reader(infile)
		header = reader.next()# 
		mydict = {rows[0]:rows[1] for rows in reader}
    	return(mydict, header)

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def upload_cds(mydict, direction, id):
	url = 'https://api.kentik.com/api/v5/customdimension/' + id + '/populator'
	value = mydict[1][1] # continent 
	match = mydict[1][0] # country
	json_template = '''
	{
		"populator": {
			"value": "{{ value }}",
			"direction": "{{ dir_ection }}",
			"{{ matching_header }}": "{{ matching_value }}"
		}
	}
	'''
	permitted_fields = ["device_name", 
						"device_type", 
						"site", 
						"interface_name", 
						"addr", 
						"port", 
						"tcp_flags", 
						"protocol", 
						"asn", 
						"lasthop_as_name", 
						"nexthop_asn", 
						"nexthop_as_name", 
						"nexthop", 
						"bgp_aspath",
						"bgp_community",
						"mac",
						"country"]
	t = Template(json_template)
# 	print("instantiated template")
	if match.lower() in permitted_fields:
		print("Uploading custom dimensions "),
		for k, v in mydict[0].iteritems():
			data = json.loads(t.render(value = v, dir_ection=direction, matching_value = k, matching_header= match))
			response = requests.post(url, headers=headers, json=data)
			sys.stdout.write('.')
			sys.stdout.flush()
			if response.status_code != 201|200:
				print(" ")
				print("  Unable to continue, could not upload {},{}:").format(k,v)
				print("  Status code: {}").format(response.status_code)
				print("  Error message: {}").format(response.json()['error'])
			else:
				sleep(.005)
				continue
	else:
		print("Could not identify {} as a valid matching field.").format(match.lower)

if __name__ == "__main__":

	parser = argparse.ArgumentParser(
		description='kcdu.py: a cli utility to upload custom dimensions to Kentik',
		epilog='''
		Note that this program can use either credentials passed via the command line or can 
		read a .kauth file located in your home directory. 
		''')
	parser.add_argument('--email', help='Kentik User Email')
	parser.add_argument('--api', help='API key for User')
	parser.add_argument("--list", type=str2bool, nargs='?', const=True, default=False, help="List existing/configured custom dimensions.")
	parser.add_argument('-c', help='Create a new custom dimension')
	parser.add_argument('-u', help='Update existing CD.  Argument supplied should be the custom dimension ID')
	parser.add_argument('-t', help='Custom dimension type. Allowable types are "string" or "uint32". Defaults to \"string\"', default='string')
	parser.add_argument('-i', help='input file formatted in CSV')
	parser.add_argument('-d', help='Matching direction. May be either \'src\' or \'dst\'')
	
	args = parser.parse_args()
	
	# Load variables
	
	if args.email:
		email = args.email
	if args.api:
		api = args.api
	elif get_creds():
		api = get_creds()['api']
		email = get_creds()['email']
	else:
		exit("Could not find .kauth file and credentials were not supplied as arguments.")
		
	headers = {"X-CH-Auth-API-Token": api, "X-CH-Auth-Email": email}
	
	# do the stuff
	
	if args.list:
		cd_dict = get_cds()
		print("ID\t\tColumn Name\t\tDisplay Name")
		for k, (v1, v2) in cd_dict.iteritems():
			print("{}\t\t{}\t\t{}").format(k, v1, v2)
		exit()
		
		
	if args.c:
		if args.t:
			if args.t in ['string', 'uint32']:
				#strip whitespace out, make column name lower case, prepend c_
				col_name = "c_" + args.c.replace(" ", "").lower()
			else:
				print("Column type (-t) must be either 'string' or 'uint32'. You have specified \'{}\'.").format(args.t)
				exit()
			id = create_cd(col_name, args.t, args.c)
		else:
			print("You must supply a column type (-t) in order to create a new custom dimension.")
	if args.u:
		# check to make sure that u is a valid column id
		# grab the dictionary of custom dimensions/ids/names
		cd_dict = get_cds()
		# iterate through it, looking for matches between args.u (the id) and cd IDs already configured in kentik
		for cd_id in cd_dict:
			if str(cd_id) in str(args.u):
				id = str(cd_id)
				print("Updating column {}. ").format(id),
# 			else:
# 				exit("Couldn't find a column to update")
		
	if args.i:
		# make sure file exists
		# ensure direction exists
		if args.d in ['src', 'dst']:
			mydict=read_csv(args.i)
			upload_cds(mydict, args.d, str(id))
			print(" ")
			print("Upload complete.")
		else:
			print("You must supply a matching direction.")
			exit()
			
	if not len(sys.argv) > 1:
		parser.print_help()
		exit()

	
	
	
	

		