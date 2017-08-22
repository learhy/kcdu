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
