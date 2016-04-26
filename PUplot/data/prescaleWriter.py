#/usr/bin/env python

table = open('prescalesHLT_2e33_v4.2','r')
iter=0
print 'Table for prescales for algo trigger prescales - 2e33'
for line in table.readlines():
    iter+=1
    entries=line.split()
    prescale=entries[4]
    path=entries[10]
    print path+": "+prescale

#    if iter%8==0:
#        print
#    if iter>127:
#        break
table.close()

