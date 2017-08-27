import numpy as np
import cv2
from numba import jit
import os
from matplotlib import pyplot as plt
import math
import csv
from sklearn import preprocessing
import numpy as np
from sklearn import preprocessing
import random
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier


@jit
def check_diff(image1,image2):
	print(image1.shape,image2.shape,"priniting shape of images")
	print(image1[400:410,400:415])
	print("printing second image..")
	print(image2[400:410,400:415])
	i = 0
	j = 0
	inc = 0
	while i < image1.shape[0]:
		j = 0
		while j < image1.shape[1]:
			if image1[i,j] != image2[i,j]:
				inc = inc + 1
			j = j + 1
		i = i + 1
	print("no of differences: ",inc)



@jit
def show_final_result(name_array):
	i = 0
	j = 0
	lc = 0
	counter = 0
	k = 0
	while k < len(name_array):
		edge_candidates = cv2.imread(DestinationFolder+name_array[k]+"_edge_candidates.bmp")
		print("printing",DestinationFolder+name_array[k]+"_edge_candidates.bmp")
		result = edge_candidates.copy()
		while i < edge_candidates.shape[0]:
			j = 0
			while j < edge_candidates.shape[1]:
				if edge_label[lc,0]==1:
					result[i,j] = Y_predicted[counter]
					counter = counter + 1
				lc = lc +1
				j = j + 1
			i = i + 1
		k = k +1
	cv2.imwrite(DestinationFolder+file_name_no_extension+"final_result.bmp",result)

@jit
def standard_deviation_image(image):
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	clahe_output = clahe.apply(image)
	result = clahe_output.copy()
	i = 0
	j = 0
	while i < image.shape[0]:
		j = 0
		while j < image.shape[1]:
			sub_image = clahe_output[i:i+9,j:j+9]
			var = np.var(sub_image)
			result[i:i+9,j:j+9] = var
			j = j+9
		i = i+9
	return result

def get_DistanceFromOD_data(image, centre):
	my_image = image.copy()
	x_cor = centre[0]
	y_cor = centre[1]
	feature_5 = np.reshape(image, (image.size,1))
	k = 0
	i = 0
	j = 0
	while i < image.shape[0]:
		j = 0
		while j < image.shape[1]:
			feature_5[k] = math.fabs(x_cor-i) + math.fabs(y_cor-j)
			j = j+1
			k = k+1
		i = i+1
	return feature_5

def count_ones(image,value):
	i = 0
	j = 0 
	k = 0
	while i < image.shape[0]:
		j = 0
		while j < image.shape[1]:
			if int(image[i,j]) == value:
				k = k+1
			j = j + 1			
		i = i+1
	return k


def get_SD_data(sd_image):	
	feature_1 = np.reshape(sd_image, (sd_image.size,1))
	print(feature_1.shape,"feature1")
	return feature_1

def get_HUE_data(hue_image):	
	feature_2 = np.reshape(hue_image,(hue_image.size,1))
	print(feature_2.shape,"feature2")
	return feature_2

def get_INTENSITY_data(intensity_image):	
	feature_3 = np.reshape(intensity_image,(intensity_image.size,1))
	print(feature_3.shape,"feature3")
	return feature_3

def get_EDGE_data(edge_candidates_image):
	feature_4 = np.reshape(edge_candidates_image,(edge_candidates_image.size,1))
	print(feature_4.shape,"feature4")
	return feature_4

def get_RED_data(red_channel):	
	feature_5 = np.reshape(red_channel, (red_channel.size,1))
	print(feature_5.shape,"feature5")
	return feature_5

def get_GREEN_data(green_channel):
	feature_6 = np.reshape(green_channel, (green_channel.size,1))
	print(feature_6.shape,"feature6")
	return feature_6

def line_of_symmetry(image):
	image_v = image.copy()
	line = 0
	prev_diff = image_v.size
	for i in range(20,image_v.shape[0]-20):
		x1, y1 = image_v[0:i,:].nonzero()
		x2, y2 = image_v[i+1:image_v.shape[0],:].nonzero()
		diff = abs(x1.shape[0] - x2.shape[0])
		if diff < prev_diff:
			prev_diff = diff
			line = i
		i = i + 35
	return line

def identify_OD(image):
	newfin = cv2.dilate(image, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)), iterations=2)
	mask = np.ones(newfin.shape[:2], dtype="uint8") * 255
	y1, ycontours, yhierarchy = cv2.findContours(newfin.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	prev_contour = ycontours[0]
	for cnt in ycontours:
		if cv2.contourArea(cnt) >= cv2.contourArea(prev_contour):
			prev_contour = cnt
			cv2.drawContours(mask, [cnt], -1, 0, -1)
	M = cv2.moments(prev_contour)
	cx = int(M['m10']/M['m00'])
	cy = int(M['m01']/M['m00'])
	print(cx,cy)
	return (cx,cy)

def identify_OD_bv_density(blood_vessel_image):
	los = line_of_symmetry(blood_vessel_image)
	sub_image = blood_vessel_image[los-100:los+100,:]
	i = 0
	index = 0
	density = -1
	rr = 0	
	while i < sub_image.shape[1]:
		x1,y1 = sub_image[:,i:i+50].nonzero()
		count = x1.shape[0]		
		if(density < count):
			density = count
			index = i
		i = i + 30	
	print(los,index)
	return (index,los)


@jit
def calculate_entropy(image):
	entropy = image.copy()
	sum = 0
	i = 0
	j = 0
	while i < entropy.shape[0]:
		j = 0
		while j < entropy.shape[1]:
			sub_image = entropy[i:i+10,j:j+10]
			histogram = cv2.calcHist([sub_image],[0],None,[256],[0,256])
			sum = 0
			for k in range(256):
				if histogram[k] != 0:					
					sum = sum + (histogram[k] * math.log(histogram[k]))
				k = k + 1
			entropy[i:i+10,j:j+10] = sum
			j = j+10
		i = i+10
	ret2,th2 = cv2.threshold(entropy,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	newfin = cv2.erode(th2, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)), iterations=1)
	return newfin

@jit
def edge_pixel_image(image,bv_image):
	edge_result = image.copy()
	edge_result = cv2.Canny(edge_result,40,100)	
	i = 0
	j = 0
	while i < image.shape[0]:
		j = 0
		while j < image.shape[1]:
			if edge_result[i,j] == 255 and bv_image[i,j] == 255:
				edge_result[i,j] = 0
			j = j+1
		i = i+1
	newfin = cv2.dilate(edge_result, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)), iterations=1)
	return newfin

def extract_bv(image):
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	contrast_enhanced_green_fundus = clahe.apply(image)
	# applying alternate sequential filtering (3 times closing opening)
	r1 = cv2.morphologyEx(contrast_enhanced_green_fundus, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)), iterations = 1)
	R1 = cv2.morphologyEx(r1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)), iterations = 1)
	r2 = cv2.morphologyEx(R1, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)), iterations = 1)
	R2 = cv2.morphologyEx(r2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)), iterations = 1)
	r3 = cv2.morphologyEx(R2, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(23,23)), iterations = 1)
	R3 = cv2.morphologyEx(r3, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(23,23)), iterations = 1)
	f4 = cv2.subtract(R3,contrast_enhanced_green_fundus)
	f5 = clahe.apply(f4)

	# removing very small contours through area parameter noise removal
	ret,f6 = cv2.threshold(f5,15,255,cv2.THRESH_BINARY)
	mask = np.ones(f5.shape[:2], dtype="uint8") * 255
	im2, contours, hierarchy = cv2.findContours(f6.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:
		if cv2.contourArea(cnt) <= 200:
			cv2.drawContours(mask, [cnt], -1, 0, -1)
	im = cv2.bitwise_and(f5, f5, mask=mask)
	ret,fin = cv2.threshold(im,15,255,cv2.THRESH_BINARY_INV)
	newfin = cv2.erode(fin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)), iterations=1)

	# removing blobs of microaneurysm & unwanted bigger chunks taking in consideration they are not straight lines like blood
	# vessels and also in an interval of area
	fundus_eroded = cv2.bitwise_not(newfin)
	xmask = np.ones(image.shape[:2], dtype="uint8") * 255
	x1, xcontours, xhierarchy = cv2.findContours(fundus_eroded.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	for cnt in xcontours:
		shape = "unidentified"
		peri = cv2.arcLength(cnt, True)
		approx = cv2.approxPolyDP(cnt, 0.04 * peri, False)
		if len(approx) > 4 and cv2.contourArea(cnt) <= 3000 and cv2.contourArea(cnt) >= 100:
			shape = "circle"
		else:
			shape = "veins"
		if(shape=="circle"):
			cv2.drawContours(xmask, [cnt], -1, 0, -1)

	finimage = cv2.bitwise_and(fundus_eroded,fundus_eroded,mask=xmask)
	blood_vessels = cv2.bitwise_not(finimage)
	return finimage



if __name__ == "__main__":
	pathFolder = "/home/sherlock/Internship@iit/exudate-detection/testing/"
	filesArray = [x for x in os.listdir(pathFolder) if os.path.isfile(os.path.join(pathFolder,x))]
	DestinationFolder = "/home/sherlock/Internship@iit/exudate-detection/testing-results/"
	LabelFolder = "/home/sherlock/Internship@iit/exudate-detection/diaretdb1-label/"
	name_array = []
	number = 0
	
	if not os.path.exists(DestinationFolder):
		os.mkdir(DestinationFolder)

	qq = 0

	for file_name in filesArray:
		print(pathFolder+'/'+file_name)
		file_name_no_extension = os.path.splitext(file_name)[0]
		name_array.append(file_name_no_extension)
		fundus1 = cv2.imread(pathFolder+'/'+file_name)
		fundus = cv2.resize(fundus1,(800,615))
		b,g,r = cv2.split(fundus)		
		hsv_fundus = cv2.cvtColor(fundus,cv2.COLOR_BGR2HSV)
		h,s,v = cv2.split(hsv_fundus)
		gray_scale = cv2.cvtColor(fundus,cv2.COLOR_BGR2GRAY)
		clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
		contrast_enhanced_fundus = clahe.apply(gray_scale)		
		contrast_enhanced_green_fundus = clahe.apply(g)
		average_intensity = np.mean(contrast_enhanced_fundus)/255
		average_hue = np.mean(h)/255
		#entropy = calculate_entropy(contrast_enhanced_fundus)
		bv_image = extract_bv(g)
		cv2.imwrite(DestinationFolder+file_name_no_extension+"_blood_vessels.bmp",bv_image)
		var_fundus = standard_deviation_image(contrast_enhanced_fundus)
		edge_feature_output = edge_pixel_image(contrast_enhanced_green_fundus,bv_image)
		#fin_edge = cv2.bitwise_and(edge_candidates,entropy)
		(cx,cy) = identify_OD_bv_density(bv_image)
		newfin = cv2.dilate(edge_feature_output, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)), iterations=1)
		edge_candidates = newfin.copy()
		edge_candidates = cv2.circle(edge_candidates,(cx,cy), 100, (0,0,0), -10)

		cv2.imwrite(DestinationFolder+file_name_no_extension+"_edge_candidates.bmp",edge_candidates)
		temp_image = cv2.imread(DestinationFolder+file_name_no_extension+"_edge_candidates.bmp")
		q,temp_i,ww = cv2.split(temp_image)
		check_diff(edge_candidates,temp_i)
		label_image = cv2.imread(LabelFolder+'/'+file_name_no_extension+"_final_label.bmp")

		feature1 = get_SD_data(var_fundus)/255
		feature2 = get_HUE_data(h)/255
		feature3 = get_INTENSITY_data(contrast_enhanced_fundus)/255
		feature4 = get_EDGE_data(edge_candidates)/255
		feature5 = get_RED_data(r)/255
		feature6 = get_GREEN_data(g)/255
		feature7 = get_DistanceFromOD_data(bv_image,(cx,cy))/(var_fundus.shape[0]+var_fundus.shape[1])

		b,gg,r = cv2.split(label_image)
		label = np.reshape(gg,(gg.size,1))/255
		co3 = count_ones(edge_candidates,255)
		print(co3,"check me")
		counter = 0
		temp = 0
		this_image_rows = 0
		with open('test.csv', 'a') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
			while counter < feature1.shape[0]:
				if feature4[counter,0] == 1:
					qq = qq + 1
					temp = counter
					this_image_rows = this_image_rows+1
					filewriter.writerow([feature1[counter,0],feature2[counter,0],feature3[counter,0],feature5[counter,0],feature6[counter,0],feature7[counter,0],average_intensity,average_hue,int(label[counter,0])])
				counter = counter +1
		
		print(feature1[temp,0],feature2[temp,0],feature3[temp,0],feature5[temp,0],feature6[temp,0],feature7[temp,0],average_intensity,average_hue,int(label[temp,0]))
		print("no of rows addded : ", this_image_rows)
		print("-----------x-------DONE-------x----------")

	print("no of pixxels in total", qq)
	print(name_array,"HEY NAMES")
	
	import numpy as np
	from sklearn import preprocessing
	import random
	import pandas as pd
	from sklearn.metrics import confusion_matrix
	from sklearn.svm import SVC
	from sklearn.metrics import accuracy_score
	from sklearn.ensemble import RandomForestClassifier
	from sklearn.neighbors import KNeighborsClassifier
	from sklearn.ensemble import AdaBoostClassifier
	from sklearn.tree import DecisionTreeClassifier
	print("fcuuk")
	dataset_train = np.loadtxt('train.txt', delimiter=",")
	#dataset_train = pd.read_csv("train.csv")
	print(dataset_train.shape,"train_shape")

	dataset_test = np.loadtxt('test.txt', delimiter=",")
	#dataset_test = pd.read_csv("test.csv")
	print(dataset_test.shape,"test_shape")

	X_train = dataset_train[:,0:7]
	Y_train = dataset_train[:,8]

	print(dataset_train[50:55,8])

	X_test = dataset_test[:,0:7]
	Y_test = dataset_test[:,8]



	print(dataset_train[100000:100130,:])


	#clf = AdaBoostClassifier(DecisionTreeClassifier(max_depth = 5),algorithm="SAMME",n_estimators=100)
	#clf = SVC(kernel = 'poly')
	#clf = KNeighborsClassifier(n_neighbors = 5)
	#clf = AdaBoostClassifier()

	clf = RandomForestClassifier(n_estimators=10)
	clf.fit(X_train, Y_train) 

	Y_predicted = clf.predict(X_test)
	print (Y_predicted)

	print("accuracy")
	print(accuracy_score(Y_test, Y_predicted))

	print("confusion matrix")
	print (confusion_matrix(Y_test,Y_predicted))

	# resultFolder = "/home/sherlock/Internship@iit/exudate-detection/results-exudates/"	
	# print(len(name_array))
	# if not os.path.exists(resultFolder):
	# 	os.mkdir(resultFolder)
	# size_m = 0
	# i = 0
	# j = 0
	# lc = 0
	# while size_m < len(name_array):
	# 	current = cv2.imread(DestinationFolder+name_array[size_m]+"_edge_candidates.bmp")
	# 	print(DestinationFolder+name_array[size_m]+"_edge_candidates.bmp")		
	# 	print("current ka size",current.shape)
	# 	x,current_m,z = cv2.split(current)
	# 	print(count_ones(current_m,255),"now again check",name_array[size_m])
	# 	i = 0		
	# 	while i < current_m.shape[0]:
	# 		j = 0
	# 		while j < current_m.shape[1]:
	# 			if current_m[i,j] == 255:
	# 				current_m[i,j] = 255*Y_predicted[lc]
	# 				lc = lc + 1
	# 			j = j + 1
	# 		i = i + 1
	# 	cv2.imwrite(resultFolder+name_array[size_m]+"_result.bmp",current_m)
	# 	size_m = size_m + 1	

	# print("DONE_-------------------x----xxxxx-xx-x")



		#print(feature1[500:510,:],feature2[500:510,:],feature3[500:510,:],feature4[500:510,:])
		
		# data = np.concatenate((feature1,feature2,feature3,feature4),axis=1)
		# data = np.float32(data)
		# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.01)
		# ret,label,center=cv2.kmeans(edge_candidates_image,2,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
		# print(center)

		# green = [0,255,0]
		# blue = [255,0,0]
		# red = [0,0,255]
		# white = [255,255,255]
		# black = [0,0,0]

		# color = [green,blue,red,white,black]
		# color = np.array(color,np.uint8)
		# label = np.reshape(label, gray_scale.shape)
		# y = color[label]
		# y = np.uint8(y)		
		# #cv2.imwrite("kmeans.bmp",y)		
		#cv2.waitKey()			
		#cv2.imwrite(DestinationFolder+file_name_no_extension+"_candidate_exudates.bmp",edge_candidates)		
		#cv2.imwrite(DestinationFolder+file_name_no_extension+"_result_exudates_kmeans.bmp",y)
		#cv2.imwrite(DestinationFolder+file_name_no_extension+"_sd_result.bmp",var_fundus)

# X = np.random.randint(25,50,(25,2))
# Y = np.random.randint(60,85,(25,2))
# Z = np.vstack((X,Y))

# # convert to np.float32
# Z = np.float32(Z)

# # define criteria and apply kmeans()
# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
# ret,label,center=cv2.kmeans(Z,2,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

# # Now separate the data, Note the flatten()
# A = Z[label.ravel()==0]
# B = Z[label.ravel()==1]

# # Plot the data
# plt.scatter(A[:,0],A[:,1])
# plt.scatter(B[:,0],B[:,1],c = 'r')
# plt.scatter(center[:,0],center[:,1],s = 80,c = 'y', marker = 's')
# plt.xlabel('Height'),plt.ylabel('Weight')
# plt.show()