file_1_name = 'highbias.tsv'
file_out_name ='279116/split_group.tsv' 
column_group = 1

GroupDic = {}
title = ''
file_1 = open(file_1_name,'r')
isTitle = True
for Line in file_1:
    if isTitle:
        title = Line
        isTitle = False
        continue
    line = Line.split('\t')
    tmp_group_list = line[column_group].split(',')
    print tmp_group_list
    for group in tmp_group_list:
        if len(group) < 1: continue
        if not group in GroupDic:
            GroupDic[group] = []
            GroupDic[group].append(Line)
            print '%s : %s'%(group,line[column_group])
        else:
            GroupDic[group].append(Line)
            print '%s : %s'%(group,line[column_group])


#output
file_out = open(file_out_name,'w')
file_out.write('Group\t%s'%(title))
for group in GroupDic:
    file_out.write('\n%s\n'%(group))
    for group_str in GroupDic[group]: 
        file_out.write('\t%s'%(group_str))
