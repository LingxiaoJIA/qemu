#Filename - out_dat_analyser.py
#Date created - 18 Nov 2011
#Last modified - 9 Dec 2012
#Author - Suhas Chakravarty
#Purpose - Extract execution time of basic blocks from 
#          uADL ISS trace (DAT output)
#Algo - For specified trace file (DAT), extract timing. 
#    Look for "TRACE" keyword in file. Thereafter, look for "I ea=<addr>", 
#    where addr is the starting address of the basic block
#       If the pred. is same as the bb, then look for second instance of this.
#       Next look for "ITIME" and record time from the "t=n" phrase in the same
#       line. Thereafter, look for "I ea=<addr>", where addr is the ending
#       address of the basic block. Again, look for "ITIME" and record time.
#       Subtract the two times to get execution time of the basic block.
#       To calculate overlap, hunt for "I ea=<addr>", where addr is 
#       ending address of the pred. Record its time instant and compare with
#       bb start time to calculate overlap. 
#4 Oct12 - Making change that was tried on 30 Sep for BB power calc. trying bbDuration - overlap instead of just
#          bbDuration.

import re
import string
import sys
#import os
import commands
import global_vars
#import bin_vars

DEBUG_PRINT = 0

Int_instNames = [ "sub", "add", 'la', "div", "mul", \
"or","mr", "xor", "and", "crxor", "creqv", "crand", "crnand", "crnor","cror", \
"clrlslwi", "clrlwi", "clrrwi", \
"nand", "neg", "nor", \
#extended mnemonics for addi and addis - 7 June 2012. Remove from load
"li", "lis", \
#shift inst's 
"rlw","rld","slw", "srw","sraw","sld","srad","srd", \
#compare inst's 
"cmp", "eqv", \
#count leading zeroes 
"cntlz" \
]

Br_instNames = [ "bc", "bl","ba","bd","be","bg", "bn", "b" ] 

Ld_instNames = [ "lbz", "lhz", "lwz", "ld", "lh", "lmw","lw" ]

St_instNames = [ "st" ]


##################################################################################
#Func Name - getInstr
# Purpose - get instruction name from given DAT trace file line
#Inputs  - 1. DAT trace file line containing assembly instruction.
#          2. m ( the initial instruction marker search result)
#Algo - extracts line start to first space and returns extracted portion
##################################################################################
def getInstr(m, codeLine):
  tmpString = codeLine[m.end():]
  n = re.search(" ", tmpString)
  instrName = tmpString[:n.start()] #assuming n is not False, i.e. there is
                                    #always a space
  return instrName

##################################################################################
#Func Name - createPowerToolInput
# Purpose - create input for Power Estimation tool (McPAT) in required format
#           for a certain BB
#Inputs  - 1. Output DAT File name of corresponding BB
#          2. dictionary containing BB execution statistics
#Outputs - Name of input file created
#Algo - Use existing McPAT input file as template, replacing stat values with
#       the ones in the dictionary
##################################################################################
def createPowerToolInput(datFile, statRec):
  pwrToolInFileName = string.replace(datFile,"dat", "xml") 
  pwrToolInFile = global_vars.inPwrTooldir + pwrToolInFileName
  statGeneralMark = "stat name="
  copy = False

  fin = open(global_vars.PwrToolTmplt, 'r')
  fout = open(pwrToolInFile, 'w')
  
  #read power tool input template file line by line
  for line in fin:
    if re.search(statGeneralMark, line) != None: #this is a stat type line
      #now look if this is a relevant stat
      relevantStatFound = 0
      for stat,val in statRec.iteritems():
        statMark = statGeneralMark + "\"" + stat + "\""
        m = re.search(statMark, line)
        if m != None: #insert value of stat in this line
          relevantStatFound = 1
          newLine = line[:m.end()] + " value=\"" + str(val) + "\"/>\n" 
          fout.write(newLine) #write out to file
          break
      
      if relevantStatFound == 0: #means this line should be simply copied 
        fout.write(line)
    else:
      fout.write(line) #simply copy line

  fin.close()
  fout.close()

  return pwrToolInFileName

##################################################################################
#Func Name - runPowerTool
# Purpose - Execute reference power tool (McPAT)
#Inputs  - 1.Appropriate power tool input file 
#Outputs - name of run log file
##################################################################################
def runPowerTool(inFileName):
  ##iterate over all the Power Tool input files
  #for inFile in os.listdir(global_vars.inPwrTooldir):
  #sys.stderr.write("Debug: Running Power Tool for %s\n\n" %inFileName) 
  logFile = string.replace(inFileName, ".xml", "mcpat_log")
  runCmd = global_vars.Pwr_Tool + " -infile " + global_vars.inPwrTooldir + \
           inFileName + " -print_level 1 " + ">& " + global_vars.outPwrTooldir \
           + logFile

  (status, output) = commands.getstatusoutput(runCmd)
  
  return logFile

##################################################################################
#Func Name - analysePowerLog
# Purpose - Extract power consumption figure from power tool run log. This is for
#           a basic block.
#Inputs  - Power tool run log
##################################################################################
def analysePowerLog(logFileName):
  mark1 = "Total Cores"
  mark2 = "Runtime Dynamic = "
  ##iterate over all Power Tool run log files
  #for logFile in os.listdir(global_vars.outPwrTooldir): 
  mark1Found = 0
  mark2Found = 0
  power = 0.0
  logFile = global_vars.outPwrTooldir + logFileName
  #sys.stderr.write("Debug: Analysing Power Log %s\n\n" %logFile)
  
  fPtr = open(logFile, 'r') #open power tool log file in read mode
  
  #iterate over each line
  for line in fPtr:
    if mark1Found == 0:
      if re.search(mark1, line) != None: #match
        mark1Found = 1
        #sys.stderr.write("Debug: Found mark 1 in %s\n" %logFileName)
      continue

    m = re.search(mark2, line)
    if m != None: #match
      #found the line with the power number
      #sys.stderr.write("Debug: Found mark 2 in %s\n\n" %logFileName)
      mark2Found = 1
      #strip away non-numeric characters
      tmpString = string.replace( line[m.end():], " W\n", "")  
      power = float(tmpString) #power in watts
      break #don't need to look at log file anymore
 
  if mark2Found == 0:
    #error condition
    sys.stderr.write("Error: Power Tool run log not in expected format\n\n")
    return -1
  else:
    return power

##################################################################################
#Func Name - analyseDat
# Purpose - read output DAT file and execute algo decribed above.
#Inputs  - Name of DAT to be analysed. Assumes it is located
#  at path specified by outDATdir in global_vars. 
#  addresses of first and last instructions in the BB/TB
#  address of last instruction in predecessor     
#Output - A file with the cycle count as analysed, after accounting 
#  for overlap. File name is input dat file with .metric extension. 
#  First line is cycle count, second (when implemented) is energy
##################################################################################
def analyseDat(iDat, bbStartAddr, bbEndAddr, predEndAddr):
  traceSection = "TRACE"
  resultSection = "RESULTS"
  iTimeMarker = "ITIME t="
  regRdMark = "R a=read"
  regWrMark = "R n="
  memRdMark1 = "M n=Mem t=read"
  memRdMark2 = "M n=Mem t=ifetch"
  memWrMark = "M n=Mem t=write"
  instrMark = "asm=\""
  instrAdrMark = "I ea="
  TimeDebug = 1
 
  ##condition for enabling Debug prints
  #if iDat == "SolveCubic_SolveCubicbb_7_main_main_3.dat":
  #  TimeDebug = 1
  #else:
  #  TimeDebug = 0

  ######################## Variables ##################################
  bbOneLong = 0 #Flag indicating Bb is one instruction long
  if bbEndAddr == bbStartAddr:
    bbOneLong = 1

  resultName = string.replace(iDat, ".dat", ".metric") #output file name
  resultFile = global_vars.resultDir +  resultName #output file full path     
  iFile = global_vars.outDATdir +  iDat #input file full path     


  #subBbSstring = instrAdrMark + subBbSaddr
  bbSstring = instrAdrMark + bbStartAddr
  bbEstring = instrAdrMark + bbEndAddr
  pEstring = instrAdrMark + predEndAddr
  phaseString = [pEstring, bbSstring, bbEstring]
  if TimeDebug:
    sys.stderr.write("Debug. PredEnd %s\n" % phaseString[0] )
    sys.stderr.write("Debug. BBStart %s\n" % phaseString[1] )
    sys.stderr.write("Debug. BBEnd %s\n" % phaseString[2] )
  
  traceStart = 0 #flag to denote whether have reached TRACE portion of DAT
 
  phase = 0 # 0 - look for predecessor's ending instruction time
            # 1 - look for BB's starting instruction time
            # 2 - look for BB's ending instruction time
  if predEndAddr == "0": #if no predecessor, skip phase 0
    phase = 1

  timeRecord = [0,0,0] #records times for the three phases, in that order
  phaseFound = 0 #Has the current phase been found
  timingDone = 0 #Flag to indicate that timing analysis of DAT is complete
  recordStats = 0 #Flag to enable recording of stats
  #endAddrFound = 0

#rresenting stats needed by McPAT, only relevant ones for now
  #statRec = { "total_cycles" : 0, "idle_cycles" : 0, "busy_cycles" : 0, \
  #            "total_instructions" : 0, "int_instructions" : 0, "branch_instructions" : 0, \
  #            "branch_mispredictions" : 0, "load_instructions" : 0, "store_instructions" : 0, \
  #            "committed_instructions" : 0, "committed_int_instructions" : 0, \
  #            "inst_window_reads" : 0, "inst_window_writes" : 0, "int_regfile_reads" : 0, \
  #            "int_regfile_writes" : 0, "function_calls" : 0, "context_switches" : 0, \
  #            "ialu_accesses" : 0, "mul_accesses" : 0, "cdb_alu_accesses" : 0, \
  #            "cdb_mul_accesses" : 0, "memory_accesses" : 0, "memory_reads" : 0, \
  #            "memory_writes" : 0 } 

  ###################### Variables end ################################
 
  iFilePtr = open(iFile, 'r') #open output DAT file 
                                    #in read mode
  resultFilePtr = open(resultFile, 'w') #open metric logging file

  #read line by line
  for codeLine in iFilePtr:
    instrMatched  = 0
    instrName = "" #placeholder for name of instruction encountered in DAT

    if traceStart == 0: #hunt for TRACE section if not found yet
      m = re.search(traceSection, codeLine)
      if m != None: #there is a match 
        traceStart = 1
      continue #skip to next line
    
    #Trace section found. Now extract timing  and access stats of block.
   
    ########################## Stats collection ###########################
    #if recordStats == 1: #these lines are part of the bb for which
    #                     #stats need to be collected

    #  #register reads #could have continues for matches?
    #  if re.search(regRdMark, codeLine) != None: #match
    #    statRec["int_regfile_reads"] = statRec["int_regfile_reads"] + 1
    #  #register writes
    #  elif re.search(regWrMark, codeLine) != None: #match
    #    statRec["int_regfile_writes"] = statRec["int_regfile_writes"] + 1
    #  #memory reads
    #  elif re.search(memRdMark1, codeLine) != None: #match
    #    statRec["memory_reads"] = statRec["memory_reads"] + 1
    #  elif re.search(memRdMark2, codeLine) != None: #match
    #    statRec["memory_reads"] = statRec["memory_reads"] + 1
    #  #memory writes
    #  elif re.search(memWrMark, codeLine) != None: #match
    #    statRec["memory_writes"] = statRec["memory_writes"] + 1
    #  
    #  #instruction logging
    #  m = re.search(instrMark, codeLine) #check if it is an instruction
    #  if m != None: #match
    #    statRec["total_instructions"] = statRec["total_instructions"] + 1
    #    instrName = getInstr(m, codeLine) #extract instruction name

    #    for intInst in Int_instNames: #iterate over all integer insts
    #                                  #to check for a match
    #      n = re.search(intInst, instrName)
    #      if n != None: #match
    #        #check if the match is at the starting. Only then is it valid
    #        if n.start() == 0:
    #          instrMatched = 1 #type of instruction has been determined
    #          statRec["int_instructions"] = statRec["int_instructions"] + 1  
    #          if intInst == Int_instNames[3] or \
    #             intInst == Int_instNames[4]: #mul or div instruction
    #            statRec["mul_accesses"] = statRec["mul_accesses"] + 1
    #            statRec["cdb_mul_accesses"] = statRec["cdb_mul_accesses"] + 1
    #          else:
    #            statRec["ialu_accesses"] = statRec["ialu_accesses"]+ 1
    #            statRec["cdb_alu_accesses"] = statRec["cdb_alu_accesses"]+ 1

    #          break
    #     
    #    #if type of instruction determined, skip this check
    #    if instrMatched == 0:
    #      for brInst in Br_instNames: #iterate over all branch insts
    #                                    #to check for a match
    #        n = re.search(brInst, instrName)
    #        if n != None: #match
    #          #check if the match is at the starting. Only then is it valid
    #          if n.start() == 0:
    #            instrMatched = 1 #type of instruction has been determined
    #            statRec["branch_instructions"] = statRec["branch_instructions"] \
    #                                             + 1  
    #            #check if this is a function call
    #            if brInst == "bl" or brInst == "bcl" or brInst == "bclrl" \
    #               or brInst == "bcctrl": 
    #              statRec["function_calls"] = statRec["function_calls"] + 1
    #              #assuming each function call also results in a return, there
    #              #are 2 context switches. But won't be true when tail calls
    #              #are chained, right? - Suhas, 23 Jan 2012
    #              statRec["context_switches"] = statRec["context_switches"] + 2

    #            break

    #    #if type of instruction determined, skip this check
    #    if instrMatched == 0:
    #      for ldInst in Ld_instNames: #iterate over all load insts
    #                                    #to check for a match
    #        n = re.search(ldInst, instrName)
    #        if n != None: #match
    #          #check if the match is at the starting. Only then is it valid
    #          if n.start() == 0:
    #            instrMatched = 1 #type of instruction has been determined
    #            statRec["load_instructions"] = statRec["load_instructions"] + 1  
    #            break

    #    #if type of instruction determined, skip this check
    #    if instrMatched == 0:
    #      for stInst in St_instNames: #iterate over all store insts
    #                                    #to check for a match
    #        n = re.search(stInst, instrName)
    #        if n != None: #match
    #          #check if the match is at the starting. Only then is it valid
    #          if n.start() == 0:
    #            instrMatched = 1 #type of instruction has been determined
    #            statRec["store_instructions"] = statRec["store_instructions"] + 1  
    #            break

    ######################## Timing Analysis ##############################
    if phaseFound == 0: #if this phase's instruction hasn't been found yet
                          #search for this phase's instruction
      m = re.search(phaseString[phase], codeLine) 
      if m != None: #match
        if phase == 1: 
          recordStats = 1 #since BB starting has been recored 
        phaseFound = 1
        if TimeDebug:
          sys.stderr.write("Debug. Found phase %d on line %s\n" \
                            % (phase, codeLine) )
      continue #skip to next line
    
    #found this phase's instruction
    #Next, look for this phase's ITIME
    m = re.search(iTimeMarker, codeLine) 
    if m != None: #there is a match
      timeRecord[phase] = int( codeLine[m.end():] ) #record time
      if TimeDebug:
        sys.stderr.write("Debug. For phase %d, time is %d on line %s\n"\
                          %(phase, timeRecord[phase], codeLine))

      #reset phase markers
      phaseFound = 0
      if (phase == 2) or ( (phase == 1) and bbOneLong ):
        timingDone = 1 #timing analysis complete
        phaseFound = 1 #not resetting flag as timing analysis is complete

      phase = phase + 1 # go to next phase

    #look for end of TRACE section to mark end of analysis of DAT
    #but only once the timing analysis has been completed
    if timingDone == 1:
      m = re.search(resultSection, codeLine) 
      if m != None: #match
        break
  ################ end of a single DAT file analysis ################

  #Debug prints
  if TimeDebug:
    sys.stderr.write("Debug. In DAT %s \n" %iDat)  
    sys.stderr.write("Pred end t=%d, BB start t=%d, end t=%d\n" \
                      %(timeRecord[0], timeRecord[1], timeRecord[2]) )  
  
  #Calculate overlap of bb with pred.
  #When bb starts on the cycle right after pred ends, there is no overlap
  #if it starts on or before the cycle the pred ends, there is a positive
  #overlap, which needs to be subtracted from the bb's cycle count
  #if it starts more than a cycle after the pred ends, there is a -ve
  #overlap, the absolute value of which needs to be added to the bb's 
  #cycle count
  overlap = timeRecord[0] - timeRecord[1] + 1 

  if bbOneLong: #if only one instruction in BB, set endtime to
                #start time
    #sys.stderr.write("BB %s is one instruction long\n" % bbStartAddr)
    timeRecord[2] = timeRecord[1]

  #duration of the bb
  bbDuration =  timeRecord[2] - timeRecord[1] + 1 - overlap
  #write to output file
  resultFilePtr.write( str(bbDuration) )

  ##################Filling up BB execution statistics record################
  ##statRec["total_cycles"] = subBbduration
  ##statRec["busy_cycles"] = subBbduration
  #statRec["total_cycles"] = subBbduration - overlap
  #statRec["busy_cycles"] = subBbduration - overlap
  ##assuming all instructions were committed. Not sure how to get the number
  ##of non-committed instructions
  #statRec["committed_instructions"] = statRec["total_instructions"]
  #statRec["committed_int_instructions"] = statRec["int_instructions"]
  #statRec["inst_window_reads"] = statRec["total_instructions"]
  #statRec["inst_window_writes"] = statRec["total_instructions"]
  #statRec["memory_accesses"] = statRec["memory_reads"] + statRec["memory_writes"]

  #Debug prints
  #if iDat == "main_mainbb_14_main_mainbb_16_out.dat":
  #  #sys.stderr.write("Debug. In file %s \n" %file)  
  #  #sys.stderr.write("Reg reads =%d, Reg Writes =%d, Mem reads =%d, Mem writes =%d \n" \
  #  #                  %(statRec["int_regfile_reads"], statRec["int_regfile_writes"], \
  #  #                    statRec["memory_reads"], statRec["memory_writes"]) )  
  #  #sys.stderr.write("Accesses: ALU =%d, MUL =%d, Function Call =%d \n" \
  #  #                  %(statRec["ialu_accesses"], statRec["mul_accesses"],\
  #  #                    statRec["function_calls"]) )  
  #  #sys.stderr.write("Instructions: Total =%d, Integer =%d, Branch =%d, Load =%d, Store =%d \n\n" \
  #  #                  %(statRec["total_instructions"], statRec["int_instructions"], \
  #  #                    statRec["branch_instructions"], statRec["load_instructions"], \
  #  #                    statRec["store_instructions"]) )  
  #  print ("\nIn file " + iDat + " stats are \n")
  #  print statRec
  
  #####################Power Stuff####################################
  #commenting out the running of McPAT as it takes a lot of time. This is for 
  #debug only. Uncomment otherwise - Suhas, 25 Jan 2012
  ##Now create the input file needed as the power tool's input for this BB
  ##bbPwrInFile = createPowerToolInput(file, statRec)
  #bbPwrInFile = createPowerToolInput(iDat, statRec)
 
  ##Run the Power Tool
  #bbPwrLogFile = runPowerTool(bbPwrInFile)

  ##Extract power consumption from power tool run log
  #subBbPower = analysePowerLog(bbPwrLogFile)
  ##subBbPower = 0.4

  ##calculate correponding energy, using the duration of the BB
  ##subBbEnergy = subBbPower * subBbduration * 1/global_vars.Proc_Frequency * 0.000001
  #subBbEnergy = subBbPower * (subBbduration - overlap) * 1/global_vars.Proc_Frequency * 0.000001
  #sys.stderr.write("Debug. In file %s \n" %file)  
  #sys.stderr.write("Power: %f W, Energy: %e J\n\n" %(subBbPower, subBbEnergy))  
  
  ##debug print
  #if DEBUG_PRINT == 1:
  #  for dat, v in cpDatRec.iteritems():
  #    print dat + ":"
  #    print v
  #    sys.stderr.write("\n")

  resultFilePtr.close()

  iFilePtr.close()


###################################### Main ######################################
if __name__ == "__main__": #if this is the top module


  ##########################Command Line Parsing begins###########################
  import getopt

  #usage message
  usage = """\
  Usage: out_dat_analyser.py [-i <name of DAT file to be analysed> -I <BB end address>]  
  """
  opts = "i:I:"
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], opts) #GNU style proc. of args
  													 #option n non-options args 
                                                     #can be mixed 
  except getopt.GetoptError, msg:
    sys.stderr.write("Error: %s\n" % str(msg))
    sys.stderr.write(usage)
    sys.exit(1)
  
  #if not args:
  #  sys.stderr.write("Error: no inputs specified\n")
  #  sys.stderr.write(usage)
  #  sys.exit(1)
  
  # process options
  for opt,arg in opts:
    if opt == '-i':
      inDatName = arg
    elif opt == '-I':
      bbEndAddr = arg

  ################################ Function Calls ################################
  
  #analyse DAT trace of ISS run to get BB timing. Record timing in
  #file in given out path
  analyseDat(inDatName, bbEndAddr)

