# reconciliation_helper

Automate the daily workflow to prepare and upload the reconciliation files:

1. Search certain directory for all bank or trustee files.

2. Call the appropriate program to convert the files.

3. Remember which files have been converted, so that it only convert new files each time it runs. New files are newly added files or same file but last modified date changed.

4. Upload resulting files to sftp.

5. Summarize the result and save it to be read later.



## Known Issues

1. When use git clone or pull or merge in a new location, the last modified time of the newly added files will be the sync time, instead of the file's original last modified time. This can cause some tests to fail.



## Trouble Shooting

Error: xlrd.biffh.XLRDError. This usually occurs when the program fails to load an Excel file using the xlrd package. Usually it is the JP Morgan broker statement. If you use Excel to open that file manually, you'll see a message saying "the file format and extension don't match." To solve the problem, save the file as "Excel workbook" (.xlsx) format. 

See error message and the Excel open error as below:

![image of program error](images/readfile_error.png)

![image of excel error](images/JPM file error.png)



## ver 0.33@2017-10-20

1. Added support for in house fund, bochk package also updated.



## ver 0.32@2017-8-17

1. Added Macau balanced fund and guarantee fund nav upload to server.




## ver 0.31@2017-8-16

1. Fixed logging issue by using new stand way of logging: logging.getLogger(__name__).

2. Now log to 2 files, one for everything, another just for errors.

3. Added DIF fund nav/units/unit_price upload to server, after these numbers are validated.

4. Valiation criteria: calculated unit_price and the unit price read from the excel file, should have a different < 0.0001 (i.e., the first 4 decimal points are identical).




## ver 0.30@2017-8-9

1. Added support for Star Helios fund (citibank).




## ver 0.29

1. Added support for Macau balanced fund and Macau guarantee fund.




## ver 0.28

1. Inside trustee.py, convert_trustee() function. Put a try/catch clause around the move() function. The reason is similar to 0.27 version, because when access rights have a problem, then move() function throws an exception, making subsequent upload and email notification process to stop. The utimate goal is to make convert_trustee() not to throw any exceptions even if something goes wrong.



## ver 0.27

1. Modified trustee.py, convert_trustee() function. The assumption in the recon_helper.py workflow is that none of the convert_xx() functions (convert_jpm, convert_bochk, etc.) throws exceptions so that subsequent upload process won't be interrupted even if one of the custodian bank files has a problem. But convert_trustee() throws an exception when one of the brokers files are missing (jpm_file, bochk_mc_file, bochk_hk_file). This is fixed.




## ver 0.26

1. Module greenblue.py has been added. Now it only filters out BOCHK files to handle, no CCB file handling yet.

2. The trustee sometimes put (A-MC) instead of (Class-A MC) in the BOCHK broker statement file, support for this filename has been added.

3. When something goes wrong in the conversion or upload process, the mail subject line becomes 'Error occurred during ...'.




## ver 0.25
1. convert_trustee() is added to enable automatic conversion, plus fix some minor bugs in convert_trustee(), like circular import and when the input file list is empty, it still do some processing.




## ver 0.24
1. trustee.py is added to include convert_trustee() function. 



## ver 0.23
1. mail.py is added to mail conversion and upload results to a list of recipients.



## ver 0.22
1. sftp.py is added to upload the csv files to sftp.clamc.com.hk.



## ver 0.21

1. Test mode option is added to config file, with a default value set to empty string (not in test mode). When doing unittest, the testing code will set it to something else, to enable test mode. This way we don't need to pollute the code in record.py with the testmode global variable.




## ver 0.2
1. A sqlite3 database is used to record the file process status, so that only new files or updated files are processed. The database contains two tables:
	
	1.1 lastest file process status (file, last modified time, pass or fail)

	1.2 all process results (id, file, last modified time, process time, pass or fail)




## ver 0.1

1. Read input files, call converter program for jpm, bochk and dif (trustee).



