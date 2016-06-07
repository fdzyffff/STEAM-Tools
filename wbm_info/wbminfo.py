import os
import argparse
import copy
from cernSSOWebParser import parseURLTables

#******************************************************************************************
def getwbm(Runnr):
    _runnr=Runnr
    pu_write=False#use to debug
    #******************************************************************************************
    def getJson(runnr):
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
        max_pu=0
        min_pu=99
        psAndInstLumis=getPSAndInstLumis(runnr)
        for ls in jsonfile:
            minLS=int(ls[0])
            maxLS=int(ls[1])
            nLS+=(maxLS-minLS+1)
            for lumi in range(minLS,maxLS+1):
                if lumi in psAndInstLumis:
                    sum_lumi+=psAndInstLumis[lumi][1]
                    tmp_pu=(psAndInstLumis[lumi][1]*80000)/(11246*nbunch)
                    if max_pu<tmp_pu:max_pu=tmp_pu
                    if min_pu>tmp_pu and tmp_pu>5:min_pu=tmp_pu

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
        lumiscaled = 10000/float(sum_lumi)*n_lumi
        aveLumi = float(sum_lumi)/n_lumi
    
        return avePU,max_pu,min_pu,lumiscaled,aveLumi
                
        
     
    
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
    
    
    
    
    jsonfile=getJson(_runnr)
    avePU,max_pu,min_pu,scaled,aveLumi=getPU(_runnr,jsonfile)
   




    print "run No : ",_runnr
    print "json : ",jsonfile
    print "ave PU : ",avePU
    print "ave Lumi : ",aveLumi
    print "*"*30
    

runList=[
260627,
256843
]
   
for runNo in runList: 
    getwbm(runNo)    
    
    
    
    
    
    
