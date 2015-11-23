import re
import string
import sys
import commands
import global_vars
import out_dat_analyser
import dat_initialiser
import cmd


##################################################################################
#Func Name - orchestrate 
#Purpose - characterise a given basic block by executing it on the ISS
#Inputs  - Assumes uninitialized DAT input file already exists
#Output - 
##################################################################################
def orchestrate(issStimNamestr, bbStartPCstr, bbEndPCstr, predEndPCstr, \
               gfatherStartPCstr, gGfatherStartPCstr, brkCntstr):
  #issInputRegPrefix = "RD n=NIA d=0x"
  #issInputMem1 = "MD n=Mem ra=0x00000000"
  #issInputMem2 = " d=0x"
  issStimPath =  ""
  extnStr = ".dat";
  issStimPref = "dat_0x";

  issRunCmd = ""
  issName = "/scratch/suhdarshan/cz_tools/uADL_ISS/g32ppcCA_twkd_regLog"
  issRunOpts = " --trace --sce --mic=0 -o "
  cliSwitch1 = " --script=/scratch/suhdarshan/cz_tools/uADL_ISS/halt.cli --script-arg="
  cliSwitch2 = " --script-arg="
  
  #===================  creating ISS input file name ===================
  #issStimName = issStimPref + startPCstr + extnStr
  #input ISS stim with full path
  issStimPath = global_vars.inDATdir + issStimNamestr
  #ISS trace output with full path
  issOutTrace = global_vars.outDATdir + issStimNamestr
  
  #ISS run command with full paths for input and output files
  issRunCmd = issName + cliSwitch1 + bbEndPCstr + cliSwitch2 +brkCntstr +\
              issRunOpts + issOutTrace + " " + issStimPath

  #===================  Init DAT  ===================
  gfatherIssTrace = ""

  if gfatherStartPCstr != "0": #grandfather exists
    if gGfatherStartPCstr != "0": #great gfather exists
      gfatherIssTrace = issStimPref + gGfatherStartPCstr + "_0x" + \
                        gfatherStartPCstr + extnStr
    else:
      gfatherIssTrace = issStimPref + gfatherStartPCstr + extnStr
 
    sys.stderr.write("Debug print. Going to init %s\n" %issStimNamestr)
    dat_initialiser.initDat(issStimNamestr, gfatherIssTrace)

  #===================  Exec ISS  ===================
  sys.stderr.write("Debug print. Going to execute %s on ISS\n" %issStimNamestr)
  (status, output) = commands.getstatusoutput(issRunCmd)

  #=================== Analyse trace  ===================
  sys.stderr.write("Debug print. Going to analyse ISS trace for %s\n" %issStimNamestr)
  out_dat_analyser.analyseDat(issStimNamestr, bbStartPCstr, \
                              bbEndPCstr, predEndPCstr) 
   
   
###################################### Main ######################################
if __name__ == "__main__": #if this is the top module


  ##########################Command Line Parsing begins###########################
  import getopt

  #usage message
  usage = """\
  Usage: orchestrate.py [ -n <ISS stim name > -s <BB start PC> -e <BB endPC> 
                        -p <pred end PC> -g <gfather start PC> 
                        -G <Ggfather start PC> -b <break count>]  
  """
  opts = "n:s:e:p:g:G:b:"
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
    if opt == '-n':
      issStimName = arg
    elif opt == '-s':
      bbStartAddr = arg
    elif opt == '-e':
      bbEndAddr = arg
    elif opt == '-p':
      predEndAddr = arg
    elif opt == '-g':
      gfatherStartAddr = arg
    elif opt == '-G':
      gGfatherStartAddr = arg
    elif opt == '-b':
      brkCnt = arg

  ################################ Function Calls ################################
  orchestrate(issStimName, bbStartAddr, bbEndAddr, predEndAddr, \
              gfatherStartAddr, gGfatherStartAddr, brkCnt)

