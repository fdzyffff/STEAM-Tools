import os
import argparse
import copy
import math
from cernSSOWebParser2 import parseURLTables

#******************************************************************************************
class getRateInformation():
    def __init__(self, type_in):
        self.type_in = type_in
    lumilist=['1.6e34','1.45e34','1.15e34','1.05e34','9.5e33','8.5e33','7.5e33','5e33','3.5e33','2e33','1e33']

    _runnr = "000000"
    index_lumi="1e33"               
    input_lumi="-1e33"             
    target_lumi="1e33"            
    useLumiScale=False
    PsNorm = 7.*107./2.

    PSforSteam = False
    
    P_hltrates=True            
    P_l1rates=False           
    pu_write=False
 
    json_name = "json.txt"

# get rate infomation from file1, need column of hltpath, rate, dataset    
    file1_name = "output.tsv"
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
    lumicolumn=0
    #******************************************************************************************
#    def getTableFromFile(self,filename):
#        table=[]
#        if ".tsv" in filename:
#            tmp_file=open(filename,'r')
#            for Line in tmp_file:
#                tmp_list = []
#                line = Line.split('\t')
#                for part in line:
#                    tmp_list.append(part)
#                table.append(tmp_list)
#            return table
#        if ".csv" in filename:
            


    def getJson(self,runnr,jfile):
        import json
        file1=open(jfile,'r')
        tmp_text = ""
        inp1={}
        for line1 in file1:
            tmp_text += line1.replace("\n","")
        inp1 = json.loads(tmp_text)
        for run in inp1:
            if str(runnr) in run:
                jsonfile=inp1[run]
                break
        return jsonfile
    
    
    def getPU(self,runnr,jsonfile):
        
        url="https://cmswbm.cern.ch/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
        tables=parseURLTables(url)
        #print url
        #print tables
        lhcfill_key=tables[3][14][1]
    
        url="https://cmswbm.cern.ch/cmsdb/servlet/FillReport?FILL=%s" % (lhcfill_key)
        tables=parseURLTables(url)
        nbunch=int(tables[3][18][1])

        totalLS=0     
        for l1 in jsonfile:
            totalLS=totalLS+l1[1]-l1[0]+1

        sumPU=0.
        sum_lumi=0
        n_lumi=0
        nLS=0
        psAndInstLumis=self.getPSAndInstLumis(runnr)
        for ls in jsonfile:
            minLS=int(ls[0])
            maxLS=int(ls[1])
            nLS+=(maxLS-minLS+1)
            for lumi in range(minLS,maxLS+1):
                if lumi in psAndInstLumis:
                    sum_lumi+=psAndInstLumis[lumi][1]
                    tmp_pu=(psAndInstLumis[lumi][1]*80000)/(11246*nbunch)

                    if self.pu_write:
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
                
    def MatchL1Seed(self,l1seed,l1predic):
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
        
     

    def getPSAndInstLumis(self,runnr):
        url="https://cmswbm.cern.ch/cmsdb/servlet/LumiSections?RUN=%s" % runnr 
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
    
    def getTriggerRates(self,runnr,jsonfile):
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
                hltRates=self.getpartTriggerRates(runnr,minLS,maxLS,totalLS)
            else:
                tmp_rates=self.getpartTriggerRates(runnr,minLS,maxLS,totalLS)
                for path in tmp_rates:
                    for i in range(len(tmp_rates[path][0])):
                        hltRates[path][0][i]+=tmp_rates[path][0][i]
        return hltRates
    
    def getpartTriggerRates(self,runnr,minLS,maxLS,totalLS):
        url="https://cmswbm.cern.ch/cmsdb/servlet/HLTSummary?fromLS=%s&toLS=%s&RUN=%s" % (minLS,maxLS,runnr)
        tables=parseURLTables(url)
    
        hltpartRates={}
        for line in tables[1][2:]:
            rates=[]
            for entry in line[3:7]:
                rates.append(float(entry.replace(",","")))
            rates[3]=rates[3]*(float(maxLS)-float(minLS)+1.0)/totalLS
            hltpartRates[line[1].split("_v")[0]]=(rates,line[9])
        return hltpartRates
    
    
    def getL1Rates(self,runnr,minLS,maxLS):
        url="https://cmswbm.cern.ch/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
        tables=parseURLTables(url)
        l1_key_mode=tables[1][1][4]
    
        url="https://cmswbm.cern.ch/cmsdb/servlet/L1Summary?fromLS=%s&toLS=%s&RUN=%s&KEY=%s" % (minLS,maxLS,runnr,l1_key_mode)
        tables=parseURLTables(url)
    
        l1Rates={}
        for line in tables[7][2:]:
            if ('L1' in line[1]):
                rates=[]
                for entry in line[4:8]:
                    rates.append(float(entry.replace(",","")))
        
                l1Rates[line[1].strip()]=(rates,int(line[8]))
        return l1Rates
    
    def getL1Prescales(self,runnr):
        url="https://cmswbm.cern.ch/cmsdb/servlet/PrescaleSets?RUN=%s" % (runnr)
        tables=parseURLTables(url)
    
        prescales={}
    
        # l1 algo paths/prescales
        for line in tables[1]:
            if not 'L1_' in line[1]:continue
            #                path     lumi
            try:
                prescales[line[1]] = (int(line[self.lumicolumn]))
            except:
                prescales[line[1]] = (0)    
    
        return prescales
    
    
    def getHLTPrescales(self,runnr):
        url="https://cmswbm.cern.ch/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (runnr)
        tables=parseURLTables(url)
        l1_hlt_mode=tables[1][1][3]
    
        url="https://cmswbm.cern.ch/cmsdb/servlet/TriggerMode?KEY=%s" % (l1_hlt_mode)
        #print url
        tables=parseURLTables(url)
    
        prescales={}
    
        for line in tables[2]:
            if ('Output' in line[1].split('_v')[0]): continue
            #                path                      lumi     
            try:
                prescales[line[1].split('_v')[0]] = (int(line[self.lumicolumn]),line[-1])
            except:
                prescales[line[1].split('_v')[0]] = (-1,'null')
    
        return prescales
    
             
    
    def getL1pre(self,steamFile):
        predic={}
        import csv
     
        l1predic={}

        if '.csv' in steamFile:
            csvFile = file(steamFile,'r')
            steamReader=csv.reader(csvFile)
        if '.tsv' in steamFile:
            steamReader=open(steamFile,'r')
        for Line in steamReader:
            if '.tsv' in steamFile:
                line = Line.split('\t')
            if '.csv' in steamFile:
                line = Line
            path = line[self.file4_l1path].split("_v")[0]
            path = path.strip()

            if path.find("L1_")!=-1:
                l1pre = int(line[self.file4_l1prescale])
                l1predic[path]=l1pre
        return l1predic 

    def getHLTpre(self,steamFile):
        predic={}
        import csv

        hltpredic={}
        if '.csv' in steamFile:
            csvFile = file(steamFile,'r')
            steamReader=csv.reader(csvFile)
        if '.tsv' in steamFile:
            steamReader=open(steamFile,'r')
        for Line in steamReader:
            if '.tsv' in steamFile:
                line = Line.split('\t')
            if '.csv' in steamFile:
                line = Line
            try:
                path = line[self.file5_hltpath].split("_v")[0]
                path = path.strip()

                if path.find("HLT_")!=-1:
                    hltpre = int(float(line[self.file5_hltprescale].replace('\r','').replace('\n','')))
                    hltpredic[path]=hltpre
            except:
                pass
        return hltpredic
    
    def getHLTmenuSteam(self,steamFile,HLTl1predic):
        hltmenu={}
        import csv
     

        if '.csv' in steamFile:
            csvFile = file(steamFile,'r')
            steamReader=csv.reader(csvFile)
        if '.tsv' in steamFile:
            steamReader=open(steamFile,'r')
        for Line in steamReader:
            if '.tsv' in steamFile:
                line = Line.split('\t')
            if '.csv' in steamFile:
                line = Line

            path = line[self.file3_hltpath].split("_v")[0]
            path = path.strip()

            if path.find("HLT_")!=-1:
                L1_seed = ''
                if (self.file3_l1seed[0] > 0):
                    for seed_i in self.file3_l1seed:
                        L1_seed += line[seed_i]+' '
                    L1_seed=L1_seed[:-1]
                    L1_seed=L1_seed.strip('\n')
                    L1_seed=L1_seed.strip('\r')
                    L1_seed=L1_seed.replace('OR','||')
                    L1_seed=L1_seed.replace(' ','')
                    L1pre=self.MatchL1Seed(L1_seed, HLTl1predic)
                    L1path=L1_seed
                else:
                    L1path="null"
                    L1pre='-1'
                hltmenu[path]=(L1path,L1pre,-1)


        return hltmenu
    
    def getHLTSteamRates(self,steamFile):
        data={}
        predic={}
        import csv
    
        if '.csv' in steamFile:
            csvFile = file(steamFile,'r')
            steamReader=csv.reader(csvFile)
        if '.tsv' in steamFile:
            steamReader=open(steamFile,'r')
        for Line in steamReader:
            if '.tsv' in steamFile:
                line = Line.split('\t')
            if '.csv' in steamFile:
                line = Line
            path = line[self.file1_hltpath].split("_v")[0]
            path = path.strip()
    
            if path.find("HLT_")!=-1:
                try:
                    rate = float(line[self.file1_hltrate])
                    rateErr = float(line[self.file1_hltrateErr])
                    prescale = 0 #hltprescales[path] #int(line[0])
                except:
                    rate = -1
                    rateErr = -1
                    prescale = -1
                try:
                    group = line[self.file1_group]
                except:
                    group = "Null"
                try:
                    dataset = line[self.file1_dataset]
                except:
                    dataset= "Null"
                data[path]=(rate,rateErr,prescale,group,dataset)
        return data
      
    def getHLTSteamCount(self,steamFile):
        data={}
        predic={}
        import csv
    
        if '.csv' in steamFile:
            csvFile = file(steamFile,'r')
            steamReader=csv.reader(csvFile)
        if '.tsv' in steamFile:
            steamReader=open(steamFile,'r')
        for Line in steamReader:
            if '.tsv' in steamFile:
                line = Line.split('\t')
            if '.csv' in steamFile:
                line = Line
            path = line[self.file6_hltpath].split("_v")[0]
            path = path.strip()

            if path.find("HLT_")!=-1:
                try:
                    count = int(float(line[self.file6_hltcount]))
                except:
                    print line[self.file6_hltcount]
                    count = -1
                data[path]=(count)
        return data
    
    
    
    
    def getRateListRun(self):
        RateInformation_dic={}
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
        n=0
        for lumi in self.lumilist:
            lumidic[lumi]=n
            n+=1

        inputLumi = float(self.input_lumi.split('e')[0])*(10**(int(self.input_lumi.split('e')[1])-30))
        targetLumi = float(self.target_lumi.split('e')[0])*(10**(int(self.target_lumi.split('e')[1])-30))
        
        if not self.useLumiScale :
            lumiScale=1.
        else:
            if inputLumi < 0:
                try:
                    jsonfile=self.getJson(self._runnr,self.json_name)
                    avePU, aveLumi=self.getPU(self._runnr,jsonfile)
                except:
                    aveLumi = targetLumi
                    print "error in input luminosity!"
                inputLumi = aveLumi
            lumiScale = targetLumi / inputLumi
        if self.type_in == "steam":
            print "#"*30
            print "#"*30
            print "type: ",self.type_in
            if self.useLumiScale:
                print "input Lumi : ",inputLumi
                print "*"*30
                print "target Lumi : ",targetLumi
                print "*"*30
            #print "prescale lumi column:",self.index_lumi
            #print "*"*30
            print "lumi sf for rate:",lumiScale
            print "*"*30
            if self.P_hltrates:
                print "steam hlt file : ",self.file1_name
            print "*"*30
            if self.P_l1rates:
                print "steam l1 file : ",_steamL1Rates
                print "*"*30
            if self.P_hltrates:
                HLTsteamRates	=self.getHLTSteamRates	(self.file1_name)
                HLTl1predic	=self.getL1pre		(self.file4_name)
                HLT_L1seed	=self.getHLTmenuSteam	(self.file3_name,HLTl1predic)
                HLT_Pre		=self.getHLTpre		(self.file5_name)
                HLTsteamCount	=self.getHLTSteamCount	(self.file6_name)
            if self.P_l1rates:
                L1steamRates=self.getL1SteamRates(self._steamL1Rates)

            for path in HLTsteamRates:
                tmp_dic={}

                steamRate=0
                steamRateErr=0
                steamcount=0
                steamcountErr=0
                dataset='null'
                group='null'
                hltPrescaleSteam=-1
                hltprescaled=-1
                SteamL1path=''
                SteamL1pre=''
                pretotal=-1

                if path in HLTsteamRates:
                    steamRate=HLTsteamRates[path][0]
                    steamRate*=lumiScale
                    steamRateErr=HLTsteamRates[path][1]
                    steamRateErr*=lumiScale
                    group='"'+HLTsteamRates[path][3]+'"'
                    dataset='"'+HLTsteamRates[path][4]+'"'
                if path in HLT_Pre:
                    hltPrescaleSteam=int(HLT_Pre[path])
    #                if PSforSteam and hltPrescaleSteam!=0:
    #                    steamRate/=hltPrescaleSteam
    #                    steamRateErr/=hltPrescaleSteam
                if path in HLTsteamCount:
                    steamcount=int(HLTsteamCount[path])
                    if self.PSforSteam and hltPrescaleSteam!=0:
                        steamcount=int(float(steamcount)/float(hltPrescaleSteam))
                    steamcountErr=math.sqrt(steamcount)
                if path in HLT_L1seed:
                    SteamL1path+=HLT_L1seed[path][0]
                    SteamL1pre+=HLT_L1seed[path][1]
                    pretotal=HLT_L1seed[path][2]                

                tmp_dic["HLT_group"]=group
                tmp_dic["HLT_dataset"]=dataset
                tmp_dic["HLT_rate"]=(steamRate,steamRateErr)
                tmp_dic["HLT_count"]=steamcount
                tmp_dic["HLT_prescale"]=hltPrescaleSteam
                tmp_dic["HLT_L1_seed"]=SteamL1path
                tmp_dic["HLT_L1_prescale"]=SteamL1pre
                RateInformation_dic[path]= tmp_dic
            RateInformation_dic["title"] = {"HLT_rate":"", "HLT_count":"", "HLT_prescale":"", "HLT_L1_seed":"", "HLT_L1_prescale":"", "HLT_group":"", "HLT_dataset":""}
            RateInformation_dic["info"] = {"type":self.type_in,"runNo":self._runnr,"lumi":self.index_lumi}


        if self.type_in == "wbm":
            self.lumicolumn=2+lumidic[self.index_lumi]
            jsonfile=self.getJson(self._runnr,self.json_name)
            avePU, aveLumi=self.getPU(self._runnr,jsonfile)
            print "#"*30
            print "#"*30
            print "type: ",self.type_in
            if self.useLumiScale:
                print "input Lumi : ",inputLumi
                print "*"*30
                print "target Lumi : ",targetLumi
                print "*"*30
            print "prescale lumi column:",self.index_lumi
            print "*"*30
            print "run No : ",self._runnr
            print "json : ",jsonfile
            print "average pile up:",avePU
            print "*"*30
            print "average Luminosity:",aveLumi
            print "*"*30
            print "lumi sf for rate:",lumiScale
            print "*"*30

            hltRates		=self.getTriggerRates(self._runnr,jsonfile)
            hltPrescales	=self.getHLTPrescales(self._runnr)
            l1Prescales		=self.getL1Prescales(self._runnr)

            #get rate list:
            for path in hltRates:
                tmp_dic = {}
                rates=hltRates[path][0]
                l1seeds=hltPrescales[path][1].strip('"').replace(" OR ","||")

                #print l1seeds


                prescaledPath=False
                hltPrescaleOnline=1
                if rates[1]!=0 and rates[1]!=rates[0]:
                    prescaledPath=True
                    hltPrescaleOnline = float(rates[1]/rates[0])

                l1Prescale=0
                L1pre=''
                L1pre=self.MatchL1Seed(l1seeds,l1Prescales)

                wbmhltPrescale=0
                if (path in hltPrescales):
                    wbmhltPrescale=hltPrescales[path][0]

                rate =rates[3]
                rateErr=0
                ncount=0
                ncountPSed=0
                if rates[2]!=0:
                    rateErr=math.sqrt(rates[2])/rates[2]*rate
                    ncount = rates[2]
                    ncountPSed = int(float(ncount)/self.PsNorm)
                rate*=lumiScale
                rateErr*=lumiScale

                tmp_dic["HLT_group"]="null"
                tmp_dic["HLT_dataset"]="null"
                tmp_dic["HLT_rate"]=(rate,rateErr)
                tmp_dic["HLT_count"]=ncount
                tmp_dic["HLT_prescale"]=wbmhltPrescale
                tmp_dic["HLT_L1_seed"]=l1seeds
                tmp_dic["HLT_L1_prescale"]=L1pre
                RateInformation_dic[path]= tmp_dic
            RateInformation_dic["title"] = {"HLT_rate":"", "HLT_count":"", "HLT_prescale":"", "HLT_L1_seed":"", "HLT_L1_prescale":"", "HLT_group":"", "HLT_dataset":""}
            RateInformation_dic["info"] = {"type":self.type_in,"runNo":self._runnr,"lumi":self.index_lumi}

        return RateInformation_dic 


class comparison():
    output_dir='./'
    file1name = ''
    
    def Bias(self,no1,no2,e1,e2):
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
    
    def my_Pull(self,no1,no2,e2):
        my_pull = ''
        if no1 == 0 and no2 == 0:
            my_pull = 'N/A'
        elif no1 != 0 and no2 == 0:
            my_pull = 'No rates in Steam'
        elif no1 == 0 and no2 != 0:
            my_pull = 'No rates in WBM'
        elif e2 == 0:
            my_pull = 'N/A'
        else:
            my_pull = str(math.fabs(no1 - no2) / e2)
        return my_pull

    def comparisonRun(self,dic_1_in,dic_2_in):
        try:
            os.mkdir(self.output_dir)
        except:
            pass
     
        #print dic_1_in["info"]
        #print dic_2_in["info"]
        if dic_2_in["info"]["type"]=="wbm" and dic_1_in["info"]["type"]=="steam":
            dic_1=dic_2_in
            dic_2=dic_1_in
        else:
            dic_1=dic_1_in
            dic_2=dic_2_in

        #print dic_1["info"]
        #print dic_2["info"]
           
        if dic_1["info"]["type"]=="wbm" and dic_2["info"]["type"]=="steam":
            spreadSheetHeader1="Path,Group,Dataset,L1Path,L1Prescale("+dic_1["info"]["lumi"]+"),Steam L1path,Steam L1Prescale,WBM hltPrescale("+dic_1["info"]["lumi"]+"),Steam hltPrescale,Wbm Count,Steam Count,,Data Rate (Hz),,,Steam Rate (Hz),,abs(Data-Steam)(Hz),,Bias : (data-steam)/max(data;steam),,Pull\n"
            spreadSheetStr1="%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%.5f,+/-,%.5f,%.5f,+/-,%.5f,%.5f,%.2f%%,+/-,%.2f%%,%s\n" 
            if self.file1name=='':self.file1name="wbm%s_steam%sHLT.csv"%(str(dic_1["info"]["runNo"]),str(dic_1["info"]["runNo"]))

        if dic_1["info"]["type"]=="steam" and dic_2["info"]["type"]=="steam":
            spreadSheetHeader1="Path,Group_1,Dataset_1,Group_2,Dataset_2,L1Path,L1Prescale("+dic_1["info"]["lumi"]+"),Steam L1path,Steam L1Prescale,WBM hltPrescale("+dic_1["info"]["lumi"]+"),Steam hltPrescale,Wbm Count,Steam Count,,Data Rate (Hz),,,Steam Rate (Hz),,abs(Data-Steam)(Hz),,Bias : (data-steam)/max(data;steam),,Pull\n"
            spreadSheetStr1="%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%.5f,+/-,%.5f,%.5f,+/-,%.5f,%.5f,%.2f%%,+/-,%.2f%%,%s\n" 
            if self.file1name=='':self.file1name="steam%s_steam%sHTL.csv"%(str(dic_1["info"]["runNo"]),str(dic_1["info"]["runNo"]))

        if dic_1["info"]["type"]=="wbm" and dic_2["info"]["type"]=="wbm":
            spreadSheetHeader1="Path,L1Path,L1Prescale("+dic_1["info"]["lumi"]+"),Steam L1path,Steam L1Prescale,WBM hltPrescale("+dic_1["info"]["lumi"]+"),Steam hltPrescale,Wbm Count,Steam Count,,Data Rate (Hz),,,Steam Rate (Hz),,abs(Data-Steam)(Hz),,Bias : (data-steam)/max(data;steam),,Pull\n"
            spreadSheetStr1="%s,%s,%s,%s,%s,%d,%d,%d,%d,%.5f,+/-,%.5f,%.5f,+/-,%.5f,%.5f,%.2f%%,+/-,%.2f%%,%s\n" 
            if self.file1name=='':self.file1name="wbm%s_wbm%sHTL.csv"%(str(dic_1["info"]["runNo"]),str(dic_1["info"]["runNo"]))


            #~~~~~~~~~~~~~~~~~~~~~~
        filetowrite1=open(self.output_dir+'/'+self.file1name,'w')    #hlt rate comparision output file 
        filetowrite1.write(spreadSheetHeader1)
 
        #print HLT comparision
        for path in dic_1:
            if path in dic_2:
                if path =="info":continue
                if path =="title":continue
                group_1 = 	dic_1[path]["HLT_group"] 
                dataset_1 =	dic_1[path]["HLT_dataset"]
                l1_seed_1 = 	dic_1[path]["HLT_L1_seed"]
                l1_pre_1 = 	dic_1[path]["HLT_L1_prescale"]
                hlt_pre_1 = 	dic_1[path]["HLT_prescale"]
                hlt_count_1 =	dic_1[path]["HLT_count"]
                hlt_rate_1 =	dic_1[path]["HLT_rate"][0]
                hlt_rateErr_1 =	dic_1[path]["HLT_rate"][1]

                group_2 = 	dic_2[path]["HLT_group"] 
                dataset_2 =	dic_2[path]["HLT_dataset"]
                l1_seed_2 = 	dic_2[path]["HLT_L1_seed"]
                l1_pre_2 = 	dic_2[path]["HLT_L1_prescale"]
                hlt_pre_2 = 	dic_2[path]["HLT_prescale"]
                hlt_count_2 =	dic_2[path]["HLT_count"]
                hlt_rate_2 = 	dic_2[path]["HLT_rate"][0]
                hlt_rateErr_2 =	dic_2[path]["HLT_rate"][1]

                relDiff,relDiffErr=self.Bias(hlt_rate_2,hlt_rate_1,hlt_rateErr_2,hlt_rateErr_1)
                abs_rate = math.fabs(hlt_rate_1 - hlt_rate_2)
                my_pull = self.my_Pull(hlt_rate_1,hlt_rate_2 , max(hlt_rateErr_1,hlt_rateErr_2))
           
                    
                if dic_1["info"]["type"]=="wbm" and dic_2["info"]["type"]=="steam":
                    filetowrite1.write(spreadSheetStr1 %(path,group_2,dataset_2,l1_seed_1,l1_pre_1,l1_seed_2,l1_pre_2,hlt_pre_1,hlt_pre_2,hlt_count_1,hlt_count_2,hlt_rate_1,hlt_rateErr_1,hlt_rate_2,hlt_rateErr_2,abs_rate,relDiff,relDiffErr,my_pull))
                if dic_1["info"]["type"]=="steam" and dic_2["info"]["type"]=="steam":
                    filetowrite1.write(spreadSheetStr1 %(path,group_1,dataset_1,group_2,dataset_2,l1_seed_1,l1_pre_1,l1_seed_2,l1_pre_2,hlt_pre_1,hlt_pre_2,hlt_count_1,hlt_count_2,hlt_rate_1,hlt_rateErr_1,hlt_rate_2,hlt_rateErr_2,abs_rate,relDiff,relDiffErr,my_pull))
                if dic_1["info"]["type"]=="wbm" and dic_2["info"]["type"]=="wbm":
                    filetowrite1.write(spreadSheetStr1 %(path,l1_seed_1,l1_pre_1,l1_seed_2,l1_pre_2,hlt_pre_1,hlt_pre_2,hlt_count_1,hlt_count_2,hlt_rate_1,hlt_rateErr_1,hlt_rate_2,hlt_rateErr_2,abs_rate,relDiff,relDiffErr,my_pull))

