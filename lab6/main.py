import time
import matplotlib

try:
    matplotlib.use('TkAgg')
except:
    pass

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Polygon as Poly2D


class SolidZ:
    def __init__(self):
        z_xy = np.array([
            [0, 0],   
            [4, 0],   
            [4, 1],   
            [1, 4],   
            [4, 4],   
            [4, 5],   
            [0, 5],   
            [0, 4],   
            [3, 1],   
            [0, 1],   
        ])

        z_front = 1.0
        z_back = 0.0
        num_points = len(z_xy)

        self.vertices = np.zeros((num_points * 2, 4))

        for i in range(num_points):
            self.vertices[i] = [z_xy[i][0], z_xy[i][1], z_back, 1]
            self.vertices[i + num_points] = [z_xy[i][0], z_xy[i][1], z_front, 1]

        self.vertices = self.vertices.T

        self.faces = []
        self.faces.append(list(range(num_points)))                 
        self.faces.append(list(range(num_points, 2 * num_points))) 

        contour_indices = list(range(num_points)) + [0]
        for i in range(num_points):
            idx1 = contour_indices[i]
            idx2 = contour_indices[i + 1]
            self.faces.append([idx1, idx2, idx2 + num_points, idx1 + num_points])

        self.edges = []
        for face in self.faces:
            for i in range(len(face)):
                self.edges.append((face[i], face[(i + 1) % len(face)]))

    def get_translation_matrix(self, dx, dy, dz):
        return np.array([[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]])

    def get_scaling_matrix(self, sx, sy, sz):
        return np.array([[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]])

    def get_rotation_matrix(self, axis, theta_degrees):
        theta = np.radians(theta_degrees)
        axis = np.array(axis) / np.linalg.norm(axis)
        u_x, u_y, u_z = axis
        c, s = np.cos(theta), np.sin(theta)
        t = 1 - c
        return np.array(
            [
                [t * u_x**2 + c, t * u_x * u_y - s * u_z, t * u_x * u_z + s * u_y, 0],
                [t * u_x * u_y + s * u_z, t * u_y**2 + c, t * u_y * u_z - s * u_x, 0],
                [t * u_x * u_z - s * u_y, t * u_y * u_z + s * u_x, t * u_z**2 + c, 0],
                [0, 0, 0, 1],
            ]
        )

    def transform(self, matrix):
        self.vertices = np.dot(matrix, self.vertices)


def generate_solid_Z():
    solid_z = SolidZ()
    
    vertices_homog = solid_z.vertices
    
    center_x = (np.max(vertices_homog[0, :]) + np.min(vertices_homog[0, :])) / 2
    center_y = (np.max(vertices_homog[1, :]) + np.min(vertices_homog[1, :])) / 2
    center_z = (np.max(vertices_homog[2, :]) + np.min(vertices_homog[2, :])) / 2
    
    scale = 0.2  
    T_center = solid_z.get_translation_matrix(-center_x, -center_y, -center_z)
    S = solid_z.get_scaling_matrix(scale, scale, scale * 0.5)  
    M_init = np.dot(S, T_center)
    
    solid_z.transform(M_init)
    
    faces = solid_z.faces
    
    return solid_z.vertices, faces


def get_matrix(tx, ty, tz, s, rx, ry, rz):
    S = np.array([[s, 0, 0, 0], [0, s, 0, 0], [0, 0, s, 0], [0, 0, 0, 1]])
    T = np.array([[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]])
    Rx = np.array([[1, 0, 0, 0], [0, np.cos(rx), -np.sin(rx), 0], [0, np.sin(rx), np.cos(rx), 0], [0, 0, 0, 1]])
    Ry = np.array([[np.cos(ry), 0, np.sin(ry), 0], [0, 1, 0, 0], [-np.sin(ry), 0, np.cos(ry), 0], [0, 0, 0, 1]])
    Rz = np.array([[np.cos(rz), -np.sin(rz), 0, 0], [np.sin(rz), np.cos(rz), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    return T @ Rz @ Ry @ Rx @ S


def plot_solid_2d(ax, transformed_verts, faces, view_dims):
    dx, dy, dz = view_dims

    polygons = []
    for face in faces:
        pts = transformed_verts[:3, face].T

        depth = np.mean(pts[:, dz])

        poly_2d = pts[:, [dx, dy]]
        polygons.append((depth, poly_2d))

    polygons.sort(key=lambda x: x[0])

    ax.clear()
    
    patches = []
    for depth, poly_coords in polygons:
        if len(poly_coords) >= 3:
            polygon = Poly2D(poly_coords, closed=True,
                             facecolor='pink', edgecolor='black', linewidth=0.5, alpha=0.9)
            ax.add_patch(polygon)
    
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.grid(True, linestyle='--')
    ax.set_aspect('equal')
    
    return ax


base_verts, faces = generate_solid_Z()
rot_state = {'rx': 0.0, 'ry': 0.0, 'last_x': 0, 'last_y': 0, 'dragging': False}
fig = plt.figure(figsize=(14, 9))
plt.subplots_adjust(left=0.05, bottom=0.05, right=0.75, top=0.90, wspace=0.3, hspace=0.3)

ax_3d = fig.add_subplot(2, 2, 1, projection='3d')
ax_xy = fig.add_subplot(2, 2, 2)  
ax_xz = fig.add_subplot(2, 2, 3)  
ax_yz = fig.add_subplot(2, 2, 4)  

for ax, title, xlbl, ylbl in zip(
        [ax_xy, ax_xz, ax_yz],
        ["Oxy: Вид Сверху (Top)", "Oxz: Вид Спереди (Front)", "Oyz: Вид Сбоку (Side)"],
        ['X', 'X', 'Y'], ['Y', 'Z', 'Z']
):
    ax.set_title(title, fontweight='bold')
    ax.set_xlabel(xlbl)
    ax.set_ylabel(ylbl)
    ax.grid(True, linestyle='--')
    ax.set_aspect('equal')
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)

ax_3d.set_title("3D Буква Z (Твердотельная)", color='blue', fontweight='bold')
try:
    ax_3d.disable_mouse_rotation()
except:
    pass

ax_text = plt.axes([0.77, 0.05, 0.2, 0.35])
ax_text.axis('off')
txt_matrix = ax_text.text(0, 1, "", family='monospace', fontsize=9, va='top')

ax_s = plt.axes([0.8, 0.85, 0.15, 0.02])
ax_tx = plt.axes([0.8, 0.80, 0.15, 0.02])
ax_ty = plt.axes([0.8, 0.75, 0.15, 0.02])
ax_tz = plt.axes([0.8, 0.70, 0.15, 0.02])

sli_s = Slider(ax_s, 'Масштаб', 0.1, 4.0, valinit=2.5)
sli_tx = Slider(ax_tx, 'X', -3.0, 3.0, valinit=0.0)
sli_ty = Slider(ax_ty, 'Y', -3.0, 3.0, valinit=0.0)
sli_tz = Slider(ax_tz, 'Z', -3.0, 3.0, valinit=0.0)

last_update_time = 0
update_interval = 3

def update_draw(force=False):
    global last_update_time 
    now = time.time() 
    if not force and (now - last_update_time < update_interval): 
        return 
    last_update_time = now 
    M = get_matrix(sli_tx.val, sli_ty.val, sli_tz.val, sli_s.val, rot_state['rx'], rot_state['ry'], 0) 
    transformed = M @ base_verts

    ax_3d.clear()
    ax_3d.set_xlim(-2, 2)
    ax_3d.set_ylim(-2, 2)
    ax_3d.set_zlim(-2, 2)
    ax_3d.set_xlabel('X')
    ax_3d.set_ylabel('Y')
    ax_3d.set_zlabel('Z')
    ax_3d.xaxis.set_tick_params(pad=1)
    ax_3d.yaxis.set_tick_params(pad=1)
    ax_3d.zaxis.set_tick_params(pad=1)

    ax_3d.set_title("3D буква Z")
    
    ax_3d.plot([-0.8, 4], [0, 0], [-0.2, -0.2], color='red', linewidth=2)
    ax_3d.text(4.0, 0, -0.2, 'X', color='red', fontsize=12)
    
    ax_3d.plot([-0.7, -0.7], [-0.1, 4], [0, 0], color='green', linewidth=2)
    ax_3d.text(-0.7, 4.1, 0, 'Y', color='green', fontsize=12)
    
    ax_3d.plot([-0.8, -0.8], [0, 0], [-0.2, 4], color='blue', linewidth=2)
    ax_3d.text(-0.7, 0, 4, 'Z', color='blue', fontsize=12)

    verts_3d = []
    for face in faces:
        verts_3d.append(transformed[:3, face].T)

    poly_3d = Poly3DCollection(verts_3d, facecolors='pink', edgecolors='k', linewidths=0.5, alpha=0.8)
    ax_3d.add_collection3d(poly_3d)

    plot_solid_2d(ax_xy, transformed, faces, (0, 1, 2))
    ax_xy.set_title("Oxy: вид сверху")
    ax_xy.set_xlabel('X')
    ax_xy.set_ylabel('Y')

    plot_solid_2d(ax_xz, transformed, faces, (0, 2, 1))
    ax_xz.set_title("Oxz: вид спереди")
    ax_xz.set_xlabel('X')
    ax_xz.set_ylabel('Z')

    plot_solid_2d(ax_yz, transformed, faces, (1, 2, 0))
    ax_yz.set_title("Oyz: вид сбоку")
    ax_yz.set_xlabel('Y')
    ax_yz.set_ylabel('Z')

    txt_matrix.set_text(f"MATRIX:\n{np.round(M, 2)}")
    fig.canvas.draw_idle()

def on_press(event):
    if event.inaxes == ax_3d:
        rot_state['dragging'] = True
        rot_state['last_x'] = event.x
        rot_state['last_y'] = event.y


def on_release(event):
    rot_state['dragging'] = False

def on_motion(event):
    if rot_state['dragging'] and event.inaxes == ax_3d:
        dx = event.x - rot_state['last_x']
        dy = event.y - rot_state['last_y']
        rot_state['ry'] += dx * 0.01
        rot_state['rx'] -= dy * 0.01
        rot_state['last_x'] = event.x
        rot_state['last_y'] = event.y
        update_draw() 
        
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

for s in [sli_s, sli_tx, sli_ty, sli_tz]:
    s.on_changed(lambda v: update_draw())

update_draw()
plt.show()
