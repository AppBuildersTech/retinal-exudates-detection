import cv2
import numpy as np
import os
import csv



def remove_OD(image):
	image_x = image.copy()
	b,green_fundus,red_fundus = cv2.split(resized_fundus)
	ret,g_channel = cv2.threshold(green_fundus,(np.amax(green_fundus)+np.mean(green_fundus))/2,255,cv2.THRESH_BINARY)
	ret,r_channel = cv2.threshold(red_fundus,(np.amax(red_fundus)+np.mean(red_fundus))/2,255,cv2.THRESH_BINARY)	
	for i in range(image_x.shape[0]):
		for j in range(image_x.shape[1]):
			if(g_channel[i,j] == r_channel[i,j]):
				image_x[i,j] = g_channel[i,j]
			else:
				image_x[i,j] = 0
	return image_x







if __name__ == "__main__":
    pathFolder = "/home/sherlock/Internship@iit/exudate-detection/diaretdb1/"
    filesArray = [x for x in os.listdir(pathFolder) if os.path.isfile(os.path.join(pathFolder,x))]
    destinationFolder = "/home/sherlock/Internship@iit/exudate-detection/diaretdb1-exudates/"

    if not os.path.exists(destinationFolder):
        os.mkdir(destinationFolder)

    for file_name in filesArray:
    	print(pathFolder+'/'+file_name)
    	file_name_no_extension = os.path.splitext(file_name)[0]
    	fundus = cv2.imread(pathFolder+'/'+file_name)
    	dim = (800,615)
    	resized_fundus = cv2.resize(fundus, dim, interpolation = cv2.INTER_AREA)    	
    	#eroded_image = remove_OD(resized_fundus)
    	cv2.imwrite(destinationFolder+file_name_no_extension+"_resized.jpg",resized_fundus)	



    
