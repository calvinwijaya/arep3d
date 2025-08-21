from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox,
    QLineEdit, QTextEdit, QSlider, QSpinBox, QDoubleSpinBox, QGroupBox, QSizePolicy,
    QDialog, QApplication, QScrollArea,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
import os
import subprocess
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingCore import vtkRenderer
import json
import vtk

class Worker(QThread):
    finished = pyqtSignal(bool, str)   # sukses/gagal + pesan log

    def __init__(self, fp, pc, out_dir):
        super().__init__()
        self.fp = fp
        self.pc = pc
        self.out_dir = out_dir

    def run(self):
        import subprocess, os

        cmd1 = [
            "geof", "./reconstruct_.json",
            f"--input_footprint={self.fp}",
            f"--input_pointcloud={self.pc}",
            f"--output_cityjson={self.out_dir}/model.json",
            f"--output_obj_lod12={self.out_dir}/model_lod12.obj",
            f"--output_obj_lod13={self.out_dir}/model_lod13.obj",
            f"--output_obj_lod22={self.out_dir}/model_lod22.obj",
            f"--output_vector2d={self.out_dir}/model_2d.gpkg"
        ]
        cmd2 = [
            "geof", "./reconstruct.json",
            f"--input_footprint={self.fp}",
            f"--input_pointcloud={self.pc}",
            f"--output_cityjson={self.out_dir}/model.json",
            f"--output_obj_lod12={self.out_dir}/model_lod12.obj",
            f"--output_obj_lod13={self.out_dir}/model_lod13.obj",
            f"--output_obj_lod22={self.out_dir}/model_lod22.obj",
            f"--output_vector2d={self.out_dir}/model_2d.gpkg"
        ]

        try:
            result1 = subprocess.run(cmd1, cwd=os.getcwd(), capture_output=True, text=True)
            if result1.returncode != 0:
                self.finished.emit(False, f"Error cmd1:\n{result1.stderr}")
                return

            result2 = subprocess.run(cmd2, cwd=os.getcwd(), capture_output=True, text=True)
            if result2.returncode != 0:
                self.finished.emit(False, f"Error cmd2:\n{result2.stderr}")
                return

            self.finished.emit(True, "Proses rekonstruksi 3D selesai.")
        except Exception as e:
            self.finished.emit(False, f"Exception: {e}")

class ReconstructTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1100)

        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Segoe UI, Arial;
                font-size: 12pt;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px; 
            }
            QLabel {
                color: #333;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                padding: 6px;
                background: white;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003f6b;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                font-family: Consolas, monospace;
                font-size: 10pt;
            }
        """)

        # ===== LEFT PANEL (with scroll) =====
        left_panel_content = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_content)
        left_panel_layout.setSpacing(15)
        left_panel_layout.setContentsMargins(15, 15, 15, 15)

        # ===== Input Building Footprint =====
        self.input_footprint = QLineEdit()
        self.btn_browse_footprint = QPushButton("Browse")
        footprint_group = self._create_input_group(
            "Input Tapak Bangunan",
            "Data tapak bangunan harus memiliki atribut 'fid' sebagai Integer64 dan dalam format Geopackage (*.gpkg) "
            "atau Shapefile (*.shp). Pastikan berisi geometri poligon valid.",
            self.input_footprint,
            self.btn_browse_footprint
        )
        left_panel_layout.addWidget(footprint_group)

        # ===== Input Point Cloud =====
        self.input_pointcloud = QLineEdit()
        self.btn_browse_pointcloud = QPushButton("Browse")
        pc_group = self._create_input_group(
            "Input Point Cloud",
            "Point cloud harus sudah diklasifikasikan menjadi ground (kelas 2) dan building (kelas 6). "
            "Format: *.las atau *.laz.",
            self.input_pointcloud,
            self.btn_browse_pointcloud
        )
        left_panel_layout.addWidget(pc_group)

        # ====== Output Directory =====
        self.output_folder = QLineEdit()
        self.btn_browse_output = QPushButton("Browse")
        out_group = self._create_input_group(
            "Folder Output",
            "Tentukan folder output untuk menyimpan semua file hasil rekonstruksi.",
            self.output_folder,
            self.btn_browse_output
        )
        left_panel_layout.addWidget(out_group)

        # ===== Process Button =====
        self.btn_process = QPushButton("Proses Rekonstruksi")
        self.btn_process.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-size: 14pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
        """)
        left_panel_layout.addWidget(self.btn_process)

        # ===== Log Console =====
        log_group = QGroupBox("Log Console")
        log_layout = QVBoxLayout()
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        log_layout.addWidget(self.log_console)
        log_group.setLayout(log_layout)
        left_panel_layout.addWidget(log_group)

        # ===== Reset Buttons =====
        reset_layout = QHBoxLayout()
        self.btn_reset_view = QPushButton("Reset View")
        self.btn_reset_all = QPushButton("Reset All")
        reset_layout.addWidget(self.btn_reset_view)
        reset_layout.addWidget(self.btn_reset_all)
        left_panel_layout.addLayout(reset_layout)

        # Scroll area for left panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(left_panel_content)

        # ===== VTK =====
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.vtk_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ===== MAIN LAYOUT =====
        main_layout = QHBoxLayout()
        main_layout.addWidget(scroll_area, 1)
        main_layout.addWidget(self.vtk_widget, 2)

        self.setup_vtk()
        self.add_axes()
        self.setLayout(main_layout)

        # Connect
        self.btn_browse_footprint.clicked.connect(self.browse_footprint)
        self.btn_browse_pointcloud.clicked.connect(self.browse_pointcloud)
        self.btn_browse_output.clicked.connect(self.browse_output_folder)
        self.btn_process.clicked.connect(self.run_geoflow)
        self.btn_reset_view.clicked.connect(self.reset_view_top)
        self.btn_reset_all.clicked.connect(self.reset_all)

    def _create_input_group(self, title, description, line_edit, browse_btn):
        group = QGroupBox(title)
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 10)
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        row = QHBoxLayout()
        row.addWidget(line_edit)
        row.addWidget(browse_btn)
        layout.addLayout(row)

        group.setLayout(layout)
        return group

    def _bold_label(self, text):
        label = QLabel(f"<b>{text}</b>")
        return label

    def set_camera_view(self, position, view_up):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(*position)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(*view_up)
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.render_window.Render()

    def reset_view_top(self):
        self.set_camera_view((0, 0, 1), (0, 1, 0))

    def reset_all(self):
        self.input_footprint.clear()
        self.input_pointcloud.clear()
        self.output_folder.clear()
        self.log_console.clear()
        self.renderer.RemoveAllViewProps()
        self.vtk_widget.GetRenderWindow().Render()
        self.log_console.append("🔄 Semua input, log, dan tampilan VTK sudah direset.")

    def browse_footprint(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih GPKG atau SHP File", "", "Vector Files (*.gpkg *.shp)")
        if file_name:
            self.input_footprint.setText(file_name)
            self.log_console.append(f"📁 Tapak bangunan terpilih: {file_name}")

    def browse_pointcloud(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih LAS atau LAZ File", "", "Point Cloud Files (*.las *.laz)")
        if file_name:
            self.input_pointcloud.setText(file_name)
            self.log_console.append(f"📁 Point Cloud terpilih: {file_name}")

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih folder Output")
        if folder:
            self.output_folder.setText(folder)
            self.log_console.append(f"📁 Folder Output terpilih: {folder}")

    def run_geoflow(self):
        fp = self.input_footprint.text()
        pc = self.input_pointcloud.text()
        out_dir = self.output_folder.text()

        if not os.path.exists(fp) or not os.path.exists(pc):
            self.log_console.append("❌ paths tidak valid.")
            return
        
        if not os.path.isdir(out_dir):
            self.log_console.append("❌ folder output tidak valid.")
            return

        self.setEnabled(False)
        self.loading = LoadingDialog(self)
        self.loading.show()

        self.worker = Worker(fp, pc, out_dir)
        self.worker.finished.connect(self.on_process_finished)
        self.worker.start()

    def add_axes(self):
        axes = vtk.vtkAxesActor()
        orientation_marker = vtk.vtkOrientationMarkerWidget()
        orientation_marker.SetOrientationMarker(axes)
        orientation_marker.SetInteractor(self.interactor)
        orientation_marker.SetViewport(0.0, 0.0, 0.2, 0.2)
        orientation_marker.SetEnabled(1)
        orientation_marker.InteractiveOff()
        orientation_marker.SetOutlineColor(0.5, 0.5, 0.5)
        self.orientation_marker_widget = orientation_marker
    
    def setup_vtk(self):
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.render_window = self.vtk_widget.GetRenderWindow()
        self.interactor = self.render_window.GetInteractor()
        self.picker = vtk.vtkPropPicker()

        style = CustomInteractorStyle(self)
        self.interactor.SetInteractorStyle(style)
        self.interactor.Initialize()

    def on_process_finished(self, success, message):
        self.setEnabled(True)
        self.loading.close()
        if success:
            self.log_console.append("✅ " + message)
            QMessageBox.information(self, "Proses selesai", message)
            model_file = os.path.join(self.output_folder.text(), "model.json")
            if os.path.exists(model_file):
                self.load_models(model_file)
                self.log_console.append("✅ Model dimuat di VTK viewer.")
            else:
                self.log_console.append("⚠️ model.json tidak ditemukan dalam folder output.")
        else:
            self.log_console.append("❌ " + message)
            QMessageBox.critical(self, "Proses gagal", message)

    def load_models(self, cityjson_file):
        self.renderer.RemoveAllViewProps()
        with open(cityjson_file, 'r') as f:
            cj = json.load(f)
        transform = cj.get("transform", {})
        scale = transform.get("scale", [1, 1, 1])
        translate = transform.get("translate", [0, 0, 0])
        raw_vertices = cj.get("vertices", [])
        vertices = [
            [
                v[0] * scale[0] + translate[0],
                v[1] * scale[1] + translate[1],
                v[2] * scale[2] + translate[2]
            ]
            for v in raw_vertices
        ]
        points = vtk.vtkPoints()
        for v in vertices:
            points.InsertNextPoint(v)

        polys = vtk.vtkCellArray()
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")

        city_objects = cj.get("CityObjects", {})
        for obj in city_objects.values():
            for geom in obj.get("geometry", []):
                if geom.get("lod") == "2.2" and geom.get("type") == "Solid":
                    semantics = geom.get("semantics", {})
                    values = semantics.get("values", [])
                    surfaces = semantics.get("surfaces", [])

                    for shell_idx, shell in enumerate(geom.get("boundaries", [])):
                        for face_idx, face in enumerate(shell):
                            if isinstance(face[0], list):
                                face = [vid for ring in face for vid in ring]

                            polygon = vtk.vtkPolygon()
                            polygon.GetPointIds().SetNumberOfIds(len(face))
                            for i, vid in enumerate(face):
                                polygon.GetPointIds().SetId(i, vid)
                            polys.InsertNextCell(polygon)

                            # kasih warna default abu2
                            color = [200, 200, 200]
                            if values and shell_idx < len(values) and face_idx < len(values[shell_idx]):
                                idx = values[shell_idx][face_idx]
                                if isinstance(idx, list):
                                    idx = idx[0]
                                if idx is not None and 0 <= idx < len(surfaces):
                                    surf_type = surfaces[idx].get("type", "")
                                    if surf_type == "RoofSurface":
                                        color = [255, 0, 0]
                                    elif surf_type == "WallSurface":
                                        color = [180, 180, 180]
                                    elif surf_type == "GroundSurface":
                                        color = [100, 255, 100]
                            colors.InsertNextTuple3(*color)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(polys)
        polydata.GetCellData().SetScalars(colors)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetScalarModeToUseCellData()
        mapper.ScalarVisibilityOn()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.parent = parent

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(self)
        movie = QMovie("loading.gif")
        label.setMovie(movie)
        movie.start()

        text = QLabel("Memproses, harap tunggu...")
        text.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        text.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(text)

        # center the dialog on parent
        if parent:
            geo = parent.geometry()
            self.setGeometry(geo.center().x() - 100, geo.center().y() - 100, 200, 200)