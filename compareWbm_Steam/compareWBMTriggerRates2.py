import os
import argparse
import copy
from cernSSOWebParser import parseURLTables

#******************************************************************************************
file1name = 'newGoogle1.csv'
spreadSheetHeader1="Path,L1Path,L1Prescale(2e33),Steam L1path,Steam L1Prescale,WBMhltPrescale(2e33),Steam hltPrescale,,Data Rate (Hz),,,Data Rate scaled (Hz),,,Steam Rate (Hz),,,Data - Steam (Hz),,,(Data - Steam)/Steam\n"

file2name = 'newGoogle2.csv'
spreadSheetHeader2="L1 Path,L1Prescale(2e33),Steam L1Prescale,,Data Rate (Hz),,,Steam Rate (Hz),,,Data - Steam (Hz),,,(Data - Steam)/Steam\n"


P_hltrates=True            #
P_l1rates=True             #

index_lium=1               #

file1_hltprescale = 3      #hlt prescale
file1_hltpath = 0          #HLT_
file1_hltrate = 4          #hlt rate
file1_hltrateErr = 6       #hlt rate error
file1_l1path = 1           #l1 path
file1_l1prescale = 2       #l1 prescale

file2_l1path = 0           #L1_
file2_l1rate = 2           #l1 rate
file2_l1rateErr = 4        #l1 rate error
file2_l1prescale = -1      #l1 prescale


#******************************************************************************************


def getPSAndInstLumis(runnr):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/LumiSections?RUN=%s" % runnr 
    tables=parseURLTables(url)

    psAndInstLumis={}
    
    for line in tables[1]:
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

def getL1Rates(runnr,minLS,maxLS):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/L1Summary?fromLS=%s&toLS=%s&RUN=%s&KEY=TSC_20150919_003445_collisions_BASE" % (minLS,maxLS,runnr)
    tables=parseURLTables(url)

    l1Rates={}
    for line in tables[7][2:]:
        if ('L1' in line[1]):
            rates=[]
            for entry in line[4:8]:
                rates.append(float(entry.replace(",","")))
    
            l1Rates[line[1].strip()]=(rates,int(line[8]))
    return l1Rates

def getL1SteamRates(steamFile):
    data={}
    predic={}
    import csv

    with open(steamFile) as csvfile:
        steamReader=csv.reader(csvfile)
        for line in steamReader:
            path = line[file2_l1path]
            path = path.strip()
            path = path.strip(' ')

            if "L1_" in path:
                try:
                    rate = float(line[file2_l1rate].replace(',',''))
                    rateErr = float(line[file2_l1rateErr])
                    if file2_l1prescale < 0:
                        l1pre=-1
                except:
                    rate = -1
                    rateErr = -1
                    l1pre=-1
                data[path]=(rate,rateErr,l1pre)
            
    return data

def getL1Prescales(runnr):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
    tables=parseURLTables(url)
    l1_hlt_mode=tables[1][1][3]

    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/TriggerMode?KEY=%s" % (l1_hlt_mode)
    tables=parseURLTables(url)

    prescales={}

    # l1 algo paths/prescales
    for line in tables[3]:
        #                path     7e33    2e33    14e33
        try:
            prescales[line[1]] = (int(line[4]),int(line[7]),int(line[3]))
        except:
            prescales[line[1]] = (-1,-1,-1)    

    #l1 tech paths/prescales
    for line in tables[4]:
        #                path     7e33    2e33    14e33
        try:
            prescales[line[1]] = (int(line[4]),int(line[7]),int(line[3]))
        except:
            prescales[line[1]] = (-1,-1,-1)
            
#    print prescales
    return prescales


def getHLTPrescales(runnr):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
    tables=parseURLTables(url)
    l1_hlt_mode=tables[1][1][3]

    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/TriggerMode?KEY=%s" % (l1_hlt_mode)
    tables=parseURLTables(url)

    prescales={}

    #HLT paths/prescales
    for line in tables[5]:
        if ('Output' in line[1].split('_v')[0]): continue
        #                path     7e33    2e33     14e33
        try:
            prescales[line[1].split('_v')[0]] = (int(line[4]),int(line[7]),int(line[3]))
        except:
            prescales[line[1].split('_v')[0]] = (-1,-1,-1)

    return prescales

def getHLTSteamRates(steamFile):
    data={}
    predic={}
    import csv

    with open(steamFile) as csvfile:
        steamReader=csv.reader(csvfile)
        for line in steamReader:
            path = line[file1_hltpath].split("_v")[0]
            path = path.strip()

            if path.find("HLT_")!=-1:
                try:
                    rate = float(line[file1_hltrate])
                    rateErr = float(line[file1_hltrateErr])
                    prescale = int(line[file1_hltprescale]) #hltprescales[path] #int(line[0])
                    L1path = line[file1_l1path]
                    L1pre = ''
                    l1pre = line[file1_l1prescale].split(" ")
                    if len(l1pre)> 1:
                        del l1pre[0]
                        l1pre.pop()
                        for i in range(len(l1pre)):
                            if i == 0:
                                L1pre += l1pre[i]
                            else:
                                L1pre = L1pre + ' | ' +l1pre[i]
                    else:
                        L1pre = l1pre[0] 

                except:
                    rate = -1
                    rateErr = -1
                    prescale = -1
                    L1path = "null"
                    L1pre = "null"
                data[path]=(rate,rateErr,prescale,L1path,L1pre)
            
            l1path = line[file1_l1path].split(" OR ")
            l1pre = line[file1_l1prescale].split(" ")
            if len(l1pre)> 1:
                del l1pre[0]
                l1pre.pop()
                    
            for l in l1path:
                l = l.strip(' ')

            for i in range(0,len(l1path)):
                if not (l1path[i].strip(' ') in predic) and (len(l1path[i].strip(' ')) > 1):
                    predic[l1path[i].strip(' ')]=int(l1pre[i])

    return data,predic
         

parser = argparse.ArgumentParser(description='compare hlt reports')

parser.add_argument('runnr',help='runnr')
parser.add_argument('--minLS',help='minimum LS (inclusive)',default=1,type=int)
parser.add_argument('--maxLS',help='maximum LS (inclusive)',default=-1,type=int)
parser.add_argument('--targetLumi',help='lumi to scale to (units of 1E30, so 7E33 is 7000)',default=-1.0,type=float)
if P_hltrates:
    parser.add_argument('--steamRates',help='csv steam hlt rate google doc',default="test1111.csv")
if P_l1rates:
    parser.add_argument('--steamL1Rates',help='csv steam L1 rate google doc',default="test2222.csv")
args = parser.parse_args()

#print args.steamRates

if P_hltrates:
    HLTsteamRates, l1steam=getHLTSteamRates(args.steamRates)
    hltRates=getTriggerRates(args.runnr,args.minLS,args.maxLS)

if P_l1rates:
    L1steamRates=getL1SteamRates(args.steamL1Rates)
    l1Rates=getL1Rates(args.runnr,args.minLS,args.maxLS)

psAndInstLumis=getPSAndInstLumis(args.runnr)
aveLumi=getAveInstLumi(psAndInstLumis,args.minLS,args.maxLS)

lumiScale=1.
if args.targetLumi!=-1: lumiScale=args.targetLumi/float(aveLumi)

l1Prescales=getL1Prescales(args.runnr)
hltPrescales=getHLTPrescales(args.runnr)

#for path in hltRates:
if P_hltrates:
    spreadSheetStr1="%s,%s,%s,%s,%s,%d,%d,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f\n" 
    
    filetowrite1=open(file1name,'w')    #hlt rate comparision output file 
    filetowrite1.write(spreadSheetHeader1)
    
    #
    HLTlist=[]
    sortdic={}
    for path in hltRates:
        sortdic[path]=hltRates[path][0][3]
    #print sorted(sortdic.iteritems(), key=lambda d:d[1], reverse = True )
    for p in sorted(sortdic.iteritems(), key=lambda d:d[1], reverse = True ):
        path=p[0]
    #
    
        rates=hltRates[path][0]
        l1seeds=hltRates[path][1]
    
    #    print l1seeds
    
        import math
    
        prescaledPath=False
        hltPrescaleOnline=1
        if rates[1]!=0 and rates[1]!=rates[0]: 
            prescaledPath=True
            hltPrescaleOnline = float(rates[1]/rates[0])
            
        l1Prescale2e33=9999999
        l1Prescale7e33=99999999
        l1Prescale14e33=99999999
        L1path=''
        L1pre=''
        SteamL1path=''
        SteamL1pre=' '
        for l1seed in l1Prescales:
            if l1seed!='' and (l1seed in l1seeds): 
                if (l1Prescales[l1seed][1]<l1Prescale2e33):
                    l1Prescale2e33=l1Prescales[l1seed][1]
                if (l1Prescales[l1seed][0]<l1Prescale7e33):
                    l1Prescale7e33=l1Prescales[l1seed][0]
                if (l1Prescales[l1seed][2]<l1Prescale14e33):
                    l1Prescale14e33=l1Prescales[l1seed][2]
                if (L1path!=''):
                    L1path=L1path+" OR "+l1seed
                    L1pre=L1pre+" | "+str(l1Prescale2e33)
                else: 
                    L1path=l1seed
                    L1pre+=str(l1Prescale2e33)
    #            if ((path in HLTsteamRates)&&(l1seed in HLTsteamRates[path][3])):
                    
    
        hltPrescale2e33=99
        hltPrescale7e33=99
        hltPrescale14e33=99
        if (path in hltPrescales):
            hltPrescale2e33=hltPrescales[path][1]
            hltPrescale7e33=hltPrescales[path][0]
            hltPrescale14e33=hltPrescales[path][2]
    
        steamRate=0
        steamRateErr=0
        hltPrescaleSteam=-1
    
        if path in HLTsteamRates:
            steamRate=HLTsteamRates[path][0]
            steamRateErr=HLTsteamRates[path][1]
            hltPrescaleSteam=HLTsteamRates[path][2]
            SteamL1path+=HLTsteamRates[path][3]
            SteamL1pre+=HLTsteamRates[path][4]
    #        print 'For STEAM path '+path+' rate is '+steamRate
    
        rate =rates[3]
        rateErr=0
        if rates[2]!=0: rateErr=math.sqrt(rates[2])/rates[2]*rate
        try:
            rateScaled=rates[3]*lumiScale
            rateScaledErr=(rateErr/rates[3])*rateScaled
        except:
            rateScaled=rates[3]*lumiScale
            rateScaledErr=rateErr*lumiScale
        
        rateUnprescaledScaled=0
        rateUnprescaledScaledErr=0
        if rates[1]!=0:
            rateUnprescaledScaled=rates[3]*rates[0]/rates[1]*lumiScale
            rateUnprescaledScaledErr=rateErr*rates[0]/rates[1]*lumiScale
    
        rateDiff = rateScaled-steamRate
        rateDiffErr = math.sqrt(rateScaledErr**2 + steamRateErr**2)
    
        relDiff = 999
        relDiffErr = 0
        if steamRate!=0:
            relDiff = rateDiff/steamRate
            relDiffErr = rateScaledErr**2/steamRate**2 + rateScaled**2*steamRateErr**2/steamRate**4
        
        HLTdic={}
        HLTdic[path]=(L1path,L1pre,SteamL1path,SteamL1pre,hltPrescale2e33,hltPrescaleSteam,rate,rateErr,rateScaled,rateScaledErr,steamRate,steamRateErr,rateDiff,rateDiffErr,relDiff,relDiffErr)
        HLTlist.append(HLTdic)
    #print HLT comparision
    for i in range(len(HLTlist)):
        for path in HLTlist[i]:
            if HLTlist[i][path][4]==HLTlist[i][path][5]:
                filetowrite1.write(spreadSheetStr1 %(path,HLTlist[i][path][0],HLTlist[i][path][1],HLTlist[i][path][2],HLTlist[i][path][3],HLTlist[i][path][4],HLTlist[i][path][5],HLTlist[i][path][6],HLTlist[i][path][7],HLTlist[i][path][8],HLTlist[i][path][9],HLTlist[i][path][10],HLTlist[i][path][11],HLTlist[i][path][12],HLTlist[i][path][13],HLTlist[i][path][14],HLTlist[i][path][15]))
    
    for i in range(len(HLTlist)):
        for path in HLTlist[i]:
            if HLTlist[i][path][4]!=HLTlist[i][path][5]:
                filetowrite1.write(spreadSheetStr1 %(path,HLTlist[i][path][0],HLTlist[i][path][1],HLTlist[i][path][2],HLTlist[i][path][3],HLTlist[i][path][4],HLTlist[i][path][5],HLTlist[i][path][6],HLTlist[i][path][7],HLTlist[i][path][8],HLTlist[i][path][9],HLTlist[i][path][10],HLTlist[i][path][11],HLTlist[i][path][12],HLTlist[i][path][13],HLTlist[i][path][14],HLTlist[i][path][15]))
    
    
    #print L1 comparision
    l1steamonly=copy.deepcopy(l1steam)
    l1wbmonly=copy.deepcopy(l1Prescales)
    l1same={}
    l1diff={}
    l1only=[]
    for l in l1Prescales:
        if l in l1steam:
            if l1Prescales[l][1]==l1steam[l]:
                l1same[l]=l1steam[l]
            else:
                l1diff[l]=(l1Prescales[l][1],l1steam[l])
            del l1steamonly[l]
            del l1wbmonly[l]
    
    
    filetowrite1.write('*'*30+'\n')
    filetowrite1.write('L1path(wbm),L1prescale(wbm),L1path(steam),L1prescale(steam)\n')
    filetowrite1.write('*'*30+'L1 path with same prescale\n')
    for l in l1same:
        filetowrite1.write('%s,%s,%s,%s\n'%(l,l1same[l],l,l1same[l]))
    filetowrite1.write('*'*30+'L1 path with different prescale\n')
    for l in l1diff:
        filetowrite1.write('%s,%s,%s,%s\n'%(l,l1diff[l][0],l,l1diff[l][1]))
    filetowrite1.write('*'*30+'l1wbmonly\n')
    for l in l1wbmonly:
        if l!='':
            filetowrite1.write('%s,%s,,\n'%(l,l1wbmonly[l][1])) 
    filetowrite1.write('*'*30+'l1steamonly\n')
    for l in l1steamonly:
        filetowrite1.write(',,%s,%s\n'%(l,l1steamonly[l]))
    
    
    filetowrite1.close()
#*****************************************************************************************************************
#for path in l1 Rates:
if P_l1rates:
    spreadSheetStr2="%s,%d,%d,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f\n"
    
    filetowrite2=open(file2name,'w')   #l1 rate comparision output file
    filetowrite2.write(spreadSheetHeader2)
    
    L1list=[]
    sortdic={}
    for path in l1Rates:
        sortdic[path]=l1Rates[path][0][2]
    for p in sorted(sortdic.iteritems(), key=lambda d:d[1], reverse = True ):
        path=p[0]
        rates=l1Rates[path][0]
        l1pre=l1Rates[path][1]
    
        import math
    
        steamRate=0
        steamRateErr=0
    
        if path in L1steamRates:
            steamRate=L1steamRates[path][0]
            steamRateErr=L1steamRates[path][1]
            steamPre=L1steamRates[path][2]
    
        rate =rates[2]
        rateErr=0
        if rates[1]!=0: rateErr=math.sqrt(rates[1])/rates[1]*rate
        try:
            rateScaled=rates[2]*lumiScale
            rateScaledErr=(rateErr/rates[2])*rateScaled
        except:
            rateScaled=rates[2]*lumiScale
            rateScaledErr=rateErr*lumiScale
        
        rateDiff = rateScaled-steamRate
        rateDiffErr = math.sqrt(rateScaledErr**2 + steamRateErr**2)
    
        relDiff = 999
        relDiffErr = 0
        if steamRate!=0:
            relDiff = rateDiff/steamRate
            relDiffErr = rateScaledErr**2/steamRate**2 + rateScaled**2*steamRateErr**2/steamRate**4
        
        L1dic={}
    #    L1dic[path]=(l1pre,steamPre,rate,rateErr,rateScaled,rateScaledErr,steamRate,steamRateErr,rateDiff,rateDiffErr,relDiff,relDiffErr)
        L1dic[path]=(l1pre,steamPre,rate,rateErr,steamRate,steamRateErr,rateDiff,rateDiffErr,relDiff,relDiffErr)
        L1list.append(L1dic)
    #print L1 comparision
    for i in range(len(L1list)):
        for path in L1list[i]:
            if L1list[i][path][0]==L1list[i][path][1]:
                filetowrite2.write(spreadSheetStr2 %(path,L1list[i][path][0],L1list[i][path][1],L1list[i][path][2],L1list[i][path][3],L1list[i][path][4],L1list[i][path][5],L1list[i][path][6],L1list[i][path][7],L1list[i][path][8],L1list[i][path][9]))
    
    for i in range(len(L1list)):
        for path in L1list[i]:
            if L1list[i][path][0]!=L1list[i][path][1]:
                filetowrite2.write(spreadSheetStr2 %(path,L1list[i][path][0],L1list[i][path][1],L1list[i][path][2],L1list[i][path][3],L1list[i][path][4],L1list[i][path][5],L1list[i][path][6],L1list[i][path][7],L1list[i][path][8],L1list[i][path][9]))
    
    
    filetowrite2.close()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
