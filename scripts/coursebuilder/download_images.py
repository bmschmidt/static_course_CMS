import sys
import re
import requests
import os

fin = open(sys.argv[1])

if len(sys.argv) >= 3:
    prefix = sys.argv[2]
else:
    prefix = "images/"

if len(sys.argv) >= 4:
    fout = open(sys.argv[3],"w")
else:
    fout = sys.stdout
    
if not prefix.endswith("/"):
    prefix += "/"

for line in fin:
    matches = re.findall(r"!\[(.*)\]\((http.*)\)", line)
    if len(matches)==0:
        continue
    else:
        for match in matches:
            url = match[1]
            basename = "__".join(url.split("/")[1:]).replace(":","+")
            fname = prefix + basename
            if os.path.exists("images/" + basename):
                os.rename("images/" + basename, fname)
            if os.path.exists(fname):
                pass
                #sys.stderr.write("{} already exists\n".format(fname))
            else:
                response = requests.get(url, stream=True)
                sys.stderr.write("downloading {}.".format(url,fname))                
                with open(fname, "wb") as handle:
                    for data in response.iter_content():
                        handle.write(data)
                sys.stderr.write(" DONE!\n")
            line = line.replace(url,fname)
        fout.write(line)


