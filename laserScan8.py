# -*- coding: utf-8 -*-
"""
VISA Resource Management needs to be running.
Make sure the TCPIP is right for the scope.
    -IP under #set up scope
Scope Setup
    -Scope should be using CH4 for data.
    -Trigger should be all the way on the left edge.
    -Avg should be on. Not too many samples though.
    

@author: N.Greeney
"""
import scopeRead as sRead
import motionControl as mC

import visa as vi
import numpy as np
import time as time
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def laserScan2D(width,height,delta,peakArea,fileName):
    #Scans an area with given width and height at a 
    #step rate of delta. peakArea is int value for 
    #the location of peak with a scale from 0 to 10,000 
    
    startTime=time.clock()
    h=0;w=0
    n=0;m=0
    
    x=np.arange(0,width+delta,delta)
    y=np.arange(0,height+delta,delta)
    Y,X=np.meshgrid(y,x)
    tValues=np.zeros((np.size(x),np.size(y)))
    vValues=np.zeros((np.size(x),np.size(y)))
    
    #set up scope
    scanRange=1000
    scope=vi.instrument("TCPIP::138.67.12.235::INSTR")
    sRead.setParam(scope,peakArea-scanRange,peakArea+scanRange)
    
    #get motor and zero location
    motor=mC.setupMotor()

    while w<=width:
        h=0
        m=0
        while h<=height:
            mC.moveTo(motor,w,h)
            time.sleep(0.5)
            x,y=sRead.getData(scope,peakArea-scanRange,peakArea+scanRange)
            t,v=findPeak(x,y)
            tValues[n,m]=t
            vValues[n,m]=v
            h=h+delta
            m=m+1
        w=w+delta
        n=n+1
        
        #Estimates Time Left
        timeLeft=(width-w)/w*(time.clock()-startTime)/60
        print 'Est. Time Left '+np.str(timeLeft)+"min"
    mC.moveTo(motor,0,0)
    
    #Contour Plot of Time
    makePlot2D(X,Y,tValues,fileName+" Time")
    
    #Contour Plot of Voltage
    makePlot2D(X,Y,vValues,fileName+" Voltage")
    
    #File Output 
    np.savez(fileName+".npz",X=X,Y=Y,tValues=tValues,vValues=vValues)
    
    #Time Taken Calc
    timeTaken=(time.clock()-startTime)/60 #in min
    print 'Time Taken '+np.str(timeTaken)
    motor.close()
    scope.close()
    return timeTaken,tValues


def laserScan1D(width,height,delta,peakArea,fileName):
    #Scans an area with given width and height at a 
    #step rate of delta. peakArea is int value for 
    #the location of peak with a scale from 0 to 10,000 
    
    startTime=time.clock()
    h=0;w=0
    n=0;m=0
    
    x=np.arange(0,width+delta,delta)
    y=np.arange(0,height+delta,delta)
    Y,X=np.meshgrid(y,x)
    tValues=np.array([[]])
    vValues=np.array([[]])
    
    
    #set up scope
    scanRange=240
    scope=vi.instrument("TCPIP::138.67.12.235::INSTR")
    sRead.setParam(scope,peakArea-scanRange,peakArea+scanRange)
    
    #get motor and zero location
    motor=mC.setupMotor()

    while w<=width:
        h=0
        m=0
        while h<=height:
            mC.moveTo(motor,w,h)
            time.sleep(3)
            t1,v1=sRead.getData(scope,peakArea-scanRange,peakArea+scanRange)
            time.sleep(1)
            t2,v2=sRead.getData(scope,peakArea-scanRange,peakArea+scanRange)
            
            t=[np.average([t1[x],t2[x]]) for x in range(len(t1))]
            v=[np.average([v1[x],v2[x]]) for x in range(len(v1))]
            
            if h==0 and w==0:
                tValues=[t]
                vValues=[v]
            else:
                tValues=np.append(tValues,[t],axis=0)
                vValues=np.append(vValues,[v],axis=0)
            h=h+delta
            m=m+1
        w=w+delta
        n=n+1
        
        #Estimates Time Left
        timeLeft=(width-w)/w*(time.clock()-startTime)/60
        print 'Est. Time Left '+np.str(timeLeft)+"min"
    mC.moveTo(motor,0,0)
    motor.close()
    scope.close()
    
    #File Output 
    np.savez(fileName+".npz",X=X,Y=Y,tValues=tValues,vValues=vValues)
    
    #Plot of Time vs Voltage
    makePlot1D(tValues,vValues,fileName)
    
    #Time Taken Calc
    timeTaken=(time.clock()-startTime)/60 #in min
    print 'Time Taken '+np.str(timeTaken)
    return timeTaken,tValues,vValues



def makePlot2D(X,Y,Z,titleName):
    #X,Y,Z are a grid of values with Z being the ploted value
    #max, min and contourDelta relate to Z
    #titleName for the Title of the graph
    
    #min=np.min(Z)
    max=np.max(Z)
    min=-0.00019
    contourDelta=(max-min)/200
    
    fig=plt.figure()
    V=np.arange(min,max+contourDelta,contourDelta)
    CS=plt.contourf(X,Y,Z,V,cmap=cm.gray)
    plt.title(titleName)
    plt.colorbar(CS,shrink=0.8,extend='neither')
    return fig


def makePlot1D(X,Y,titleName):
    
    X=np.array(X)
    Y=np.array(Y)
    
    delta=np.max(Y)
    
#    fig=plt.figure()
    tPeaks=np.zeros(X.shape[0])
    vPeaks=np.zeros(X.shape[0])
    
    n=0
    while n<X.shape[0]:
        plt.plot(X[n],Y[n]-delta*n)
        
#        tPeaks[n],vPeaks[n]=findPeak(X[n],Y[n]-delta*n)
        n=n+1
    
#    plt.plot(tPeaks,vPeaks)
    
    plt.title(titleName)


    return #fig

def findPeak(dataX,dataY):
    mean=np.mean(dataY)
    std=np.std(dataY)
    indexes=np.where(dataY<(mean-std))[0]
    
    i=0
    while abs(indexes[i]-indexes[i+1])<=5 and i+1<np.size(indexes)-1 :
        i=i+1
    
    peakY=np.min(dataY[indexes[0]:indexes[i]])
    peakInd=np.where(dataY==peakY)[0][0]
    peakX=dataX[peakInd]
    return peakX,peakY

#def findPeak(dataX,dataY):
#    #find the max and min Y and then find the index that Y relates
#    #to to get the time for that max
#    maxY=np.max(dataY)
#    minY=np.min(dataY)
#    maxYInd=np.where(dataY==maxY)
#    minYInd=np.where(dataY==minY)
#    #timeIndex=np.min([minYInd[0][0],maxYInd[0][0]])
#    peakX=dataX[maxYInd[0][0]]
#    return peakX,maxY

def mult1DScan(width,height,delta,peakArea,fileName,scans):
    n=0
    
    while n<scans:
        laserScan1D(width,height,delta,peakArea,fileName+"_"+np.str(n))
        
        n=n+1
    
    return