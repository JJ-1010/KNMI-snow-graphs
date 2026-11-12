import zipfile
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

#parsing zipfiles
snowpath=os.getcwd()+'/data/'
files=os.listdir(snowpath)

csvh=b'# STN,YYYYMMDD,   SX\n'
snh=b'# STN         NAME\n'
lines_=[]
stations_=[]

for file in files:
    if (file.endswith('.zip')):
        with zipfile.ZipFile(snowpath+file,'r') as z:
            fils=z.namelist()
            for ff in fils:
                with z.open(ff,'r') as f:
                    lines=f.readlines()
                s,e=0,0
                for i,l in enumerate(lines):
                    if(l.startswith(b'# STN ')):
                        s=i
                    if(l.startswith(b'# SX')):
                        e=i
                    if(l.startswith(b'# STN,YYYY')):
                        break
                lines_+=lines[i+1:]
                stations_+=lines[s+1:e]
                
with open(snowpath+'out.csv','wb+') as f:
    f.write(csvh+b''.join(lines_))
    
with open(snowpath+'out_stations.csv','wb+') as f:
    f.write(snh+b''.join(stations_))

#wrangling
df=pd.read_csv(snowpath+'out.csv')
df.columns=[c.strip().split(' ')[-1] for c in df.columns]
    
stations=pd.read_csv(snowpath+'out_stations.csv')
c1=stations.columns[0]
stations=stations[c1].str.strip().str.split('\s{2,}',expand=True)
stations.columns=['STN','NAME']
stations.STN=stations.STN.apply(lambda x:x[2:])
stations.columns=[c.strip() for c in stations.columns]

df.SX=df.SX.str.strip()
df.loc[df.SX=='','SX']=0
df.SX=df.SX.fillna(0).astype(int)

df.loc[df.SX>900,'SX']=0
df.SX.value_counts()
std=dict(zip(stations['STN'].str.strip().astype(int),stations.NAME.str.strip()))
df.STN=df.STN.apply(lambda x:std.get(x,x))

#simple winter season 2025/2026 -> same grouping
df['Y']=df.YYYYMMDD.astype(str).apply(lambda x:x[:4])
df['M']=df.YYYYMMDD.astype(str).apply(lambda x:x[4:6])
df['S']=df.Y.astype(int)+(df.M.astype(int)>6)*1

#%%
#data kieke

def plot_occurence(snowwy,stn='all'):
    plt.figure()
    plt.bar(snowwy.SX.value_counts().index,np.log10(snowwy.SX.value_counts().values))
    plt.xlabel('snow height')
    plt.ylabel('log occurence (days)')
    plt.title(f'how often there is snow at weather station: {stn}')
    plt.ylim(0,3.5)
    plt.xlim(0,30)
    plt.grid()
    return
    
def plot_all(df,function):
    function(df)
    for station in set(df['STN']):
        _df=df[df['STN']==station].copy()
        if(_df.empty):
            print(station,'empty')
        function(_df,station)
    return

snowwy=df[df.SX>0].copy()
plot_all(snowwy,plot_occurence)

#%%
#witte kerst

def plot_kerst(df,stn='all'):
    sneeuw=df.copy()
    sneeuw.SX=(sneeuw.SX>0)*1
    sneeuw=sneeuw.groupby('Y').SX.sum()
    
    plt.figure()
    plt.plot(sneeuw.index.astype(int),sneeuw.values)
    plt.xlabel('jaar')
    plt.ylabel('sneeuw kerstdagen')
    plt.title(f'sneeuw tijdens kerst per jaar station: {stn}')
    plt.xlim(1955,2027)
    plt.ylim(0,3)
    plt.grid()
    return
    
snowwy=df.copy()
snowwy['D']=snowwy.YYYYMMDD.astype(str).apply(lambda x:x[6:])
snowwy=snowwy[(snowwy.M=='12')&((snowwy.D=='25')|(snowwy.D=='26'))]
plot_all(snowwy,plot_kerst)

#%%
#gemiddelde hoeveelheid sneeuw (dagen x hoogte sneeuwdek) per winter

def plot_sneeuwdagen(df,stn='all'):
    sneeuw=df.copy()
    if(stn!='all'):
        sneeuw=sneeuw[sneeuw.STN==stn]
    sneeuw=sneeuw.groupby('S').SX.mean()
    plt.figure()
    plt.plot(sneeuw.index,sneeuw.values)
    plt.xlabel('jaar')
    plt.ylabel('sneeuw gemiddeld 360d (cm)')
    plt.title(f'sneeuwdek gemiddeld per jaar station: {stn}')
    plt.xlim(1955,2027)
    plt.ylim(0,2)
    plt.grid()
    return
    
snowwy=df.copy()
plot_all(snowwy,plot_sneeuwdagen)

#sneeuw is best wel een raar woord als je het vaak leest