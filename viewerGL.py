#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
import pyrr
import numpy as np
from cpe3d import Object3D
from random import randint

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
        self.window = glfw.create_window(800, 800, 'OpenGL', None, None)
        """ monitors = glfw.get_monitors()
        screen_size = glfw.get_video_mode(monitors[0]) """
        # paramétrage de la fonction de gestion des évènements
        glfw.set_key_callback(self.window, self.key_callback)
        # activation du context OpenGL pour la fenêtre
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        # activation de la gestion de la profondeur
        GL.glEnable(GL.GL_DEPTH_TEST)
        # choix de la couleur de fond
        GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

        self.objs = []
        self.touch = {}
        glfw.set_cursor_pos(self.window, 400, 400)
        self.x_cursor, self.y_cursor = glfw.get_cursor_pos(self.window)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def run(self):
        #spawn aleatoire d'UN adversaire
        self.objs[2].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[1].transformation.rotation_euler), pyrr.Vector3([0, 0, randint(25,50)*((-1)**randint(1,2))]))
        
        self.objs[2].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[1].transformation.rotation_euler), pyrr.Vector3([randint(25,50)*((-1)**randint(1,2)), 0, 0]))
        
        # boucle d'affichage
        while not glfw.window_should_close(self.window):
            # nettoyage de la fenêtre : fond et profondeur
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.update_key()
            
            self.cursor_camera()

            for obj in self.objs:
                GL.glUseProgram(obj.program)
                if isinstance(obj, Object3D):
                    self.update_camera(obj.program)
                obj.draw()
            
        

            # changement de buffer d'affichage pour éviter un effet de scintillement
            glfw.swap_buffers(self.window)
            # gestion des évènements
            glfw.poll_events()
    

    def cursor_camera(self):
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
        self.objs[1].transformation.rotation_euler[pyrr.euler.index().yaw] += dx/500
        self.objs[1].transformation.rotation_euler[pyrr.euler.index().roll] += (-dy/500)*np.cos(alpha)
        self.objs[1].transformation.rotation_euler[pyrr.euler.index().pitch] += (-dy/500)*np.sin(alpha)
        self.objs[1].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), 
                                              pyrr.Vector3([np.sin(dx/500)*3, np.sin(dy/500)*3, -6 + (np.cos(dx/500) + np.cos(dy/500))*3]))
        self.x_cursor, self.y_cursor = x, y

    



    def key_callback(self, win, key, scancode, action, mods):
        # sortie du programme si appui sur la touche 'échappement'
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)
        self.touch[key] = action
    
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

    def update_key(self):
        self.character_speed = 0.1
        if glfw.KEY_LEFT_SHIFT in self.touch and self.touch[glfw.KEY_LEFT_SHIFT] > 0:
            self.character_speed = 0.3
        
        if glfw.KEY_W in self.touch and self.touch[glfw.KEY_W] > 0:
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.objs[1].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])

        if glfw.KEY_S in self.touch and self.touch[glfw.KEY_S] > 0:
            self.objs[0].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.objs[1].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, self.character_speed]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])

        if glfw.KEY_A in self.touch and self.touch[glfw.KEY_A] > 0:
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.objs[1].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])

        if glfw.KEY_D in self.touch and self.touch[glfw.KEY_D] > 0:
            self.objs[0].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.objs[1].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([self.character_speed, 0, 0]))
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])
        

        if glfw.KEY_I in self.touch and self.touch[glfw.KEY_I] > 0:
            self.objs[1].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[2].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.2]))
        if glfw.KEY_K in self.touch and self.touch[glfw.KEY_K] > 0:
            self.objs[1].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[2].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.2]))
        if glfw.KEY_J in self.touch and self.touch[glfw.KEY_J] > 0:
             self.objs[1].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[2].transformation.rotation_euler), pyrr.Vector3([0.2, 0, 0]))
        if glfw.KEY_L in self.touch and self.touch[glfw.KEY_L] > 0:
            self.objs[1].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[2].transformation.rotation_euler), pyrr.Vector3([0.2, 0, 0]))
        if glfw.KEY_O in self.touch and self.touch[glfw.KEY_O] > 0:
            self.objs[1].transformation.rotation_euler[pyrr.euler.index().yaw] -= 0.1
        
        if glfw.KEY_SPACE in self.touch and self.touch[glfw.KEY_SPACE] > 0:
            self.cam.transformation.rotation_euler = self.objs[0].transformation.rotation_euler.copy() 
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 0.5, -0.8])
            