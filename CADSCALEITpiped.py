import os.path
from time import gmtime, strftime
from CADjob import CADjob
from SCALEITjob import SCALEITjob
from logFile import logFile
from SIGMAAjob import SIGMAAjob

class pipeline():
	# class to run CAD job to combine F and SIGF columns from
	# two merged mtz files, then to scale the 2nd datasets F 
	# structure factors against the 1st datasets
	def __init__(self,where,inputFile,jobName):

		# specify where output files should be written
		self.outputDir 			= where
		self.makeOutputDir()
		self.txtInputFile 		= inputFile
		self.jobName 			= jobName
		self.runLog 			= logFile('{}/{}_runLog_1.txt'.format(self.outputDir,jobName))

		# specify output files for parts of pipeline
		self.CADoutputMtz 		= '{}/{}_CADcombined.mtz'.format(self.outputDir,self.jobName)
		self.SCALEITinputMtz 	= self.CADoutputMtz
		self.SCALEIToutputMtz 	= '{}/{}_SCALEITcombined.mtz'.format(self.outputDir,self.jobName)

	def makeOutputDir(self):
		# if the above sub directory does not exist, make it
		if not os.path.exists(self.outputDir):
			os.makedirs(self.outputDir)
			print 'New sub directory "{}" made to contain output files'.format(self.outputDir)

	def runPipeline(self):

		# read input file
		success = self.readInputs()	
		if success is False:
			return 1

		# run SIGMAA job
		sigmaa = SIGMAAjob(self.SIGMAAinputMtz,self.Mtz1LabelName,self.RfreeFlag,
						   self.inputPDBfile,self.outputDir,self.runLog)	
		success = sigmaa.run()
		if success is False:
			return 2
		self.CADinputMtz1 = sigmaa.outputMtz

		# run CAD job 
		cad = CADjob(self.CADinputMtz1,self.CADinputMtz2,self.CADinputMtz3,
					 self.Mtz1LabelName,self.Mtz2LabelName,self.Mtz3LabelName,
					 self.Mtz1LabelRename,self.Mtz2LabelRename,self.Mtz3LabelRename,
					 self.CADoutputMtz,self.outputDir,self.runLog)
		success = cad.run()
		if success is False:
			return 3

 		# run SCALEIT job 
		scaleit = SCALEITjob(self.SCALEITinputMtz,self.SCALEIToutputMtz,
							 self.Mtz1LabelRename,self.Mtz2LabelRename,
							 self.outputDir,self.runLog)
		success = scaleit.run()
		if success is False:
			return 4

		# end of pipeline reached	
		return 0

	def readInputs(self):
		# open input file and parse inputs for CAD job

		# if Input.txt not found, flag error
		if self.checkFileExists(self.txtInputFile) is False:
			self.runLog.writeToLog('Required input file {} not found..'.format(self.txtInputFile))
			return False

		self.runLog.writeToLog('Reading inputs from {}'.format(self.txtInputFile))

		# parse input file
		inputFile = open(self.txtInputFile,'r')
		for line in inputFile.readlines():
			if line.split()[0] == 'END':
				break
			elif line[0] == '#':
				continue
			elif line.split()[0] == 'filename1':
				self.SIGMAAinputMtz 	= line.split()[1]
			elif line.split()[0] == 'labels1':
				self.Mtz1LabelName 		= line.split()[1]
			elif line.split()[0] == 'RfreeFlag1':
				self.RfreeFlag 			= line.split()[1]
			elif line.split()[0] == 'filename2':
				self.CADinputMtz2 		= line.split()[1]
			elif line.split()[0] == 'labels2':
				self.Mtz2LabelName 		= line.split()[1]
			elif line.split()[0] == 'filename3':
				self.CADinputMtz3 		= line.split()[1]
			elif line.split()[0] == 'labels3':
				self.Mtz3LabelName 		= line.split()[1]
			elif line.split()[0] == 'label1rename':
				self.Mtz1LabelRename 	= line.split()[1]
			elif line.split()[0] == 'label2rename':
				self.Mtz2LabelRename 	= line.split()[1]
			elif line.split()[0] == 'label3rename':
				self.Mtz3LabelRename 	= line.split()[1]
			elif line.split()[0] == 'inputPDBfile':
				self.inputPDBfile 		= line.split()[1]
		inputFile.close()
		return True

	def checkFileExists(self,filename):
		# method to check if file exists
		if os.path.isfile(filename) is False:
			ErrorString = 'File {} not found'.format(filename)
			print ErrorString
			self.runLog.writeToLog(ErrorString)
			return False
		else:
			return True
