import numpy as np
import os
import cv2
import dlib
import imutils
import math


def DistanceOfX(A):
    return abs(A[1][0]-A[0][0])


def DistanceOfY(A):
    return abs(A[1][1]-A[0][1])


# 算出整張臉的角度 如果太歪(大於15度)就要重拍
def GetFaceAngle( points ):
    v1 = [points[0][0], points[0][1], points[1][0],points[1][1]]

    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]

    angle1 = math.atan2( dy1, dx1 )
    angle1 = int( angle1 * 180 / math.pi )

    return angle1



# 找出臉最寬的位置 ( 1前額 2頰骨 3下顎 )
def Step1( forehead, cheekbones, jaw ) :
  # 應該要用真正長度 不是x軸長度
  if LongestPart( forehead, cheekbones, jaw ) == DistanceOfX( jaw ) :
    return 3
  elif DistanceOfX( cheekbones ) / DistanceOfX( forehead ) < 1.04 :
    return 1
  elif LongestPart( forehead, cheekbones, jaw ) == DistanceOfX( cheekbones ) :
    return 2


def LongestPart(forehead, cheekbones, jaw):
    return max(DistanceOfX(forehead), DistanceOfX(cheekbones), DistanceOfX(jaw))


# 比較臉部長寬比 ( 1長>寬 2長=寬 )
def Step2( length, width ) :
  if ( length / width ) > 1.25 : return 1
  else : return 2


# 比較前額與下頜寬度 ( 1前額=下頜 2前額>下頜 3前額<下頜 )
def Step3( forehead, jaw ) :
  largest = max( DistanceOfX( forehead ), DistanceOfX( jaw ) )
  shortest = min( DistanceOfX( forehead ), DistanceOfX( jaw ) )
  if largest / shortest < 1.31 :
    return 1
  elif largest == DistanceOfX( forehead ) :
    return 2
  elif largest == DistanceOfX( jaw ) :
    return 3


# 找出下巴形狀 ( 1尖 2方 3圓 )
def Step4( face, cheekL, cheekR, chinL, chinR ) :
  # 計算下巴角度
  # # print( min( angle( chinL ), angle( chinR ) ) )
  if ( min( GetChinAngle( chinL ), GetChinAngle( chinR ) ) <= 160 ) :
    return 2
  
  # 計算臉頰占整個臉的比例
  proportion = ( GetAreaOfPolygon( cheekL ) + GetAreaOfPolygon( cheekR ) ) / GetAreaOfPolygon( face )
  # print( proportion )
  
  if ( proportion < 0.288 ) : return 1
  elif ( proportion < 0.30 ) : return 3
  else : return 2


def GetChinAngle(points):
    v1 = []
    v2 = []
    for i in range(len(points)):
        if (i<=1):
            for j in range(len(points[i])):
                v1.append(points[i][j])

        if (i>=1):
            for j in range(len(points[i])):
                v2.append(points[i][j])

    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = v2[2] - v2[0]
    dy2 = v2[3] - v2[1]

    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1*180/math.pi)
    # print(angle1)

    angle2 = math.atan2(dy2,dx2)
    angle2 = int(angle2*180/math.pi)
    # print(angle2)

    if angle1 * angle2 >= 0:
        included_angle = abs(angle1-angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        if included_angle > 180:
            included_angle = 360 - included_angle

    return (180-included_angle)



def GetAreaOfPolygon(points):
    area = 0
    # 計算多邊形面積
    p1 = points[0]
    for i in range(1, len(points)-1):
        p2 = points[i]
        p3 = points[i+1]

        # 計算向量
        vecp1p2 = [p2[0]-p1[0],p2[1]-p1[1]]
        vecp2p3 = [p3[0]-p2[0],p3[1]-p2[1]]

        # 判斷順時針還是逆時針，順時針面積為正，逆時針面積為負
        vecMult = vecp1p2[0] * vecp2p3[1] - vecp1p2[1] * vecp2p3[0] # 判斷正負方向
        sign = 0
        if(vecMult>0):
            sign = 1
        elif(vecMult<0):
            sign = -1

        area += GetAreaOfTriangle(p1, p2, p3) * sign

    return abs(area)


def GetAreaOfTriangle(p1, p2, p3):
    line1 = math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)
    line2 = math.sqrt((p2[0]-p3[0])**2+(p2[1]-p3[1])**2)
    line3 = math.sqrt((p1[0]-p3[0])**2+(p1[1]-p3[1])**2)

    # 海倫公式
    s = (line1+line2+line3) / 2
    return math.sqrt(s*(s-line1)*(s-line2)*(s-line3))


def IsOblong(answer):
  if answer == "1111": return True
  elif answer == "1112": return True
  elif answer == "1113": return True
  elif answer == "1121": return True
  elif answer == "1122": return True
  elif answer == "1123": return True
  elif answer == "1211": return True
  elif answer == "2112": return True
  elif answer == "2113": return True
  elif answer == "2121": return True
  elif answer == "2122": return True
  elif answer == "2123": return True
  elif answer == "2131": return True
  elif answer == "2132": return True
  elif answer == "2133": return True
  elif answer == "3111": return True
  elif answer == "3112": return True
  elif answer == "3113": return True
  elif answer == "3131": return True
  elif answer == "3132": return True
  elif answer == "3133": return True
  else: return False


def IsSquare( answer ) :
  if answer == "1212" : return True
  elif answer == "1213" : return True
  elif answer == "1223" : return True
  elif answer == "2212" : return True
  elif answer == "2231" : return True
  elif answer == "2232" : return True
  elif answer == "2233" : return True
  elif answer == "3212" : return True
  elif answer == "3213" : return True
  elif answer == "3232" : return True
  elif answer == "3233" : return True
  else : return False
  

def IsOval( answer ) :
  if answer == "2211" : return True
  elif answer == "2221" : return True
  elif answer == "2222" : return True
  else : return False


def IsCircle( answer ) :
  if answer == "2213" : return True
  elif answer == "2223" : return True
  else : return False 


def IsTriangle( answer ) :
  if answer == "1221" : return True
  elif answer == "1222" : return True
  else : return False 


def IsDiamond( answer ) :
  if answer == "2111" : return True
  else : return False


def run():
    detector = dlib.get_frontal_face_detector()
    path = os.path.join(os.path.dirname(__file__), "datas", "shape_predictor_81_face_landmarks.dat")
    predictor = dlib.shape_predictor(path)

    # cv2讀取影象
    path = os.path.join(os.path.dirname(__file__), "images", "saved.jpg")
    img = cv2.imread( path )
    img = imutils.resize( img, width = 960 )

    # 取灰度
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 檢查CascadeClassifier能不能用
    classfier = cv2.CascadeClassifier('D:\\opencv\\opencv\\build\\etc\\haarcascades\\haarcascade_frontalface_alt2.xml')
    faces = classfier.detectMultiScale(img_gray, scaleFactor=1.08, minNeighbors=5, minSize=(32, 32))
    i = -1
    for (x, y, w, h) in faces: i = 1
    if i == -1: return "error1"

    # 人臉數rects
    rects = detector(img_gray, 1)
    if len(rects)!=1: return "error2"

    forehead = []
    cheekbones = []
    jaw = []
    faceLength = []
    cheekL = []
    cheekR = []
    chinL = []
    chinR = []
    face = []
    faceWidth = []

    # 標記特徵點
    for i in range(len(rects)):
        landmarks = np.matrix([[p.x, p.y] for p in predictor(img, rects[i]).parts()])
        for idx, point in enumerate(landmarks):
            # 81點的座標 idx的值+1才是特徵點 ( idx = 1 --> 特徵點2 )
            pos = (point[0, 0], point[0, 1])
            # print( "asdf", idx, pos )
            if ( ( idx + 1 ) == 75 or ( idx + 1 ) == 76 ): forehead.append(pos)
            if ( ( idx + 1 ) == 2 or ( idx + 1 ) == 16 ): cheekbones.append(pos)
            if ( ( idx + 1 ) == 5 or ( idx + 1 ) == 13 ): jaw.append(pos)
            if ( ( idx + 1 ) == 9 or ( idx + 1 ) == 70 ): faceLength.append(pos)
        
            if ( ( idx + 1 ) >= 2 and ( idx + 1 ) <= 8 ): cheekL.append(pos)
            if ( ( idx + 1 ) >= 10 and ( idx + 1 ) <= 16 ): cheekR.append(pos)
  
            if ( ( idx + 1 ) >= 4 and ( idx + 1 ) <= 6 ): chinL.append(pos)
            if ( ( idx + 1 ) >= 12 and ( idx + 1 ) <= 14 ): chinR.append(pos)
        
            if ( ( ( idx + 1 ) >= 1 ) and ( ( idx + 1 ) <= 17 ) ) or ( ( ( idx + 1 ) <= 69 ) or  ( ( idx + 1 ) >= 81 ) ):
                face.append( pos )
            if( ( ( idx + 1 ) == 1 ) or ( ( idx + 1 ) == 17 ) ):
                faceWidth.append(pos)


            # 利用cv2.circle給每個特徵點畫一個圈，共81個
            cv2.circle(img, pos, 7, color=(255, 255, 255))
            # 利用cv2.putText輸出1-81
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, str(idx+1), pos, font, 0.8, (0, 255, 0), 1, cv2.LINE_AA)

    if abs(GetFaceAngle(faceWidth)) > 15: return "error3"

    # 第一步 找出臉最寬的位置 ( 1前額 2頰骨 3下顎 )
    # 第二步 比較臉部長寬比 ( 1長>寬 2長=寬 )
    # 第三步 比較前額與下頜寬度 ( 1前額=下頜 2前額>下頜 3前額<下頜 )
    # 第四步 找出下巴形狀 ( 1尖 2方 3圓 )

    answer = str( Step1( forehead, cheekbones, jaw ) ) +\
             str( Step2( DistanceOfY( faceLength ), LongestPart( forehead, cheekbones, jaw )  ) ) +\
             str( Step3( forehead, jaw ) ) + str( Step4( face, cheekL, cheekR, chinL, chinR ) )

    if IsOblong( answer ) : return "oblong"
    if IsSquare( answer ) : return "square"
    if IsOval( answer ) : return "oval"
    if IsCircle( answer ) : return "circle"
    if IsTriangle( answer ) : return "triangle"
    if IsDiamond( answer ) : return "diamond"
