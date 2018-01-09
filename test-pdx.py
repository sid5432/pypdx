#!/usr/bin/python3
import xmltodict
import json

xmlfile = "sample-pdx.xml";

with open(xmlfile,'r') as myfile:
    xmldata = myfile.read()


# print( xmldata )

bomtree = xmltodict.parse(xmldata)

output = "pdx.dump"
fh = open(output,'w')

print(json.dumps( bomtree, indent=8, separators=(',',':') ), file=fh )
fh.close()

# only one
bomroot = bomtree['ProductDataeXchangePackage']

print("BOM: keys")
for xkey in bomroot.keys():
    if isinstance(bomroot[xkey],str):
        print(xkey,": ",bomroot[xkey])
    else:
        print(xkey)


print("\nHistory: ---------------------------------------------");
hist = bomroot['History']['HistoryItem']
for keys in hist.keys():
    print( keys,": ",hist[keys] )

print("\nAdditional: ---------------------------------------------");
additional = bomroot['AdditionalAttributes']
xkey = '@groupLabel';
print( "\t@groupLabel: ",additional[xkey] )

for item in additional['AdditionalAttribute']:
    # print("\t'%s': '%s'" % (item['@name'],item['@value']) )
    print("\t'%s'" % item['@name'] )

print("\nItems: ---------------------------------------------");
items = bomroot['Items']['Item']

ikeylist = {}
count = 0
for item in items:
    # print("\t", item.keys() )
    count += 1
    
    istoplevel = "*" if (item['@isTopLevel'] == 'Yes') else " ";
    
    print("\t", istoplevel, count, ": ", item['@description'], " " )
    for xkey in item.keys():
        ikeylist[xkey] = 1
        # print("\t\t",xkey," ",item[xkey]);
        if isinstance(item[xkey], dict):
            print("\t\t",xkey," has keys:")
            for zkey in item[xkey]:
                print("\t\t\t",zkey,"...",type(item[xkey][zkey]) )
        elif isinstance(item[xkey],list):
            print("\t\t",xkey," is list: # of records ", len(item[xkey]) )
        else:
            print("\t\t",xkey," is attribute ",type(item[xkey]))

    


print("\nAll item keys: ---------------------------------------");

for xkey in sorted(ikeylist.keys()):
    print("\t'%s'" % xkey)



