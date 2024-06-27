#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
import pyrr
import numpy as np
from cpe3d import Object3D
from random import randint
from math import atan2

class ViewerGL:
    def __init__(self):
        # initialisation de la librairie GLFW
        glfw.init()
        # paramétrage du context OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # création et paramétrage de la fenêtre
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(1000, 1000, 'OpenGL', None, None)
        """ monitors = glfw.get_monitors()
        screen_size = glfw.get_video_mode(monitors[0]) """
        # paramétrage de la fonction de gestion des évènements
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        # activation du context OpenGL pour la fenêtre
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        # activation de la gestion de la profondeur
        GL.glEnable(GL.GL_DEPTH_TEST)
        # choix de la couleur de fond
        GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

        self.movement = False
        self.sprint = False
        self.turning = False
        self.hitboxList = []
        self.objs = []
        self.touch = {}
        self.bullets_dir = [None for i in range(6)]
        self.NPCs_bullets_dir = [None for i in range(3)]
        self.last_shoot_state = 0
        glfw.set_cursor_pos(self.window, 400, 400)
        self.x_cursor, self.y_cursor = glfw.get_cursor_pos(self.window)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        
        

    def run(self):
        #initialisation de la liste hitboxList
        for i in range(len(self.objs)):
            if self.objs[i].hasHitbox :
                self.hitboxList.append(self.objs[i].hitbox)
        
        
        
        #spawn aleatoire des adversaires
        for i in range(6):
            #parametres pour coordonner les spawn des NPC et déplacement de leur Hitbox
            a1, a2, a3, a4 = randint(25,50), randint(1,2), randint(25,50), randint(1,2)
            self.objs[1 + i].transformation.translation += \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[7].transformation.rotation_euler), 
                                                pyrr.Vector3([a1*((-1)**a2), 0, a3*((-1)**a4)]))
            #mise à jour des hitbox après aparition
            self.hitboxList[1+i][0] += \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[7].transformation.rotation_euler), 
                    pyrr.Vector3([a1*((-1)**a2), 0, a3*((-1)**a4)]))
            self.hitboxList[1 +i][1] += \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[7].transformation.rotation_euler), 
                    pyrr.Vector3([a1*((-1)**a2), 0, a3*((-1)**a4)]))
        
        # spawn des guns de NPCs
        for i in range(3):
            self.objs[8 + i].transformation.translation = self.objs[1 + i].transformation.translation + pyrr.Vector3([-0.3, 1.7, 3])
            
            
        
        #spawn aleatoire d'un contenaire
        """ a1 = randint(10,40)
        a2 = randint(10,40)
        p1 = (-1)**randint(1,2)
        p2 = (-1)**randint(1,2)
        
        self.objs[3].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[3].transformation.rotation_euler), pyrr.Vector3([0, 0, p1*a1]))
        self.objs[4].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[4].transformation.rotation_euler), pyrr.Vector3([0, 0,p1*a1]))
        
        self.objs[3].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[3].transformation.rotation_euler), pyrr.Vector3([p2*a2, 0, 0]))
        self.objs[4].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[4].transformation.rotation_euler), pyrr.Vector3([p2*a2, 0,0])) """
        
        # boucle d'affichage
        while not glfw.window_should_close(self.window):
            # nettoyage de la fenêtre : fond et profondeur
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.update_key()
            self.cursor_camera()

            game_speed = 0.1*self.turning + 0.4*self.movement + 0.5*self.sprint

            for i in range(6):
                if self.objs[11 + i].visible:
                    self.objs[11 + i].transformation.translation += self.bullets_dir[i]*game_speed
                    self.hitboxList[11 + i][0] += self.bullets_dir[i]*game_speed
                    self.hitboxList[11 + i][1] += self.bullets_dir[i]*game_speed
                self.come(game_speed, 1 + i)
            
            for i in range(3):
                if not self.objs[17 + i].visible:
                    self.NPC_shoot(1 + i)
                
                if self.objs[17 + i].visible:
                    self.objs[17 + i].transformation.translation += self.NPCs_bullets_dir[i]*game_speed
                    self.hitboxList[17 + i][0] += self.NPCs_bullets_dir[i]*game_speed
                    self.hitboxList[17 + i][1] += self.NPCs_bullets_dir[i]*game_speed

            for obj in self.objs:
                GL.glUseProgram(obj.program)
                if isinstance(obj, Object3D):
                    self.update_camera(obj.program)
                obj.draw()
            
            
            self.colision_management()
            
            # changement de buffer d'affichage pour éviter un effet de scintillement
            glfw.swap_buffers(self.window)
            # gestion des évènements
            glfw.poll_events()
    

    def cursor_camera(self):
        self.turning = False
        x, y = glfw.get_cursor_pos(self.window)
        dx = (x - self.x_cursor)
        dy = (y - self.y_cursor)
        self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += dx/500
        self.cam.transformation.rotation_euler[pyrr.euler.index().roll] += dy/500
        self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw] += dx/500
        # self.objs[1].transformation.rotation_euler[pyrr.euler.index().yaw] += dx/500
        # vec_rota = [dx/500, dy/500, 0]
        # rot = pyrr.matrix44.create_from_eulers(vec_rota)
        # self.objs[1].transformation.rotation_euler = pyrr.matrix44.multiply(self.objs[1].transformation.rotation_euler, rot)
        alpha = self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw]

        self.objs[7].transformation.rotation_euler[pyrr.euler.index().yaw] += dx/500
        #self.objs[7].transformation.rotation_euler[pyrr.euler.index().roll] += (-dy/500)*np.cos(alpha)
        #self.objs[7].transformation.rotation_euler[pyrr.euler.index().pitch] += (-dy/500)*np.sin(alpha)
        self.objs[7].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), 
                                              pyrr.Vector3([np.sin(dx/500)*3, np.sin(dy/500)*3, -6 + (np.cos(dx/500) + np.cos(dy/500))*3]))
        self.x_cursor, self.y_cursor = x, y
        if dx != 0 or dy != 0:
            self.turning = True

    # methode gérant les colision entre deux hitbox
    def hitbox_interaction(self,hb1,hb2):
        x1_min, y1_min, z1_min = hb1[0][0], hb1[0][1], hb1[0][2] 
        x1_max, y1_max, z1_max = hb1[1][0], hb1[1][1], hb1[1][2]
        
        x2_min, y2_min, z2_min = hb2[0][0], hb2[0][1], hb2[0][2] 
        x2_max, y2_max, z2_max = hb2[1][0], hb2[1][1], hb2[1][2]
        
        return not (x1_max < x2_min or  
                        x1_min > x2_max or  
                        y1_max < y2_min or  
                        y1_min > y2_max or  
                        z1_max < z2_min or  
                        z1_min > z2_max)
    
    # gestion generale des colision 
    def colision_management(self):
        #interraction NPC / PC:
        for i in range(6):
            hb1, hb2 = self.hitboxList[0], self.hitboxList[i+1]
            
            if self.hitbox_interaction(hb1, hb2):
                print("colision NPC / PC")
        
        #interraction balles / NPC
        for i in range(4):
            hb1 = self.hitboxList[i + 11]
            for i in range(6):
                hb2 = self.hitboxList[i + 1] 
                if self.hitbox_interaction(hb1, hb2):
                    print("Beau Tir BG")
        
        #interraction PC / Map
        hb1 = self.hitboxList[0]
        if  hb1[0][0] > 50 or hb1[0][0] < -50 or hb1[0][2] > 50 or hb1[0][2] < -50 :
            print("dehors")
    
    def key_callback(self, win, key, scancode, action, mods):
        # sortie du programme si appui sur la touche 'échappement'
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)
        self.touch[key] = action
    
    def mouse_button_callback(self, win, button, action, mods):
        self.touch[button] = action
    
    def add_object(self, obj):
        self.objs.append(obj)

    def set_camera(self, cam):
        self.cam = cam

    def update_camera(self, prog):
        GL.glUseProgram(prog)
        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "translation_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_view")
        # Modifie la variable pour le programme courant
        translation = -self.cam.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_view")
        # Modifie la variable pour le programme courant
        rotation_center = self.cam.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(-self.cam.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)
    
        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1) :
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.cam.projection)


    def player_shoot(self):
        first_usable_bullet_adress = 0
        for i in range(6):
            if not self.objs[16 - i].visible:
                first_usable_bullet_adress = 16 - i

        if first_usable_bullet_adress != 0:
            self.objs[first_usable_bullet_adress].visible = True
            self.objs[first_usable_bullet_adress].transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.6, 4])
            

            """ problème ici : il faudrait que les hitbox soient cohérentes avec les positions """
            #self.hitboxList[first_usable_bullet_adress][0] += self.objs[0].transformation.translation + pyrr.Vector3([0, 1.6, 4])
            #self.hitboxList[first_usable_bullet_adress][1] += self.objs[0].transformation.translation + pyrr.Vector3([0, 1.6, 4])
            
            
            alpha = self.objs[0].transformation.rotation_euler[pyrr.euler.index().yaw]
            beta = self.cam.transformation.rotation_euler[pyrr.euler.index().roll]
            self.objs[first_usable_bullet_adress].transformation.translation -= \
                    pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), 
                                                pyrr.Vector3([np.sin(alpha)*4, np.sin(beta)*4, -4 + np.cos(alpha)*4]))
            
            self.hitboxList[first_usable_bullet_adress][0] -= pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), 
                                                pyrr.Vector3([np.sin(alpha)*4, np.sin(beta)*4, -4 + np.cos(alpha)*4])) 
            self.hitboxList[first_usable_bullet_adress][1] -= pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), 
                                                pyrr.Vector3([np.sin(alpha)*4, np.sin(beta)*4, -4 + np.cos(alpha)*4])) 
            
            self.bullets_dir[first_usable_bullet_adress - 11] = pyrr.Vector3([-np.sin(alpha), -np.sin(beta), np.cos(alpha)])
    
    def NPC_shoot(self, NPC_id):
        NPC_bullet_adress = NPC_id + 16

        self.objs[NPC_bullet_adress].visible = True
        alpha = self.objs[NPC_id].transformation.rotation_euler[pyrr.euler.index().yaw]
        self.objs[NPC_bullet_adress].transformation.translation = self.objs[NPC_id].transformation.translation + pyrr.Vector3([-2*np.sin(alpha), 1, 2*np.cos(alpha)])
        
        self.hitboxList[NPC_bullet_adress][0] += self.objs[NPC_id].transformation.translation + pyrr.Vector3([-2*np.sin(alpha), 1, 2*np.cos(alpha)])
        self.hitboxList[NPC_bullet_adress][1] += self.objs[NPC_id].transformation.translation + pyrr.Vector3([-2*np.sin(alpha), 1, 2*np.cos(alpha)])
        
        self.NPCs_bullets_dir[NPC_bullet_adress - 17] = pyrr.Vector3([-np.sin(alpha), 0, np.cos(alpha)])
    
    #methode permettant de faire venir les NPC
    def come(self, game_speed, NPC_id):
        p0 = self.objs[0].transformation.translation
        p1 = self.objs[NPC_id].transformation.translation
        dir = p0-p1
        dir.y = 0
        dir = pyrr.vector3.normalise(dir)
        theta = atan2(dir[2], dir[0])
        self.objs[NPC_id].transformation.rotation_euler[pyrr.euler.index().yaw] = theta - np.pi/2
        if NPC_id < 4:
            self.objs[7 + NPC_id].transformation.rotation_euler[pyrr.euler.index().yaw] = theta + np.pi
            alpha = theta - np.pi/2
            self.objs[7 + NPC_id].transformation.translation = self.objs[NPC_id].transformation.translation + pyrr.Vector3([-2*np.sin(alpha), 1, 2*np.cos(alpha)])
        p1 += 0.05*dir*game_speed
        self.hitboxList[NPC_id][0] += 0.05*dir*game_speed
        self.hitboxList[NPC_id][1] += 0.05*dir*game_speed
        
    # Methode permettant de se deplacer
    def update_key(self):
        self.character_speed = 0.1
        self.movement = False
        self.sprint = False
        is_sprinting = False
        
        if glfw.KEY_LEFT_SHIFT in self.touch and self.touch[glfw.KEY_LEFT_SHIFT] > 0:
            self.character_speed = 0.2
            is_sprinting = True
        
        if glfw.KEY_W in self.touch and self.touch[glfw.KEY_W] > 0:
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            
            self.hitboxList[0][0] += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.hitboxList[0][1] += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            
            self.objs[7].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])
            self.movement = True
            
            if is_sprinting:
                self.sprint = True

        if glfw.KEY_S in self.touch and self.touch[glfw.KEY_S] > 0:
            self.objs[0].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            
            self.hitboxList[0][0] -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.hitboxList[0][1] -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))

            self.objs[7].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])
            self.movement = True
            if is_sprinting:
                self.sprint = True
        
        if glfw.KEY_N in self.touch and self.touch[glfw.KEY_N] > 0:
           print(self.hitboxList[0])
           """print(self.hitboxList[11])
           print(self.hitboxList[12])
           print(self.hitboxList[13])
           print(self.hitboxList[14])
           print(self.hitboxList[15])
           print(self.hitboxList[16])
           print(self.hitboxList[1])
           print(self.hitboxList[2])
           print(self.hitboxList[3])
           print(self.hitboxList[4])
           print(self.hitboxList[5])
           print(self.hitboxList[6])"""
           print("**********************************************************************")


        if glfw.KEY_A in self.touch and self.touch[glfw.KEY_A] > 0:
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            
            self.hitboxList[0][0] += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.hitboxList[0][1] += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            
            
            self.objs[7].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])
            self.movement = True
            if is_sprinting:
                self.sprint = True

        if glfw.KEY_D in self.touch and self.touch[glfw.KEY_D] > 0:
            self.objs[0].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            
            self.hitboxList[0][0] -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.hitboxList[0][1] -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            
            self.objs[7].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])
            self.movement = True
            if is_sprinting:
                self.sprint = True
            
        
        if glfw.KEY_SPACE in self.touch and self.touch[glfw.KEY_SPACE] > 0:
            self.cam.transformation.rotation_euler = self.objs[0].transformation.rotation_euler.copy() 
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 0.5, -0.8])
        
        if glfw.MOUSE_BUTTON_LEFT in self.touch and self.touch[glfw.MOUSE_BUTTON_LEFT] > 0 and self.last_shoot_state == 0:
            self.player_shoot()
            #print(self.hitboxList)
        if glfw.MOUSE_BUTTON_LEFT in self.touch:    
            self.last_shoot_state = self.touch[glfw.MOUSE_BUTTON_LEFT]
            
       
        
