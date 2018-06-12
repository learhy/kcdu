# kcdu
Kentik Custom Dimension Uploader

```
drohan$ ./kcdu.py
usage: kcdu.py [-h] [-email EMAIL] [-api API] [-c C] [-t T] [-i I] [-d D]

kcdu.py: a cli utility to upload custom dimensions to Kentik

optional arguments:
  -h, --help    show this help message and exit
  -email EMAIL  Kentik User Email
  -api API      API key for User
  -c C          Create a new custom dimension
  -t T          Custom dimension type. Allowable types are "string" or
                "uint32". Defaults to "string"
  -i I          input file formatted in CSV
  -d D          Matching direction. May be either 'src' or 'dst'

Note that this program can use either credentials passed via the command line
or can read a .kauth file located in your home directory.
```

As referenced above, the .kauth file looks thusly (an example is included in the repo):
```
{
   "email":"user@example.com",
   "api":"7z0235b2nz3fake3fec49edb1f4823ba"
}
```

# CSV Format
`kcdu` relies upon a simple csv structure in order to work.  Two columns are supported currently (one day I'll add a 3rd, but so far I've not found the time).  The first column is the populator matching criteria and the first row informs the script about what dimension the matching will take place on.  Accordingly, the first row in the first column must contain one of the following strings:

```
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
                        
```

Under the 1st row of the first column will be the matching criteria of the selected dimension.  So if you'd selected 'addr', you'd add a list of ip address, one per row.

The first row of the second column is disregarded entirely.

Each subsequent row in the 2nd column is the value that will be written when the criteria corresponding to the value in the 1st column is matched on ingest. 

For example:

```
Daniels-MBP:kcdu drohan$ cat ./bgp_comm1.csv | head -5
bgp_community,policy_name
0:10089,policy_1
0:14061,policy_2
0:15133,policy_3
0:15169,policy_4
```

And here's an example of running this:

```

Daniels-MBP:kcdu drohan$ ./kcdu.py -t string -c destroutepolicy -d dst -i ./bgp_comm1.csv
Custom dimension "destroutepolicy" created as id: 3444
Reading input file.
Uploading custom dimensions .............................................................................................................................................................................................................................................................................
Upload complete.
```

