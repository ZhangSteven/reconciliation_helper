
# coding=utf-8
#
# Handle dif BOCHK files
# 
from steven_utils.file import getFilenameWithoutPath
from steven_utils.utility import writeCsv, dictToValues
from bochk_revised.main import dateFromFilename, writeHoldingCsv, getRawCashPositions \
							 , cashPosition, getCashHeaders
from toolz.functoolz import compose
from functools import partial, reduce
from os.path import join
import logging
logger = logging.getLogger(__name__)



def processFiles(files, outputDir):
	"""
	[Iterable] files, [String] outputDir
		=> ([List] output files, [List] successful files, [List] failed files)
	
	This function does not throw any exceptions.
	"""
	isHoldingFile = compose(
		lambda s: s.lower().startswith('boc broker statement')
	  , getFilenameWithoutPath
	)

	isCashFile = compose(
		lambda s: s.lower().startswith('boc bank statement')
	  , getFilenameWithoutPath
	)


	try:
		date, outputHoldingCsvFiles, successfulHoldingFiles, failedHoldingFiles = \
			processHoldingFiles(filter(isHoldingFile, files), outputDir)

		outputCashCsvFiles, successfulCashFiles, failedCashFiles = \
			processCashFiles(filter(isCashFile, files), date, outputDir)

		return outputHoldingCsvFiles + outputCashCsvFiles \
			 , successfulHoldingFiles + successfulCashFiles \
			 , failedHoldingFiles + failedCashFiles

	except:
		logger.exception('processFiles()')
		return [], [], files



def processHoldingFiles(files, outputDir):
	"""
	[Iterable] files, [String] output directory => 
		( [String] date (yyyy-mm-dd)
		, [List] output files
		, [List] successfully processed files
		, [List] failed processed files
		)
	"""
	getDateFromFiles = compose(
		lambda L: L[-1]
	  , sorted
	  , partial(map, dateFromFilename)
	  , partial(map, getFilenameWithoutPath)
	)

	def getResult(acc, file):
		"""
		[Tuple] ([List] output files, [List] successful files, [List] failed files) acc
		[String] file
			=> acc
		"""
		try:
			return ( acc[0] + [writeHoldingCsv(outputDir, file)]
				   , acc[1] + [file]
				   , acc[2]
				   )
		except:
			return (acc[0], acc[1], acc[2] + [file])
	# end of getResult()

	return getDateFromFiles(files)
		 , reduce(getResult, files, ([], [], []))



def processCashFiles(files, date, outputDir):
	"""
	[Iterable] files, [String] date, [String] output directory => 
		( [List] output files
		, [List] successfully processed files
		, [List] failed processed files
		)
	"""
	# [Iterable] files => [Iterable] cash positions
	getCashPositions = lambda date, files: \
	compose(
		partial(map, partial(cashPosition, date))
	  , chain.from_iterable
	  , partial(map, getRawCashPositions)
	)(files)


	writeCashCsv = lambda date, outputDir, positions: \
	writeCsv( 
		join(outputDir, 'dif_' + date + '_cash.csv')
	  , chain( [getCashHeaders()]
	  		 , map(partial(dictToValues, getCashHeaders()), positions))
	  , delimiter='|'
	)


	def getResult(acc, file):
		"""
		[Tuple] ([List] output files, [List] successful files, [List] failed files) acc
		[String] file
			=> acc
		"""
		try:
			return ( acc[0] + [writeCashCsv(date, outputDir, file)]
				   , acc[1] + [file]
				   , acc[2]
				   )
		except:
			return (acc[0], acc[1], acc[2] + [file])
	# end of getResult()

	return reduce(getResult, files, ([], [], []))