def mask_create(hsv,L,U):
    lower = np.array(L)
    upper = np.array(U)
    mask = cv2.inRange(hsv, lower, upper)
    return mask
#colors_distributions function
def colors_distributions(a_frame):#RGB
    the_frame = a_frame.copy()
    hsv = cv2.cvtColor(the_frame, cv2.COLOR_BGR2HSV)
    masks =[
            mask_create(hsv,[-30,0,10],[30, 255, 255]),#RED
            mask_create(hsv,[30,0,10],[90, 255, 255]),#GREEN
            mask_create(hsv,[90,0,10],[150, 255, 255]),#BLUE
            ]
    Data=[]
    colors = [(0,0,255),(0,255,0),(255,0,0)]
    counterc = 0
    for mask in masks:
        cnts =cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)# find countours
        cnts = imutils.grab_contours(cnts)
        total_area=1
        tcy=tcx=acx=acy=counter=0
        for c in cnts:
            counter+=1
            area = cv2.contourArea(c)
            if area >50:
                #cv2.drawContours(the_frame,[c],-1,color,3)
                M = cv2.moments(c)
                cx = int(M["m10"]/M["m00"])
                cy = int(M["m01"]/M["m00"])
                tcx += int(cx*area) # Total center x
                tcy += int(cy*area) # Total center y
                total_area +=area
        total_area=int(total_area)
        if(tcx !=0 and tcy !=0):
            acx = int(tcx//(total_area))
            acy = int(tcy//(total_area))
            Data.append([acx,acy,total_area])
            cv2.circle(the_frame,(acx,acy),20,colors[counterc],3)
            cv2.putText(the_frame, "Weight :"+str(total_area), (acx+25,acy-10), font,  1, colors[counterc])
        counterc+=1
    return (the_frame,Data)
#Showing the frame custom function / no return
def print_frame(frame,name,res=(800,450)):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, res[0], res[1])
    cv2.imshow(name,frame)
#Closing operation / return a frame
def doClose(val,the_frame):
    kernel = np.ones((val,val))# sane as structure element
    res = cv2.morphologyEx(the_frame,cv2.MORPH_CLOSE, kernel)#closing op
    return res 
#Countour by light / return frame,data(cx,cy,w,h),binary_frame
def Lux_contourious(a_frame):
    the_frame= a_frame.copy()
    # Brightness Mask
    hls = cv2.cvtColor(the_frame,cv2.COLOR_BGR2HLS)
    lower = np.array([0,170,0])
    upper = np.array([180,255,255])
    mask = cv2.inRange(hls, lower, upper)
    mask = doClose(15,mask)
    cnts =cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    Data=[]
    binary_rec = np.zeros_like(the_frame)#the purpose is to black out all the image and keep only the contour
    
    for c in cnts:
        area = cv2.contourArea(c)
        if area >50:
            rotrect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rotrect)
            box = np.int0(box)
            if abs(rotrect[1][0] - rotrect[1][1]) <=4 :
                cv2.drawContours(the_frame,[box],-1,(0,255,0),3)
                cv2.drawContours(binary_rec,[box],-1,(255,255,255),-1)
                Data.append([int(rotrect[0][0]),int(rotrect[0][1]),int(rotrect[1][0]),int(rotrect[1][1])])#cx,cy,w,h
    binary_rec = cv2.split(binary_rec)[0]
    return (the_frame,Data,binary_rec)
#Countour by edge/ return frame,data(cx,cy,w,h)
def Edges_countourious(a_frame):
    the_frame= a_frame.copy()
     # Edges Mask
    blur = cv2.GaussianBlur(the_frame,(5,5),0)
    mask = cv2.Canny(the_frame,55,100)
    mask = doClose(10,the_frame)
    cnts =cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    Data=[]
    for c in cnts:
        area = cv2.contourArea(c)
        if area >50:
            approx = cv2.approxPolyDP(c, 0.04 * cv2.arcLength(c, True), True)
            rotrect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rotrect)
            box = np.int0(box)
            if rotrect[1][0] > rotrect[1][1]:
                ratio = rotrect[1][0]//rotrect[1][1]
            else:
                ratio = rotrect[1][1]//rotrect[1][0]
            if ratio<1.4 and len(approx) >6 and  len(approx) <9:
                cv2.drawContours(the_frame,[box],-1,(0,255,255),3)
                cv2.drawContours(the_frame,[approx],-1,(0,0,255),3)
                Data.append([int(rotrect[0][0]),int(rotrect[0][1]),int(rotrect[1][0]),int(rotrect[1][1])])#cx,xy,w,h
    return (the_frame,Data)
#Contour edge and light/ return frame, data(cx,xy,w,h)
def Star_catcher(a_frame):
    Data=[]
    the_frame= a_frame.copy()
    binary_rec = np.zeros_like(the_frame)#the purpose is to black out all the image and keep only the contour
    #Creating masks 
    # Brightness Mask
    hls = cv2.cvtColor(the_frame,cv2.COLOR_BGR2HLS)
    lower = np.array([0,170,0])
    upper = np.array([180,255,255])
    Lmask = cv2.inRange(hls, lower, upper)
    Lmask = doClose(15,Lmask)
    # Edges Mask
    blur = cv2.GaussianBlur(the_frame,(5,5),0)
    Emask = cv2.Canny(blur,55,100)
    Emask = doClose(10,Emask)
    #By light
    Lcnts =cv2.findContours(Lmask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    Lcnts = imutils.grab_contours(Lcnts)
    List_of_L_centers = []
    for lc in Lcnts:
        area = cv2.contourArea(lc)
        if area >50:
            rotrect = cv2.minAreaRect(lc)
            if abs(rotrect[1][0] - rotrect[1][1]) <=4 :
                List_of_L_centers.append(rotrect[0])#center(x,y)
    #By edges
    Ecnts =cv2.findContours(Emask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    Ecnts = imutils.grab_contours(Ecnts)
    for ec in Ecnts:
        smash = False
        area = cv2.contourArea(ec)
        if area >50:
            height = the_frame.shape[0]
            width = the_frame.shape[1]
            the_h_zone = height//5
            the_w_zone = width//5
            approx = cv2.approxPolyDP(ec, 0.04 * cv2.arcLength(ec, True), True)
            rotrect = cv2.minAreaRect(ec)
            for center in List_of_L_centers:
                if abs(rotrect[0][0] -center[0]) < the_w_zone and abs(rotrect[0][1] -center[1]) < the_h_zone:
                    smash = True 
                    break
            box = cv2.boxPoints(rotrect)
            box = np.int0(box)

            if rotrect[1][0] > rotrect[1][1]:
                ratio = rotrect[1][0]//rotrect[1][1]
            else:
                ratio = rotrect[1][1]//rotrect[1][0]

            if smash and ratio<1.4 and len(approx) ==8:
                cv2.drawContours(the_frame,[box],-1,(0,255,255),3)
                cv2.drawContours(the_frame,[approx],-1,(0,0,255),3)
                cv2.drawContours(binary_rec,[box],-1,(255,255,255),-1)
                Data.append([int(rotrect[0][0]),int(rotrect[0][1]),int(rotrect[1][0]),int(rotrect[1][1])])#cx,cy,w,h
    binary_rec = cv2.split(binary_rec)[0]
    return (the_frame,Data,binary_rec)
#Dust reduction / return frame
def Dust_reduction(the_frame):
    se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))
    se2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dustr = cv2.morphologyEx(the_frame, cv2.MORPH_CLOSE, se1)#Closing,gathering neighborhood pixels into a big structure
    return cv2.morphologyEx(dustr, cv2.MORPH_OPEN, se2)
#Dust detector/ return frame,data(cx,xy)
def Dust_detector(the_frame):
    Dust_reduction_frame = Dust_reduction(the_frame)
    gray_frame = cv2.cvtColor(the_frame,cv2.COLOR_BGR2GRAY)
    gray_dust_free_frame = cv2.cvtColor(Dust_reduction_frame,cv2.COLOR_BGR2GRAY)
    (thresh, binary_dust_frame) = cv2.threshold(gray_frame, 22, 255, cv2.THRESH_BINARY )
    (thresh, binary_dust_free_frame) = cv2.threshold(gray_dust_free_frame, 12, 255, cv2.THRESH_BINARY )
    result_frame = cv2.bitwise_and(cv2.bitwise_not(binary_dust_free_frame), binary_dust_frame)
    cnts = cv2.findContours(result_frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)
    Data=[]
    for c in cnts:
        area = cv2.contourArea(c)
        if area >1:
            rotrect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rotrect)
            box = np.int0(box)
            Data.append([int(rotrect[0][0]),int(rotrect[0][1])])#center
    return (result_frame,Data)
#Bright spot detector
def bright_spot_detector(the_frame):
    return Lux_contourious(the_frame)# for now
#Galaxies or gazes/ return frame,data(cx,cy)
def galaxies_or_gazes_detection(a_frame):
    the_frame= a_frame.copy()
    gray_frame = cv2.cvtColor(the_frame,cv2.COLOR_BGR2GRAY)
    (thresh, binary_frame) = cv2.threshold(gray_frame, 22, 255, cv2.THRESH_BINARY )
    (dust_frame,dust_Data) = Dust_detector(the_frame)#binary
    (_,_,bright_spot_frame) = bright_spot_detector(the_frame)
    (_,_,star_frame) = Star_catcher(the_frame)

    frame_without_dust_and_bright_spot = cv2.bitwise_and(binary_frame,cv2.bitwise_not(cv2.bitwise_or(cv2.bitwise_or(bright_spot_frame,dust_frame),star_frame)))
    #cnt
    cnts = cv2.findContours(frame_without_dust_and_bright_spot,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)
    Data=[]
    for c in cnts:
        area = cv2.contourArea(c)
        if area >2000:
            rotrect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rotrect)
            box = np.int0(box)
            Data.append([int(rotrect[0][0]),int(rotrect[0][1]),int(rotrect[1][0]),int(rotrect[1][1])])#cx,cy,w,h
            cv2.drawContours(the_frame,[box],-1,(0,255,255),3)
    #frame
    #result = cv2.bitwise_and(the_frame,the_frame,mask = frame_without_dust_and_bright_spot)
    result=the_frame
    return (result,Data)
