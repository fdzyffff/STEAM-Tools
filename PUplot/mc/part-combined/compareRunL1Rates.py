import os
import argparse
import math

from cernSSOWebParser import parseURLTables

parser = argparse.ArgumentParser(description='check prescales in column using data in another column')

parser.add_argument('--refRun',help='reference run number',type=int)
parser.add_argument('--refLSRange',help='reference run LS range',default='1,9999',type=str)
parser.add_argument('--testRun',help='test run number ',type=int)
parser.add_argument('--testLSRange',help='test run LS range',default='-1,-1',type=str)
args = parser.parse_args()

refRunNum = args.refRun
minLSRef  = int(args.refLSRange.split(',')[0])
maxLSRef  = int(args.refLSRange.split(',')[1])

testRunNum = args.testRun
minLSTest  = int(args.testLSRange.split(',')[0])
maxLSTest  = int(args.testLSRange.split(',')[1])

def getPSAndInstLumis(runNum):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/LumiSections?RUN=%s" % runNum 
    tables=parseURLTables(url)

    psAndInstLumis={}
    
    for line in tables[0]:
        offset=0
        if line[0]=="L S": offset=41
        lumiSec=int(line[0+offset])
        preScaleColumn=int(line[1+offset])
        instLumi=float(line[3+offset])
        if instLumi==0.0: instLumi=50
        psAndInstLumis[lumiSec]=(preScaleColumn,instLumi)
    return psAndInstLumis


def getAveInstLumi(psAndInstLumis,minLSRef,maxLSRef):
    lumiSum=0.;
    nrLumis=0;
    if maxLSRef==-1: maxLSRef=max(psAndInstLumis.keys())
    for lumi in range(minLSRef,maxLSRef+1):
        if lumi in psAndInstLumis:
            nrLumis+=1
            lumiSum+=psAndInstLumis[lumi][1]
    if nrLumis!=0: return lumiSum/nrLumis
    else: return 0


def getL1TriggerRates(runnr,minLS,maxLS):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/L1Summary?fromLS=%s&toLS=%s&RUN=%s" % (minLS,maxLS,runnr)
    tables=parseURLTables(url)


    l1Rates={}
    for line in tables[6]:
      if (line[1].startswith('L1_')):
        #print line[1],line[6].replace(',','')                                                                                                            
        l1Rates[line[1]]=(float(line[6].replace(',','')))

    return l1Rates

def getL1Prescales(runnr,dataColumn,targetColumn):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
    tables=parseURLTables(url)
    l1_hlt_mode=tables[1][1][3]

    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/TriggerMode?KEY=%s" % (l1_hlt_mode)
    tables=parseURLTables(url)

    prescales={}

    # l1 algo paths/prescales                                                                                                                             
    for line in tables[3]:
        try:
            prescales[line[1]] = (int(line[targetColumn+2]),int(line[dataColumn+2]))
        except:
            prescales[line[1]] = (-1,-1)
    #l1 tech paths/prescales                                                                                                                              
    for line in tables[4]:
        try:
            prescales[line[1]] = (int(line[targetColumn+2]),int(line[dataColumn+2]))
        except:
            prescales[line[1]] = (-1,-1)

    return prescales

psAndInstLumisRef=getPSAndInstLumis(refRunNum)
psAndInstLumisTest=getPSAndInstLumis(testRunNum)

nLSRef = len(psAndInstLumisRef)
if (maxLSRef>nLSRef):
    print 'maxLSRef out of range!!! '
    print 'changing maxLSRef to '+str(nLSRef)
    maxLSRef = nLSRef

columnRef = psAndInstLumisRef[minLSRef][0]
print 'prescale column for reference run: '+str(columnRef)
for ls in range(minLSRef,maxLSRef+1):
    if (psAndInstLumisRef[ls][0]!=columnRef):
        print 'prescale column changed at LS='+str(ls)+'!!!'
        print 'changing maxLSRef to '+str(ls-1)
        maxLSRef = ls-1
        break

columnTest = psAndInstLumisTest[minLSTest][0]
print 'prescale column for test run: '+str(columnTest)
for ls in range(minLSTest,maxLSTest+1):
    if (psAndInstLumisTest[ls][0]!=columnTest):
        print 'prescale column changed at LS='+str(ls)+'!!!'
        print 'changing maxLSTest to '+str(ls-1)
        maxLSTest = ls-1
        break


aveLumiRef=getAveInstLumi(psAndInstLumisRef,minLSRef,maxLSRef)
print 'ref. run average lumi. = '+("%.2f"%aveLumiRef)+'e30'
aveLumiTest=getAveInstLumi(psAndInstLumisTest,minLSTest,maxLSTest)
print 'test run average lumi. = '+("%.2f"%aveLumiTest)+'e30'

lumiScale=float(aveLumiTest)/float(aveLumiRef)

l1RatesRef=getL1TriggerRates(refRunNum,minLSRef,maxLSRef)
l1PrescalesRef=getL1Prescales(refRunNum,columnRef,columnTest)

l1RatesTest=getL1TriggerRates(testRunNum,minLSTest,maxLSTest)
l1PrescalesTest=getL1Prescales(testRunNum,columnRef,columnTest)

filename = 'compareRates_'+str(testRunNum)+'LS'+str(minLSTest)+'-'+str(maxLSTest)+'_to_' \
    +str(refRunNum)+'LS'+str(minLSRef)+'-'+str(maxLSRef)+'.txt'
fout = open(filename, 'w')

for path in l1RatesTest:

    rateRef=l1RatesRef[path]
    rateTest=l1RatesTest[path]

    l1PrescaleRef=999999
    l1PrescaleTest=999999
    if (path in l1PrescalesRef):
        l1PrescaleRef=l1PrescalesRef[path][1]
    if (path in l1PrescalesTest):
        l1PrescaleTest=l1PrescalesTest[path][0]

    if (l1PrescaleRef==999999): l1PrescaleRef=1
    if (l1PrescaleTest==999999): l1PrescaleTest=1

    try:
        rateRefScaled=rateRef*lumiScale*(l1PrescaleRef)/(l1PrescaleTest)
    except:
        rateRefScaled=rate*lumiScale


    diff=rateTest-rateRefScaled
    if (rateRefScaled>0.0): ratio=rateTest/rateRefScaled
    else: ratio = -1.0

    fout.write( '{0:75}, {1:8}, {2:8}, {3:6}, {4:6}, {5:6d}, {6:6d}'.format( \
            path,"%.2f"%rateTest,"%.2f"%rateRefScaled,"%.2f"%ratio,"%.2f"%diff, \
                l1PrescaleRef,l1PrescaleTest)+' \n' )
    

os.system('mv '+filename+' tmp_'+filename)
os.system('sort -rn -t "," -k 4 tmp_'+filename+' > '+filename)
os.system('rm tmp_'+filename)

header = 'path , test rate , scaled ref. rate , test rate - ref. rate ,' \
    +'l1p ref '+str(columnRef)+' , hltp ref '+str(columnRef)+' , ' \
    +'l1p test '+str(columnTest)+' , hltp test '+str(columnTest)+' \n'

os.system('echo -e "'+header+'\n$(cat '+filename+')" > '+filename)

print 'output written to',filename
