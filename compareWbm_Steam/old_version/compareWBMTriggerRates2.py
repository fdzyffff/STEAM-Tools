import os
import argparse
import copy
from math import *
from cernSSOWebParser import parseURLTables

#******************************************************************************************
def comparison(Runnr,Lumi,input_file,output_dir,steamLumi):
    _runnr=Runnr
    index_lumi=Lumi               #
    PsNorm = 7.*107./2.
    PSforSteam = False
    
    P_hltrates=True            #
    P_l1rates=False             #
    pu_write=False

# get rate infomation from file1, need column of hltpath, rate, dataset    
    file1_hltpath = 1          #HLT_
    file1_hltrate = 4          #hlt rate
    file1_hltrateErr = 6       #hlt rate error
    file1_dataset = 2          #l1 prescale
    file1_group = 3          #l1 prescale
    
# not use file2
    file2_l1path = 1           #L1_
    file2_l1rate = 3           #l1 rate
    file2_l1rateErr = 5        #l1 rate error
    file2_l1prescale = 0      #l1 prescale
    
    
    #******************************************************************************************
    if P_hltrates:
        _steamRates=input_file
    if P_l1rates:
        _steamL1Rates="test2222.csv"
    if pu_write:
        PU_file_name=str(_runnr)+'_pu.tsv'
        PU_file=open(output_dir+'/'+PU_file_name,'w')
        PU_list=[
        'HLT_Ele27_WPLoose_Gsf',
        'HLT_IsoMu20',
        'HLT_IsoMu22',
        'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ',
        'HLT_PFHT800',
        'HLT_Ele15_IsoVVVL_PFHT350',
        'HLT_Photon90_R9Id90_HE10_IsoM',
        'HLT_Photon36_R9Id90_HE10_Iso40_EBOnly_VBF',
        'HLT_DiPFJetAve320']


    _json="json.csv"
    menu_lumibiasdic={
    '1e33':3,
    '2e33':2,
    '5e33':0
    }
# get L1 seed information from file3, need hlt name, l1 seed.
    file3_name = 'L1Seed.tsv'
    file3_hltpath = 0           #HLT_
    file3_l1seed = [18]         #L1_seed
    
# get L1 PS information from file4, need l1 name, l1 PS
    file4_name = 'L1_PS.csv'
    file4_l1path = 1           #L1_
    file4_l1prescale = 5     #l1 prescale
 
# get HLT PS information from file5, need hlt name, hlt PS
    file5_name = 'outputTSV.tsv'
    file5_hltpath = 2           #HLT_
    file5_hltprescale = 8       #hlt prescale

# get HLT Count information from file6, need hlt name, hlt Count
    file6_name = 'outputCounts.tsv'
    file6_hltpath = 1           #HLT_
    file6_hltcount = 5      #hlt prescale

    #******************************************************************************************
    file1name = 'HLT.csv'
    spreadSheetHeader1="Path,Group,Dataset,L1Path,L1Prescale("+index_lumi+"),Steam L1path,Steam L1Prescale,WBM hltPrescale("+index_lumi+"),Steam hltPrescale,Wbm Count,Wbm prescaled Count,Steam Count,,Data Rate (Hz),,,Steam Rate (Hz),,abs(Data-Steam)(Hz),,Bias : (data-steam)/max(data;steam),,Pull\n"
    #spreadSheetHeader1="Path,L1Path,L1Prescale(2e33),Steam L1path,Steam L1Prescale,totalprescale,WBMhltPrescale("+index_lumi+"),Steam hltPrescale,,Data Rate (Hz),,,Data Rate scaled (Hz),,,Steam Rate (Hz),,,Steam Rate rehltscaled(Hz),,,Steam rate l1prescaled,,,Bias(datascaled-steam),,,Bias(data-steam)\n"
    
    file2name = 'L1.csv'
    spreadSheetHeader2="L1 Path,L1Prescale(2e33),Steam L1Prescale,,Data Rate (Hz),,,Scaled Data Rate,,,Steam Rate (Hz),,,Data - Steam (Hz),,,(Data - Steam)/Steam\n"
    
    file3name = 'specficHLTpaths.csv'
    #******************************************************************************************
    lumidic={
    '1e33':10,
    '2e33':9,
    '3.5e33':8,
    '5e33':7,
    '7.5e33':6,
    '8.5e33':5,
    '9.5e33':4,
    '1.05e34':3,
    '1.15e34':2,
    '1.45e34':1,
    '1.6e34':0,
    }
    lumicolumn=2+lumidic[index_lumi]
    #******************************************************************************************
    def getJson(runnr,jfile):
        import json
        file1=open('json.txt','r')
        inp1={}
        for line1 in file1:
            inp1 = json.loads(line1)
            break
        for run in inp1:
            if str(runnr) in run:
                jsonfile=inp1[run]
                break
        return jsonfile
    
    
    def getPU(runnr,jsonfile):
        
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
        tables=parseURLTables(url)
        lhcfill_key=tables[3][14][1]
    
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReport?FILL=%s" % (lhcfill_key)
        tables=parseURLTables(url)
        nbunch=int(tables[3][18][1])

        totalLS=0     
        for l1 in jsonfile:
            totalLS=totalLS+l1[1]-l1[0]+1

        sumPU=0.
        sum_lumi=0
        n_lumi=0
        nLS=0
        psAndInstLumis=getPSAndInstLumis(runnr)
        for ls in jsonfile:
            minLS=int(ls[0])
            maxLS=int(ls[1])
            nLS+=(maxLS-minLS+1)
            for lumi in range(minLS,maxLS+1):
                if lumi in psAndInstLumis:
                    sum_lumi+=psAndInstLumis[lumi][1]
                    tmp_pu=(psAndInstLumis[lumi][1]*80000)/(11246*nbunch)

                    if pu_write:
                        hltRates=getpartTriggerRates(runnr,lumi,lumi,1)
                        print 'lumi section:',lumi,'in Run: ',runnr,'  ',n_lumi,'/',totalLS
                        for path in PU_list:
                            print path,hltRates[path][0][3]
                            PU_file.write(path+',%0.2f,%f\n' %(tmp_pu,hltRates[path][0][3]))

                    sumPU+=psAndInstLumis[lumi][1]*tmp_pu
                    n_lumi+=1
        if n_lumi != nLS:
            print "warning! miss lumi section!"
        avePU = sumPU/sum_lumi
        aveLumi = float(sum_lumi)/float(nLS)
    
        return avePU, aveLumi
                
    def MatchL1Seed(l1seed,l1predic):
        tmp_list=[]
        i_last = 0
        L1_start = False
        for i in range(len(l1seed)):
            if i<3:continue
           # print l1seed[i-3:i]
            if l1seed[i-3:i]=='L1_' and L1_start==False:
                L1_start=True
                tmp_list.append(l1seed[i_last:i-3])
                i_last=i-3
            if (l1seed[i]==' ' or l1seed[i]=='|' or l1seed[i]==')') and L1_start==True:
                L1_start=False
                tmp_list.append(l1seed[i_last:i])
                i_last=i
            if i==len(l1seed)-1:
                tmp_list.append(l1seed[i_last:i+1])
        text=''
        for l in tmp_list:
            if 'L1_' in l:
                try:
                    text+=str(l1predic[l])
                except:
                    text+=str(0)
            else:
                text+=l
        text=text.strip('\n')
        text=text.strip('\r')
        return text
        
     
    
    def Bias(no1,no2,e1,e2):
        t = 0
        bia = 0
        error = 0
        if no1 < no2:
            t=no1
            no1=no2
            no2=t
        if no1 > 0:
            bia = ((no1 - no2)/no1) * 100
            error = ((1/no1)**2) * (e2**2)
            error += ((no2/(no1*no1))**2) * (e1**2)
            error = math.sqrt(error)*100
        return bia, error
    
    def my_Pull(no1,no2,e2):
        my_pull = ''
        if no1 == 0 and no2 == 0:
            my_pull = 'N/A'
        elif no1 != 0 and no2 == 0:
            my_pull = 'No rates in Steam'
        elif no1 == 0 and no2 != 0:
            my_pull = 'No rates in WBM'
        else:
            my_pull = str(math.fabs(no1 - no2) / e2)
        return my_pull

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
    #    print psAndInstLumis
        return psAndInstLumis
    
    
    def getAveInstLumi(psAndInstLumis,jsonfile):
        lumiSum=0.;
        nrLumis=0;
        for ls in jsonfile:
            minLS=int(ls[0])
            maxLS=int(ls[1])
            for lumi in range(minLS,maxLS+1):
                if lumi in psAndInstLumis:
                    nrLumis+=1
                    lumiSum+=psAndInstLumis[lumi][1]
            if nrLumis!=0: return lumiSum/nrLumis
        else: return 0
    
    
    def getTriggerRates(runnr,jsonfile):
        hltRates={}
        totalLS = 0
        i_flag = True
        for l1 in jsonfile:
            totalLS=totalLS+l1[1]-l1[0]+1
    
        for ls in jsonfile:
            minLS=int(ls[0])
            maxLS=int(ls[1])
            if i_flag:
                i_flag=False
                hltRates=getpartTriggerRates(runnr,minLS,maxLS,totalLS)
            else:
                tmp_rates=getpartTriggerRates(runnr,minLS,maxLS,totalLS)
                for path in tmp_rates:
                    for i in range(len(tmp_rates[path][0])):
                        hltRates[path][0][i]+=tmp_rates[path][0][i]
        return hltRates
    
    def getpartTriggerRates(runnr,minLS,maxLS,totalLS):
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/HLTSummary?fromLS=%s&toLS=%s&RUN=%s" % (minLS,maxLS,runnr)
        tables=parseURLTables(url)
    
        hltpartRates={}
        for line in tables[1][2:]:
            rates=[]
            for entry in line[3:7]:
                rates.append(float(entry.replace(",","")))
            rates[3]=rates[3]*(float(maxLS)-float(minLS)+1.0)/totalLS
            hltpartRates[line[1].split("_v")[0]]=(rates,line[9])
        return hltpartRates
    
    
    def getL1Rates(runnr,minLS,maxLS):
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
        tables=parseURLTables(url)
        l1_key_mode=tables[1][1][4]
    
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/L1Summary?fromLS=%s&toLS=%s&RUN=%s&KEY=%s" % (minLS,maxLS,runnr,l1_key_mode)
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
                        else:
                            l1pre=int(line[file2_l1prescale])
                    except:
                        rate = -1
                        rateErr = -1
                        l1pre=-1
                    data[path]=(rate,rateErr,l1pre)
                
        return data
    
    def getL1Prescales(runnr):
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/PrescaleSets?RUN=%s" % (runnr)
        tables=parseURLTables(url)
    
        prescales={}
    
        # l1 algo paths/prescales
        for line in tables[1]:
            if not 'L1_' in line[1]:continue
            #                path     lumi
            try:
                prescales[line[1]] = (int(line[lumicolumn]))
            except:
                prescales[line[1]] = (0)    
    
        return prescales
    
    
    def getHLTPrescales(runnr):
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
        tables=parseURLTables(url)
        l1_hlt_mode=tables[1][1][3]
    
        url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/TriggerMode?KEY=%s" % (l1_hlt_mode)
        #print url
        tables=parseURLTables(url)
    
        prescales={}
    
        for line in tables[2]:
            if ('Output' in line[1].split('_v')[0]): continue
            #                path                      lumi     
            try:
                prescales[line[1].split('_v')[0]] = (int(line[lumicolumn]),line[15])
            except:
                prescales[line[1].split('_v')[0]] = (-1,'null')
    
        return prescales
    
             
    
    def getL1pre(steamFile):
        predic={}
        import csv
     
        l1predic={}
        with open(steamFile) as csvfile:
            steamReader=csv.reader(csvfile)
            for line in steamReader:
                path = line[file4_l1path].split("_v")[0]
                path = path.strip()
    
                if path.find("L1_")!=-1:
                    l1pre = int(line[file4_l1prescale])
                    l1predic[path]=l1pre
        return l1predic 

    def getHLTpre(steamFile):
        predic={}
        import csv

        hltpredic={}
        if '.csv' in steamFile:
            with open(steamFile) as csvfile:
                steamReader=csv.reader(csvfile)
                for line in steamReader:
                    path = line[file5_hltpath].split("_v")[0]
                    path = path.strip()
    
                    if path.find("HLT_")!=-1:
                        hltpre = int(line[file5_hltprescale])
                        hltpredic[path]=hltpre
        if '.tsv' in steamFile:
            tmp_file = open(steamFile,'r')
            for Line in tmp_file:
                line = Line.split('\t')
                try:
                    path = line[file5_hltpath].split("_v")[0]
                    path = path.strip()

                    if path.find("HLT_")!=-1:
                        hltpre = int(float(line[file5_hltprescale].replace('\r','').replace('\n','')))
                        hltpredic[path]=hltpre
                except:
                    pass
        return hltpredic
    
    def getHLTmenuSteam(steamFile):
        hltmenu={}
        import csv
     
        HLTl1predic=getL1pre(file4_name)
        HLTpre=getHLTpre(file5_name)
        if '.csv' in steamFile:
            with open(steamFile) as csvfile:
                steamReader=csv.reader(csvfile)
                for line in steamReader:
                    path = line[file3_hltpath].split("_v")[0]
                    path = path.strip()

                    if path.find("HLT_")!=-1:
                        if path in HLTpre:hltpre=int(HLTpre[path])
                        else: hltpre=-99
                        L1_seed = ''
                        if (file3_l1seed[0] > 0):
                            for seed_i in file3_l1seed:
                                L1_seed += line[seed_i]+' '
                            L1_seed=L1_seed[:-1]
                            L1_seed=L1_seed.strip('\n')
                            L1_seed=L1_seed.strip('\r')
                            L1pre=MatchL1Seed(L1_seed, HLTl1predic)
                            L1path=L1_seed
                        else:
                            L1path="null"
                            L1pre='-1'
                        hltmenu[path]=(L1path,L1pre,-1,hltpre)
        if '.tsv' in steamFile:
            file_hlt=open(steamFile,'r')
            for Line in file_hlt:
                line=Line.split('\t')
                path = line[file3_hltpath].split("_v")[0]
                path = path.strip()

                if path.find("HLT_")!=-1:
                    if path in HLTpre:hltpre=int(HLTpre[path])
                    else: hltpre=-99
                    L1_seed = ''
                    if (file3_l1seed[0] > 0):
                        for seed_i in file3_l1seed:
                            L1_seed += line[seed_i]+' '
                        L1_seed=L1_seed[:-1]
                        L1_seed=L1_seed.strip('\n')
                        L1_seed=L1_seed.strip('\r')
                        L1pre=MatchL1Seed(L1_seed, HLTl1predic)
                        L1path=L1_seed
                    else:
                        L1path="null"
                        L1pre='-1'
                    hltmenu[path]=(L1path,L1pre,-1,hltpre)


        return hltmenu,HLTl1predic
    
    def getHLTSteamRates(steamFile):
        data={}
        predic={}
        import csv
    
        HLTmenu,L1predic=getHLTmenuSteam(file3_name)
        if '.csv' in steamFile:
            with open(steamFile) as csvfile:
                steamReader=csv.reader(csvfile)
                for line in steamReader:
                    path = line[file1_hltpath].split("_v")[0]
                    path = path.strip()
        
                    if path.find("HLT_")!=-1:
                        try:
                            rate = float(line[file1_hltrate])
                            rateErr = float(line[file1_hltrateErr])
                            prescale = 0 #hltprescales[path] #int(line[0])
                            if path in HLTmenu:
                                l1path = HLTmenu[path][0]
                                l1pre = HLTmenu[path][1]
                                l1pretotal = HLTmenu[path][2]
                                hltprescale = HLTmenu[path][3]
                            else:
                                l1path = 'null'
                                l1pre = '-1'
                                l1pretotal = -1.
                        except:
                            rate = -1
                            rateErr = -1
                            prescale = -1
                            l1path = 'null'
                            l1pre = '-1'
                            l1pretotal = -1.
                            hltprescale = -1
                        data[path]=(rate,rateErr,prescale,l1path,l1pre,l1pretotal,hltprescale)
      
        if '.tsv' in steamFile:
            file_hlt=open(steamFile,'r')
            for Line in file_hlt:
                line=Line.split('\t')
                path = line[file1_hltpath].split("_v")[0]
                path = path.strip()
    
                if path.find("HLT_")!=-1:
                    try:
                        rate = float(line[file1_hltrate])
                        rateErr = float(line[file1_hltrateErr])
                        prescale = 0#int(line[file1_hltprescale]) #hltprescales[path] #int(line[0])
                        dataset = line[file1_dataset]
                        group = line[file1_group]
                        if path in HLTmenu:
                            l1path = HLTmenu[path][0]
                            l1pre = HLTmenu[path][1]
                            l1pretotal = HLTmenu[path][2]
                            hltprescale = HLTmenu[path][3]
                        else:
                            l1path = 'null'
                            l1pre = '-1'
                            l1pretotal = -1.
                    except:
                        rate = -1
                        rateErr = -1
                        prescale = -1
                        l1path = 'null'
                        l1pre = '-1'
                        l1pretotal = -1.
                        hltprescale = -1
                        dataset='null'
                        group='null'
                    data[path]=(rate,rateErr,prescale,l1path,l1pre,dataset,hltprescale,group)
        return data,L1predic
    
    def getHLTSteamCount(steamFile):
        data={}
        predic={}
        import csv
    
        if '.csv' in steamFile:
            with open(steamFile) as csvfile:
                steamReader=csv.reader(csvfile)
                for line in steamReader:
                    path = line[file6_hltpath].split("_v")[0]
                    path = path.strip()
        
                    if path.find("HLT_")!=-1:
                        try:
                            count = int(line[file6_hltcount])
                        except:
                            count = -1
                        data[path]=(count)
      
        if '.tsv' in steamFile:
            file_hlt=open(steamFile,'r')
            for Line in file_hlt:
                line=Line.split('\t')
                path = line[file6_hltpath].split("_v")[0]
                path = path.strip()
    
                if path.find("HLT_")!=-1:
                    try:
                        count = int(float(line[file6_hltcount]))
                    except:
                        print line[file6_hltcount]
                        count = -1
                    data[path]=(count)
        return data
    
    
    
    
    jsonfile=getJson(_runnr,_json)
    avePU, aveLumi=getPU(_runnr,jsonfile)
    
    targetLumi = float(index_lumi.split('e')[0])*(10**(int(index_lumi.split('e')[1])-30))
    
    print "run No : ",_runnr
    print "json : ",jsonfile
    print "target Lumi : ",targetLumi
    print "*"*30
    if P_hltrates:
        print "steam hlt file : ",_steamRates
    print "*"*30
    if P_l1rates:
        print "steam l1 file : ",_steamL1Rates
        print "*"*30
    #print args.steamRates
    
    print "average pile up:",avePU
    print "*"*30
    print "average Luminosity:",aveLumi
    print "*"*30
    
    if P_hltrates:
        HLTsteamRates, l1steam=getHLTSteamRates(_steamRates)
        HLTsteamCount=getHLTSteamCount(file6_name)
        hltRates=getTriggerRates(_runnr,jsonfile)
    
    if P_l1rates:
        L1steamRates=getL1SteamRates(_steamL1Rates)
    #    l1Rates=getL1Rates(args.runnr,args.minLS,args.maxLS)
    
    if steamLumi <= 0 : 
        lumiScale=1.
    else:
        lumiScale = aveLumi / steamLumi
    print "lumi sf for steam:",lumiScale
    print "*"*30

    hltPrescales=getHLTPrescales(_runnr)
    l1Prescales=getL1Prescales(_runnr)
#    try:
#        hltPrescales=getHLTPrescales(_runnr)
#    except:
#        hltPrescales={}
#    try:
#        l1Prescales=getL1Prescales(_runnr)
#    except:
#        l1Prescales={}
    try:
        os.mkdir(output_dir)
    except:
        pass
 
    #for path in hltRates:
    if P_hltrates:
        
        file1name=str(_runnr)+file1name
        filetowrite1=open(output_dir+'/'+file1name,'w')    #hlt rate comparision output file 
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
            l1seeds=hltPrescales[path][1].strip('"').replace(" OR ","||")
        
        #    print l1seeds
        
            import math
        
            prescaledPath=False
            hltPrescaleOnline=1
            if rates[1]!=0 and rates[1]!=rates[0]: 
                prescaledPath=True
                hltPrescaleOnline = float(rates[1]/rates[0])
                
            l1Prescale=99999999
            L1path=l1seeds
            L1pre=''
            SteamL1path=''
            SteamL1pre=' '
            L1pre=MatchL1Seed(l1seeds,l1Prescales)
                        
        
            wbmhltPrescale=99
            if (path in hltPrescales):
                wbmhltPrescale=hltPrescales[path][0]
        
            steamRate=0
            steamRateErr=0
            steamcount=0
            steamcountErr=0
            dataset='null'
            group='null'
            hltPrescaleSteam=-1
            hltprescaled=-1
            pretotal=-1
        
            if path in HLTsteamRates:
                steamRate=HLTsteamRates[path][0]
                steamRate*=lumiScale
                steamRateErr=HLTsteamRates[path][1]
                steamRateErr*=lumiScale
                hltPrescaleSteam=int(HLTsteamRates[path][6])
#                if PSforSteam and hltPrescaleSteam!=0:
#                    steamRate/=hltPrescaleSteam
#                    steamRateErr/=hltPrescaleSteam
                steamcount=int(HLTsteamCount[path])
                if PSforSteam and hltPrescaleSteam!=0:
                    steamcount=int(float(steamcount)/float(hltPrescaleSteam))
                steamcountErr=0
                dataset='"'+HLTsteamRates[path][5]+'"'
                group='"'+HLTsteamRates[path][7]+'"'
                if HLTsteamRates[path][6]!=0:
                    hltprescaled=float(HLTsteamRates[path][2])/float(HLTsteamRates[path][6])
                SteamL1path+=HLTsteamRates[path][3]
                SteamL1pre+=HLTsteamRates[path][4]
                pretotal=HLTsteamRates[path][5]
        #        print 'For STEAM path '+path+' rate is '+steamRate
        
            rate =rates[3]
            rateErr=0
            ncount=0
            ncountPSed=0
            if rates[2]!=0: 
                rateErr=math.sqrt(rates[2])/rates[2]*rate
                ncount = rates[2]
                ncountPSed = int(float(ncount)/PsNorm)
    #        try:
    #            rateScaled=rates[3]*lumiScale
    #            rateScaledErr=(rateErr/rates[3])*rateScaled
    #        except:
    #            rateScaled=rates[3]*lumiScale
    #            rateScaledErr=rateErr*lumiScale
            
            rateUnprescaledScaled=0
            rateUnprescaledScaledErr=0
            if rates[1]!=0:
                rateUnprescaledScaled=rates[3]*rates[0]/rates[1]*lumiScale
                rateUnprescaledScaledErr=rateErr*rates[0]/rates[1]*lumiScale
    
            steamRateHLTPred = steamRate*hltprescaled 
            steamRateHLTPredErr = steamRateErr*hltprescaled  
     
#            ratePred=steamRateHLTPred/pretotal
#            ratePredErr=steamRateHLTPredErr/pretotal 
    
    #        rateDiff = rateScaled-ratePred
    #        rateDiffErr = math.sqrt(rateScaledErr**2 + ratePredErr**2)
        
#            relDiff,relDiffErr=Bias(ratePred,rate,ratePredErr,rateErr)
            relDiff,relDiffErr=Bias(steamRate,rate,steamRateErr,rateErr)
            abs_rate = fabs(rate-steamRate)
            my_pull = my_Pull(rate, steamRate, steamRateErr)
    #        if steamRate!=0:
    #            relDiff = rateDiff/ratePred
    #            relDiffErr = rateScaledErr**2/ratePred**2 + rateScaled**2*ratePredErr**2/ratePred**4
    #            relDiffErr = relDiffErr**0.5
    #            relDiff*=100
    #            relDiffErr *=100
           
            HLTdic={}
#            HLTdic[path]=(L1path,L1pre,SteamL1path,SteamL1pre,int(pretotal),wbmhltPrescale,hltPrescaleSteam,rate,rateErr,steamRate,steamRateErr,steamRateHLTPred,steamRateHLTPredErr,relDiff,relDiffErr)
            HLTdic[path]=(group,dataset,L1path,L1pre,SteamL1path,SteamL1pre,wbmhltPrescale,hltPrescaleSteam,ncount,ncountPSed,steamcount,rate,rateErr,steamRate,steamRateErr,abs_rate,relDiff,relDiffErr,my_pull)
            HLTlist.append(HLTdic)
        #print HLT comparision
        spreadSheetStr1="%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%d,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.5f,%.2f%%,+/-,%.2f%%,%s\n" 
        for i in range(len(HLTlist)):
            for path in HLTlist[i]:
                filetowrite1.write(spreadSheetStr1 %(path,HLTlist[i][path][0],HLTlist[i][path][1],HLTlist[i][path][2],HLTlist[i][path][3],HLTlist[i][path][4],HLTlist[i][path][5],HLTlist[i][path][6],HLTlist[i][path][7],HLTlist[i][path][8],HLTlist[i][path][9],HLTlist[i][path][10],HLTlist[i][path][11],HLTlist[i][path][12],HLTlist[i][path][13],HLTlist[i][path][14],HLTlist[i][path][15],HLTlist[i][path][16],HLTlist[i][path][17],HLTlist[i][path][18]))
        
        
        #print L1 comparision
        l1steamonly=copy.deepcopy(l1steam)
        l1wbmonly=copy.deepcopy(l1Prescales)
        l1same={}
        l1diff={}
        l1only=[]
        for l in l1Prescales:
            if l in l1steam:
                if l1Prescales[l]==l1steam[l]:
                    l1same[l]=l1steam[l]
                else:
                    l1diff[l]=(l1Prescales[l],l1steam[l])
                del l1steamonly[l]
                del l1wbmonly[l]
        
        
#        filetowrite1.write('*'*30+'\n')
#        filetowrite1.write('L1path(wbm),L1prescale(wbm),L1path(steam),L1prescale(steam)\n')
#        filetowrite1.write('*'*30+'L1 path with same prescale\n')
#        for l in l1same:
#            filetowrite1.write('%s,%s,%s,%s\n'%(l,l1same[l],l,l1same[l]))
#        filetowrite1.write('*'*30+'L1 path with different prescale\n')
#        for l in l1diff:
#            filetowrite1.write('%s,%s,%s,%s\n'%(l,l1diff[l][0],l,l1diff[l][1]))
#        filetowrite1.write('*'*30+'l1wbmonly\n')
#        for l in l1wbmonly:
#            if l!='':
#                filetowrite1.write('%s,%s,,\n'%(l,l1wbmonly[l])) 
#        filetowrite1.write('*'*30+'l1steamonly\n')
#        for l in l1steamonly:
#            filetowrite1.write(',,%s,%s\n'%(l,l1steamonly[l]))
#        
#        
        filetowrite1.close()
    #*****************************************************************************************************************
    #for path in l1 Rates:
    if P_l1rates:
        spreadSheetStr2="%s,%d,%d,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f,%.2f,+/-,%.2f\n"
        
        file2name=str(_runnr)+file2name
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
            relDiffErr = 999
            if steamRate!=0:
                relDiff = rateDiff/steamRate
                relDiffErr = (rateScaledErr**2)/(steamRate**2) + (rateScaled**2)*(steamRateErr**2)/(steamRate**4)
                relDiffErr = relDiffErr**0.5
            
            L1dic={}
        #    L1dic[path]=(l1pre,steamPre,rate,rateErr,rateScaled,rateScaledErr,steamRate,steamRateErr,rateDiff,rateDiffErr,relDiff,relDiffErr)
            L1dic[path]=(l1pre,steamPre,rate,rateErr,rateScaled,rateScaledErr,steamRate,steamRateErr,rateDiff,rateDiffErr,relDiff,relDiffErr)
            L1list.append(L1dic)
        #print L1 comparision
        for i in range(len(L1list)):
            for path in L1list[i]:
                if L1list[i][path][0]==L1list[i][path][1]:
                    filetowrite2.write(spreadSheetStr2 %(path,L1list[i][path][0],L1list[i][path][1],L1list[i][path][2],L1list[i][path][3],L1list[i][path][4],L1list[i][path][5],L1list[i][path][6],L1list[i][path][7],L1list[i][path][8],L1list[i][path][9],L1list[i][path][10],L1list[i][path][11]))
        
        for i in range(len(L1list)):
            for path in L1list[i]:
                if L1list[i][path][0]!=L1list[i][path][1]:
                    filetowrite2.write(spreadSheetStr2 %(path,L1list[i][path][0],L1list[i][path][1],L1list[i][path][2],L1list[i][path][3],L1list[i][path][4],L1list[i][path][5],L1list[i][path][6],L1list[i][path][7],L1list[i][path][8],L1list[i][path][9],L1list[i][path][10],L1list[i][path][11]))
        
        
        filetowrite2.close()
        
        
#    testlist=[
#    'HLT_Ele27_WPLoose_Gsf', 
#    'HLT_IsoMu20',
#    'HLT_IsoMu22',
#    'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ',
#    'HLT_PFHT800',
#    'HLT_Ele15_IsoVVVL_PFHT350',
#    'HLT_Photon90_R9Id90_HE10_IsoM',
#    'HLT_Photon36_R9Id90_HE10_Iso40_EBOnly_VBF',
#    'HLT_DiPFJetAve320']
#    file3name=str(_runnr)+file3name
#    filetowrite3=open(output_dir+'/'+file3name,'w')   #l1 rate comparision output file
#    filetowrite3.write(spreadSheetHeader1)
#    
#    for path in testlist:
#        for i in range(len(HLTlist)):
#            if path in HLTlist[i]:
#                filetowrite3.write(spreadSheetStr1 %(path,HLTlist[i][path][0],HLTlist[i][path][1],HLTlist[i][path][2],HLTlist[i][path][3],HLTlist[i][path][4],HLTlist[i][path][5],HLTlist[i][path][6],HLTlist[i][path][7],HLTlist[i][path][8],HLTlist[i][path][9],HLTlist[i][path][10],HLTlist[i][path][11],HLTlist[i][path][12],HLTlist[i][path][13]))
#    
#
    return avePU    
    
    
    
    
comparison(279116,'9.5e33','output.tsv','279116',-10000)    
    
    
    
    
    
    
