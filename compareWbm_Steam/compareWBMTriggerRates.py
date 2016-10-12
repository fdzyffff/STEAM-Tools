import os
from compareWBMTriggerRates2 import *
#####################################################################################
# input 1, get information from wbm
c1 = getRateInformation("wbm")
c1._runnr = "279116"
c1.output_dir = "example_outputFile"
c1.json_name = "json.txt"
c1.index_lumi = "9.5e33"
c1.useLumiScale = False
#c1.target_lumi = "9.5e33"
#c1.useLumiScale = True

dic_1 = c1.getRateListRun()
#print dic_1["info"]
#####################################################################################

#####################################################################################
# input 2, get information from steam tables
#input steam information
c2 = getRateInformation("steam")
c2._runnr = "279116"
c2.output_dir = "example_outputFile"
c2.useLumiScale = False
#c2.input_lumi = "9.5e33"
#c2.target_lumi = "9.5e33"

# get steam rates from file
c2.file1_name = "examples_inputFiles/output.tsv"
c2.file1_hltpath = 1          #HLT_
c2.file1_hltrate = 4          #hlt rate
c2.file1_hltrateErr = 6       #hlt rate error
c2.file1_dataset = 2          #l1 prescale
c2.file1_group = 3          #l1 prescale
    
# get L1 seed information from file3, need hlt name, l1 seed.
c2.file3_name = 'examples_inputFiles/L1Seed.tsv'
c2.file3_hltpath = 0           #HLT_
c2.file3_l1seed = [18]         #L1_seed
    
# get L1 PS information from file4, need l1 name, l1 PS
c2.file4_name = 'examples_inputFiles/L1_PS.csv'
c2.file4_l1path = 1           #L1_
c2.file4_l1prescale = 5     #l1 prescale
 
# get HLT PS information from file5, need hlt name, hlt PS
c2.file5_name = 'examples_inputFiles/outputTSV.tsv'
c2.file5_hltpath = 2           #HLT_
c2.file5_hltprescale = 8       #hlt prescale

# get HLT Count information from file6, need hlt name, hlt Count
c2.file6_name = 'examples_inputFiles/outputCounts.tsv'
c2.file6_hltpath = 1           #HLT_
c2.file6_hltcount = 5      #hlt prescale

dic_2 = c2.getRateListRun()
#print dic_1["info"]
#print dic_2["info"]
#print c1.index_lumi
#print c2.index_lumi
#####################################################################################
#run comparison
output_1 = comparison()
output_1.output_dir = "example_outputFile"
output_1.comparisonRun(dic_1, dic_2)


