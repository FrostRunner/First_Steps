Check_blobs
===========
<b>Назначение</b>
Скрипт для извлечения и проверки блобов на парс из всей базы Exchange 2013.

При нахождении ошибок в парсе будет сформирован файл с зафейлившемся блобом в папке ..\blobs_storage\garbage
вида Message_<MailboxId>.txt_<MessageDocumentId=XXX>_<TypeBlob>.txt

Пример: Message_105.txt_MessageDocumentId=1118_PropertyBlob.txt


<b>Требования</b></p>
  1) Параметры по умолчанию в скрипте следующие, их необходимо изменить под свое окружение.

db_path = r"E:\DB\RND13.edb" - путь до базы из которой планируется извлечение блобов 
used_database = "RND13" - имя базы
bin = "C:\\tools" - путь до каталога с файлом ese.dll
tmp = "C:\\tmp" - путь к папки temp

  2) Файлы eseblob.exe и mail_restore_2013.exe должны лежать в папке C:\tools\

<b>Команды</b></p>
Что бы запустить программу необходимо запустить скрипт с помощью питона и указать путь к папке куда будут сохранены базы блобов и файлы с ошибками

C:\Python27\python.exe check_blob.exe C:\blobs
