"""
**************************************************************************
*                  E-Yantra Robotics Competition
*                  ================================
*  This software is intended to check version compatiability of open source software
*  Theme: Thirsty Crow
*  MODULE: Task1.1
*  Filename: detect.py
*  Version: 1.0.0
*  Date: October 31, 2018
*
*  Author: e-Yantra Project, Department of Computer Science
*  and Engineering, Indian Institute of Technology Bombay.
*
*  Software released under Creative Commons CC BY-NC-SA
*
*  For legal information refer to:
*        http://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
*
*
*  This software is made available on an “AS IS WHERE IS BASIS”.
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or
*  breach of the terms of this agreement.
*
*  e-Yantra - An MHRD project under National Mission on Education using
*  ICT(NMEICT)
*
**************************************************************************
"""

import numpy as np
import cv2
import cv2.aruco as aruco
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import pygame
import time 
from objloader import *


texture_object = None
texture_background = None
camera_matrix = None
dist_coeff = None
cap = cv2.VideoCapture(1)
waterpitcher_low = None
waterpitcher_med = None
waterpitcher_hig = None
pileofstone_hig = None
pileofstone_low = None
crow = None
INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [ 1.0, 1.0, 1.0, 1.0]])

################## Define Utility Functions Here #######################
"""
Function Name : getCameraMatrix()
Input: None
Output: camera_matrix, dist_coeff
Purpose: Loads the camera calibration file provided and returns the camera and
         distortion matrix saved in the calibration file.
"""
def getCameraMatrix():
        global camera_matrix, dist_coeff
        with np.load('Camera.npz') as X:
                camera_matrix, dist_coeff, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]



########################################################################

############# Main Function and Initialisations ########################
"""
Function Name : main()
Input: None
Output: None
Purpose: Initialises OpenGL window and callback functions. Then starts the event
         processing loop.
"""
def main():
        glutInit()
        getCameraMatrix()
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(625, 100)
        glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
        window_id = glutCreateWindow("OpenGL")
        init_gl()
        glutDisplayFunc(drawGLScene)
        glutIdleFunc(drawGLScene)
        glutReshapeFunc(resize)
        glutMainLoop()

"""
Function Name : init_gl()
Input: None
Output: None
Purpose: Initialises various parameters related to OpenGL scene.
"""
def init_gl():
        global texture_object, texture_background
        global waterpitcher_low
        global crow
        global waterpitcher_med
        global waterpitcher_hig
        global pileofstone_hig
        global pileofstone_low
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        texture_background = glGenTextures(1)
        texture_object = glGenTextures(1)
        waterpitcher_low = OBJ('waterpitcher(low).obj', swapyz = True)
        crow=OBJ('crow.obj', swapyz = True)
        waterpitcher_med = OBJ('waterpitcher(medium).obj', swapyz = True)
        waterpitcher_hig = OBJ('waterpitcher(high).obj', swapyz = True)
        pileofstone_hig = OBJ('pileofstone(high).obj', swapyz = True)
        pileofstone_low = OBJ('pileofstone(dim).obj', swapyz = True)
"""
Function Name : resize()
Input: None
Output: None
Purpose: Initialises the projection matrix of OpenGL scene
"""
def resize(w,h):
        ratio = 1.0* w / h
        glMatrixMode(GL_PROJECTION)
        glViewport(0,0,w,h)
        gluPerspective(45, ratio, 1.0, 100.0)

"""
Function Name : drawGLScene()
Input: None
Output: None
Purpose: It is the main callback function which is called again and
         again by the event processing loop. In this loop, the webcam frame
         is received and set as background for OpenGL scene. ArUco marker is
         detected in the webcam frame and 3D model is overlayed on the marker
         by calling the overlay() function.
"""
def drawGLScene():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ar_list = []
        ret, frame = cap.read()
        if ret == True:
                draw_background(frame)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                ar_list = detect_markers(frame)
                for i in ar_list:
                          if i[0] == 0:
                                  overlay(frame, ar_list, i[0],pileofstone_hig)
                                  
                                  

                          if i[0] == 2:
                                  overlay(frame, ar_list, i[0],waterpitcher_low)
                                  time.sleep(3)
                                  overlay(frame, ar_list, i[0],waterpitcher_med)
                                  time.sleep(3)
                                  

##                       if i[0] == 0:
##                                overlay(frame, ar_list, i[0],waterpitcher_med)
## ##                      if i[0] == 1:
##   ##                             overlay(frame, ar_list, i[0],waterpitcher_low)
##                       if i[0] == 2:
##                                overlay(frame, ar_list, i[0],pileofstone_hig )
####                       if i[0] == 6:
####                                overlay(frame, ar_list, i[0],"texture_4.png")
##
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
        glutSwapBuffers()

########################################################################

######################## Aruco Detection Function ######################
"""
Function Name : detect_markers()
Input: img (numpy array)
Output: aruco list in the form [(aruco_id_1, centre_1, rvec_1, tvec_1),(aruco_id_2,
        centre_2, rvec_2, tvec_2), ()....]
Purpose: This function takes the image in form of a numpy array, camera_matrix and
         distortion matrix as input and detects ArUco markers in the image. For each
         ArUco marker detected in image, paramters such as ID, centre coord, rvec
         and tvec are calculated and stored in a list in a prescribed format. The list
         is returned as output for the function
"""
def detect_markers(img):
        markerLength = 100
        aruco_list = []
        ######################## INSERT CODE HERE ########################

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)

        parameters = aruco.DetectorParameters_create()
        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters = parameters)
        global Xc,Yc

        with np.load('Camera.npz') as X:
              camera_matrix, dist_coeff, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]
              corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters = parameters)
              rvec, tvec,_= aruco.estimatePoseSingleMarkers(corners, markerLength, camera_matrix, dist_coeff)

              j=0
              if ids is not None:
                      for i in ids:


                              Xc=(corners[j][0][0][0]+corners[j][0][1][0]+corners[j][0][2][0]+corners[j][0][3][0])/4
                              Yc=(corners[j][0][0][1]+corners[j][0][1][1]+corners[j][0][2][1]+corners[j][0][3][1])/4
                              aruco_centre=(Xc,Yc)

                              rvect = np.array([rvec[j].reshape(1,1,3)])
                              tvect = np.array([tvec[j].reshape(1,1,3)])
                              tup1 = (int(i),aruco_centre,rvect[0],tvect[0])
                              aruco_list.append(tup1)
                              j=j+1

        return aruco_list
########################################################################


################# This is where the magic happens !! ###################
############### Complete these functions as  directed ##################
"""
Function Name : draw_background()
Input: img (numpy array)
Output: None
Purpose: Takes image as input and converts it into an OpenGL texture. That
         OpenGL texture is then set as background of the OpenGL scene
"""
def draw_background(img):

        imageData= cv2.flip(img,0)
        imageData=cv2.cvtColor(imageData, cv2.COLOR_BGR2RGB)
        imageData=Image.fromarray(imageData,"RGB")
        ix=imageData.size[0]
        iy=imageData.size[1]
        s=imageData.size
        s=tuple(s)
        imageData=imageData.tobytes("raw","RGB",0,-1)
        glEnable(GL_TEXTURE_2D)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
        glBindTexture(GL_TEXTURE_2D, texture_background)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, ix, iy,
        0, GL_RGB, GL_UNSIGNED_BYTE, imageData)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_REPEAT)
        #glGenerateMipmap(GL_TEXTURE_2D);


        glBindTexture(GL_TEXTURE_2D,texture_background)
        glPushMatrix()
        glTranslatef(0.0,0.0,-10.0)
        #ilEnable(IL_ORIGIN_SET);
        #ilOriginFunc(IL_ORIGIN_LOWER_LEFT);
        glBegin(GL_QUADS)
        glTexCoord2f(0.0,1.0);glVertex3f(-6.0,-3.0,0.0)
        glTexCoord2f(1.0,1.0);glVertex3f(6.0,-3.0,0.0)
        glTexCoord2f(1.0,0.0);glVertex3f(6.0,3.0,0.0)
        glTexCoord2f(0.0,0.0);glVertex3f(-6.0,3.0,0.0)
        glEnd()
        #glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        glFlush()
        #glutSwapBuffers()


        return None

"""
Function Name : init_object_texture()
Input: Image file path
Output: None
Purpose: Takes the filepath of a texture file as input and converts it into OpenGL
         texture. The texture is then applied to the next object rendered in the OpenGL
         scene.
"""
def init_object_texture(image_filepath):
        tex = cv2.imread(image_filepath)
        tex=Image.fromarray(tex,"RGB")
        ix=tex.size[0]
        iy=tex.size[1]
        s=tex.size
        s=tuple(s)
        tex=tex.tobytes("raw","RGB",0,-1)
        glEnable(GL_TEXTURE_2D)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
        glBindTexture(GL_TEXTURE_2D, texture_background)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, ix, iy,
         0, GL_RGB, GL_UNSIGNED_BYTE, tex)


        glBindTexture(GL_TEXTURE_2D,texture_background)
        glPushMatrix()
        glTranslatef(0.0,0.0,-10.0)
        #glMatrixMode(GL_TEXTURE_2D);
        #glScalef(1,-1,1);
        glBegin(GL_QUADS)
        glTexCoord2f(0.0,1.0);glVertex3f(-6.0,-3.0,0.0)
        glTexCoord2f(1.0,1.0);glVertex3f(6.0,-3.0,0.0)
        glTexCoord2f(1.0,0.0);glVertex3f(6.0,3.0,0.0)
        glTexCoord2f(0.0,0.0);glVertex3f(-6.0,3.0,0.0)
        glEnd()
        glPopMatrix()
        #glutSolidTeapot(0.5)
        #glPushMatrix()
        #view_matrix = view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0][0][0]],
                        #[rmtx[1][0],rmtx[1][1],rmtx[1][2],0],
                        #[rmtx[2][0],rmtx[2][1],rmtx[2][2],4],
                        #[0.0       ,0.0       ,0.0       ,1.0    ]])
        #view_matrix = np.transpose(view_matrix)
        #glLoadMatrixd(view_matrix)
        #glutSolidTeapot(0.5)
        #glPopMatrix()
        return None

"""
Function Name : overlay()
Input: img (numpy array), aruco_list, aruco_id, texture_file (filepath of texture file)
Output: None
Purpose: Receives the ArUco information as input and overlays the 3D Model of a teapot
         on the ArUco marker. That ArUco information is used to
         calculate the rotation matrix and subsequently the view matrix. Then that view matrix
         is loaded as current matrix and the 3D model is rendered.

         Parts of this code are already completed, you just need to fill in the blanks. You may
         however add your own code in this function.
"""
def overlay(img, ar_list, ar_id, object_file):
        if(ar_list[0][0]==ar_id):
                index = 0

        elif(ar_list[1][0]==ar_id):
                index = 1

        elif(ar_list[2][0]==ar_id):
                index = 2

        if(ar_id == 0):
                centre, rvec, tvec = ar_list[index][1], ar_list[index][2], ar_list[index][3]
                rmtx = cv2.Rodrigues(rvec)[0]
                tmtx = cv2.Rodrigues(tvec)[0]

                view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],(tvec[0][0][0])/200
                                         ],
                                [rmtx[1][0],rmtx[1][1],rmtx[1][2],(tvec[0][0][1])/300],
                                [rmtx[2][0],rmtx[2][1],rmtx[2][2],(tvec[0][0][2])/130],
                                [0     ,0     ,0.0       ,1    ]])

                view_matrix = view_matrix * INVERSE_MATRIX
                view_matrix = np.transpose(view_matrix)
                glPushMatrix()
                glLoadMatrixd(view_matrix)
                glCallList(object_file.gl_list)
                glPopMatrix()
                

##        elif(ar_id == 1):
##                centre, rvec, tvec = ar_list[index][1], ar_list[index][2], ar_list[index][3]
##                rmtx = cv2.Rodrigues(rvec)[0]
##                tmtx = cv2.Rodrigues(tvec)[0]
##
##                view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],(tvec[0][0][0])/80],
##                                [rmtx[1][0],rmtx[1][1],rmtx[1][2],(tvec[0][0][1])/50],
##                                [rmtx[2][0],rmtx[2][1],rmtx[2][2],(tvec[0][0][2])/50],
##                                [0     ,0     ,1       ,1    ]])
##
##                view_matrix = view_matrix * INVERSE_MATRIX
##                view_matrix = np.transpose(view_matrix)
##                glPushMatrix()
##                glLoadMatrixd(view_matrix)
##                glCallList(object_file.gl_list)
##                glPopMatrix()


        elif(ar_id == 2):
                centre, rvec, tvec = ar_list[index][1], ar_list[index][2], ar_list[index][3]
                rmtx = cv2.Rodrigues(rvec)[0]
                tmtx = cv2.Rodrigues(tvec)[0]

                view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],(tvec[0][0][0])/160],
                                [rmtx[1][0],rmtx[1][1],rmtx[1][2],(tvec[0][0][1])/372],
                                [rmtx[2][0],rmtx[2][1],rmtx[2][2],(tvec[0][0][2])/140],
                                [0     ,1     ,0       ,1   ]])

                view_matrix = view_matrix * INVERSE_MATRIX
                view_matrix = np.transpose(view_matrix)
                glPushMatrix()
                glLoadMatrixd(view_matrix)
                glCallList(object_file.gl_list)
                glPopMatrix()
                



##        if(len(ar_list)==2):
##                for x in ar_list:
##                        if x[0] == 0:
##                                if ar_id == ar_list[0][0]:
##                                        centre, rvec, tvec = ar_list[0][1], ar_list[0][2], ar_list[0][3]
##
##                                        rmtx = cv2.Rodrigues(rvec)[0]
##                                        tmtx = cv2.Rodrigues(tvec)[0]
##
##                                        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],(tvec[0][0][0])/100],
##                                                        [rmtx[1][0],rmtx[1][1],rmtx[1][2],(tvec[0][0][1])/300],
##                                                        [rmtx[2][0],rmtx[2][1],rmtx[2][2],(tvec[0][0][2])/100],
##                                                        [1.0     ,1.0     ,1.0       ,0.0    ]])
##
##                                        view_matrix = view_matrix * INVERSE_MATRIX
##                                        view_matrix = np.transpose(view_matrix)
##                                        glPushMatrix()
##                                        glLoadMatrixd(view_matrix)
##                                        glCallList(waterpitcher.gl_list)
##                                        glPopMatrix()
##                                elif ar_id == ar_list[1][0]:
##                                        centre, rvec, tvec = ar_list[1][1], ar_list[1][2], ar_list[1][3]
##
##                                        rmtx = cv2.Rodrigues(rvec)[0]
##                                        tmtx = cv2.Rodrigues(tvec)[0]
##
##                                        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],(tvec[0][0][0])/100],
##                                                        [rmtx[1][0],rmtx[1][1],rmtx[1][2],(tvec[0][0][1])/300],
##                                                        [rmtx[2][0],rmtx[2][1],rmtx[2][2],(tvec[0][0][2])/100],
##                                                        [1.0     ,1.0     ,1.0       ,0.0    ]])
##
##                                        view_matrix = view_matrix * INVERSE_MATRIX
##                                        view_matrix = np.transpose(view_matrix)
##                                        glPushMatrix()
##                                        glLoadMatrixd(view_matrix)
##                                        glCallList(waterpitcher.gl_list)
##                                        glPopMatrix()
##
##                        elif x[0] == 1:
##                                if ar_id == ar_list[0][0]:
##                                        centre1, rvec1, tvec1 = ar_list[0][1], ar_list[0][2], ar_list[0][3]
##
##                                        rmtx1 = cv2.Rodrigues(rvec1)[0]
##                                        tmtx1 = cv2.Rodrigues(tvec1)[0]
##
##                                        view_matrix1 = np.array([[rmtx1[0][0],rmtx1[0][1],rmtx1[0][2],(tvec1[0][0][0])/100],
##                                                        [rmtx1[1][0],rmtx1[1][1],rmtx1[1][2],(tvec1[0][0][1])/300],
##                                                        [rmtx1[2][0],rmtx1[2][1],rmtx1[2][2],(tvec1[0][0][2])/100],
##                                                        [1.0     ,1.0     ,1.0       ,0.0    ]])
##
##                                        view_matrix1 = view_matrix1 * INVERSE_MATRIX
##                                        view_matrix1 = np.transpose(view_matrix1)
##                                        glPushMatrix()
##                                        glLoadMatrixd(view_matrix1)
##                                        glCallList(crow.gl_list)
##                                        glPopMatrix()
##                                elif ar_id == ar_list[1][0]:
##                                        print(ar_list[1][0])
##                                        centre1, rvec1, tvec1 = ar_list[1][1], ar_list[1][2], ar_list[1][3]
##
##                                        rmtx1 = cv2.Rodrigues(rvec1)[0]
##                                        tmtx1 = cv2.Rodrigues(tvec1)[0]
##
##                                        view_matrix1 = np.array([[rmtx1[0][0],rmtx1[0][1],rmtx1[0][2],(tvec1[0][0][0])/100],
##                                                        [rmtx1[1][0],rmtx1[1][1],rmtx1[1][2],(tvec1[0][0][1])/300],
##                                                        [rmtx1[2][0],rmtx1[2][1],rmtx1[2][2],(tvec1[0][0][2])/100],
##                                                        [1.0     ,1.0     ,1.0       ,0.0    ]])
##
##                                        view_matrix1 = view_matrix1 * INVERSE_MATRIX
##                                        view_matrix1 = np.transpose(view_matrix1)
##                                        glPushMatrix()
##                                        glLoadMatrixd(view_matrix1)
##                                        glCallList(crow.gl_list)
##                                        glPopMatrix()
        #init_object_texture(texture_file)

        ##print(ar_list)
        #glutSolidTeapot(0.5)
        ##for i in ar_list:
           ## if i[0] == 0:
               ## glCallList(waterpitcher.gl_list)
            ##if i[0] == 1:

                ##lPopMatrix()


########################################################################

if __name__ == "__main__":
        main()


