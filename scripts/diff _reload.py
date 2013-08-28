import os
import re
import sys
import fts_compare
import json

fts_edit_path = r'c:\tools\fts_edit.exe' 

diff_dict = {
                fts_compare._absentLeftToRight:{},
                fts_compare._absentRightToLeft:{},
                fts_compare._propsDifferences:{},
                fts_compare._movedProps:{},
                fts_compare._childrenCount:{},
                fts_compare._children:{},
            }

def run_cmd(incom_command):
    exit_code = os.system(incom_command)
    if not exit_code:
        print(incom_command)
    else:
        print "***FAIL***"
        print (incom_command, exit_code)
        print "***FAIL***"
            
            
def dump_fts_to_json(fts_path):
    print fts_path
    cmd = '%s list fts-path="%s" text-path="%s"' % (fts_edit_path, fts_path, fts_path.replace('.fts', '.txt'))
    run_cmd(cmd)

def merge_results(data):
    new_dict = data[0]
    fileLeft = data[1]
    fileRight = data[2]
    for key in diff_dict:
        for prop in new_dict[key]:
            if key in (fts_compare._propsDifferences, fts_compare._movedProps):
                prop_id = prop[0][3]
                if prop_id not in diff_dict[key]:
                    diff_dict[key][prop_id] = [1, prop, fileLeft, fileRight]
                else:
                    diff_dict[key][prop_id][0] += 1
                continue
            if key == fts_compare._children:
                merge_results(prop)
                continue               
            if prop[3] not in diff_dict[key]:
                diff_dict[key][prop[3]] = 1
            else:
                diff_dict[key][prop[3]] += 1
   
def write_results():
    with open('diff.csv', 'w') as f:
        f.write(';'.join(['PROPERTY ID', 'FAILS AMOUNT', 'EXAMPLE FILES', 'ORIGINAL', 'RESTORED', '\n']))
        for key in sorted(diff_dict):
            f.write(key + '\n')
            if key in (fts_compare._propsDifferences, fts_compare._movedProps):
                for prop in diff_dict[key]:
                    f.write(';'.join([prop, str(diff_dict[key][prop][0]), '%s - %s' % (str(diff_dict[key][prop][2]), str(diff_dict[key][prop][3])), str(diff_dict[key][prop][1][0][4:]), str(diff_dict[key][prop][1][1][4:]), '\n']))
                f.write('\n')
                continue
            for prop in diff_dict[key]:
                f.write(';'.join([prop, str(diff_dict[key][prop]), '\n']))
            f.write('\n')

            
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
          

def source_dict_fts(before_dir, after_dir):
    result_dict = {}
    for root, dirs, files in os.walk(before_dir):
        for file in filter(lambda x: x.endswith('.fts'), files):
            tmp_path = '%s\\%s' % (root, file)
            #dump_fts_to_json(tmp_path)
            repl_tmp = tmp_path.replace('.fts', '.txt')
            try:
                fts_dict = fts_to_dict(repl_tmp)   ###              
            except Exception as err:
                print "%s - %s" % (file, err.message)
                continue
            search_key = fts_dict['PidTagSearchKey']
            print search_key
            result_dict[search_key] = [repl_tmp]
    for root, dirs, files in os.walk(after_dir):
        for file in filter(lambda x: x.endswith('.fts'), files):
            tmp_path = '%s\\%s' % (root, file)
            #dump_fts_to_json(tmp_path)
            repl_tmp = tmp_path.replace('.fts', '.txt')
            fts_dict = fts_to_dict(repl_tmp)   ###
            search_key = fts_dict['PidTagSearchKey']
            print search_key
            for result_key, result_value in result_dict.items():
                if search_key in result_key:
                    if os.path.basename(os.path.dirname(result_value[0])) == os.path.basename(os.path.dirname(repl_tmp)):
                        result_value.append(repl_tmp)
    if result_dict == {}:
        raise Exception("ololo")    
    return result_dict
        
          
def main(args):
    before_dir = args[1]
    after_dir = args[2]
    source_bla = source_dict_fts(before_dir, after_dir)
    
    for value in source_bla.values():
        # print value
        if len(value) >= 2:
            merge_results(fts_compare.compare(value[0], value[1]))
        else:
            print "*** MISS    %s" % value           
    write_results()

if __name__ == "__main__":
    main(sys.argv)
