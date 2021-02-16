import numpy as np
import os
import cv2
import dlib
import imutils
import math

def DistanceOfX( A ) :
  return abs( A[1][0] - A[0][0] )


def DistanceOfY( A ) :
  return abs( A[1][1] - A[0][1] )


def Distance( A ) :
    return math.sqrt( DistanceOfX( A )**2 + DistanceOfY( A )**2 )


def rotate(image, angle, center = None, scale = 1.0):
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    return rotated


def GetAngle( points ):
    v1 = [points[0][0], points[0][1], points[1][0],points[1][1]]

    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]

    angle1 = math.atan2( dy1, dx1 )
    angle1 = int( angle1 * 180 / math.pi )

    return angle1


def run(glassesAddr):
    detector = dlib.get_frontal_face_detector()
    path = os.path.join(os.path.dirname(__file__), "datas", "shape_predictor_81_face_landmarks.dat")
    predictor = dlib.shape_predictor(path)

    # 打開臉部照片
    path = os.path.join(os.path.dirname(__file__), "images", "saved.jpg")
    faceImg = cv2.imread(path)
    faceImg = imutils.resize( faceImg, width = 640 )

    faceImg_gray = cv2.cvtColor(faceImg, cv2.COLOR_RGB2GRAY)
    rects = detector(faceImg_gray, 1)

    distanceOfEye = []
    leftEye = []
    rightEye = []
    faceWidth = []
    bridge  = []

    # 標記特徵點
    for i in range(len(rects)):
        landmarks = np.matrix([[p.x, p.y] for p in predictor(faceImg,rects[i]).parts()])
        for idx, point in enumerate(landmarks):
            pos = (point[0, 0], point[0, 1])

            if ( ( idx + 1 ) == 39 or ( idx + 1 ) == 44 ) : distanceOfEye.append( pos )
            if ( ( idx + 1 ) == 37 or ( idx + 1 ) == 40 ) : leftEye.append( pos )
            if ( ( idx + 1 ) == 43 or ( idx + 1 ) == 46 ) : rightEye.append( pos )
            if ( ( idx + 1 ) == 1 or ( idx + 1 ) == 17 ) : faceWidth.append( pos )
            if ( ( idx + 1 ) == 28 ) : bridge.append( pos )

            # 利用cv2.circle給每個特徵點畫一個圈，共81個
            cv2.circle(faceImg, pos, 7, color=(255, 255, 255))
            # 利用cv2.putText輸出1-81
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(faceImg, str(idx+1), pos, font, 0.8, (0, 255, 0), 1, cv2.LINE_AA)

    path = os.path.join(os.path.dirname(__file__), "images", "saved.jpg")
    faceImg = cv2.imread(path)

    # 打開眼鏡照片
    path = os.path.join(os.path.dirname(__file__), glassesAddr)
    glassesImg = cv2.imread( path )
    glassesImg = imutils.resize( glassesImg, width = int( Distance( distanceOfEye ) * 2.5 ) )

    # 把臉部照片轉正
    tempImg = rotate( faceImg, GetAngle( faceWidth ) )

    # 開始合成臉部照片和眼鏡照片 並把照片轉回原本的樣子
    src_mask = 255 * np.ones(glassesImg.shape, glassesImg.dtype)
    center = ( bridge[0][0], bridge[0][1]+8 )
    outputImg = cv2.seamlessClone(glassesImg, tempImg, src_mask, center, cv2.MIXED_CLONE )
    outputImg = rotate( outputImg, -GetAngle( faceWidth ) )


    # 開啟人臉辨識器
    classfier = cv2.CascadeClassifier('D:\\opencv\\opencv\\build\\etc\\haarcascades\\haarcascade_frontalface_alt2.xml')
    gray = cv2.cvtColor(faceImg, cv2.COLOR_BGR2GRAY)
    faces = classfier.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(32, 32))

    # 抓出人臉的位置
    for (x, y, w, h) in faces:
        a = x + w/2
        b = y + h/2
        center = (int(a),int(b))

    # 只剪取人臉 然後把臉貼回原照片 -> 目的是為了去掉旋轉後留下的黑色區塊
    tempImg = outputImg[int(b-((h/2)*1.2)):int(b+((h/2)*1.2)), int(a-((w/2)*1.2)):int(a+((w/2)*1.2))]
    faceImg[int(b-((h/2)*1.2)):int(b+((h/2)*1.2)), int(a-((w/2)*1.2)):int(a+((w/2)*1.2))] = tempImg

    path = os.path.join(os.path.dirname(__file__), "images", "result.jpg")
    cv2.imwrite( path, faceImg )

    #cv2.imwrite( path, outputImg )
