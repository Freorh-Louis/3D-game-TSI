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

    # Playable character
    m = Mesh.load_obj('male.obj')
    m.normalize()
    m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
    tr = Transformation3D()
    tr.translation.y = -np.amin(m.vertices, axis=0)[1]
    tr.translation.z = -2
    tr.rotation_center.z = 0.2
    texture = glutils.load_texture('white.jpg')
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr, True, m.hitbox())
    viewer.add_object(o)
    viewer.objs[0].visible = False

    # NPCs
    texture = glutils.load_texture('red.jpg')
    for i in range(6):
        tr = Transformation3D()
        tr.translation.y = -np.amin(m.vertices, axis=0)[1]
        tr.translation.z = -2
        tr.rotation_center.z = 0.2
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr,True, m.hitbox())
        viewer.add_object(o)

    # Guns
    m = Mesh.load_obj('Gun.obj')
    m.normalize()
    m.apply_matrix(pyrr.matrix44.create_from_scale([1, 1, 1, 0.5]))
    texture = glutils.load_texture('Gun.png')
    for i in range(4):
        tr = Transformation3D()
        tr.translation.y = -np.amin(m.vertices, axis=0)[1]
        tr.translation.z = -2
        tr.rotation_center.z = 0.2
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr, True, 0)
        viewer.add_object(o)
    viewer.objs[7].transformation.translation = viewer.objs[7].transformation.translation + pyrr.Vector3([-0.3, 1.7, 3])
    viewer.objs[7].transformation.rotation_euler[pyrr.euler.index().yaw] -= np.pi/2

    # Player bullets
    m = Mesh.load_obj('Sphere.obj')
    m.normalize()
    m.hitbox()
    m.apply_matrix(pyrr.matrix44.create_from_scale([0.1, 0.1, 0.1, 0.05]))
    texture = glutils.load_texture('green.png')
    for i in range(6):
        tr = Transformation3D()
        tr.translation.y = -np.amin(m.vertices, axis=0)[1]
        tr.translation.z = -2
        tr.rotation_center.z = 0.2
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr, True, m.hitbox())
        viewer.add_object(o)
        viewer.objs[11 + i].visible = False
        
    # NPCs bullets
    texture = glutils.load_texture('red1.jpg')
    for i in range(3):
        tr = Transformation3D()
        tr.translation.y = -np.amin(m.vertices, axis=0)[1]
        tr.translation.z = -2
        tr.rotation_center.z = 0.2
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr,True, m.hitbox())
        viewer.add_object(o)
        viewer.objs[17 + i].visible = False

    

    # Container
    m = Mesh.load_obj('cube.obj')
    m.normalize()
    m.hitbox()
    m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
    tr = Transformation3D()
    tr.translation.y = -np.amin(m.vertices, axis=0)[1]
    tr.translation.z = -2
    tr.rotation_center.z = 0.2
    texture = glutils.load_texture('container.jpg')
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr,True,m.hitbox())
    viewer.add_object(o)

    # Container
    m = Mesh.load_obj('cube.obj')
    m.normalize()
    m.hitbox()
    m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
    tr = Transformation3D()
    tr.translation.y = -np.amin(m.vertices, axis=0)[1]
    tr.translation.z = -2
    tr.rotation_center.z = 0.2
    texture = glutils.load_texture('container.jpg')
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr,True,m.hitbox())
    viewer.add_object(o)

    viewer.objs[4].transformation.translation = viewer.objs[4].transformation.translation + pyrr.Vector3([0, 0, 5])


    # Map
    # Les mi sont les objets face base/ face sommet/face droite ... du cube qui sert de map
    # on défini dans l'ordre : objet, point, normale, couleur, texture, sommet, face que l'on
    # met dans une liste de parametre pour charger 6 fois un objet "face du cube"
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
                   (p0 + ng + c + t0), (p3 + ng + c + t1), (p7 + ng + c + t2),(p4 + ng + c + t3),
                   (p2 + nd + c + t0), (p1 + nd + c + t1), (p5 + nd + c + t2), (p6 + nd + c + t3),
                   (p2 + na + c + t0), (p3 + na + c + t1), (p7 + na + c + t2), (p6 + na + c + t3)]
    
    texture = glutils.load_texture('concrete.jpg')
    
    #boucle d'affichage des faces du cube
    for i in range(6):
        m.vertices = np.array([liste_param[4*i],liste_param[4*i+1],liste_param[4*i+2],liste_param[4*i+3]], np.float32)
        m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, Transformation3D(), False, 0)
        viewer.add_object(o)
    

    
    vao = Text.initalize_geometry()
    texture = glutils.load_texture('fontB.jpg')
    o = Text('.', np.array([-0.05, -0.05], np.float32), np.array([0.05, 0.05], np.float32), vao, 2, programGUI_id, texture,False,0) 
    viewer.add_object(o)

    # Centre la caméra sur le joueur au début
    viewer.cam.transformation.rotation_euler = viewer.objs[0].transformation.rotation_euler.copy() 
    viewer.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
    viewer.cam.transformation.rotation_center = viewer.objs[0].transformation.translation + viewer.objs[0].transformation.rotation_center
    viewer.cam.transformation.translation = viewer.objs[0].transformation.translation + pyrr.Vector3([0, 1.7, -0.4])
    
    viewer.run()

def new_func(program3d_id):
    return program3d_id


if __name__ == '__main__':
    main()