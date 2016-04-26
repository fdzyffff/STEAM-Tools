import os
from compareWBMTriggerRates2 import comparison

rundic={
'259721':'1e33',
'259626':'1e33',
'256843':'2e33',
'256801':'2e33',
'260627':'5e33'
}
PUdic={}

output_dir='Results'
try:
    os.mkdir(output_dir)
except:
    pass

print "*"*60
print "*"*60
print "Run number,  lumi:"
for run in rundic:
    print run,rundic[run]
print "*"*60
print "*"*60

#get comparison result for Run
for run in rundic:
    input_file='/afs/cern.ch/user/x/xgao/CMSSW_7_6_3/src/RateEstimate/'+run+'/Results/'+run+'_rates_v4p4_V3__frozen_2015_25ns14e33_v4p4_HLT_V1_1_matrixRates.tsv'
    output_dir_tmp=output_dir+"/"+run
    PUdic[run]=comparison(int(run),rundic[run],input_file,output_dir_tmp)

file_pu=open(output_dir+'/steamPU.tsv','w')


#output PU of specific Run
print "*"*60
print "*"*60
print "Run number,  ave PU:"
for run in PUdic:
    print run,': ',PUdic[run]
    file_pu.write(run+'\t%f\n' %(PUdic[run]))


