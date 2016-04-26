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
    
    
