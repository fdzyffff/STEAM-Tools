import os
import argparse
import copy
from cernSSOWebParser import parseURLTables


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

    lumidic={}
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
                lumidic[lumi]=(psAndInstLumis[lumi][1],tmp_pu)
    return lumidic



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

def getjson(inputdic,jsonfile,minPU,maxPU):
    jsonlist=[]
    for ls in jsonfile:
        flag_start=False
        for lumi in range(int(ls[0]),int(ls[1])+1):
            if inputdic[lumi][1]>minPU and inputdic[lumi][1]<maxPU:
                if not flag_start:
                    start_lumi=lumi
                    flag_start=True
                if flag_start and (lumi==int(ls[1])):
                    flag_start=False
                    final_lumi=lumi
                    tmplist=[]
                    tmplist.append(start_lumi,final_lumi)
                    jsonlist.append(tmplist)
            elif flag_start:
                flag_start=False
                final_lumi=lumi-1
                tmplist=[]
                tmplist.append(start_lumi,final_lumi)
                jsonlist.append(tmplist)
    return jsonlist 

jsondic={}
print getjson(getPU(260627,getJson(260627)),getJson(260627),13.5,15.5) 
jsondic[260627]=getjson(getPU(260627,getJson(260627)),getJson(260627),13.5,15.5)
tmp_file=open('json1.txt','w')
tmp_file.close()
print jsondic

