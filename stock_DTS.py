#DTS System for Stock Exchange.
import csv
from datetime import timedelta, date, datetime

class DTS(object):

    def __init__(self, xmlName):
        self.xmlName = xmlName
        self.data = {}
        self.range = {}
        self.result = [] #[(date, time, val, msg),]
        self.dates = []
        self.buyStack = []
        self.dip = 45  #can be changed with anyother value i.e customizable

    def processingCSVData(self):
        """
        This function will read the CSV file and arrange the data in dictionary of dictionaries
        ex: { date1 : [(time1, close_val1),(time1, close_val2)],
              date2 : [(time2, close_val1),(time2, close_val2)],
              date3 : [(time3, close_val1),(time3, close_val2)]
              }
              {date1: (min, max)
        """
        with open(self.xmlName, 'rb') as f:
            reader = csv.reader(f)
            currentDate = None  #temp variable
            for row in reader:
                if row[0].strip() == 'Symbol':
                    continue
                currentDate = row[1]
                if currentDate in self.data:
                    self.data[currentDate].append((row[2], row[6]))
                    self.calculateMinMax(row[6], currentDate)
                else:
                    self.data[currentDate] = []
                    self.data[currentDate].append((row[2], row[6]))
                    #initializing min-max range values
                    self.range[currentDate] = {'min':row[6] , 'max':row[6]}
                    self.dates.append(currentDate)


    def calculateMinMax(self, closeVal, currentDate):
        """
        Calculate min and max for a particular date
        """
        if closeVal > self.range[currentDate]['max']:
            self.range[currentDate]['max'] = closeVal

        elif closeVal < self.range[currentDate]['min']:
            self.range[currentDate]['min'] = closeVal

        else:
            pass

    def DTSSystem(self, inputDate):
        """
        Implementation of Dip logic.
        """

        val = self.data[inputDate]
        buyRef = 0
       
        for timeVal,closeVal in val:
            if timeVal.strip() == '09:16':
                if self.range[inputDate]['min'] <= closeVal and self.range[inputDate]['max'] >= closeVal:
                    self.result.append((inputDate, timeVal, closeVal, "Buy 1 Lot"))
                    buyRef = closeVal
                    self.buyStack.append((timeVal,closeVal))
            else:
                if (float(buyRef) - float(closeVal)) >= self.dip:
                    self.result.append((inputDate, timeVal, closeVal, "Buy 1 Lot"))
                    buyRef = float(buyRef) - float(self.dip)
                    self.buyStack.append((timeVal,closeVal))
                    
                elif self.buyStack != []:
                    if (float(closeVal) - float(self.buyStack[-1][1])) >= self.dip: #increase of 45
                        self.result.append((inputDate, timeVal, closeVal, "Sell 1 Lot bought at:"+self.buyStack[-1][1]))
                        self.buyStack.pop()
                        buyRef =  float(buyRef) + float(self.dip)
                        
                else:
                     pass
    def applyDTSonAlldates(self):
        """
        This will apply DTS functionality for all the dates present in the CSV file.
        """
        for date in self.dates:
            self.DTSSystem(date)
        self._printResult()

    def _printResult(self):
        """
        This will print the complete results of Buy and sell for all the dates present in the CSV file
        """
        for elem in self.result:
            print elem

    def applyDTSonDuration(self, startDate, endDate):
        """
        This function takes startDate and endDate and applies DTS system on each date
        between startDate and endDate(including startDate and endDate)
        @param startDate: type 'str' format: YYYYMMDD
        @param endDate: type 'str' format: YYYYMMDD
        """
        weekend = [5,6]  #this list will be used to ignore the weekend dates and Stock Exchange is close on those days.
        inputDateDuration = []  #list of all the dates between passed startDate and endDate
        start_date = datetime.strptime(startDate, '%Y%m%d').date()
        end_date = datetime.strptime(endDate, '%Y%m%d').date()
        d = start_date
        delta = timedelta(days=1)
        while d <= end_date:
            #Weekends dates are Ignored and also the date for which there is no data those dates are also ignored ex:'20150917'
            if d.weekday() not in [5,6] and (d.strftime('%Y%m%d') in self.data):
                inputDateDuration.append(d.strftime("%Y%m%d"))
                d += delta
            else:
                d += delta
        for currentDate in inputDateDuration:
            self.DTSSystem(currentDate)
        self._printResult()

    #added on 6th Oct
    def DTSSystemBuyingLevels(self, inputDate):
        """
        Implementation of Dip logic for multiple Buying level NOT ON 9:16 CLOSING
        """

        val = self.data[inputDate]
        buyRef = 0
        print "Range",self.range[inputDate]['max'],self.range[inputDate]['min']
        for timeVal,closeVal in val:
            if timeVal.strip() == '09:16':
                if self.range[inputDate]['min'] <= closeVal and self.range[inputDate]['max'] >= closeVal:
                    self.result.append((inputDate, timeVal, closeVal, "Buy 1 Lot"))

                    if ( float(self.range[inputDate]['max']) - float(self.dip)) >= float(self.range[inputDate]['min']):
                        buyRef = float(self.range[inputDate]['max']) - float(self.dip)
                        print buyRef
                    self.buyStack.append((timeVal,closeVal))
            else:
                if float(closeVal) <= buyRef:
                    
                    self.result.append((inputDate, timeVal, closeVal, "Buy 1 Lot"))
                    if buyRef - float(self.dip) >= float(self.range[inputDate]['min']):
                        buyRef = buyRef - float(self.dip)
                        self.buyStack.append((timeVal,closeVal))
                    
                elif self.buyStack != []:
                    if (float(closeVal) - float(self.buyStack[-1][1])) >= self.dip: #increase of 45
                        self.result.append((inputDate, timeVal, closeVal, "Sell 1 Lot bought at:"+self.buyStack[-1][1]))
                        self.buyStack.pop()
                        buyRef =  float(buyRef) + float(self.dip)
                        
                else:
                     pass
    #added on 6th Oct
    def ApplyDTSSystemBuyingLevelsOnDuration(self, startDate, endDate):
        """
        """
        weekend = [5,6]  #this list will be used to ignore the weekend dates and Stock Exchange is close on those days.
        inputDateDuration = []  #list of all the dates between passed startDate and endDate
        start_date = datetime.strptime(startDate, '%Y%m%d').date()
        end_date = datetime.strptime(endDate, '%Y%m%d').date()
        d = start_date
        delta = timedelta(days=1)
        while d <= end_date:
            #Weekends dates are Ignored and also the date for which there is no data those dates are also ignored ex:'20150917'
            if d.weekday() not in [5,6] and (d.strftime('%Y%m%d') in self.data):
                inputDateDuration.append(d.strftime("%Y%m%d"))
                d += delta
            else:
                d += delta
        for currentDate in inputDateDuration:
            self.DTSSystemBuyingLevels(currentDate)
        self._printResult()
        

if __name__ == '__main__':
    obj = DTS("output.csv")
    obj.processingCSVData()
    #obj.applyDTSonAlldates()  #uncomment this function if you want to apply the DTS system for all the dates in CSV file
    startDate = '20150901' #1st Sept,2015
    endDate = '20150910'   #10th Sept,2015
    #obj.applyDTSonDuration(startDate, endDate) #this function is for date duration
    obj.ApplyDTSSystemBuyingLevelsOnDuration('20150901', '20150901')
