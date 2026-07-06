from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pyqtgraph as pg


MINI_3D_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
body{margin:0;background:#0d0e10;overflow:hidden;}
canvas{display:block;}
</style>
</head>
<body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d0e10);
var camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 100);
camera.position.set(0, 3, 5);
camera.lookAt(0, 0, 0);
var renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(4,10,5);
scene.add(sun);
scene.add(new THREE.GridHelper(10, 20, 0x1a1e2a, 0x1a1e2a));
var mFrame = new THREE.MeshPhongMaterial({color:0x282828});
var mDark  = new THREE.MeshPhongMaterial({color:0x1a1a1a});
var mOrange= new THREE.MeshPhongMaterial({color:0xff6600});
var mLens  = new THREE.MeshPhongMaterial({color:0x4fc3f7,transparent:true,opacity:0.8});
var drone = new THREE.Group();
var armDeg = [45,135,225,315];
for(var ai=0;ai<4;ai++){
  var arm=new THREE.Mesh(new THREE.BoxGeometry(2.2,0.07,0.12),mFrame);
  arm.rotation.y=armDeg[ai]*Math.PI/180;
  drone.add(arm);
}
drone.add(function(){var m=new THREE.Mesh(new THREE.BoxGeometry(0.7,0.09,0.7),mFrame);return m;}());
var canopyB=new THREE.Mesh(new THREE.BoxGeometry(0.3,0.07,0.26),mFrame);
canopyB.position.set(0,0.07,0.34);drone.add(canopyB);
var canopyT=new THREE.Mesh(new THREE.SphereGeometry(0.17,10,7,0,Math.PI*2,0,Math.PI*0.5),new THREE.MeshPhongMaterial({color:0x222222}));
canopyT.position.set(0,0.09,0.3);drone.add(canopyT);
var lns=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,0.04,14),mLens);
lns.rotation.x=Math.PI/2-0.3;lns.position.set(0,0.09,0.48);drone.add(lns);
var antS=new THREE.Mesh(new THREE.CylinderGeometry(0.012,0.012,0.55,5),new THREE.MeshPhongMaterial({color:0x888888}));
antS.position.set(0.1,0.45,-0.35);drone.add(antS);
var mPos=[{x:0.78,z:0.78,cw:1},{x:-0.78,z:0.78,cw:-1},{x:0.78,z:-0.78,cw:-1},{x:-0.78,z:-0.78,cw:1}];
var props=[];
for(var mi=0;mi<4;mi++){
  var md=mPos[mi];
  var duct=new THREE.Mesh(new THREE.TorusGeometry(0.4,0.055,10,36),mFrame);
  duct.rotation.x=Math.PI/2;duct.position.set(md.x,0.04,md.z);drone.add(duct);
  var motB=new THREE.Mesh(new THREE.CylinderGeometry(0.09,0.09,0.11,12),mDark);
  motB.position.set(md.x,0.05,md.z);drone.add(motB);
  var bell=new THREE.Mesh(new THREE.CylinderGeometry(0.085,0.09,0.08,12),mOrange);
  bell.position.set(md.x,0.13,md.z);drone.add(bell);
  var pg2=new THREE.Group();pg2.position.set(md.x,0.19,md.z);
  for(var bi=0;bi<3;bi++){
    var ba=bi/3*Math.PI*2;
    var bl=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.014,0.08),new THREE.MeshPhongMaterial({color:0x666666,transparent:true,opacity:0.8}));
    bl.position.set(Math.cos(ba)*0.22,0,Math.sin(ba)*0.22);
    bl.rotation.y=ba+Math.PI/2;bl.rotation.x=0.12*md.cw;pg2.add(bl);
  }
  drone.add(pg2);props.push({g:pg2,cw:md.cw});
}
var mLedG=new THREE.MeshPhongMaterial({color:0x00ff44,emissive:0x00ff44,emissiveIntensity:1});
var mLedR=new THREE.MeshPhongMaterial({color:0xff2222,emissive:0xff2222,emissiveIntensity:1});
[{x:0.45,z:0.82},{x:-0.45,z:0.82}].forEach(function(l){var ld=new THREE.Mesh(new THREE.SphereGeometry(0.025,5,4),mLedG);ld.position.set(l.x,0.05,l.z);drone.add(ld);});
[{x:0.45,z:-0.82},{x:-0.45,z:-0.82}].forEach(function(l){var ld=new THREE.Mesh(new THREE.SphereGeometry(0.025,5,4),mLedR);ld.position.set(l.x,0.05,l.z);drone.add(ld);});
scene.add(drone);
var tR=0,tP=0,tY=0,cR=0,cP=0,cY=0;
function updateAttitude(r,p,y){tR=r*Math.PI/180;tP=p*Math.PI/180;tY=y*Math.PI/180;}
var propA=0,lastT=performance.now();
var autoTheta=0;
function animate(){
  requestAnimationFrame(animate);
  var now=performance.now(),dt=Math.min((now-lastT)/1000,0.05);lastT=now;
  var k=1-Math.pow(0.015,dt);
  cR+=(tR-cR)*k;cP+=(tP-cP)*k;cY+=(tY-cY)*k;
  drone.rotation.order='YXZ';drone.rotation.y=cY;drone.rotation.x=cP;drone.rotation.z=-cR;
  propA+=dt*18;
  for(var pi=0;pi<props.length;pi++){props[pi].g.rotation.y=propA*props[pi].cw;}
  autoTheta+=dt*0.2;
  camera.position.x=5*Math.sin(0.6)*Math.sin(autoTheta);
  camera.position.y=5*Math.cos(0.6);
  camera.position.z=5*Math.sin(0.6)*Math.cos(autoTheta);
  camera.lookAt(0,0,0);
  renderer.render(scene,camera);
}
animate();
window.addEventListener('resize',function(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});
</script>
</body>
</html>"""


class MiniGraph(pg.PlotWidget):
    MAX = 200
    def __init__(self, color="#4fc3f7", parent=None):
        super().__init__(parent)
        self.setBackground("#0d0e10")
        self.getPlotItem().hideAxis("left")
        self.getPlotItem().hideAxis("bottom")
        self.getPlotItem().setContentsMargins(0,0,0,0)
        self.showGrid(x=False, y=False)
        self.curve = self.plot(pen=pg.mkPen(color, width=2))
        self._data = []

    def add(self, val):
        self._data.append(val)
        if len(self._data) > self.MAX:
            self._data = self._data[-self.MAX:]
        self.curve.setData(self._data)


def small_label(text):
    l = QLabel(text)
    l.setStyleSheet("color:#555;font-size:10px;letter-spacing:2px;background:transparent;border:none;")
    return l


def card(layout_widget):
    w = QWidget()
    w.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
    l = QVBoxLayout(w)
    l.setContentsMargins(14,12,14,12)
    l.setSpacing(6)
    return w, l


class SportDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#0d0e10;")
        root = QVBoxLayout(self)
        root.setContentsMargins(10,10,10,10)
        root.setSpacing(8)

        # === ШАПКА ===
        header = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet("color:#4fc3f7;font-size:10px;background:transparent;")
        title = QLabel("WHOOPHUB")
        title.setStyleSheet("color:#4fc3f7;font-size:13px;font-weight:700;letter-spacing:2px;background:transparent;")
        sep = QLabel("|")
        sep.setStyleSheet("color:#333;background:transparent;")
        self.drone_lbl = QLabel("BetaFPV Air 75 II Champion")
        self.drone_lbl.setStyleSheet("color:#555;font-size:12px;background:transparent;")
        self.armed_lbl = QLabel("DISARMED")
        self.armed_lbl.setStyleSheet("color:#4caf50;background:#1a2a1a;border:1px solid #2a5a2a;border-radius:4px;padding:2px 10px;font-size:11px;letter-spacing:1px;")
        self.port_lbl = QLabel("НЕ ПОДКЛЮЧЕНО")
        self.port_lbl.setStyleSheet("color:#4fc3f7;background:#1a1e2a;border:1px solid #2a3a5a;border-radius:4px;padding:2px 10px;font-size:11px;")
        header.addWidget(dot)
        header.addWidget(title)
        header.addWidget(sep)
        header.addWidget(self.drone_lbl)
        header.addStretch()
        header.addWidget(self.armed_lbl)
        header.addWidget(self.port_lbl)
        root.addLayout(header)

        # === СТРОКА 1: 4 карточки ===
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        # Напряжение
        self.v_card, vl = card(self)
        vl.addWidget(small_label("НАПРЯЖЕНИЕ"))
        self.v_val = QLabel("--")
        self.v_val.setStyleSheet("color:#4fc3f7;font-size:30px;font-weight:700;background:transparent;border:none;")
        self.v_bar_bg = QWidget()
        self.v_bar_bg.setFixedHeight(3)
        self.v_bar_bg.setStyleSheet("background:#1a1e2a;border-radius:1px;")
        self.v_bar = QWidget(self.v_bar_bg)
        self.v_bar.setGeometry(0,0,0,3)
        self.v_bar.setStyleSheet("background:#4fc3f7;border-radius:1px;")
        self.v_sub = QLabel("-- %")
        self.v_sub.setStyleSheet("color:#444;font-size:10px;background:transparent;border:none;")
        vl.addWidget(self.v_val)
        vl.addWidget(self.v_bar_bg)
        vl.addWidget(self.v_sub)

        # Ток
        self.c_card, cl = card(self)
        cl.addWidget(small_label("ТОК / РАСХОД"))
        self.c_val = QLabel("--")
        self.c_val.setStyleSheet("color:#ff9800;font-size:30px;font-weight:700;background:transparent;border:none;")
        self.c_sub = QLabel("-- мАч")
        self.c_sub.setStyleSheet("color:#444;font-size:10px;background:transparent;border:none;")
        cl.addWidget(self.c_val)
        cl.addStretch()
        cl.addWidget(self.c_sub)

        # RSSI
        self.r_card, rl = card(self)
        rl.addWidget(small_label("RSSI"))
        self.r_val = QLabel("--")
        self.r_val.setStyleSheet("color:#4caf50;font-size:30px;font-weight:700;background:transparent;border:none;")
        rssi_bars = QHBoxLayout()
        rssi_bars.setSpacing(3)
        self.rssi_segs = []
        for i in range(5):
            seg = QWidget()
            seg.setFixedHeight(10)
            seg.setStyleSheet("background:#2a2e38;border-radius:1px;")
            rssi_bars.addWidget(seg)
            self.rssi_segs.append(seg)
        self.r_sub = QLabel("Нет сигнала")
        self.r_sub.setStyleSheet("color:#444;font-size:10px;background:transparent;border:none;")
        rl.addWidget(self.r_val)
        rl.addLayout(rssi_bars)
        rl.addWidget(self.r_sub)

        # Сессия
        self.t_card, tl = card(self)
        tl.addWidget(small_label("СЕССИЯ"))
        self.t_val = QLabel("00:00")
        self.t_val.setStyleSheet("color:#e040fb;font-size:30px;font-weight:700;background:transparent;border:none;")
        self.rec_lbl = QLabel("● REC ВЫКЛ")
        self.rec_lbl.setStyleSheet("color:#444;font-size:10px;background:transparent;border:none;")
        tl.addWidget(self.t_val)
        tl.addStretch()
        tl.addWidget(self.rec_lbl)

        for w in [self.v_card, self.c_card, self.r_card, self.t_card]:
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row1.addWidget(w)
        root.addLayout(row1)

        # === СТРОКА 2: График + Attitude + мини 3D ===
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        # График
        graph_w, gl = card(self)
        gl.addWidget(small_label("НАПРЯЖЕНИЕ — ИСТОРИЯ"))
        self.mini_graph = MiniGraph("#4fc3f7")
        self.mini_graph.setMinimumHeight(80)
        gl.addWidget(self.mini_graph)

        # Attitude
        att_w, al = card(self)
        att_w.setFixedWidth(200)
        al.addWidget(small_label("ATTITUDE"))
        self.att_rows = {}
        for name, color in [("R","#4fc3f7"),("P","#ff9800"),("Y","#e040fb")]:
            row = QHBoxLayout()
            lbl = QLabel(name)
            lbl.setStyleSheet(f"color:#555;font-size:10px;background:transparent;min-width:12px;")
            bar_bg = QWidget()
            bar_bg.setFixedHeight(3)
            bar_bg.setStyleSheet("background:#1a1e2a;border-radius:1px;")
            val = QLabel("0.0°")
            val.setFixedWidth(45)
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            val.setStyleSheet(f"color:{color};font-size:11px;font-weight:600;background:transparent;")
            row.addWidget(lbl)
            row.addWidget(bar_bg, 1)
            row.addWidget(val)
            al.addLayout(row)
            self.att_rows[name] = (bar_bg, val)
        al.addStretch()

        # Мини 3D
        drone3d_w = QWidget()
        drone3d_w.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        drone3d_w.setFixedWidth(220)
        d3l = QVBoxLayout(drone3d_w)
        d3l.setContentsMargins(0,0,0,0)
        d3l.setSpacing(0)
        lbl3d = QLabel("3D МОДЕЛЬ")
        lbl3d.setStyleSheet("color:#555;font-size:10px;letter-spacing:2px;padding:8px 14px 4px;background:transparent;")
        self.mini_web = QWebEngineView()
        self.mini_web.setHtml(MINI_3D_HTML, QUrl("http://localhost"))
        self.mini_web.setMinimumHeight(130)
        d3l.addWidget(lbl3d)
        d3l.addWidget(self.mini_web)

        row2.addWidget(graph_w, 1)
        row2.addWidget(att_w)
        row2.addWidget(drone3d_w)
        root.addLayout(row2)

        # === СТРОКА 3: RC + Моторы + FC Info ===
        row3 = QHBoxLayout()
        row3.setSpacing(8)

        # RC каналы
        rc_w, rcl = card(self)
        rcl.addWidget(small_label("RC КАНАЛЫ"))
        self.rc_bars = []
        for name, color in [("R","#4fc3f7"),("P","#4fc3f7"),("T","#ff9800"),("Y","#4fc3f7")]:
            r = QHBoxLayout()
            l = QLabel(name)
            l.setStyleSheet("color:#555;font-size:9px;background:transparent;min-width:10px;")
            bb = QWidget()
            bb.setFixedHeight(4)
            bb.setStyleSheet("background:#1a1e2a;border-radius:2px;")
            v = QLabel("1500")
            v.setFixedWidth(34)
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            v.setStyleSheet(f"color:{color};font-size:9px;background:transparent;")
            r.addWidget(l)
            r.addWidget(bb,1)
            r.addWidget(v)
            rcl.addLayout(r)
            self.rc_bars.append((bb, v, color))
        rcl.addStretch()

        # Моторы
        mot_w, ml = card(self)
        ml.addWidget(small_label("МОТОРЫ"))
        self.motor_widgets = []
        for i in range(4):
            r = QHBoxLayout()
            l = QLabel(f"M{i+1}")
            l.setStyleSheet("color:#555;font-size:9px;background:transparent;min-width:16px;")
            bb = QWidget()
            bb.setFixedHeight(4)
            bb.setStyleSheet("background:#1a1e2a;border-radius:2px;")
            v = QLabel("1000")
            v.setFixedWidth(34)
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            v.setStyleSheet("color:#4caf50;font-size:9px;background:transparent;")
            r.addWidget(l)
            r.addWidget(bb,1)
            r.addWidget(v)
            ml.addLayout(r)
            self.motor_widgets.append((bb,v))
        ml.addStretch()

        # FC Info
        fc_w, fcl = card(self)
        fcl.addWidget(small_label("FC INFO"))
        self.fc_rows = {}
        for key, label in [("variant","Прошивка"),("version","Версия"),("board","Плата")]:
            r = QHBoxLayout()
            k = QLabel(label)
            k.setStyleSheet("color:#444;font-size:10px;background:transparent;")
            v = QLabel("--")
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            v.setStyleSheet("color:#ccc;font-size:10px;background:transparent;")
            r.addWidget(k)
            r.addStretch()
            r.addWidget(v)
            fcl.addLayout(r)
            self.fc_rows[key] = v
        sensors_row = QHBoxLayout()
        self.sensor_lbls = {}
        for s, key in [("GYRO","Гироскоп"),("ACC","Акселерометр"),("BARO","Барометр"),("GPS","GPS")]:
            lbl = QLabel(s)
            lbl.setStyleSheet("background:#1a1e2a;border:1px solid #2a2e3a;border-radius:3px;padding:1px 5px;font-size:9px;color:#444;")
            sensors_row.addWidget(lbl)
            self.sensor_lbls[key] = lbl
        fcl.addLayout(sensors_row)
        fcl.addStretch()

        for w in [rc_w, mot_w, fc_w]:
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row3.addWidget(w)
        root.addLayout(row3)

        # Таймер
        self._secs = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

        # 3D обновление
        self._roll = self._pitch = self._yaw = 0.0
        self._dirty3d = False
        self._3d_timer = QTimer()
        self._3d_timer.timeout.connect(self._flush3d)
        self._3d_timer.start(50)

    def _tick(self):
        self._secs += 1
        m = self._secs // 60
        s = self._secs % 60
        self.t_val.setText(f"{m:02d}:{s:02d}")

    def _flush3d(self):
        if self._dirty3d:
            self.mini_web.page().runJavaScript(
                f"updateAttitude({self._roll},{self._pitch},{self._yaw});"
            )
            self._dirty3d = False

    def set_port(self, port):
        self.port_lbl.setText(port)

    def set_drone_name(self, name):
        self.drone_lbl.setText(name)

    def update_voltage(self, v, warn_v=3.3, empty_v=3.0, full_v=4.35):
        self.v_val.setText(f"{v:.2f}В")
        pct = max(0, min(100, int((v - empty_v) / (full_v - empty_v) * 100)))
        color = "#4caf50" if v > warn_v + 0.1 else "#ff9800" if v > empty_v else "#f44336"
        self.v_val.setStyleSheet(f"color:{color};font-size:30px;font-weight:700;background:transparent;border:none;")
        self.v_sub.setText(f"{pct}% заряда")
        self.mini_graph.add(v)
        # Обновляем полоску заряда
        total_w = self.v_bar_bg.width()
        self.v_bar.setGeometry(0, 0, int(total_w * pct / 100), 3)
        self.v_bar.setStyleSheet(f"background:{color};border-radius:1px;")

    def update_current(self, current, mah):
        self.c_val.setText(f"{current:.1f}А")
        self.c_sub.setText(f"{int(mah)} мАч использовано")

    def update_rssi(self, rssi):
        self.r_val.setText(f"{rssi:.0f}%")
        color = "#4caf50" if rssi > 50 else "#ff9800" if rssi > 25 else "#f44336"
        self.r_val.setStyleSheet(f"color:{color};font-size:30px;font-weight:700;background:transparent;border:none;")
        filled = int(rssi / 100 * 5)
        for i, seg in enumerate(self.rssi_segs):
            seg.setStyleSheet(f"background:{'#4caf50' if i < filled else '#2a2e38'};border-radius:1px;")
        self.r_sub.setText("Хороший" if rssi > 50 else "Слабый" if rssi > 25 else "Критический")

    def update_attitude(self, roll, pitch, yaw):
        self._roll = roll
        self._pitch = pitch
        self._yaw = yaw
        self._dirty3d = True
        labels = {"R": f"{roll:.1f}°", "P": f"{pitch:.1f}°", "Y": f"{yaw:.0f}°"}
        for k, (bar, val) in self.att_rows.items():
            val.setText(labels[k])

    def update_rc(self, channels):
        names = ["R","P","T","Y"]
        for i, (bb, val, color) in enumerate(self.rc_bars):
            if i < len(channels):
                v = channels[i]
                val.setText(str(v))
                pct = max(0, min(100, int((v-1000)/10)))
                bb.setStyleSheet(
                    f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                    f"stop:0 {color},stop:{pct/100+0.001} {color},"
                    f"stop:{pct/100+0.002} #1a1e2a,stop:1 #1a1e2a);"
                    f"border-radius:2px;"
                )

    def update_motors(self, motors):
        for i, (bb, val) in enumerate(self.motor_widgets):
            v = motors[i] if i < len(motors) else 1000
            pct = max(0, min(100, int((v-1000)/10)))
            color = "#f44336" if pct > 80 else "#ff9800" if pct > 50 else "#4caf50"
            val.setText(str(v))
            bb.setStyleSheet(
                f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {color},stop:{pct/100+0.001} {color},"
                f"stop:{pct/100+0.002} #1a1e2a,stop:1 #1a1e2a);"
                f"border-radius:2px;"
            )

    def update_fc_info(self, variant=None, version=None, board=None):
        if variant:
            self.fc_rows["variant"].setText(variant)
        if version:
            self.fc_rows["version"].setText(version)
        if board:
            self.fc_rows["board"].setText(board.get("board_id","--"))

    def update_status(self, status):
        armed = status.get("armed", False)
        self.armed_lbl.setText("ARMED" if armed else "DISARMED")
        self.armed_lbl.setStyleSheet(
            "color:#f44336;background:#2a1a1a;border:1px solid #5a2a2a;"
            "border-radius:4px;padding:2px 10px;font-size:11px;letter-spacing:1px;"
            if armed else
            "color:#4caf50;background:#1a2a1a;border:1px solid #2a5a2a;"
            "border-radius:4px;padding:2px 10px;font-size:11px;letter-spacing:1px;"
        )
        for key, lbl in self.sensor_lbls.items():
            if key in status.get("sensors", []):
                lbl.setStyleSheet("background:#1a2a1a;border:1px solid #2a4a2a;border-radius:3px;padding:1px 5px;font-size:9px;color:#4caf50;")
            else:
                lbl.setStyleSheet("background:#1a1e2a;border:1px solid #2a2e3a;border-radius:3px;padding:1px 5px;font-size:9px;color:#444;")

    def reset(self):
        self._secs = 0
        self.t_val.setText("00:00")
        self.port_lbl.setText("НЕ ПОДКЛЮЧЕНО")