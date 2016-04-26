import ROOT
import time
import sys
import myref1
from math import *
from scipy.stats import binom
from array import array
from cernSSOWebParser import parseURLTables


xsectionDatasets ={
'QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8':1837410000.,#2237000000.,
'QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8':140932000.,#161500000.,
'QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8':19204300.,#22110000.,
'QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8':2762530.,#3000114.3,
'QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8':471100.,#493200.,
'QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8':117276.,#120300.,
'QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8':7823.,#7475.,
'QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8':648.2,#587.1,
#'QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8':186.9,#167.,
#'QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8':32.293,#28.25,
#'QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8':9.4183,#8.195,
#'QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8':0.84265,#0.7346,
#'QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8':0.114943,#0.1091,
#'QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8':0.00682981,#0.0,
#'QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8':0.000165445,#0.0,

#'QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8',
#'QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8',
#'QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8',
#'QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8',
#'QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8',
#'QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8',
## EM fraction evaluated using fraction "(!HLT_BCToEFilter_v1 && HLT_EmFilter_v1)" in plain QCD sample 
'QCD_Pt-15to20_EMEnriched_TuneCUETP8M1_13TeV_pythia8':1279000000.0*0.0018,
'QCD_Pt-20to30_EMEnriched_TuneCUETP8M1_13TeV_pythia8':557600000.0*0.0096,
'QCD_Pt-30to50_EMEnriched_TuneCUETP8M1_13TeV_pythia8':136000000.0*0.073,
'QCD_Pt-50to80_EMEnriched_TuneCUETP8M1_13TeV_pythia8':19800000.0*0.146,
'QCD_Pt-80to120_EMEnriched_TuneCUETP8M1_13TeV_pythia8':2800000.0*0.125,
'QCD_Pt-120to170_EMEnriched_TuneCUETP8M1_13TeV_pythia8':477000.0*0.132,
## Mu fraction evaluated using fraction "MCMu3" in plain QCD sample 
'QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8':1279000000.0*0.003,
'QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8':557600000.0*0.0053,
'QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8':136000000.0*0.01182,
'QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8':19800000.0*0.02276,
'QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8':2800000.0*0.03844,
'QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8':477000.0*0.05362,

'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8':60290.,#16000.,
'DYToLL_M_1_TuneCUETP8M1_13TeV_pythia8':20000,#about 6960. x3
}
totalXsection=0.0
for dataset in xsectionDatasets:
    totalXsection+=xsectionDatasets[dataset]
#rundic={
#'259721':20.73,
#'259626':16.86,
#'256843':10.98,
#'256801':12.87,
#'260627':13.92
#}
#
pathlist1=[
'HLT_IsoMu20',
'HLT_IsoTkMu20',
'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ',
'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL',
'HLT_Mu30_TkMu11',
'HLT_IsoMu17_eta2p1_LooseIsoPFTau20_SingleL1',
'HLT_Mu20',
'HLT_Ele27_WPLoose_Gsf',
'HLT_Ele27_eta2p1_WPLoose_Gsf',
'HLT_Ele15_IsoVVVL_PFHT350_PFMET50',
'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL',
'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL',
'HLT_DoubleEle24_22_eta2p1_WPLoose_Gsf',
'HLT_Ele27_eta2p1_WPLoose_Gsf_DoubleMediumIsoPFTau40_Trk1_eta2p1_Reg',
'HLT_Ele23_CaloIdL_TrackIdL_IsoVL',
'HLT_LooseIsoPFTau50_Trk30_eta2p1_MET80',
'HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg',
'HLT_Ele27_eta2p1_WPLoose_Gsf_LooseIsoPFTau20',
'HLT_QuadPFJet_DoubleBTagCSV_VBF_Mqq200',
'HLT_AK8DiPFJet250_200_TrimMass30_BTagCSV0p45',
'HLT_Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50',
'HLT_MonoCentralPFJet80_PFMETNoMu90_JetIdCleaned_PFMHTNoMu90_IDTight',
'HLT_DiPFJetAve500',
'HLT_AK8PFHT600_TrimR0p1PT0p03Mass50_BTagCSV0p45',
'HLT_HT400_DisplacedDijet40_Inclusive',
'HLT_PFHT200_DiPFJetAve90_PFAlphaT0p57',
'HLT_PFHT800'
]

pathlisttest=['HLT_Dimuon0_Jpsi_Muon']

Yrangelist=[
[0,0.000000000001],
[0,0.00000000001],
[0,0.0000000001],
[0,0.000000001],
[0,0.00000001],
[0,0.0000001],
[0,0.000001],
[0,0.00001],
[0,0.0001],
[0,0.001],
[0,0.01],
[0,0.1]
]


def getnbx(run):
    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?RUN=%s&DB=default" % (run)
    tables=parseURLTables(url)
    lhcfill_key=tables[3][14][1]

    url="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/FillReport?FILL=%s" % (lhcfill_key)
    tables=parseURLTables(url)
    nbunch=int(tables[3][18][1])

    return nbunch


def getrate(run,pathlist,lumi):

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
    steamFile = '/afs/cern.ch/user/x/xgao/work/RateEstimate_mc_22_02_16/'+lumi+'/Results-bak/mergedRates_MC_'+run+'.tsv'
    
#    if lumi == '2e33':
#        HLTprescaledic=myref1.getNTuplesPrescale('/afs/cern.ch/user/x/xgao/eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Spring15/Hui_HLTRates_2e33_25ns_V4p4_V1/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/QCD15/160204_205959/0000/hltbits_1.root')
#    if lumi == '7e33':
#        HLTprescaledic=myref1.getNTuplesPrescale('/afs/cern.ch/user/x/xgao/eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Spring15/Hui_HLTRates_2e33_25ns_V4p4_V1_3rd_round/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/QCD15/160212_042205/0000/hltbits_1.root')

    #print HLTprescaledic
    if '.csv' in steamFile:
        with open(steamFile) as csvfile:
            steamReader=csv.reader(csvfile)
            for line in steamReader:
                success=False
                if line[column_path].split('_v')[0] in pathlist:
                    rate = float(line[column_rate])
                    err = float(line[column_error])
                    success = True
                    ratedic [column_path] = (run,rate,err,success,lumi)

    if '.tsv' in steamFile:
        tmp_file=open(steamFile,'r')
        for Line in tmp_file:
            line=Line.split('\t')
            success=False
            path=line[column_path].split('_v')[0]
            if line[column_path].split('_v')[0] in pathlist:
                rate = float(line[column_rate])
                err = float(line[column_error])
                #~~~~~~~~~~~~~total crossXection   
                rate /= totalXsection
                err /= totalXsection
#                print 'before unprescale : ',rate
               # try:
               #     if HLTprescaledic[line[column_path].split('_v')[0]]!=0:
               #         rate*=float(HLTprescaledic[line[column_path].split('_v')[0]])
               #         err*=float(HLTprescaledic[line[column_path].split('_v')[0]])
               # except:
               #     pass
#                print 'after unprescale : ',rate
#                print "******************"
                success = True
                #ratedic [line[column_path].split('_v')[0]] = (run,rate,err,success,lumi,HLTprescaledic[line[column_path].split('_v')[0]])
                ratedic [line[column_path].split('_v')[0]] = (run,rate,err,success,lumi,-1)#,HLTprescaledic[line[column_path].split('_v')[0]])
        tmp_file.close()

        for path in pathlist:
            if not ratedic[path][3] :
                print "Error get path: "+path+" in run:"+run+" in lumi: "+lumi


    return ratedic

def getPU(rundic):

    rundic['8to12']=10
    rundic['13to17']=15
    rundic['18to22']=20
    rundic['23to27']=25
    rundic['28to32']=30

def Leg():
    legend=TLegend(0.6,0.6,0.8,0.8)
    legend.AddEntry()

#main~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
rundic1={}
rundic2={}
rundic3={}
pathlist=[]
pathlist=pathlist1
#pathlist=myref1.getsteampath('/afs/cern.ch/user/x/xgao/work/RateEstimate_mc_22_02_16/7e33/Results/mergedRates_MC_23to27.tsv')

getPU(rundic1)
print rundic1
#~~~~7e33~~~~~~~~~
gdic1={}
for run in rundic1:
    tmp_list=[]
    tmp_dic={}
    tmp_dic=getrate(run,pathlist,'7e33')
    tmp_list.append(tmp_dic)
    gdic1[run]=tmp_list

#myref1.press_any_key_exit()
#~~~~2e33~~~~~~~~~
getPU(rundic2)
gdic2={}
for run in rundic2:
    tmp_list=[]
    tmp_dic={}
    tmp_dic=getrate(run,pathlist,'2e33')
    tmp_list.append(tmp_dic)
    gdic2[run]=tmp_list

#~~~~1e34~~~~~~~~~~
rundic3['23to27']=25
rundic3['28to32']=30
gdic3={}

for run in rundic3:
    tmp_list=[]
    tmp_dic={}
    tmp_dic=getrate(run,pathlist,'1e34')
    tmp_list.append(tmp_dic)
    gdic3[run]=tmp_list

#plot~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  #creat index.html to show in websit:
htmfile=open('mc_plot_part/index.html','w')
htmfile.write('<!DOCTYPE html>\n')
htmfile.write('<html>\n')
htmfile.write('<style>.image { float:right; margin: 5px; clear:justify; font-size: 6px; font-family: Verdana, Arial, sans-serif; text-align: center;}</style>\n')
  #~~~~~~~~~~~~~~
c1 = ROOT.TCanvas( 'c1', 'A Simple Graph with error bars', 200, 10, 700, 500 )
c1.SetGrid()
hfile = ROOT.TFile('kkk.root', 'RECREATE', 'Demo ROOT file with histograms' )

j=1
for path in pathlist:
    x1, y1 = array( 'f' ), array( 'f' )
    ex1, ey1 = array( 'f' ), array( 'f' )
   
    n1=0 
    for run in rundic1:
        x1.append(rundic1[run])
        ex1.append(0.0)
        y1.append(gdic1[run][0][path][1])
        ey1.append(gdic1[run][0][path][2])
        n1+=1

    x2, y2 = array( 'f' ), array( 'f' )
    ex2, ey2 = array( 'f' ), array( 'f' )

    n2=0
    for run in rundic2:
        x2.append(rundic2[run])
        ex2.append(0.0)
        y2.append(gdic2[run][0][path][1])
        ey2.append(gdic2[run][0][path][2])
        n2+=1

    x3, y3 = array( 'f' ), array( 'f' )
    ex3, ey3 = array( 'f' ), array( 'f' )

    n3=0
    for run in rundic3:
        x3.append(rundic3[run])
        ex3.append(0.0)
        y3.append(gdic3[run][0][path][1])
        ey3.append(gdic3[run][0][path][2])
        n3+=1
#    print path
#    print x
#    print y

#plot~~~~~~~~~~~~~~~~~~~~~~~~~~~`
    gr = ROOT.TGraphErrors( n1, x1, y1, ex1, ey1 )
    gr.SetMarkerColor( 4 )
    gr.SetLineColor( 4 )
    gr.SetMarkerStyle( 21 )
    gr.SetTitle( path  )
    gr.GetXaxis().SetTitle( '< PU >' )
    gr.GetYaxis().SetTitle( 'Rates MC (Hz) / CrossSection (pb)' )
    gr.GetYaxis().SetTitleSize(0.042)
    gr.GetYaxis().SetTitleOffset(1.03)
    for i in range(len(Yrangelist)):
        if max(max(y1),max(y2),max(y3))<Yrangelist[i][1]:
            gr.GetYaxis().SetRangeUser(Yrangelist[i][0],Yrangelist[i][1])
            break
    gr.Draw( 'AP' )
    gr.Fit("pol1")
    gr.GetFunction("pol1").SetLineColor(4)

    chi_gr1 = gr.GetFunction("pol1").GetChisquare()
    p0_gr1  = gr.GetFunction("pol1").GetParameter(0)
    p1_gr1  = gr.GetFunction("pol1").GetParameter(1)
    gr.Write()

    c1.Update()

#~~~~~~~~~~~~~~~~~~~~~~~

    print x2
    print y2

    gr2 = ROOT.TGraphErrors( n2, x2, y2, ex2, ey2 )
#    gr = ROOT.TGraph( n, x, y )
    gr2.SetMarkerColor( 1 )
    gr2.SetLineColor( 1 )
    gr2.SetMarkerStyle( 20 )

    gr2.Draw( 'P' )
    gr2.Fit("pol1")
    gr2.GetFunction("pol1").SetLineColor(1)

    chi_gr2 = gr2.GetFunction("pol1").GetChisquare()
    p0_gr2  = gr2.GetFunction("pol1").GetParameter(0)
    p1_gr2  = gr2.GetFunction("pol1").GetParameter(1)
    gr2.Write()

    c1.Update()



#~~~~~~~~~~~~~~~~~~~~~~~

    print x3
    print y3

    gr3 = ROOT.TGraphErrors( n3, x3, y3, ex3, ey3 )
#    gr = ROOT.TGraph( n, x, y )
    gr3.SetMarkerColor( 2 )
    gr3.SetLineColor( 2 )
    gr3.SetMarkerStyle( 20 )

    gr3.Draw( 'P' )
#    gr3.Fit("pol1")
#    gr3.GetFunction("pol1").SetLineColor(2)

    gr3.Write()

    c1.Update()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    legend=ROOT.TLegend(0.1,0.8,0.6,0.9)
    legend.AddEntry(gr,"7e33 : %0.2g X + %0.2g , #chi^{2}:%0.2f" % (p1_gr1,p0_gr1,chi_gr1),"lp")
    legend.AddEntry(gr2,"2e33 : %0.2g X + %0.2g , #chi^{2}:%0.2f" % (p1_gr2,p0_gr2,chi_gr2),"lp")
    legend.AddEntry(gr3,"1e34","lp")# : %g X + %g , #chi^{2}:%f" % (p1_gr1,p0_gr1,chi_gr1),"lp")
    legend.Draw()





    p_path = 'mc_plot_part/'+path 
    c1.Print('%s.png'%(p_path))

    htmfile.write("<div class=image><a href='"+path+".png'><img width=398 height=229 border=0 src='"+path+".png'></a><div style='width:398px'>"+path+"</div></div>\n")


#print processing
    print "*"*20
    print "*** %d/%d finished ***"%(j,len(pathlist))
    print "*"*20
    j+=1
htmfile.write('</html>')
