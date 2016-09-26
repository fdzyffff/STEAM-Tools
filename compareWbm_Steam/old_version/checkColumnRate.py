import os
import argparse

from cernSSOWebParser import parseURLTables

parser = argparse.ArgumentParser(description='check prescales in column using data in another column')

parser.add_argument('--refRun',help='run number to get data rates from',type=int)
parser.add_argument('--refLSRange',help='reference LS range',default='1,9999',type=str)
parser.add_argument('--targetColumn',help='check what rate would be in this prescale column',default=10,type=int)
parser.add_argument('--targetLumi',help='lumi to scale to (units of 1E30, so 7E33 is 7000)',default=-1.0,type=float)
args = parser.parse_args()

runnr = args.refRun
minLS = int(args.refLSRange.split(',')[0])
maxLS = int(args.refLSRange.split(',')[1])


def getPSAndInstLumis(runnr):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/LumiSections?RUN=%s" % runnr 
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


def getAveInstLumi(psAndInstLumis,minLS,maxLS):
    lumiSum=0.;
    nrLumis=0;
    if maxLS==-1: maxLS=max(psAndInstLumis.keys())
    for lumi in range(minLS,maxLS+1):
        if lumi in psAndInstLumis:
            nrLumis+=1
            lumiSum+=psAndInstLumis[lumi][1]
    if nrLumis!=0: return lumiSum/nrLumis
    else: return 0


def getTriggerRates(runnr,minLS,maxLS):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/HLTSummary?fromLS=%s&toLS=%s&RUN=%s" % (minLS,maxLS,runnr)
    tables=parseURLTables(url)

    hltRates={}
    for line in tables[1][2:]:
        rates=[]
        for entry in line[3:7]:
            rates.append(float(entry.replace(",","")))
                        
        hltRates[line[1].split("_v")[0]]=(rates,line[9])
    return hltRates

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

def getHLTPrescales(runnr,dataColumn,targetColumn):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
    tables=parseURLTables(url)
    l1_hlt_mode=tables[1][1][3]

    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/TriggerMode?KEY=%s" % (l1_hlt_mode)
    tables=parseURLTables(url)

    prescales={}

    #HLT paths/prescales
    for line in tables[5]:
        if ('Output' in line[1].split('_v')[0]): continue
        try:
            prescales[line[1].split('_v')[0]] = (int(line[targetColumn+2]),int(line[dataColumn+2]))
        except:
            prescales[line[1].split('_v')[0]] = (-1,-1)

    return prescales

psAndInstLumis=getPSAndInstLumis(runnr)

nLS = len(psAndInstLumis)
if (maxLS>nLS):
    print 'maxLS out of range!!! '
    print 'changing maxLS to '+str(nLS)
    maxLS = nLS

dataColumn = psAndInstLumis[minLS][0]
print 'prescale column for reference run: '+str(dataColumn)
for ls in range(minLS,maxLS+1):
    if (psAndInstLumis[ls][0]!=dataColumn):
        print 'prescale column changed at LS='+str(ls)+'!!!'
        print 'changing maxLS to '+str(ls-1)
        maxLS = ls-1
        break

aveLumi=getAveInstLumi(psAndInstLumis,minLS,maxLS)
print 'reference average lumi. = '+("%.2f"%aveLumi)+'e30'

lumiScale=1.
if args.targetLumi!=-1: lumiScale=args.targetLumi/float(aveLumi)

hltRates=getTriggerRates(runnr,minLS,maxLS)
l1Prescales=getL1Prescales(runnr,dataColumn,args.targetColumn)
hltPrescales=getHLTPrescales(runnr,dataColumn,args.targetColumn)

filename = 'rate_'+("%.2f"%args.targetLumi).replace('.','pt')+'e30col'+str(args.targetColumn)+'_from'+str(runnr)+'.txt'
fout = open(filename, 'w')

for path in hltRates:

    rates=hltRates[path][0]
    l1seeds=hltRates[path][1]

    import math

    l1PrescaleData=999999
    l1PrescaleTarget=999999
    for l1seed in l1Prescales:
        if l1seed!='' and (l1seed in l1seeds): 
            if (l1Prescales[l1seed][1]<l1PrescaleData):
                l1PrescaleData=l1Prescales[l1seed][1]
            if (l1Prescales[l1seed][0]<l1PrescaleTarget):
                l1PrescaleTarget=l1Prescales[l1seed][0]
    if (l1PrescaleData==999999): l1PrescaleData=1
    if (l1PrescaleTarget==999999): l1PrescaleTarget=1

    hltPrescaleData=1
    hltPrescaleTarget=1
    if (path in hltPrescales):
        hltPrescaleData=hltPrescales[path][1]
        hltPrescaleTarget=hltPrescales[path][0]

    rate=rates[3]
    rateErr=0
    if rates[2]!=0: rateErr=math.sqrt(rates[2])/rates[2]*rate
    try:
        rateScaled=rate*lumiScale*(hltPrescaleData*l1PrescaleData)/(l1PrescaleTarget*hltPrescaleTarget)
        rateScaledErr=(rateErr/rate)*rateScaled
    except:
        rateScaled=rate*lumiScale
        rateScaledErr=rateErr*lumiScale
        
    fout.write( '{0:75}, {1:8}, {2:8}, {3:6d}, {4:6d}, {5:6d}, {6:6d}'.format( \
            path,"%.2f"%rate,"%.2f"%rateScaled,l1PrescaleData,hltPrescaleData, \
            l1PrescaleTarget,hltPrescaleTarget)+' \n' )
    

os.system('mv '+filename+' tmp_'+filename)
os.system('sort -rn -t "," -k 3 tmp_'+filename+' > '+filename)
os.system('rm tmp_'+filename)

header = 'path , rate '+("%.2f" % aveLumi)+'e30 col '+str(dataColumn)+' , ' \
    +'scaled rate '+("%.2f" % args.targetLumi)+'e30 col '+str(args.targetColumn)+' , ' \
    +'l1p col '+str(dataColumn)+' , hltp col '+str(dataColumn)+' , ' \
    +'l1p col '+str(args.targetColumn)+' , hltp col '+str(args.targetColumn)+' \n'

os.system('echo -e "'+header+'\n$(cat '+filename+')" > '+filename)

print 'output written to',filename
