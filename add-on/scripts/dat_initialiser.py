import re
import sys
import global_vars
import fileinput

##################################################################################
#Func Name - initDat
# Purpose - Init registers and memory locations in the incomplete DAT file  by 
#           reading the RESULTS section of the given DAT file 
#Inputs  - incmpltDat - Incomplete DAT file to be inited
#          initingDat - DAT file whose RESULTS section will be used for initing
##################################################################################
def initDat(incmpltDat, initingDat):
  initingDatPtr = 0
  incmpltDatFile = global_vars.inDATdir + incmpltDat
  initingDatFile = global_vars.outDATdir + initingDat

  datHeader = [""" TEST id=0
INIT

CORE n=:powerpc

"""]

  initingDatPtr = open(initingDatFile ,'r')

  start = 0
  for datLine in initingDatPtr:
    if start == 0:
      m = re.search("RESULTS", datLine) #look for start of RESULTS section
      if m != None:
        start = 1
        continue
    else:
      datHeader.append(datLine) #copy RESULTS section of initing DAT
                                #to temporary buffer
 
  initingDatPtr.close() #close initing DAT file
  
  #13 June 2012 - Not adding NIA initing line because that has been done
  #while building prelim DATs. Even though RESULTS section of initing DAT 
  #will have a value for NIA, since it is inserted at top of prelimDAT, 
  #the later NIA set will take effect.

  #insert temp buffer at top of incomplete DAT file
  init = 1
  for line in fileinput.input(incmpltDatFile, inplace=1):
    if init == 1: #in the insertion phase
      for str in datHeader:
        print str
 
      init = 0 #insertion over

    print line, 


###################################### Main ######################################
if __name__ == "__main__": #if this is the top module


  ##########################Command Line Parsing begins###########################
  import getopt

  #usage message
  usage = """\
  Usage: out_dat_analyser.py [-i <OUT DAT file of the predecessor> -o <IN dat file to ISS>]  
  """
  opts = "i:o:"
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], opts) #GNU style proc. of args
  													 #option n non-options args 
                                                     #can be mixed 
  except getopt.GetoptError, msg:
    sys.stderr.write("Error: %s\n" % str(msg))
    sys.stderr.write(usage)
    sys.exit(1)

  for opt,arg in opts:
    if opt == '-i':
      initingDat = arg
    elif opt == '-o':
      incmpltDat = arg

  initDat(incmpltDat, initingDat)

