# -*- coding: UTF8 -*-
import operator
import json
import re
import sys
import os
import shutil
import subprocess

# user = "win12\Administrator"
# pasw = "Acronis123"
# mail = "Administrator@win12.dcon.local"
mail_restore_path = r'C:\tools\mail_restore_2013.exe'
db_path = r"E:\DB\RND13.edb"
ews_location = r"C:\tools\EwsCmd.exe"
used_database = "RND13"
bin = "C:\\tools"
tmp = "C:\\tmp"
eseblob_cmd = r"C:\tools\eseblob.exe parse"
rdata = (r"C:\workdir\blob_fts\0_0.txt")



def set_env(db_path, bin, tmp):
    set_cmd = 'C:\\tools\ese_edit.exe set-env db:"%s" bin:"%s" tmp:"%s"' % (db_path, bin, tmp)
    run_cmd(set_cmd)

def list_tables():
    run_cmd("C:\\tools\ese_edit.exe list-tables like-name:Message_")



def setup():
    disk_name = os.getenv("HOMEDRIVE")
    user_name = os.getenv("HOMEPATH")
    ps_folder_path = r"%s%s\Documents\WindowsPowerShell" % (disk_name, user_name)
    ps1_path = r"%s%s\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1" % (disk_name, user_name)
    if not os.path.exists("C:\ProgramData\ps.exe"):
        run_cmd(r'mklink "C:\ProgramData\ps.exe" "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"')
    if os.path.exists(ps1_path):
        with open(ps1_path, 'r') as f:
            data = f.read()
            if not "add-pssnapin microsoft.exchange.management.powershell.e2010" in unicode(data, 'utf-16'):
                run_cmd("C:\ProgramData\ps.exe -inputformat none -command \"& {echo 'add-pssnapin microsoft.exchange.management.powershell.e2010' >> $Profile}\"")
    else:
        if not os.path.exists(ps_folder_path):
            os.mkdir(ps_folder_path)
            run_cmd("C:\ProgramData\ps.exe -inputformat none -command \"& {echo 'add-pssnapin microsoft.exchange.management.powershell.e2010' >> $Profile}\"")

def run_cmd(incom_command):
    exit_code = os.system(incom_command)
    if not exit_code:
		print(incom_command)
    else:
        print(incom_command, exit_code)
        raise

def upload_blobs(tmp_dir):
    create_folder(tmp_dir)
    cmd = "C:\\tools\ese_edit.exe list-tables like-name:Message_"
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in proc.stdout:
        #the real code does filtering here
        reg = "(.*) derived:.*"
        search_items = re.search(reg, line)
        if search_items:
            mailbox_num = re.match(reg, line).group(1)
            mailbox_num = str(mailbox_num.rstrip())
            ccmd = 'C:\\tools\ese_edit.exe show-table table:%s cols:PropertyBlob,RecipientList,OffPagePropertyBlob,MessageDocumentId json:true > %s/%s.txt' % (mailbox_num, tmp_dir, mailbox_num)
            run_cmd(ccmd)
    

def create_folder(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print output_dir, "is deleted"
    os.mkdir(output_dir)
    print output_dir, "is created"
            
def read_blob_files(blob_storage_path, garbage_folder):
    for root, dirs, files in os.walk(blob_storage_path):
        for file in filter(lambda x: x.endswith('.txt'), files):
            with open(r"%s\%s" % (root,file), 'r') as f:
                print file
                data = json.load(f)
                for key, dicts in data.items():
                    for item, value in dicts.items():
                        if value != "null":
                            if type(value) != int:
                                # print value
                                if parse_blob(value) != 0:
                                    with open(r"%s\%s_%s_%s.txt" % (garbage_folder, file, key, item), 'w') as f:
                                        f.write(value)

def parse_blob(blob):
    # print eseblob_cmd
    p = subprocess.Popen(eseblob_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    with p.stdin as stdin:
        stdin.write("%s\n" % blob)
    out, err = p.communicate()
    if err:
        print err
    else:
        return 0
    
    
def main(args):
    workdir = args[1]
    tmp_dir = r"%s\blobs_storage" % workdir
    garbage_folder = r"%s\garbage" % tmp_dir
    # #setup()
    # #run_cmd(r'C:\programdata\ps.exe -inputformat none -command "& {Dismount-Database -Identity %s}"' % used_database)
    # set_env(db_path, bin, tmp)
    # list_tables()
    # upload_blobs(tmp_dir)
    
    create_folder(garbage_folder)
    read_blob_files(tmp_dir, garbage_folder)

if __name__ == "__main__":
    main(sys.argv)