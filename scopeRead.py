import visa as v
import numpy as np
import matplotlib.pyplot as plt
 
#min and max are sample numbers not time measurements
#far left is 1 and far right is 10000
def scopeRead(min=1,max=10000):
    #define and connect to the scope lepton
    scope=v.instrument("TCPIP::138.67.12.235::INSTR")
 
    #set the info that you want to get from the scope
    setParam(scope,min,max)
    #get the info you asked for
    X,Y=getData(scope,min,max)
 
 
    plt.plot(X,Y)
    #close connection to free up instrument
    scope.close()
 
 
def setParam(scope,min,max):
    scope.write("DATa:SOUrce CH4") #choose which Channel to get
    scope.write("DATa:ENCdg ASCIi") #can be ASCIi/RIBinary/RPBinary/SRIbinary/SRPbinary
    scope.write("DATa:WIDth 2") #1 byte give vertical range of -128 to 127 and 2 bytes gives range of -32768 to 32767
    scope.write("DATa:STARt "+np.str(min)) #1 is far left edge
    scope.write("DATa:STOP "+np.str(max)) #10,000 is far right edge
 
 
def getData(scope,min,max):
    #info = scope.ask("WFMPRe?") #has all the detailed info about scaling
 
    Xscaling = float(scope.ask("WFMPre:XINcr?")) #scaling factor for the x axis
    Yscaling = float(scope.ask("WFMPre:YMUlt?")) #scaling factor for the y axis
    Xunit = scope.ask("WFMPre:XUNit?")[1:-1]     #units that the x axis are in
    Yunit = scope.ask("WFMPre:YUNit?")[1:-1]     #units that the x axis are in
    Xzero = float(scope.ask("WFMPre:XZEro?"))    #position in x units that the first sample is at
    Yzero = float(scope.ask("WFMPre:YZEro?"))    #bit index that the 0 is located at for the y axis
 
    #get y values and convert to values rather then bit indexes
    raw = scope.ask("CURVe?")
    data=np.array([float(s) for s in raw.split(',')])
    dataY=(data+Yzero)*Yscaling
 
    #create x data range in values and not indexes
    dataX=np.arange(min,max+1,1)
    dataX=((dataX*Xscaling)+Xzero)*1E6
    
    return dataX,dataY