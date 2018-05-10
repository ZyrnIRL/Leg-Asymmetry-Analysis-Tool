import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from scipy.signal import argrelmax, argrelmin
from scipy import ndimage
from scipy import signal

firstLine = 'timestamp,accel_x (m/s2),accel_y (m/s2),accel_z (m/s2),gyro_x (deg/s),gyro_y (deg/s),gyro_z (deg/s),mag_x (uT),mag_y (uT),mag_z (uT)\n'

labels = firstLine.strip().split(',')
timeIndex = labels.index('timestamp')
accel_xIndex = labels.index('accel_x (m/s2)')
accel_yIndex = labels.index('accel_y (m/s2)')
accel_zIndex = labels.index('accel_z (m/s2)')
gyro_xIndex = labels.index('gyro_x (deg/s)')
gyro_yIndex = labels.index('gyro_y (deg/s)')
gyro_zIndex = labels.index('gyro_z (deg/s)')
mag_xIndex = labels.index('mag_x (uT)')
mag_yIndex = labels.index('mag_y (uT)')
mag_zIndex = labels.index('mag_z (uT)')

valueIndices = [accel_xIndex, accel_yIndex, accel_zIndex, gyro_xIndex, gyro_yIndex, gyro_zIndex, mag_xIndex, mag_yIndex, mag_zIndex]

def initializePlots(app):
	app.Graph1 = PlotCanvas(app.widget_Graph1)
	app.Graph2 = PlotCanvas(app.widget_Graph2)

def clearPlots(app):
	app.Graph1.clear()
	app.Graph2.clear()

def analyze(app):
	app.progressBar_Analysis.setValue(1)
	left = False
	right = False
	if not app.leftData is None:
		leftData = numpy.asarray(app.leftData)[1:]
		left = True
	if not app.rightData is None:
		rightData = numpy.asarray(app.rightData)[1:]
		right = True
	
	result = ''
	#app.progressBar_Analysis.setValue(app.progressBar_Analysis.value() + increment)
	
	if left and right:
		leftData = leftData[:, [timeIndex, accel_yIndex]]
		rightData = rightData[:, [timeIndex, accel_yIndex]]
		
		leftPeaks, rightPeaks = getPeaksUnfiltered(leftData, rightData)
	
		leftDataFilter = butterFilter(leftData)
		rightDataFilter = butterFilter(rightData)
	
		leftPeaksFilter, rightPeaksFilter = getPeaksFiltered(leftDataFilter, rightDataFilter)		
		
		
		if app.leftFiltered and app.rightFiltered:
			angles = []
			for pair in zip(leftPeaks, rightPeaks):
				symVals = calculation(pair[0], pair[1])
				angles.append(symVals[3])
			
			result += 'Leg Symmetry Results (both filtered manually)\n'
			
			count = 1
			for angle in angles:
				result += '\tAngle {}: {}\n'.format(count, angle)
				count += 1
			
			
			result += '\n\tAverage: {}'.format(numpy.mean(angles))
			#print('Average Raw:', numpy.mean(angles))
			
			#angles = []
			#for pair in zip(leftPeaksFilter, rightPeaksFilter):
			#	symVals = calculation(pair[0], pair[1])
			#	angles.append(symVals[3])
			
			#print('Average Filter:', numpy.mean(angles))
		
			app.Graph1.plot(leftData, 'r')
			app.Graph1.plot(rightData, 'b')
			app.Graph1.setTitle('Left vs Right Leg Data')
			
			#app.Graph2.plot(leftDataFilter, 'r')
			#app.Graph2.plot(rightDataFilter, 'b')
		
		elif app.leftFiltered and (not app.rightFiltered):
			#angles = []
			#for pair in zip(leftPeaks, rightPeaks):
			#	symVals = calculation(pair[0], pair[1])
			#	angles.append(symVals[3])
			#
			#print('Average Raw:', numpy.mean(angles))
			
			print('attempting to filter right')
			
			angles = []
			for pair in zip(leftPeaks, rightPeaksFilter):
				symVals = calculation(pair[0], pair[1])
				angles.append(symVals[3])
			
			result += 'Leg Symmetry Results (left filtered manually, right filtered in program)\n'
			
			count = 1
			for angle in angles:
				result += '\tAngle {}: {}\n'.format(count, angle)
				count += 1
			
			
			result += '\n\tAverage: {}'.format(numpy.mean(angles))
			
			#print('Average Filter:', numpy.mean(angles))
		
			app.Graph1.plot(leftData, 'r')
			app.Graph1.plot(rightDataFilter, 'b')
			app.Graph1.setTitle('Left vs Filtered Right Leg Data')
			
			app.Graph2.plot(rightData, 'r')
			app.Graph2.plot(rightDataFilter, 'b')
			app.Graph2.setTitle('Right vs Filtered Right Leg Data')
		
		elif (not app.leftFiltered) and app.rightFiltered:
			#angles = []
			#for pair in zip(leftPeaks, rightPeaks):
			#	symVals = calculation(pair[0], pair[1])
			#	angles.append(symVals[3])
			
			#print('Average Raw:', numpy.mean(angles))
			
			print('attempting to filter left')
			
			angles = []
			for pair in zip(leftPeaksFilter, rightPeaks):
				symVals = calculation(pair[0], pair[1])
				angles.append(symVals[3])
			
			result += 'Leg Symmetry Results (left filtered in program, right filtered manually)\n'
			
			count = 1
			for angle in angles:
				result += '\tAngle {}: {}\n'.format(count, angle)
				count += 1
			
			
			result += '\n\tAverage: {}'.format(numpy.mean(angles))
			
			#print('Average Filter:', numpy.mean(angles))
			
			app.Graph1.plot(leftDataFilter, 'r')
			app.Graph1.plot(rightData, 'b')
			app.Graph1.setTitle('Filtered Left vs Right Leg Data')
			
			app.Graph2.plot(leftData, 'r')
			app.Graph2.plot(leftDataFilter, 'b')
			app.Graph2.setTitle('Left vs Filtered Left Leg Data')
			
		else:
			angles = []
			for pair in zip(leftPeaks, rightPeaks):
				symVals = calculation(pair[0], pair[1])
				angles.append(symVals[3])
			
			result += 'Leg Symmetry Results (both unfiltered)\n'
			
			count = 1
			for angle in angles:
				result += '\tAngle {}: {}\n'.format(count, angle)
				count += 1
			
			
			result += '\n\tAverage: {}\n\n'.format(numpy.mean(angles))
			
			#print('Average Raw:', numpy.mean(angles))
			
			print('attempting to filter both')
			
			angles = []
			for pair in zip(leftPeaksFilter, rightPeaksFilter):
				symVals = calculation(pair[0], pair[1])
				angles.append(symVals[3])
			
			result += 'Leg Symmetry Results (both filtered in program)\n'
			
			count = 1
			for angle in angles:
				result += '\tAngle {}: {}\n'.format(count, angle)
				count += 1
			
			
			result += '\n\tAverage: {}'.format(numpy.mean(angles))
			
			#print('Average Filter:', numpy.mean(angles))
		
			app.Graph1.plot(leftData, 'r')
			app.Graph1.plot(rightData, 'b')
			app.Graph1.setTitle('Left vs Right Leg Data')
			
			app.Graph2.plot(leftDataFilter, 'r')
			app.Graph2.plot(rightDataFilter, 'b')
			app.Graph2.setTitle('Filtered Left vs Filtered Right Leg Data')
		
	elif left:
		leftData = leftData[:, [timeIndex, accel_yIndex]]
		
		app.Graph1.plot(leftData, 'r')
		app.Graph1.setTitle('Left Leg Data')
		
		if not app.leftFiltered:
			leftDataFilter = butterFilter(leftData)
			app.Graph2.plot(leftDataFilter, 'r')
			app.Graph2.setTitle('Filtered Left Leg Data')
			
	elif right:
		rightData = rightData[:, [timeIndex, accel_yIndex]]
		
		app.Graph1.plot(rightData, 'b')
		app.Graph1.setTitle('Right Leg Data')
		
		if not app.rightFiltered:
			rightDataFilter = butterFilter(rightData)
			app.Graph2.plot(rightDataFilter, 'b')
			app.Graph2.setTitle('Filtered Right Leg Data')
	
	app.textBrowser_Results.setPlainText(result)
	app.progressBar_Analysis.setValue(100)

def getPeaksUnfiltered(leftData, rightData):
	leftPoints = leftData.astype(numpy.float)
	leftPeaks = leftPoints[argrelmax(leftPoints)[0]]
	leftPeakPeaks = leftPeaks[argrelmax(leftPeaks)[0]]
	leftPeakPeakPeaks = leftPeakPeaks[argrelmax(leftPeakPeaks)[0]]

	rightPoints = rightData.astype(numpy.float)
	rightPeaks = rightPoints[argrelmax(rightPoints)[0]]
	rightPeakPeaks = rightPeaks[argrelmax(rightPeaks)[0]]
	rightPeakPeakPeaks = rightPeakPeaks[argrelmax(rightPeakPeaks)[0]]

	return leftPeakPeakPeaks[:, 1], rightPeakPeakPeaks[:, 1]

def getPeaksFiltered(leftData, rightData):
	leftPoints = leftData.astype(numpy.float)
	leftPeaks = leftPoints[argrelmax(leftPoints)[0]]
	leftPeakPeaks = leftPeaks[argrelmax(leftPeaks)[0]]
	leftPeakPeakPeaks = leftPeakPeaks[argrelmax(leftPeakPeaks)[0]]
	
	rightPoints = rightData.astype(numpy.float)
	rightPeaks = rightPoints[argrelmax(rightPoints)[0]]
	rightPeakPeaks = rightPeaks[argrelmax(rightPeaks)[0]]
	rightPeakPeakPeaks = rightPeakPeaks[argrelmax(rightPeakPeaks)[0]]
	
#	return leftPeaks[:, 1], rightPeaks[:, 1]
#	return leftPeakPeaks[:, 1], rightPeakPeaks[:, 1]
	return leftPeakPeakPeaks[:, 1], rightPeakPeakPeaks[:, 1]
	
#	indexes = signal.find_peaks_cwt(leftPoints[:, 1], numpy.arange(1, 550))


def butter_lowpass(cutoff, fs, order=5):
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
	return b, a

def butterFilter(data):
	cutoff = 10
	time = float(data[:, 0][-1])
	samples = len(data[:, 0])
	fs = samples / time
	order = 4
	
	b, a = butter_lowpass(cutoff, fs, order=order)
	filterData = signal.lfilter(b, a, data[:, 1].astype(numpy.float))
	filterData = numpy.column_stack([data[:, 0].astype(numpy.float), filterData])
	return filterData
	

#def butterFilterOld(data):
#	time = float(data[:, 0][-1])
#	samples = len(data[:, 0])
#	frequency = (samples / time) * (2 * numpy.pi) # Sample frequency -> rad/s
#	cutoff = 10 * (2 * numpy.pi) # 10Hz -> rad/s
#	
#	print(cutoff / frequency)
#	
#	b, a = signal.butter(4, 0.1, 'lowpass')
#	
#	filterData = signal.filtfilt(b, a, data[:, 1].astype(numpy.float))
#
#	filterData = numpy.column_stack([data[:, 0].astype(numpy.float), filterData])
#	
#	return filterData	

#def variables(data):
#	vars = []
#	for index in valueIndices:
#		value = data[1:, index].astype(numpy.float)
#		smoothValue = ndimage.gaussian_filter1d(value, 5)
#		
#		relMax = numpy.sort(value[argrelmax(value)[0]])
#		relMin = numpy.sort(value[argrelmin(value)[0]])
#		
#		smoothRelMax = numpy.sort(smoothValue[argrelmax(smoothValue)[0]])
#		smoothRelMin = numpy.sort(smoothValue[argrelmin(smoothValue)[0]])
#		
#		
#		print(relMax[int(-len(relMax) * 0.07):])
#		print(relMin[:int(len(relMin) * 0.07)])
#		
#		avgMax = numpy.mean(relMax[int(-len(relMax) * 0.07):])
#		avgMin = numpy.mean(relMin[:int(len(relMin) * 0.07)])
#		
#		vars.append([labels[index] + ' avgMax', avgMax])
#		vars.append([labels[index] + ' avgMin', avgMin])
#		
#	return vars

def calculation(X_left, X_right):
	absval = abs(X_left - X_right)
	symIndex_left = (absval / X_left) * 100
	symIndex_right = (absval / X_right) * 100
	symIndex_avg = (absval / numpy.mean([X_left, X_right])) * 100

	check = 45 - numpy.degrees(numpy.arctan(X_left / X_right))
	if check > 90:
		symAngle = ((check - 180) / 90) * 100
	else:
		symAngle = (check / 90) * 100
	
	return symIndex_left, symIndex_right, symIndex_avg, symAngle

"""
Code taken from SciPy Cookbook.
May be of use.
2017-07-13
http://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
"""
def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=numpy.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    
    return y[int(window_len/2-1):-int(window_len/2+1)]

class PlotCanvas(FigureCanvasQTAgg):

	def __init__(self, parent=None, width=7, height=5, dpi=100):
		fig = pyplot.Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		
		FigureCanvasQTAgg.__init__(self, fig)
		self.setParent(parent)
		
		FigureCanvasQTAgg.setSizePolicy(self,
				QSizePolicy.Expanding,
				QSizePolicy.Expanding)
		FigureCanvasQTAgg.updateGeometry(self)
		self.draw()

	def plot(self, data, color):
		#time = data[1:, xIndex]
		#accel_x = data[1:, yIndex]
		
		ax = self.figure.add_subplot(111)
		ax.plot(data[:, 0].astype(numpy.float), data[:, 1].astype(numpy.float), color + '-')
		#ax.set_title('PyQt Matplotlib Example')
		ax.set_xlabel(labels[timeIndex])
		ax.set_ylabel(labels[accel_yIndex])
		#ax.set_xticks(numpy.arange(0, max(time)+1, 1.0))
		self.draw()
	
	def setTitle(self, title):
		ax = self.figure.get_axes()[0]
		ax.set_title(title)
		self.draw()
	
	def clear(self):
		ax = self.figure.get_axes()[0]
		self.figure.delaxes(ax)
		self.figure.add_subplot(111)
		self.draw()
	
#	def smoothPlot(self, data, xIndex, yIndex, type, color):
#		#time = data[1:, xIndex]
#		#accel_x = data[1:, yIndex]
#		
#		ax = self.figure.add_subplot(111)
#		ax.plot(data[1:, xIndex].astype(numpy.float), smooth(data[1:, yIndex].astype(numpy.float), window = type), color + '-')
#		#ax.set_title('PyQt Matplotlib Example')
#		ax.set_xlabel(data[0, xIndex])
#		ax.set_ylabel(data[0, yIndex])
#		#ax.set_xticks(numpy.arange(0, max(time)+1, 1.0))
#		self.draw()
#	
#	def butterPlot(self, data, xIndex, yIndex):
#		ax = self.figure.add_subplot(111)
#		
#		dataY = butterFilter(data, yIndex)
#		
#		ax.plot(data[1:, xIndex].astype(numpy.float), dataY, 'b-')
#		
#		ax.set_xlabel(data[0, xIndex])
#		ax.set_ylabel(data[0, yIndex])
#		self.draw()
#	
#	def gaussPlot(self, data, xIndex, yIndex, window, color):
#		#time = data[1:, xIndex]
#		#accel_x = data[1:, yIndex]
#		
#		ax = self.figure.add_subplot(111)
#		ax.plot(data[1:, xIndex].astype(numpy.float), ndimage.gaussian_filter1d(data[1:, yIndex].astype(numpy.float), window), color + '-')
#		#ax.set_title('PyQt Matplotlib Example')
#		ax.set_xlabel(data[0, xIndex])
#		ax.set_ylabel(data[0, yIndex])
#		#ax.set_xticks(numpy.arange(0, max(time)+1, 1.0))
#		self.draw()