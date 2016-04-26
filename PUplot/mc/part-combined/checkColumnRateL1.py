import os
import argparse
import math

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

l1Rates=getL1TriggerRates(runnr,minLS,maxLS)
l1Prescales=getL1Prescales(runnr,dataColumn,args.targetColumn)

filename = 'l1rate_'+("%.2f"%args.targetLumi).replace('.','pt')+'e30col'+str(args.targetColumn)+'_from'+str(runnr)+'.txt'
fout = open(filename, 'w')

for path in l1Rates:

    print path,l1Rates[path]

    rate=l1Rates[path]

    l1PrescaleData=999999
    l1PrescaleTarget=999999
    if (path in l1Prescales): 
        l1PrescaleData=l1Prescales[path][1]
        l1PrescaleTarget=l1Prescales[path][0]

    if (l1PrescaleData==999999): l1PrescaleData=1
    if (l1PrescaleTarget==999999): l1PrescaleTarget=1

    try:
        rateScaled=rate*lumiScale*(l1PrescaleData)/(l1PrescaleTarget)
    except:
        rateScaled=rate*lumiScale
        
    fout.write( '{0:75}, {1:8}, {2:8}, {3:6d}, {4:6d}'.format( \
            path,"%.2f"%rate,"%.2f"%rateScaled,l1PrescaleData,l1PrescaleTarget)+' \n' )
    

os.system('mv '+filename+' tmp_'+filename)
os.system('sort -rn -t "," -k 3 tmp_'+filename+' > '+filename)
os.system('rm tmp_'+filename)

header = 'path , rate '+("%.2f" % aveLumi)+'e30 col '+str(dataColumn)+' , ' \
    +'scaled rate '+("%.2f" % args.targetLumi)+'e30 col '+str(args.targetColumn)+' , ' \
    +'l1p col '+str(dataColumn)+' , l1p col '+str(args.targetColumn)+' \n'

os.system('echo -e "'+header+'\n$(cat '+filename+')" > '+filename)

print 'output written to',filename
