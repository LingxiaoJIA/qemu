#5 Dec 2012 - Collecting all ISS related functions in one python top module

import re
import string
import sys
import commands
import global_vars
import out_dat_analyser_singleBB
import dat_initialiser
import cmd


##################################################################################
#Func Name - orchestrate 
#Purpose - characterise a given basic block by executing it on the ISS
#Inputs  - Assumes uninited DAT input file already exists
#Output - 
##################################################################################
def orchestrate(startPCstr, endPCstr, predStartPCstr):
  #issInputRegPrefix = "RD n=NIA d=0x"
  #issInputMem1 = "MD n=Mem ra=0x00000000"
  #issInputMem2 = " d=0x"
  issStimPath =  ""
  extnStr = ".dat";
  issStimPref = "dat_0x";

  issRunCmd = ""
  issName = "/scratch/suhdarshan/cz_tools/uADL_ISS/g32ppcCAregLog"
  issRunOpts = " --trace --sce --mic=0 -o "
  cliSwitch = " --script=/scratch/suhdarshan/cz_tools/uADL_ISS/halt_simple.cli --script-arg="
  issTracePath = global_vars.outDATdir
  
  #===================  creating ISS input file name ===================
  issStimName = issStimPref + startPCstr + extnStr
  #input ISS stim with full path
  issStimPath = global_vars.inDATdir + issStimName
  #ISS trace output with full path
  issTrace = issTracePath + issStimName
  
  #ISS run command with full paths for input and output files
  issRunCmd = issName + cliSwitch + endPCstr + issRunOpts + issTrace\
              + " " + issStimPath

  #===================  Init DAT  ===================
  predIssTrace = issStimPref + predStartPCstr + extnStr

  if predStartPCstr != "0": #pred exists
    dat_initialiser.initDat(issStimName, predIssTrace)

  #===================  Exec ISS  ===================
  (status, output) = commands.getstatusoutput(issRunCmd)

  #=================== Analyse trace  ===================
  out_dat_analyser_singleBB.analyseDat(issStimName, endPCstr) 
   
   
###################################### Main ######################################
if __name__ == "__main__": #if this is the top module


  ##########################Command Line Parsing begins###########################
  import getopt

  #usage message
  usage = """\
  Usage: orchestrate.py [-s <BB start PC> -e <BB endPC> -p <pred BB start PC>]  
  """
  opts = "s:e:p:"
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
    if opt == '-s':
      bbStartAddr = arg
    elif opt == '-e':
      bbEndAddr = arg
    elif opt == '-p':
      predStartdAddr = arg

  ################################ Function Calls ################################
  orchestrate(bbStartAddr, bbEndAddr, predStartAddr)

