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
		print("Unable to create custom dimension column. Exiting.")
		print("Status code: {}").format(response.status_code)
		print("Error message: {}").format(response.json()['error'])
		exit()
	else:
		print("Custom dimension \"{}\" created as id: {}").format(display_name, \
			response.json()['customDimension']['id'])
		return(response.json()['customDimension']['id'])


def read_csv(filen):
	with open(filen, mode='r') as infile:
		print("Reading input file.")
		reader = csv.reader(infile)
		header = reader.next()
		mydict = {rows[0]:rows[1] for rows in reader}
		# the above line needs to be changed to account for multiple columns in the spreadsheet, not only 2
    	return(mydict, header)


def upload_cds(mydict, direction, id):
	url = 'https://api.kentik.com/api/v5/customdimension/' + id + '/populator'
	value = mydict[1][1] # continent 
	match = mydict[1][0] # country
	print(value)
	print(match)
	json_template = '''
	{
		"populator": {
			"value": "{{ value }}",
			"direction": "{{ dir_ection }}",
			"{{ matching_header }}": "{{ matching_value }}"
		}
	}
	'''
	print(json_template)
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
	print("instantiated template")
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
	parser.add_argument('-email', help='Kentik User Email')
	parser.add_argument('-api', help='API key for User')
	parser.add_argument('-c', help='Create a new custom dimension')
	parser.add_argument('-t', help='Custom dimension type. Allowable types are "string" or "uint32". Defaults to \"string\"', default='string')
	parser.add_argument('-i', help='input file formatted in CSV')
	parser.add_argument('-d', help='Matching direction. May be either \'src\' or \'dst\'')
	
	args = parser.parse_args()
	
	# Load variables
	
	if get_creds():
		api = get_creds()['api']
		email = get_creds()['email']
		
	else:
		email = args.email
		api = args.api
	headers = {"X-CH-Auth-API-Token": api, "X-CH-Auth-Email": email}
	
	# do the stuff
	
	if args.c:
	# make sure that 
		if args.t:
			if args.t in ['string', 'uint32']:
				col_name = "c_" + args.c.lower()
				id = create_cd(col_name, args.t, args.c)
			else:
				print("Column type (-t) must be either 'string' or 'uint32'. You have specified \'{}\'.").format(args.t)
			
		else:
			print("You must supply a column type (-t) in order to create a new custom dimension.")
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

	
	
	
	

		