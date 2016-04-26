

input_File='test.tsv'
output_File='output.tsv'


file3_hltpath = 2           #HLT_
file3_hltprescale = 9      #hlt prescale
file3_l1seed = 16           #L1_seed
file3_l1prescale = 9      #l1 prescale

file4_l1path = 0           #L1_
file4_l1prescale = 1      #l1 prescale



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

def getHLTmenuSteam(steamFile):
    hltmenu={}
    import csv
 
    HLTl1predic=getL1pre('L1menu.csv')
    if '.csv' in steamFile:
        with open(steamFile) as csvfile:
            steamReader=csv.reader(csvfile)
            for line in steamReader:
                path = line[file3_hltpath].split("_v")[0]
                path = path.strip()
    
                if path.find("HLT_")!=-1:
                    if (file3_l1seed > 0):
                        L1path = line[file3_l1seed].split(' OR ')
                        L1pre = ''
                        L1pretotal = 1
                        hltpre = int(line[file3_hltprescale])
                        for i in range(len(L1path)):
                            if L1path[i] in HLTl1predic:
                                if i == 0:
                                    L1pre = str(HLTl1predic[L1path[i]])
                                else:
                                    L1pre = L1pre + '|' +str(HLTl1predic[L1path[i]]) 
                                #L1pretotal*=int(HLTl1predic[L1path[i]])
                                L1pretotal=int(line[file3_l1prescale])
                                if L1pretotal == 0:
                                    L1pretotal =1
    
                            else:
                                L1pre = L1pre + '-1|'
                    else:
                        L1path="null"
                        L1pre='-1'
                    hltmenu[path]=(line[file3_l1seed],L1pre,float(L1pretotal),hltpre)

    if '.tsv' in steamFile:
        file_hlt=open(steamFile,'r')
        for Line in file_hlt:
            line=Line.split('\t')
            path = line[file3_hltpath].split("_v")[0]
            path = path.strip()

            if path.find("HLT_")!=-1:
                if (file3_l1seed > 0):
                    L1path = line[file3_l1seed].split(' OR ')
                    L1pre = ''
                    L1pretotal = 1
                    hltpre = int(line[file3_hltprescale])
                    for i in range(len(L1path)):
                        if L1path[i] in HLTl1predic:
                            if i == 0:
                                L1pre = str(HLTl1predic[L1path[i]])
                            else:
                                L1pre = L1pre + '|' +str(HLTl1predic[L1path[i]])
                            #L1pretotal*=int(HLTl1predic[L1path[i]])
                            L1pretotal=int(line[file3_l1prescale])
                            if L1pretotal == 0:
                                L1pretotal =1

                        else:
                            L1pre = L1pre + '-1|'
                else:
                    L1path="null"
                    L1pre='-1'
                hltmenu[path]=(line[file3_l1seed],L1pre,float(L1pretotal),hltpre)

    return hltmenu,HLTl1predic

dic1,dic2=getHLTmenuSteam('GRun_V58.tsv')

#print dic1
if '.tsv' in input_File:
    file_input=open(input_File,'r')
    file_output=open(output_File,'w')
    for Line in file_input:
        text=''
        line=Line.split('\t')
        for i in range(len(line)):
            if i == 3:
                #if line[1].split('_v')[0] in dic1:
                try:
                    text+=dic1[line[1].split('_v')[0]][0]+'\t'+dic1[line[1].split('_v')[0]][1]+'\t'
                except:
                    text+='\t'+'\t'
                text+=line[i]+'\t'
            elif i == len(line)-1:
                text+=line[i]
            else:
                text+=line[i]+'\t'
        #text+='\n'
        file_output.write(text)
