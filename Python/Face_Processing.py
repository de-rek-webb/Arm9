import cv2

def face_to_dotmap(frame,rects):
    for (i,rect) in enumerate(rects):
        (x1,y1,w,h) = self.find_rect(rect)
        shape = self.predictor(frame,rect)
        shape2 = self.shape_to_np_jaw(shape,x1,y1,w,h)
        shape = face_utils.shape_to_np(shape)
        blank_image = np.zeros(frame.shape, dtype=np.uint8)
        channels =  frame.shape[2]
        ignore_color = (255,)*channels
        cv2.fillPoly(blank_image, shape2, ignore_color)
        masked_img = cv2.bitwise_and(frame,blank_image)

        gray_mask = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)

        invert_mask = cv2.bitwise_not(gray_mask)

        img_blur = cv2.blur(invert_mask, (10,10))
        #img_blur = cv2.bilateralFilter(invert_mask,9,75,75)
        result = self.dodge(gray_mask,img_blur)
        edge = cv2.Canny(result,100,200)
        box = edge[rect.top():rect.bottom(),rect.left():rect.right()]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        blank_image2 = np.zeros(frame.shape,dtype=np.uint8)
        blank_image2 = cv2.cvtColor(blank_image2, cv2.COLOR_BGR2GRAY)

        x_off = (blank_image2.shape[1]//2) - (box.shape[1]//2)
        y_off = (blank_image2.shape[0]//2) - (box.shape[0]//2)
        blank_image2[y_off:y_off+box.shape[0],x_off:x_off+box.shape[1]] = box

        cv2.imwrite("output"+".jpg",blank_image2)

        coords = np.argwhere(blank_image2 == 255)
        return coords
    #                    thin_array = self.thin_array(coords)
    #                    print(thin_array)
