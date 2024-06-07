from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Text
import numpy as np
import OpenGL.GL as GL
import pyrr

def main():
    viewer = ViewerGL()

    viewer.set_camera(Camera())
    viewer.cam.transformation.rotation_center = viewer.cam.transformation.translation.copy()

    program3d_id = glutils.create_program_from_file('shader.vert', 'shader.frag')
    programGUI_id = glutils.create_program_from_file('gui.vert', 'gui.frag')

    m = Mesh.load_obj('stegosaurus.obj')
    m.normalize()
    m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
    tr = Transformation3D()
    tr.translation.y = -np.amin(m.vertices, axis=0)[1]
    tr.translation.z = -2
    tr.rotation_center.z = 0.2
    texture = glutils.load_texture('white.jpg')
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr)
    viewer.add_object(o)

    # Les mi sont les objets face base/ face sommet/face droite ... du cube qui sert de map
    # on défini dans l'ordre : objet, point, normale, couleur, texture, sommet, face que l'on
    # met dans une liste de paramètre pour charger 6 fois un objet "face du cube"
    
    # appel de l'objet
    m = Mesh()
    
    #points du cube
    p0, p1, p2, p3 = [-50, 0, -50], [50, 0, -50], [50, 0, 50], [-50, 0, 50]
    p4, p5, p6, p7 = [-50, 50, -50], [50, 50, -50], [50, 50, 50], [-50, 50, 50]
    
    #normales et couleur
    n, c = [0, 1, 0], [1,1,1]
    ns = [0,-1,0]
    nf = [0,0,1]
    ng = [1,0,0]
    nd = [0,-1,0]
    na = [0,0,-1]
    #texture
    t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
    liste_param = [(p0 + n + c + t0), (p1 + n + c + t1), (p2 + n + c + t2), (p3 + n + c + t3),
                   (p4 + ns + c + t0), (p5 + ns + c + t1), (p6 + ns + c + t2), (p7 + ns + c + t3),
                   (p0 + nf + c + t0), (p1 + nf + c + t1),(p5 + nf + c + t2),(p4 + nf + c + t3),
                   (p0 + ng + c + t0),(p3 + ng + c + t1), (p7 + ng + c + t2),(p4 + ng + c + t3),
                   (p2 + nd + c + t0), (p1 + nd + c + t1), (p5 + nd + c + t2), (p6 + nd + c + t3),
                   (p2 + na + c + t0), (p3 + na + c + t1), (p7 + na + c + t2), (p6 + na + c + t3)]
    
    texture = glutils.load_texture('grass.jpg')
    print(liste_param[2])
    for i in range(6):

        #sommets
        m.vertices = np.array([liste_param[i],liste_param[i+1] ,liste_param[i+2] , liste_param[i+3], np.float32])
        #faces
        m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
        #declaration de l'objet 3D
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, Transformation3D())
        
        #ajout de l'objet 3D
        viewer.add_object(o)
    

    
    vao = Text.initalize_geometry()
    texture = glutils.load_texture('fontB.jpg')
    o = Text('Bonjour les', np.array([-0.8, 0.3], np.float32), np.array([0.8, 0.8], np.float32), vao, 2, programGUI_id, texture)
    viewer.add_object(o)
    o = Text('3ETI', np.array([-0.5, -0.2], np.float32), np.array([0.5, 0.3], np.float32), vao, 2, programGUI_id, texture)
    viewer.add_object(o)


    viewer.cam.transformation.rotation_euler = viewer.objs[0].transformation.rotation_euler.copy() 
    viewer.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
    viewer.cam.transformation.rotation_center = viewer.objs[0].transformation.translation + viewer.objs[0].transformation.rotation_center
    viewer.cam.transformation.translation = viewer.objs[0].transformation.translation + pyrr.Vector3([0, 0.5, -5])

    viewer.run()


if __name__ == '__main__':
    main()