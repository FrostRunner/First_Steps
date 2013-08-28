# -*- coding: UTF8 -*-
import operator
import json
import re
import sys
import os
import shutil
import subprocess


db_path = r"C:\Program Files\Microsoft\Exchange Server\V15\Mailbox\Mailbox Database 0577352175\Mailbox Database 0577352175.edb"
used_database = "RND13"
bin = "C:\\tools"
tmp = "C:\\tmp"
eseblob_cmd = r"C:\tools\eseblob.exe parse"
mail_restore_path = r'C:\tools\mail_restore_2013.exe'



def set_env(db_path, bin, tmp):
    set_cmd = 'C:\\tools\ese_edit.exe set-env db:"%s" bin:"%s" tmp:"%s"' % (db_path, bin, tmp)
    run_cmd(set_cmd)


def run_cmd(incom_command):
    exit_code = os.system(incom_command)
    if not exit_code:
		print(incom_command)
    else:
        print(incom_command, exit_code)
        raise



def read_file(xml_path):
    xml_dict = {}
    code_numbers = [2606, 2607, 2608]
    with open(xml_path, 'r') as f:
        data = f.readlines()
    for line in data:
        reg = "(.*code=\")(\d*)(.*metadata of e-mail ')(\w*)(.*folder ')(\w*)(.*of mailbox ')([\w-]*)"
        # import pdb; pdb.set_trace()
        search_items = re.search(reg, line)
        if search_items:
            code_num = re.match(reg, line).group(2)
            email_num = re.match(reg, line).group(4)
            folder_num = re.match(reg, line).group(6)
            mailbox_guid = re.match(reg, line).group(8)
            if int(code_num) in range(2006,2608):
                xml_dict[email_num] = [folder_num, mailbox_guid]
    return xml_dict
            
   
def search_mailbox_number(mailbox_guid):
    cmd = r"c:\tools\ese_edit.exe show-record table:Mailbox where:MailboxInstanceGuid=%s cols:MailboxNumber" % mailbox_guid
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    for line in p.stdout:
        reg = "\[(\d*)\]"
        search_items = re.search(reg, line)
        if search_items:
            return search_items.group(1)
    

    
def run(xml_dict_items):
    result_dict = {}
    counter = 1
    
    for email_num, folder_mailbox in xml_dict_items.items():
        mailbox_number = search_mailbox_number(folder_mailbox[1])
        cmd = r"c:\tools\ese_edit.exe show-record table:Message_%s where:MessageId=%s cols:MessageClass" % (mailbox_number, email_num)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        for line in p.stdout:
            reg = "(MessageClass = )\[(.*)\]"
            search_items = re.search(reg, line)
            if search_items:
                print search_items.group(2)
                if search_items.group(2) in result_dict.keys():
                    result_dict[search_items.group(2)] += 1 
                else:
                    result_dict[search_items.group(2)] = counter
    for i in result_dict.items():
        print i
 
                
   
def main(args):
    xml_path = args[1]
    set_env(db_path, bin, tmp)
    xml_dict_items = read_file(xml_path)
    run(xml_dict_items)

if __name__ == "__main__":
    main(sys.argv)
