#!/usr/bin/env python
#-- coding: utf-8 --

import os
import re
import sys

# accept the file name from the shell
try:
    file_name = sys.argv[1]
except:
    search_res = os.popen('l |grep *.cml')
    res = search_res.read().splitlines()
    file_name = res [0]

# read the *.cml file from avogadro
cml_fh = open(file_name, 'r')
cml_fh.seek(0)

# open a *.lt file to write
name_parts = file_name.split('.')
head_name = name_parts[0]
lt_fh = open('%s.lt' % head_name, 'w')
lt_fh.seek(0)

# two headlines <molecule> and <atomArray>
cml_fh.readline()
cml_fh.readline()

# write the headlines of *.lt file
lt_fh.writelines(["import oplsaa.lt\n", "\n", "%s inherits OPLSAA {\n" % head_name, "\n", "    # atom-id mol-id atom-type charge X Y Z # comments\n", "   write(\"Data Atoms\") {\n"])

# write the atom list of *.lt file
elems = []
atom_ids = []
while True:
    line = cml_fh.readline()
    if "atom id" in line:
        p = re.search(r'^\s*\<atom id="a(\d+)"\s+elementType="([A-Za-z]+)"\s+.*x3="(-*[0-9\.]+)"\s+y3="(-*[0-9\.]+)"\s+z3="(-*[0-9\.]+)".*$', line)
        atom_id = int(p.group(1))
        atom_ids.append(atom_id)
        elem = p.group(2)
        elems.append(elem)
        pos_x = float(p.group(3))
        pos_y = float(p.group(4))
        pos_z = float(p.group(5))
        lt_fh.write("        $atom:%s%d  $mol:...  @atom:  0.00  %12.5f  %12.5f  %12.5f  #\n" % (elem, atom_id, pos_x, pos_y, pos_z))
    else:
        break
lt_fh.writelines(["    }\n", "\n", "    # bond-id atom-id1 atom-id2\n", "    write(\"Data Bond List\") {\n"])

# write the bond list of *.lt file
# jump through the line: <bondArray>
cml_fh.readline()
while True:
    line = cml_fh.readline()
    if "bond atomRefs2" in line:
        p = re.search(r'^\s*\<bond atomRefs2="a(\d+)\s+a(\d+)".*$', line)
        atom_id1 = int(p.group(1))
        atom_id2 = int(p.group(2))
        lt_fh.write("        $bond:%s%d%s%d  $atom:%s%d  $atom:%s%d\n" % (elems[atom_id1-1], atom_id1, elems[atom_id2-1], atom_id2, elems[atom_id1-1], atom_id1, elems[atom_id2-1], atom_id2))
    else:
        break
lt_fh.writelines(["    }\n", "}\n"])

# finishment
cml_fh.close()
lt_fh.close()
