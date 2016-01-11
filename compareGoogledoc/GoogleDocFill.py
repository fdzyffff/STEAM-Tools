#!/usr/bin/python
# -*- coding: utf-8 -*-

from name_change_map import *
import math
# STORM official Google Doc exported as TAB separated values
filetofill1=open('frozen_2015_25ns14e33_v4.4_HLT_V1_Rate_v2_hltmenu_13TeV_2.0e33_20151017_p.tsv','r')
filetofill2=open('frozen_2015_25ns14e33_v4.4_HLT_V1_25ns_data_Run_256843_Rates.tsv','r')

# open output file
filetowrite=open('newGoogleDoc.tsv','w')


#format parameters
file1_prescale = 3	#prescale
file1_path = 0		#HLT_
file1_rate = 4		#rate
file1_pm_symbal = 5	#' ±' or '+-'
file1_rateerror = 6	#errors

file2_prescale = 0      #prescale
file2_path = 1          #HLT_
file2_rate = 3          #rate
file2_pm_symbal = 4     #' ±' or '+-'
file2_rateerror = 5     #errors

namechange=False

#**************************************************************************************************************
#define function
def Ratio(no1,no2,e1,e2):
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




#read from file1
pathlist1=[]
ratelist1=[]
errlist1=[]
scalelist1=[]
name_change_use_file1={}
for line in filetofill1:
    path1=line.split('\t')
    if 'HLT_' in path1[file1_path] or 'Alca_' in path1[file1_path]:
        if '±' in path1[file1_pm_symbal] or '+-' in path1[file1_pm_symbal]:
            if namechange and path1[file1_path] in name_change_map:
                pathlist1.append(name_change_map[path1[file1_path]].strip(' '))
                name_change_use_file1[path1[file1_path]]=name_change_map[path1[file1_path]]
            else:
                pathlist1.append(path1[file1_path].strip(' '))
            scalelist1.append(path1[file1_prescale].strip(' '))
            ratelist1.append(path1[file1_rate])
            errlist1.append(path1[file1_rateerror])
#        else :
rates1=dict(zip(pathlist1, ratelist1))
errors1=dict(zip(pathlist1, errlist1))
prescale1=dict(zip(pathlist1, scalelist1))


#read from file2
pathlist2=[]
ratelist2=[]
errlist2=[]
scalelist2=[]
name_change_use_file2={}
for line in filetofill2:
    path2=line.split('\t')
    if 'HLT_' in path2[file2_path] or 'Alca_' in path2[file2_path]:
        if '±' in path2[file2_pm_symbal] or '+-' in path2[file2_pm_symbal]:
            if namechange and path2[file2_path] in name_change_map:
                pathlist2.append(name_change_map[path2[file2_path]].strip(' '))
                name_change_use_file2[path2[file2_path]]=name_change_map[path2[file2_path]]
            else:
                pathlist2.append(path2[file2_path].strip(' '))
            scalelist2.append(path2[file2_prescale].strip(' '))
            ratelist2.append(path2[file2_rate])
            errlist2.append(path2[file2_rateerror])


rates2=dict(zip(pathlist2, ratelist2))
errors2=dict(zip(pathlist2, errlist2))
prescale2=dict(zip(pathlist2, scalelist2))

num_samepath = 0
num_samevalue = 0
num_diff_value = 0
num_file1_last = 0
num_file2_last = 0

bias={}
biaslist=[]
biaserrors={}
#write the value of the path in both files
filetowrite.write('file1:\t' + filetofill1.name + '\n')
filetowrite.write('file2:\t' + filetofill2.name + '\n')
filetowrite.write('\tfile1\t\t\t\t\t\tfile2\t\t\t\n')
filetowrite.write('path\tprescale1\t\trate1\t\t\tprescale2\t\trate2\t\t\t\tbias\n')
for p0 in pathlist1:
    if p0 in pathlist2:
	num_samepath += 1
	if rates1[p0] != rates2[p0]:
            bias[p0] = 0.0
            biaserrors[p0] = 0.0
            bias[p0],biaserrors[p0] = Ratio(float(rates1[p0]),float(rates2[p0]),float(errors1[p0]),float(errors2[p0]))
            biaslist.append(bias[p0])
            num_diff_value += 1
            
for p in sorted(bias.iteritems(), key=lambda d:d[1], reverse = True ): 
    p0=p[0]
    filetowrite.write(p0 + '\t' + prescale1[p0]+ '\t'+rates1[p0]+'\t ±\t'+errors1[p0]+'\t\t'+prescale2[p0]+'\t'+rates2[p0]+'\t ±\t'+errors2[p0]+'\t\t%.2f%%\t±\t%.2f%%\n'%(bias[p0],biaserrors[p0]))


for p0 in pathlist1:
    if p0 in pathlist2:
        if prescale1[p0] != prescale2[p0]:
            filetowrite.write('********************************************************************************************************\n')
            filetowrite.write('Different prescale in :'+p0+'\t'+prescale1[p0]+'<----------->'+prescale2[p0]+'\trate:'+rates1[p0]+'\t'+rates2[p0]+'\n')
        del rates1[p0]
        del rates2[p0]
        del errors1[p0]
        del errors2[p0]

#write the path not matched
filetowrite.write('********************************************************************************************************\n')
filetowrite.write('path not matched in ' + filetofill1.name + '\n')
filetowrite.write('********************************************************************************************************\n')
for p1 in rates1:
    filetowrite.write('\t'+ p1 + '\n')
    num_file1_last += 1

filetowrite.write('********************************************************************************************************\n')
filetowrite.write('path not matched in ' + filetofill2.name + '\n')
filetowrite.write('********************************************************************************************************\n')
for p2 in rates2:
    filetowrite.write('\t'+ p2 + '\n')
    num_file2_last += 1

#write the path which use name_change_map
filetowrite.write('********************************************************************************************************\n')
if namechange:
    filetowrite.write('name changed path in ' + filetofill1.name + '\n')
    filetowrite.write('********************************************************************************************************\n')
    for old,new in name_change_use_file1.items():
        filetowrite.write('\t%s ---> %s\n' %(old,new))
    
    filetowrite.write('********************************************************************************************************\n')
    filetowrite.write('name changed path in ' + filetofill2.name + '\n')
    filetowrite.write('********************************************************************************************************\n')
    for old,new in name_change_use_file2.items():
        filetowrite.write('\t%s -> %s\n' %(old,new))
    
#write sum
filetowrite.write('********************************************************************************************************\n')
filetowrite.write('Numbers of the same path between file1 and file2 is: %d \n'%(num_samepath))
#filetowrite.write('Numbers of the path with different value between "' +filetofill1.name + '" and "' + filetofill2.name + '" is: %d \n'%(num_samepath))
filetowrite.write('Numbers of the rest path in "' +filetofill1.name  + '" is: %d \n'%(num_file1_last))
filetowrite.write('Numbers of the rest path in "' +filetofill2.name  + '" is: %d \n'%(num_file2_last))
#close file
filetofill1.close()
filetofill2.close()
filetowrite.close()
