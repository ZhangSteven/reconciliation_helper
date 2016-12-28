# reconciliation_helper

Automate the daily workflow to prepare and upload the reconciliation files:

1. Search certain directory for all bank or trustee files.

2. Call the appropriate program to convert the files.

3. Remember which files have been converted, so that it only convert new files each time it runs. New files are newly added files or same file but last modified date changed.

4. Upload resulting files to sftp.

5. Summarize the result and save it to be read later.



++++++++++
Todo
++++++++++
1. Do we need to move testing mode to config file? or some default parameter to functions.

2. Add force process options, so that we can force process files in a certain folder, and/or whose last modified date is not older X days than that in the record.

3. Remove the database from .gitignore, but add a small tool to show its content, and delete all its contents.



++++++++++
ver 0.2
++++++++++
1. A sqlite3 database is used to record the file process status, so that only new files or updated files are processed. The database contains two tables:
	
	a. file process status (file, last modified time, pass or fail)
	b. list of process operations (id, file, last modified time, process time, pass or fail)

	It is designed like this because later we may need to force process files no matter whether they are newer or is updated since last processed.


++++++++++
ver 0.1
++++++++++
1. Read input files, call converter program for jpm, bochk and dif (trustee).



