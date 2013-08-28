# -*- coding: UTF8 -*-
import re
import sys
import os
import shutil

# user = "win12\Administrator"
# pasw = "Acronis123"
# mail = "Administrator@win12.dcon.local"
mail_restore_path = r'C:\tools\mail_restore_2013.exe'
db_path = r"E:\DB\RND13.edb"
ews_location = r"C:\tools\EwsCmd.exe"
used_database = "RND13"

def setup():
    # orig_ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    # tmp_ps_path = "C:\ProgramData\ps.exe"
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
   
def upload_fts(user, pasw, mail):
    output_dir = "C:\%s" % mail
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        print output_dir, "is created"
    else:
        shutil.rmtree(output_dir)
        print output_dir, "is deleted"
        os.mkdir(output_dir)
        print output_dir, "is created"
    list_cmd = r"c:\workdir\EwsCmd.exe list credentials=%s,%s mailbox=%s > test.txt" % (user, pasw, mail)
    run_cmd(list_cmd)
    folder_list = []
    with open("test.txt", 'r') as f:
        for line in f:
            reg = "(.*) \(\d*\)"
            search_items = re.search(reg, line)
            if search_items:
                folder_list.append(search_items.group(1))
            else:
                print "SWAP ", "*"*5, line
        for item in folder_list:
            item = re.sub(r"([:?*<>|])", "", item)
            if not os.path.exists("%s\\%s" % (output_dir, item)):
                os.mkdir("%s\\%s" % (output_dir, item))
            export_cmd = "%s export credentials=%s,%s mailbox=%s folder=\"%s\" dir=\"%s\\%s\"" % (ews_location, user, pasw, mail, item, output_dir, item )
            run_cmd(export_cmd)
                        
def get_fts_restore(path, tmp_dir):
    folder_list = []
    with open("test.txt", 'r') as file:
        for line in file:
            reg = "(.*) \(\d*\)"
            search_items = re.search(reg, line)
            if search_items:
                folder_list.append(re.match(reg, line).group(1))
            else: 
                print "SWAP ", "*"*5, line
        for item in folder_list:
            if not os.path.exists("%s\\%s" % (tmp_dir, item)):
                item = re.sub(r"([:?*<>|])", "", item)
                os.mkdir("%s\\%s" % (tmp_dir, item))
                output_path = "%s\\%s" % (tmp_dir, item)
                cmd = '%s restore-folder-fts database-path:"%s" mailbox-name:"Sergey Uzhakov" folder-path:"%s" fts-path:"%s"' % (mail_restore_path, db_path, item, output_path)
                print cmd
                run_cmd(cmd)

def create_subfolder(work_dir, tmp_dir):
    for root, dirs, files in os.walk(work_dir):
        for dir in dirs:
            out = "%s\%s" % (tmp_dir, dir)
            create_folder(out)
            
def create_folder(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print output_dir, "is deleted"
    os.mkdir(output_dir)
    print output_dir, "is created"
 
def main(args):
    user = args[1]
    pasw = args[2]
    mail = args[3]
    setup()
    run_cmd(r'C:\programdata\ps.exe -inputformat none -command "& {Mount-Database -Identity %s}"' % used_database)
    # # upload_fts(user, pasw, mail)
    
    # work_dir = "C:\\%s" % mail
    # tmp_dir = '%s_tmp' % work_dir
    # create_folder(tmp_dir)
    # # run_cmd(r'C:\programdata\ps.exe -inputformat none -command "& {Dismount-Database -Identity %s}"' % used_database)
    # get_fts_restore(work_dir, tmp_dir)

if __name__ == "__main__":
    main(sys.argv)