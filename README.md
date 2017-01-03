# reconciliation_helper

Automate the daily workflow to prepare and upload the reconciliation files:

1. Search certain directory for all bank or trustee files.

2. Call the appropriate program to convert the files.

3. Remember which files have been converted, so that it only convert new files each time it runs. New files are newly added files or same file but last modified date changed.

4. Upload resulting files to sftp.

5. Summarize the result and save it to be read later.



++++++++++++++
Known Issues
++++++++++++++
1. When use git clone or pull or merge in a new location, the last modified time of the newly added files will be the sync time, instead of the file's original last modified time. This can cause some tests to fail.




++++++++++
Todo
++++++++++
1. Do we need to move testing mode to config file? or some default parameter to functions.

2. Add force process options, so that we can force process certain files:

	a. files in a certain folder.
	b. files whose last modified date is within X days compared that in the record.
	c. a particular file

3. Add a small tool to show its content, and delete all its contents, maybe just a short description on how to use sqlite3 CLI to do the trick?

4. Let write_csv() functions return the resulting file path, so that the upload function can use them to upload.

5. Add send email function to notify user about the process results.

6. Add upload result to the database, so that we don't need to upload old files?



++++++++++
ver 0.22
++++++++++
1. sftp.py is added to upload the csv files to sftp.clamc.com.hk.



++++++++++
ver 0.21
++++++++++
1. Test mode option is added to config file, with a default value set to empty string (not in test mode). When doing unittest, the testing code will set it to something else, to enable test mode. This way we don't need to pollute the code in record.py with the testmode global variable.



++++++++++
ver 0.2
++++++++++
1. A sqlite3 database is used to record the file process status, so that only new files or updated files are processed. The database contains two tables:
	
	a. lastest file process status (file, last modified time, pass or fail)
	b. all process results (id, file, last modified time, process time, pass or fail)



++++++++++
ver 0.1
++++++++++
1. Read input files, call converter program for jpm, bochk and dif (trustee).



