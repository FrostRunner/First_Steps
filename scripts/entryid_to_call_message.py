import re
import sys
import os
import subprocess

db_path = r"E:\DB\RND13.edb"
bin_folder = "C:\\tools"
tmp = "C:\\tmp"


def run_cmd(incom_command):
    exit_code = os.system(incom_command)
    if not exit_code:
        print(incom_command)
    else:
        print(incom_command, exit_code)
        raise Exception("Command should not run")


def set_env(db_path, bin_folder, tmp):
    set_cmd = "C:\\tools\ese_edit.exe set-env db:%s bin:%s tmp:%s" % (db_path, bin_folder, tmp)
    run_cmd(set_cmd)


def get_mailbox_instance_id(entry_id):
    mailbox_instance_id = entry_id[8:40]
    return mailbox_instance_id


def get_message_object_id(entry_id):
    message_object_id = entry_id[-48:-16]
    return message_object_id


def get_folder_object_id(entry_id):
    folder_object_id = entry_id[44:80]
    return folder_object_id


def create_folder_id(entry_id, folder_replid):
    folder_id = "%s%s00" % (entry_id[44:92], folder_replid)
    return folder_id


def id_to_guid(data):
    data_group = ["%s%s%s%s" % (data[6:8], data[4:6], data[2:4], data[0:2]), "%s%s" % (data[10:12], data[8:10]),
                  "%s%s" % (data[14:16], data[12:14]), data[16:20], data[20:]]
    return "-".join(data_group)


def search_mailbox_number(mailbox_guid):
    cmd = r"c:\tools\ese_edit.exe show-record table:Mailbox where:MailboxInstanceGuid=%s cols:MailboxNumber" % mailbox_guid
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    for line in p.stdout:
        reg = "\[(\d*)\]"
        search_items = re.search(reg, line)
        if search_items:
            return search_items.group(1)


def search_replid(mailbox_number, mail_guid):
    cmd = r"ese_edit.exe show-record table:ReplidGuidMap_%s where:guid=%s cols:Replid" % (mailbox_number, mail_guid)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    for line in p.stdout:
        reg = "\[(\d*)\]"
        search_items = re.search(reg, line)
        if search_items:
            int_repl = int(search_items.group(1))
            str_repr = str.upper(format(int_repl, '02x'))
            return str(str_repr)


def run(entry_id, mail_replid, mailbox_number):
    body = entry_id[-48:]
    message_id = "%s%s00" % (body, mail_replid)
    cmd = r"ese_edit.exe show-record table:Message_%s where:MessageId=%s" % (mailbox_number, message_id)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    for line in p.stdout:
        print(line)


def check_folder_id(folder_id, entry_id, replid, mailbox_number):
    body = entry_id[-48:]
    message_id = "%s%s00" % (body, replid)
    check_folder = r"ese_edit.exe show-record table:Message_%s where:MessageId=%s cols:FolderId" % (mailbox_number, message_id)
    p = subprocess.Popen(check_folder, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    for line in p.stdout:
        reg = "(FolderId = )\[(\w*)\]"
        search_items = re.search(reg, line)
        if search_items:
            folder_id_in_message = search_items.group(2)
            print("FolderId in message = %s" % folder_id_in_message)
            print("FolderId from EntryId = %s" % folder_id)
            if folder_id_in_message == folder_id:
                print("=" * 40)
                print("FoldersId is equal!!!")
                print("=" * 40)
            else:
                print("=" * 40)
                print("WARNING!!!   FoldersId is not equal!!!")
                print("=" * 40)


def main(args):
    entry_id = args[1]
    set_env(db_path, bin_folder, tmp)
    mailbox_instance_id = get_mailbox_instance_id(entry_id)
    mailbox_guid = id_to_guid(mailbox_instance_id)
    folder_object_id = get_folder_object_id(entry_id)
    message_object_id = get_message_object_id(entry_id)
    mail_guid = id_to_guid(message_object_id)
    mailbox_number = search_mailbox_number(mailbox_guid)
    mail_replid = search_replid(mailbox_number, mail_guid)
    folder_guid = id_to_guid(folder_object_id)
    folder_replid = search_replid(mailbox_number, folder_guid)
    folder_id = create_folder_id(entry_id, folder_replid)
    run(entry_id, mail_replid, mailbox_number)
    check_folder_id(folder_id, entry_id, mail_replid, mailbox_number)

if __name__ == "__main__":
    main(sys.argv)
