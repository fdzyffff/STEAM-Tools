import os
from compareWBMTriggerRates2 import comparison

c1 = comparison()
c1._runnr = "279116"
c1.output_dir = "example_outputFile"
c1.json_name = "json.txt"
c1.index_lumi = "9.5e33"

# get steam rates from file
c1.file1_name = "examples_inputFiles/output.tsv"
c1.file1_hltpath = 1          #HLT_
c1.file1_hltrate = 4          #hlt rate
c1.file1_hltrateErr = 6       #hlt rate error
c1.file1_dataset = 2          #l1 prescale
c1.file1_group = 3          #l1 prescale
    
# get L1 seed information from file3, need hlt name, l1 seed.
c1.file3_name = 'examples_inputFiles/L1Seed.tsv'
c1.file3_hltpath = 0           #HLT_
c1.file3_l1seed = [18]         #L1_seed
    
# get L1 PS information from file4, need l1 name, l1 PS
c1.file4_name = 'examples_inputFiles/L1_PS.csv'
c1.file4_l1path = 1           #L1_
c1.file4_l1prescale = 5     #l1 prescale
 
# get HLT PS information from file5, need hlt name, hlt PS
c1.file5_name = 'examples_inputFiles/outputTSV.tsv'
c1.file5_hltpath = 2           #HLT_
c1.file5_hltprescale = 8       #hlt prescale

# get HLT Count information from file6, need hlt name, hlt Count
c1.file6_name = 'examples_inputFiles/outputCounts.tsv'
c1.file6_hltpath = 1           #HLT_
c1.file6_hltcount = 5      #hlt prescale

c1.comparisonRun()


