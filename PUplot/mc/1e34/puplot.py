import ROOT
import time
import os
import sys
import myref1
from math import *
from scipy.stats import binom
from array import array
from cernSSOWebParser import parseURLTables

#rundic={
#'259721':20.73,
#'259626':16.86,
#'256843':10.98,
#'256801':12.87,
#'260627':13.92
#}
#
pathlist1=[
'HLT_IsoMu22',
'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ',
'HLT_Photon120_R9Id90_HE10_IsoM',
'HLT_Ele27_WPLoose_Gsf',
'HLT_QuadPFJet_VBF',
'HLT_PFHT400',
'HLT_Mu24_eta2p1',
'HLT_Ele27_WPLoose_Gsf_CentralPFJet30_BTagCSV07',
'HLT_IsoMu16_eta2p1_MET30',
'HLT_DiPFJetAve260'
]




Yrangelist=[
[0,10],
[0,100],
[0,400]
]


def getnbx(run):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (run)
    tables=parseURLTables(url)
    lhcfill_key=tables[3][14][1]

    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReport?FILL=%s" % (lhcfill_key)
    tables=parseURLTables(url)
    nbunch=int(tables[3][18][1])

    return nbunch


def getrate(run,pathlist):

    column_path = 1
    column_rate = 3
    column_error = 5
    column_prescale = 0
#    nbx = getnbx(run)
    ratedic={}
    import csv

    #set zero~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    for path in pathlist:
        ratedic[path]=('0',-1.,-1.,False)

    #open file~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # steamFile = '/afs/cern.ch/user/x/xgao/CMSSW_7_6_3/src/RateEstimate/'+run+'/Results/compareWbm_Steam/'+run+'specficHLTpaths.csv'
   # steamFile = '/afs/cern.ch/user/x/xgao/CMSSW_7_6_3/src/RateEstimate/compareWbm_Steam/Results/'+run+'/'+run+'specficHLTpaths.csv'
    steamFile = '/afs/cern.ch/user/x/xgao/work/RateEstimate_mc_22_02_16/7e33/Results/mergedRates_MC_'+run+'.tsv'
    if '.csv' in steamFile:
        with open(steamFile) as csvfile:
            steamReader=csv.reader(csvfile)
            for line in steamReader:
                success=False
                if line[column_path].split('_v')[0] in pathlist:
                    rate = float(line[column_rate])
                    err = float(line[column_error])
                    success = True
                    ratedic [line[0]] = (run,rate,err,success)

    if '.tsv' in steamFile:
        tmp_file=open(steamFile,'r')
        for Line in tmp_file:
            line=Line.split('\t')
            success=False
            if line[column_path].split('_v')[0] in pathlist:
                rate = float(line[column_rate])
                err = float(line[column_error])
                success = True
                ratedic [line[column_path].split('_v')[0]] = (run,rate,err,success)
        tmp_file.close()

        for path in pathlist:
            if not ratedic[path][3] :
                print "Error get path: "+path+" in run:"+run


    return ratedic

def getPU(rundic):

    rundic['8to12']=10
    rundic['13to17']=15
    rundic['18to22']=20
    rundic['23to27']=25
    rundic['28to32']=30


def my_plot(pathlist,out_dir):
#plot~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

      #creat index.html to show in websit:
    try:
        os.mkdir(out_dir)
    except:
        pass
    
    htmfile=open(out_dir+'/index.html','w')
    htmfile.write('<!DOCTYPE html>\n')
    htmfile.write('<html>\n')
    htmfile.write('<style>.image { float:right; margin: 5px; clear:justify; font-size: 6px; font-family: Verdana, Arial, sans-serif; text-align: center;}</style>\n')
      #~~~~~~~~~~~~~~
    c1 = ROOT.TCanvas( 'c1', 'A Simple Graph with error bars', 200, 10, 700, 500 )
    c1.SetGrid()
    hfile = ROOT.TFile('kkk.root', 'RECREATE', 'Demo ROOT file with histograms' )
    
    j=1
    for path in pathlist:
        x, y = array( 'f' ), array( 'f' )
        ex, ey = array( 'f' ), array( 'f' )
       
        n=0 
        for run in rundic:
            x.append(rundic[run])
            ex.append(0.0)
            y.append(gdic[run][0][path][1])
            ey.append(gdic[run][0][path][2])
            n+=1
    
        print path
        print x
        print y
    
        gr = ROOT.TGraphErrors( n, x, y, ex, ey )
    #    gr = ROOT.TGraph( n, x, y )
        gr.SetMarkerColor( 4 )
        gr.SetMarkerStyle( 21 )
        gr.SetTitle( path  )
        gr.GetXaxis().SetTitle( '< PU >' )
        gr.GetYaxis().SetTitle( 'Steam Rates MC 7e33 (Hz)' )
        gr.GetYaxis().SetTitleSize(0.068)
        gr.GetYaxis().SetTitleOffset(0.63)
        for i in range(len(Yrangelist)):
            if max(y)<Yrangelist[i][1]:
                gr.GetYaxis().SetRangeUser(Yrangelist[i][0],Yrangelist[i][1])
                break
        gr.Draw( 'AP' )
        gr.Fit("pol1")
    
        gr.Write()
    
        c1.Update()
        p_path = out_dir+'/'+path 
        c1.Print('%s.png'%(p_path))
    
        htmfile.write("<div class=image><a href='"+path+".png'><img width=398 height=229 border=0 src='"+path+".png'></a><div style='width:398px'>"+path+"</div></div>\n")
    
    
    #print processing
        print "*"*20
        print "*** %d/%d finished ***"%(j,len(pathlist))
        print "*"*20
        j+=1
    htmfile.write('</html>')


#main~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
rundic={}
pathlist=[]
pathlist=myref1.getsteampath('/afs/cern.ch/user/x/xgao/work/RateEstimate_mc_22_02_16/7e33/Results/mergedRates_MC_23to27.tsv')

getPU(rundic)
print rundic
gdic={}
for run in rundic:
    tmp_list=[]
    tmp_dic={}
    tmp_dic=getrate(run,pathlist)
    tmp_list.append(tmp_dic)
    gdic[run]=tmp_list

my_plot(pathlist1,'7e33_mc_plot_part')
my_plot(pathlist,'7e33_mc_plot')
