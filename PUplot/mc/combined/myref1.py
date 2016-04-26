def press_any_key_exit():
    import termios
    import sys
    import os
    msg='press any key to continue ...\n'
    fd = sys.stdin.fileno()

    old_ttyinfo = termios.tcgetattr(fd)

    new_ttyinfo = old_ttyinfo[:]

    new_ttyinfo[3] &= ~termios.ICANON
    new_ttyinfo[3] &= ~termios.ECHO

    sys.stdout.write(msg)
    sys.stdout.flush()
    termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
    os.read(fd, 7)

    termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)

def getgroupdic(steamFile):
    file_path=1
    file_group=2
    groupdic={}
    grouplist=[]
    if '.tsv' in steamFile:
        filesteam=open(steamFile,'r')
        for Line in filesteam:
            line=Line.split('\t')
            path=line[file_path].split('_v')[0]
            if not 'HLT_' in path:continue
            if len(line[file_group]) <2:continue
            tmpgrouplist=line[file_group].split(',')
            for group in tmpgrouplist:
                if group in grouplist:
                    tmplist=[]
                    tmplist=groupdic[group]
                    tmplist.append(path)
                    groupdic[group]=tmplist
                else:
                    tmplist=[]
                    tmplist.append(path)
                    groupdic[group]=tmplist
                    grouplist.append(group)


        return groupdic
    if '.csv' in steamFile:
        with open(steamFile) as csvfile:
            steamReader=csv.reader(csvfile)

            for line in steamReader:
                path=line[file_path].split('_v')[0]
                if not 'HLT_' in path:continue
                if len(line[file_group]) <2:continue
                grouplist=line[file_group].split(',')
                for group in grouplist:
                    groupdic[group].append(group)

        return groupdic

def getsteampath(steamFile):
    file_path=1
    steamlist=[]
    if '.tsv' in steamFile:
        filesteam=open(steamFile,'r')
        for Line in filesteam:
            line=Line.split('\t')
            path=line[file_path].split('_v')[0]
            if not 'HLT_' in path:continue
            if path not in steamlist:
                steamlist.append(path)


        return steamlist
    if '.csv' in steamFile:
        import csv
        with open(steamFile) as csvfile:
            steamReader=csv.reader(csvfile)

            for line in steamReader:
                path=line[file_path].split('_v')[0]
                if not 'HLT_' in path:continue
                if path not in steamlist:
                    steamlist.append(path)

        return steamlist

def getHLTprescaledic(steamFile):
    file_path=1
    file_prescale=0
    hltprescaledic={}
    if '.tsv' in steamFile:
        filesteam=open(steamFile,'r')
        for Line in filesteam:
            line=Line.split('\t')
            path=line[file_path].split('_v')[0]
            if not 'HLT_' in path:continue
            hltprescaledic[path]=line[file_prescale]


        return hltprescaledic
    if '.csv' in steamFile:
        import csv
        with open(steamFile) as csvfile:
            steamReader=csv.reader(csvfile)

            for line in steamReader:
                path=line[file_path].split('_v')[0]
                if not 'HLT_' in path:continue
                hltprescaledic[path]=line[file_prescale]

        return hltprescaledic

def getNTuplesPrescale(rootfile):
    import ROOT
    prescales={}
  # take the first "hltbit" file                                                                                                   
    dirpath = ''
    filenames = []

    _file0 = ROOT.TFile.Open(rootfile)
    chain = ROOT.gDirectory.Get("HltTree")

    for leaf in chain.GetListOfLeaves():
        name = leaf.GetName()
        if (("HLT_" in name) or ("L1_" in name)) and not ("Prescl" in name):
            trigger=name
            i=0
            pname=name+'_Prescl'
            for event in chain:
                value=getattr(event,pname)
                if (i>=2): break
                i+=1
            prescales[trigger.split('_v')[0]]=value

    return prescales


def my_mkdir(output_dir):
    import os
    tmplist=output_dir.split('/')
    for i in range(len(tmplist)):
        tmpstr=''
        try:
            for j in range(i+1):
                if j == 0:
                    tmpstr=tmplist[j]
                else:
                    tmpstr=tmpstr+'/'+tmplist[j]
            os.mkdir(tmpstr)
        except:
            pass

def printgrouprates(pathList,comparisonFile,output_dir,outputname):
    import os
    file_path=0
    firstline=True

    my_mkdir(output_dir)

    filetowrite=open(output_dir+'/'+outputname+'.csv','w')
    with open(comparisonFile) as csvfile:
        steamReader=csv.reader(csvfile)
        for line in steamReader:
            path=line[file_path].split('_v')[0]
            if (not 'HLT_' in path) and (not firstline) :continue
            if (path in pathList) or firstline:
                firstline=False
                text=''
                for i in range(len(line)):
                    text=text+line[i]+','
                text=text[:-1]
                filetowrite.write(text+'\n')
            
    filetowrite.close()

def cvs_to_excel():
    import xlwt
    import cvs

    myexcel = xlwt.Workbook()
    
    for group in dic:
        mysheet = myexcel.add_sheet(group)
        csvfilename='Results/group/'+group+'.csv'
        csvfile = file(csvfilename,"rb")
        reader = csv.reader(csvfile)
        l = 0
        for line in reader:
            r = 0
            for i in line:
                mysheet.write(int(l),int(r),i)
                r=r+1
            l=l+1
        
    myexcel.save("Results/group/myexcel.xls")
    
    
