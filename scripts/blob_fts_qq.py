import operator
import os
import re
import sys
import json
db = "\"C:\Program Files\Microsoft\Exchange Server\V15\Mailbox\AdminBase\AdminBase.edb\""
bin = "C:\\tools"
tmp = "C:\\tmp"
eseblob_cmd = r"C:/tools/eseblob.exe parse"
rdata = (r"C:\workdir\blob_fts\0_0.txt")
set_cmd = "C:\\tools\ese_edit.exe set-env db:%s bin:%s tmp:%s" % (db, bin, tmp)
mailssage_no = "message_105"
cmd = "C:\\tools\ese_edit.exe show-table table:%s content:true json:true > %s.txt" % (mailssage_no, mailssage_no)
print set_cmd
os.system(set_cmd)
print cmd
os.system(cmd)

def dump_blob(data, path):
    with open(path,"w") as f:
        f.write(data)

def get_blob_dict(search_key):
    rdata = ("message_105.txt")
    with open(rdata, 'r') as f:
        data = f.read()
        re_obj = re.findall('"OffPagePropertyBlob" : "([A-Z\d]*)",\s.*\s*"PropertyBlob" : "([A-Z\d]*)"', data)
        for item in re_obj:
            dump_blob(item[1], "blobs\\111blob.txt")
            property_blob = get_blob_data("blobs\\111blob.txt")
            if check_blob_data(property_blob, search_key):
                dump_blob(item[0], "blobs\\111blob.txt")
                off_page_property_blob = get_blob_data("blobs\\111blob.txt")
                result_dict = {}
                for item in property_blob.values():
                    result_dict[item['Tag']] = item['Value']
                for item in off_page_property_blob.values():
                    result_dict[item['Tag']] = item['Value']    
                return result_dict    
                
def fts_to_dict(path):
    fts_dict = {}
    with open(path, 'r') as f:
        data = json.load(f) 
        for list in data[0]:
            fts_dict[list[3]] = list[-1]
        for dict in data[1:]:
            for list in dict['props'][0]: 
                if list[3] in fts_dict:
                    continue           
                fts_dict[list[3]] = list[-1]
    return fts_dict                

def get_blob_data(blob_path):
    blod_stream = os.popen(" %s < %s" % (eseblob_cmd, blob_path))
    try:
        return json.load(blod_stream)
    except:
        print "failed to load %s " % blob_path
    
def check_blob_data(blob_data, search_key):
    used_blob = {}
    if blob_data:
        if map(lambda y: y['Value'], filter(lambda x: x['Tag'] == 'PidTagSearchKey', blob_data.values()))[0] == search_key:
            return True
        
def find_catches(blob_dict, fts_dict):
    print '***Blob properties without matches in FTS***'
    for prop in blob_dict.keys():
        if prop not in fts_dict.keys() and "0x%s" % prop not in fts_dict.keys():
            print prop
    
    temp_prop = []    
    print "\n\n***Blob FTS diff***"
    for fts_prop, fts_value in fts_dict.items():
        blob_tags = blob_dict.keys()
        if fts_prop in blob_tags or fts_prop[2:] in blob_tags:
            blob_value = blob_dict[filter(lambda x: x == fts_prop or x == fts_prop[2:], blob_dict.keys())[0]]
            if fts_value != blob_value:
                print "%s - not equal (%s - %s)" % (fts_prop, fts_value, blob_value)
            else:
                print "%s - equal" % fts_prop
        else:
            temp_prop.append(fts_prop)    

    print "\n\n***FTS properties without matches in blob:***" 
    for prop in temp_prop:
        print prop    
        
def main(args):
    blobs_path = args[1]
    fts_dict = fts_to_dict(rdata)
    search_key = fts_dict['PidTagSearchKey']
    blob_dict = get_blob_dict(search_key)
    find_catches(blob_dict, fts_dict)
    
if __name__ == "__main__":
    main(sys.argv)
    
    