import sys

import open3d as o3d
import smplx
import torch
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QLabel, QDoubleSpinBox


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.beta = torch.zeros((1, 10), dtype=torch.float32)
        self.init_ui()

        # smpl
        self.model = smplx.create("models")

        # open3d
        self.mesh = o3d.geometry.TriangleMesh()
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="SMPL-Demo", width=1920, height=1080)
        self.update_o3d()

    def init_ui(self):
        self.setWindowTitle("SMPL Viewer")
        h_layout = QVBoxLayout()
        for i in range(10):
            v_layout = QHBoxLayout()

            label = QLabel(f"Beta{i}:")
            v_layout.addWidget(label)

            box = QDoubleSpinBox()
            box.setRange(-10.0, 10.0)
            box.setSingleStep(1.0)
            box.setValue(0)
            box.setObjectName(str(i))
            box.valueChanged.connect(self.value_changed)
            v_layout.addWidget(box)

            h_layout.addLayout(v_layout)

        widget = QWidget()
        widget.setLayout(h_layout)
        self.setCentralWidget(widget)

    def value_changed(self, value):
        self.beta[0, int(self.sender().objectName())] = value
        self.update_o3d()

    def update_o3d(self):
        with torch.no_grad():
            output = self.model(betas=self.beta, return_verts=True)
        vertices = output.vertices.detach().cpu().numpy().squeeze()
        self.vis.remove_geometry(self.mesh)
        self.mesh.vertices = o3d.utility.Vector3dVector(vertices)
        self.mesh.triangles = o3d.utility.Vector3iVector(self.model.faces)
        self.mesh.compute_vertex_normals()
        self.mesh.paint_uniform_color([0.3, 0.3, 0.3])
        self.vis.add_geometry(self.mesh)
        # self.vis.update_geometry(self.mesh)
        self.vis.poll_events()
        self.vis.update_renderer()


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
