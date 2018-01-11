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

# ------------------------------------------------------------------------------------------
mfgattr = {}
def appmfg_dict(item):
    for xkey in item:
        mfgattr[xkey] = 1
    return

def appmfg_list( mfglist ):
    for item in mfglist:
        appmfg_dict(item)
    return

# ------------------------------------------------------------------------------------------
attattr = {}
def att_dict(item):
    for xkey in item:
        attattr[xkey] = 1
    return

def att_list( attlist ):
    for item in attlist:
        att_dict(item)
    return

# ------------------------------------------------------------------------------------------
bomattr = {}
def bom_dict(item):
    for xkey in item:
        bomattr[xkey] = 1
    return

def bom_list( bomlist ):
    for item in bomlist:
        bom_dict(item)
    return


# ------------------------------------------------------------------------------------------
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
        
        # ...............................................
        if xkey == 'ApprovedManufacturerList':
            zz = item[xkey]['ApprovedManufacturerListItem']
            if isinstance(zz, dict):
                # print("\t\t**ApprovedManufacturerListItem** : dict")
                appmfg_dict(zz)
            elif isinstance(zz, list):
                # print("\t\t**ApprovedManufacturerListItem** : list")
                appmfg_list(zz)
            else:
                print("\t\t**ApprovedManufacturerListItem** : ????????")
                
        elif xkey == 'Attachments':
            zz = item[xkey]['Attachment']
            if isinstance(zz, dict):
                att_dict(zz)
            elif isinstance(zz, list):
                att_list(zz)
            else:
                print("\t\t**Attachment** : ????????")
            
                
        elif xkey == 'BillOfMaterial':
            zz = item[xkey]['BillOfMaterialItem']
            if isinstance(zz, dict):
                bom_dict(zz)
            elif isinstance(zz, list):
                bom_list(zz)
            else:
                print("\t\t**BOM** : ????????")


print("\nAll item keys: ---------------------------------------");

for xkey in sorted(ikeylist.keys()):
    print("\t'%s'" % xkey)

# ===============================================================
print("\nApproved mfg keys: ---------------------------------------");

for xkey in sorted(mfgattr.keys()):
    print("\t'%s'" % xkey)

print("\nAttachment keys: ---------------------------------------");

for xkey in sorted(attattr.keys()):
    print("\t'%s'" % xkey)

print("\nBOM keys: ---------------------------------------");

for xkey in sorted(bomattr.keys()):
    print("\t'%s'" % xkey)
