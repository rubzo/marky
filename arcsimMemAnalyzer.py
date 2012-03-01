#!/usr/bin/python
import shutil

################## CONFIGURATION Section ####################################################################

massifFileHeader = "Massif TimeDelta ms,Massif TimeDelta s,Massif Heap B,Massif Heap MB"
massifEmptyOutput = ",,,"
arcsimFileHeader = "ArcSim TimeStamp ms,ArcSim TimeDelta s,ArcSim Mem B,ArcSim Mem MB"
arcsimEmptyOutput = ",,,"

analyzerOutFileHeader = massifFileHeader + "," + arcsimFileHeader + "\n"

################## CLASS Section ############################################################################
class MassifSnapshot:
	timeDeltaMs = 0 # time since startup in milliseconds
	timeDeltaS = 0 # time since startup in seconds
	
	heapUsefulB = 0 # current useful heap memory allocated by arcsim in Byte
	heapExtraB = 0 # current extra heap memory used due to arcsim allocations in Byte
	heapTotalB = 0 # current total heap memory used by arcsim in Byte
	
	heapUsefulMB = 0 # current useful heap memory allocated by arcsim in MByte
	heapExtraMB = 0 # current extra heap memory used due to arcsim allocations in MByte
	heapTotalMB = 0 # current total heap memory used by arcsim in MByte
		
	# constructor takes a list with entries like the following "timeDelta", "heapUsefulB","heapExtraB"
	def __init__(self, _dataSet):
		assert (len(_dataSet) == 3), "Given list has the wrong format!"
		
		self.timeDeltaMs = float(_dataSet[0])
		self.timeDeltaS = self.timeDeltaMs / 1000.0
		
		self.heapUsefulB = int(_dataSet[1])
		self.heapExtraB = int(_dataSet[2])
		self.heapTotalB = self.heapUsefulB + self.heapExtraB
		
		self.heapUsefulMB = self.heapUsefulB / (1024.0*1024.0)
		self.heapExtraMB = self.heapExtraB / (1024.0*1024.0)
		self.heapTotalMB = self.heapTotalB / (1024.0*1024.0)

	def getFileOutput(self):
		output = str(self.timeDeltaMs) + ","
		output += str(self.timeDeltaS) + ","
		output += str(self.heapUsefulB) + ","
		output += str(self.heapUsefulMB)
		
		return output

	# print data in this object
	def printData(self):
		print("timeDeltaMs:\t" +  self.timeDeltaMs)
		print("timeDeltaS:\t" +  self.timeDeltaS)
		print("heapUsefulB:\t" +  self.heapUsefulB, " B")
		print("heapExtraB:\t" +  self.heapExtraB, " B")
		print("heapTotalB:\t" +  self.heapTotalB, " B")
		print("heapUsefulMB:\t" +  self.heapUsefulMB, " MB")
		print("heapExtraMB:\t" +  self.heapExtraMB, " MB")
		print("heapTotalMB:\t" +  self.heapTotalMB, " MB")

#------------------------------------------------------------------------------------------------------------#
class ArcSimSnapshot:
	timeStampMs = 0 	# timeStamp in milliseconds
	timeDeltaS = 0 		# time since startup in seconds
	
	internalMemB = 0 	# current arcsim internal memory size in Byte
	internalMemMB = 0 	# current arcsim internal memory size in MByte
		
	# constructor takes a list with entries like the following "timeStampMs", "internalMemB"
	def __init__(self, _dataSet, _timeStampBaseMs):
		assert (len(_dataSet) == 2), "Given list has the wrong format!"
		
		self.timeStampMs = float(_dataSet[0])
		self.timeDeltaS = (self.timeStampMs - _timeStampBaseMs) / 1000.0
		
		self.internalMemB = int(_dataSet[1])
		self.internalMemMB = self.internalMemB / (1024.0*1024.0)

	def getFileOutput(self):
		output = str(self.timeStampMs) + ","
		output += str(self.timeDeltaS) + ","
		output += str(self.internalMemB) + ","
		output += str(self.internalMemMB)
		
		return output
		
	# print data in this object
	def printData(self):
		print("timeStampNs:\t" +  self.timeStampNs)
		print("timeStampMs:\t" +  self.timeStampMs)
		print("timeDeltaS:\t" +  self.timeDeltaS)
		print("internalMemB:\t" +  self.internalMemB, " B")
		print("internalMemMB:\t" +  self.internalMemMB, " MB")

################## FUNCTION Section #########################################################################

# Snapshot format in massif output files:
#-----------
#snapshot=0
#-----------
#time=0
#mem_heap_B=0
#mem_heap_extra_B=0
#mem_stacks_B=0
#heap_tree=empty
#
def parseMassifOutput(_massifOutFileName):
	snapshots = list()

	massifFile = open(_massifOutFileName)

	lastEntry = ["0","0","0"]
	snapshotDataSet = ["","",""]
	lineEntries = 0;
	
	for line in massifFile.readlines():
		if(lineEntries == 3):
			snapshots.append(MassifSnapshot(lastEntry))
			snapshots.append(MassifSnapshot(snapshotDataSet))
			
			lastEntry = snapshotDataSet
			snapshotDataSet = ["","",""]
			lineEntries = 0;	
		
		if line.strip():
			if(line.startswith("time=")):
				snapshotDataSet[0] = line.strip()[5:]
				lastEntry[0] = snapshotDataSet[0]
				lineEntries += 1
			elif(line.startswith("mem_heap_B=")):
				snapshotDataSet[1] = line.strip()[11:]
				lineEntries += 1
			elif(line.startswith("mem_heap_extra_B=")):
				snapshotDataSet[2] = line.strip()[17:]
				lineEntries += 1

	massifFile.close()
		
	return snapshots


def parseArcSimOutput(_arcsimOutFileName, _startTime):
	snapshots = list()
	# add empty start time snapshot
	snapshots.append(ArcSimSnapshot([str(_startTime),"0"], _startTime))
	
	arcsimFile = open(_arcsimOutFileName)

	for line in arcsimFile.readlines():
		if line.strip():
			dataSet = line.split(",")
			snapshots.append(ArcSimSnapshot(dataSet, _startTime))

	arcsimFile.close()
	
	return snapshots


def dumpMemProfileToFile(_analyzerOutFileName, _massifSnapshots, _arcsimSnapshots):
	try:
		resultFile = open(_analyzerOutFileName, "w")

		resultFile.write(analyzerOutFileHeader)
		massifDataPos = 0 
		arcsimDataPos = 0
		
		while(massifDataPos < len(_massifSnapshots) or 
			  arcsimDataPos < len(_arcsimSnapshots)):
			
			if(massifDataPos < len(_massifSnapshots)):
				resultFile.write(_massifSnapshots[massifDataPos].getFileOutput())
				massifDataPos += 1
			else:
				resultFile.write(massifEmptyOutput)
			
			resultFile.write(",")
			
			if(arcsimDataPos < len(_arcsimSnapshots)):
				resultFile.write(_arcsimSnapshots[arcsimDataPos].getFileOutput())
				arcsimDataPos += 1
			else:
				resultFile.write(arcsimEmptyOutput)
				
			resultFile.write("\n")
	
	finally:
		resultFile.close()

# _arcSimOutName: Name of the mem profile arcsim creates
# _massifOutName: Name of the mem profile massif creates
# _analyzerOutName: Name of the resulting output file this script produces
# _startTime: Start timestamp in milliseconds when the arcsim run started
##
def analyzeArcSimMem(_arcSimOutName, _massifOutName, _analyzerOutName, _startTime):
	# parse massif output
	massifSnapshots = parseMassifOutput(_massifOutName)
	
	# parse arcsim output
	arcsimSnapshots = parseArcSimOutput(_arcSimOutName, _startTime)
	
	# dump mem data to file
	dumpMemProfileToFile(_analyzerOutName, massifSnapshots, arcsimSnapshots)
	
	# copy results
	shutil.copy(_analyzerOutName, "/tmp")
	
	
	