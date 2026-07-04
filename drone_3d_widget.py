from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
body{margin:0;background:#1a1b1e;overflow:hidden;}
canvas{display:block;}
#info{position:absolute;top:10px;left:10px;color:#4fc3f7;font-family:monospace;font-size:13px;background:rgba(0,0,0,0.6);padding:8px 12px;border-radius:6px;pointer-events:none;}
#label{position:absolute;top:10px;right:10px;color:#ff9800;font-family:monospace;font-size:12px;background:rgba(0,0,0,0.6);padding:6px 10px;border-radius:6px;pointer-events:none;}
#hint{position:absolute;bottom:10px;left:10px;color:#7a7d81;font-family:monospace;font-size:11px;background:rgba(0,0,0,0.5);padding:4px 8px;border-radius:4px;pointer-events:none;}
</style>
</head>
<body>
<div id="info">Roll: 0.0 | Pitch: 0.0 | Yaw: 0.0</div>
<div id="label">BetaFPV Air 75 II Champion</div>
<div id="hint">Drag: rotate | Wheel: zoom</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1b1e);

var camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 100);
camera.position.set(0, 5, 9);
camera.lookAt(0, 0, 0);

var renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.6));
var sun = new THREE.DirectionalLight(0xffffff, 0.8);
sun.position.set(4, 10, 5);
sun.castShadow = true;
scene.add(sun);

var floorMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 24),
    new THREE.MeshPhongMaterial({color:0x1e2023})
);
floorMesh.rotation.x = -Math.PI/2;
floorMesh.position.y = -1.5;
floorMesh.receiveShadow = true;
scene.add(floorMesh);
scene.add(new THREE.GridHelper(24, 48, 0x2a2d30, 0x242628));

var mFrame  = new THREE.MeshPhongMaterial({color:0x282828, shininess:60});
var mDark   = new THREE.MeshPhongMaterial({color:0x1a1a1a, shininess:40});
var mOrange = new THREE.MeshPhongMaterial({color:0xff6600, shininess:150});
var mPCB    = new THREE.MeshPhongMaterial({color:0x0a1f0a, shininess:30});
var mCam    = new THREE.MeshPhongMaterial({color:0x111111, shininess:200});
var mLens   = new THREE.MeshPhongMaterial({color:0x222266, shininess:255, transparent:true, opacity:0.85});
var mAnt    = new THREE.MeshPhongMaterial({color:0x999999, shininess:80});
var mWire   = new THREE.MeshPhongMaterial({color:0x1155ff, shininess:40});
var mCanopy = new THREE.MeshPhongMaterial({color:0x222222, shininess:80});
var mLedG   = new THREE.MeshPhongMaterial({color:0x00ff44, emissive:0x00ff44, emissiveIntensity:1.0});
var mLedR   = new THREE.MeshPhongMaterial({color:0xff2222, emissive:0xff2222, emissiveIntensity:1.0});

var drone = new THREE.Group();

// РАМА - 4 луча под 45 градусов
var armDegrees = [45, 135, 225, 315];
for (var ai = 0; ai < armDegrees.length; ai++) {
    var arm = new THREE.Mesh(
        new THREE.BoxGeometry(2.6, 0.07, 0.13),
        mFrame
    );
    arm.rotation.y = armDegrees[ai] * Math.PI / 180;
    arm.castShadow = true;
    drone.add(arm);
}

// Центральная пластина
drone.add(function(){
    var m = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.09, 0.75), mFrame);
    m.castShadow = true;
    return m;
}());

// PCB
var pcb = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.04, 0.6), mPCB);
pcb.position.y = 0.07;
drone.add(pcb);

// КАНОПИ КАМЕРЫ
var canopyBase = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.08, 0.28), mFrame);
canopyBase.position.set(0, 0.07, 0.36);
drone.add(canopyBase);

var canopyTop = new THREE.Mesh(
    new THREE.SphereGeometry(0.18, 12, 8, 0, Math.PI*2, 0, Math.PI*0.55),
    mCanopy
);
canopyTop.position.set(0, 0.1, 0.32);
drone.add(canopyTop);

var canopyFront = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.22, 0.06), mFrame);
canopyFront.position.set(0, 0.12, 0.47);
drone.add(canopyFront);

// Камера
var camBody = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.13, 0.1), mCam);
camBody.position.set(0, 0.13, 0.42);
camBody.rotation.x = -0.3;
drone.add(camBody);

var lens = new THREE.Mesh(new THREE.CylinderGeometry(0.052, 0.052, 0.05, 16), mLens);
lens.rotation.x = Math.PI/2 - 0.3;
lens.position.set(0, 0.1, 0.5);
drone.add(lens);

var wire = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.3, 5), mWire);
wire.position.set(0.07, 0.1, 0.25);
wire.rotation.z = 0.25;
drone.add(wire);

// АНТЕННА
var antBase = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.12, 6), mAnt);
antBase.position.set(0.1, 0.1, -0.38);
drone.add(antBase);

var antStick = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.65, 6), mAnt);
antStick.position.set(0.1, 0.51, -0.38);
drone.add(antStick);

var antTip = new THREE.Mesh(
    new THREE.SphereGeometry(0.025, 6, 5),
    new THREE.MeshPhongMaterial({color:0xffffff})
);
antTip.position.set(0.1, 0.86, -0.38);
drone.add(antTip);

// LED спереди зелёные
var ledFront = [{x:0.5,z:0.92},{x:-0.5,z:0.92}];
for (var li = 0; li < ledFront.length; li++) {
    var led = new THREE.Mesh(new THREE.SphereGeometry(0.03, 6, 5), mLedG);
    led.position.set(ledFront[li].x, 0.06, ledFront[li].z);
    drone.add(led);
}

// LED сзади красные
var ledBack = [{x:0.5,z:-0.92},{x:-0.5,z:-0.92}];
for (var li2 = 0; li2 < ledBack.length; li2++) {
    var led2 = new THREE.Mesh(new THREE.SphereGeometry(0.03, 6, 5), mLedR);
    led2.position.set(ledBack[li2].x, 0.06, ledBack[li2].z);
    drone.add(led2);
}

// ДАКТЫ + МОТОРЫ + ПРОПЕЛЛЕРЫ
var motorData = [
    {x: 0.88, z: 0.88,  cw:  1, pc:0x888888},
    {x:-0.88, z: 0.88,  cw: -1, pc:0x666666},
    {x: 0.88, z:-0.88,  cw: -1, pc:0x666666},
    {x:-0.88, z:-0.88,  cw:  1, pc:0x888888}
];

var propellers = [];

for (var mi = 0; mi < motorData.length; mi++) {
    var md = motorData[mi];
    var mx = md.x;
    var mz = md.z;

    // Дакт
    var duct = new THREE.Mesh(
        new THREE.TorusGeometry(0.46, 0.06, 12, 40),
        mFrame
    );
    duct.rotation.x = Math.PI/2;
    duct.position.set(mx, 0.04, mz);
    duct.castShadow = true;
    drone.add(duct);

    // 2 стойки дакта
    var strutAngles = [0, Math.PI/2];
    for (var si = 0; si < strutAngles.length; si++) {
        var strut = new THREE.Mesh(
            new THREE.CylinderGeometry(0.02, 0.02, 0.82, 5),
            mFrame
        );
        strut.rotation.z = Math.PI/2;
        strut.rotation.y = strutAngles[si];
        strut.position.set(mx, 0.04, mz);
        drone.add(strut);
    }

    // Корпус мотора
    var motBody = new THREE.Mesh(
        new THREE.CylinderGeometry(0.1, 0.1, 0.13, 14),
        mDark
    );
    motBody.position.set(mx, 0.05, mz);
    drone.add(motBody);

    // Оранжевый колокол
    var bell = new THREE.Mesh(
        new THREE.CylinderGeometry(0.095, 0.1, 0.09, 14),
        mOrange
    );
    bell.position.set(mx, 0.14, mz);
    drone.add(bell);

    // Пропеллер 3 лопасти
    var propGroup = new THREE.Group();
    propGroup.position.set(mx, 0.2, mz);

    for (var bi = 0; bi < 3; bi++) {
        var bAng = (bi / 3) * Math.PI * 2;
        var bx = Math.cos(bAng);
        var bz = Math.sin(bAng);

        var bladeMat = new THREE.MeshPhongMaterial({
            color: md.pc,
            shininess: 60,
            transparent: true,
            opacity: 0.82
        });
        var blade = new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.015, 0.09), bladeMat);
        blade.position.set(bx*0.26, 0, bz*0.26);
        blade.rotation.y = bAng + Math.PI/2;
        blade.rotation.x = 0.15 * md.cw;
        propGroup.add(blade);

        var tipMat = new THREE.MeshPhongMaterial({color: md.pc});
        var tip = new THREE.Mesh(new THREE.SphereGeometry(0.048, 6, 5), tipMat);
        tip.position.set(bx*0.52, 0, bz*0.52);
        propGroup.add(tip);
    }

    var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.03, 10), mDark);
    propGroup.add(hub);

    drone.add(propGroup);
    propellers.push({group: propGroup, cw: md.cw});
}

scene.add(drone);

// ОРБИТА КАМЕРЫ
var camTheta = 0.5;
var camPhi = 0.6;
var camR = 9;
var drag = false;
var lastX = 0;
var lastY = 0;

renderer.domElement.addEventListener('mousedown', function(e) {
    drag = true; lastX = e.clientX; lastY = e.clientY;
});
window.addEventListener('mouseup', function() { drag = false; });
window.addEventListener('mousemove', function(e) {
    if (!drag) return;
    camTheta -= (e.clientX - lastX) * 0.007;
    camPhi   -= (e.clientY - lastY) * 0.007;
    if (camPhi < 0.08) camPhi = 0.08;
    if (camPhi > 1.4)  camPhi = 1.4;
    lastX = e.clientX;
    lastY = e.clientY;
});
renderer.domElement.addEventListener('wheel', function(e) {
    camR += e.deltaY * 0.007;
    if (camR < 3)  camR = 3;
    if (camR > 18) camR = 18;
}, {passive:true});

// ATTITUDE
var tR = 0, tP = 0, tY = 0;
var cR = 0, cP = 0, cY = 0;

function updateAttitude(roll, pitch, yaw) {
    tR = roll  * Math.PI / 180;
    tP = pitch * Math.PI / 180;
    tY = yaw   * Math.PI / 180;
    document.getElementById('info').innerText =
        'Roll: ' + roll.toFixed(1) + '   Pitch: ' + pitch.toFixed(1) + '   Yaw: ' + yaw.toFixed(1);
}

// АНИМАЦИЯ
var propA = 0;
var lastT = performance.now();

function animate() {
    requestAnimationFrame(animate);
    var now = performance.now();
    var dt = (now - lastT) / 1000;
    if (dt > 0.05) dt = 0.05;
    lastT = now;

    var k = 1.0 - Math.pow(0.015, dt);
    cR += (tR - cR) * k;
    cP += (tP - cP) * k;
    cY += (tY - cY) * k;

    drone.rotation.order = 'YXZ';
    drone.rotation.y =  cY;
    drone.rotation.x =  cP;
    drone.rotation.z = cR;

    propA += dt * 20;
    for (var pi = 0; pi < propellers.length; pi++) {
        propellers[pi].group.rotation.y = propA * propellers[pi].cw;
    }

    camera.position.x = camR * Math.sin(camPhi) * Math.sin(camTheta);
    camera.position.y = camR * Math.cos(camPhi);
    camera.position.z = camR * Math.sin(camPhi) * Math.cos(camTheta);
    camera.lookAt(0, 0, 0);

    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>"""


class Drone3DWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web = QWebEngineView()
        self.web.setHtml(HTML, QUrl("http://localhost"))
        layout.addWidget(self.web)

        self._roll  = 0.0
        self._pitch = 0.0
        self._yaw   = 0.0
        self._dirty = False

        self._timer = QTimer()
        self._timer.timeout.connect(self._flush)
        self._timer.start(50)

    def update_attitude(self, roll, pitch, yaw):
        self._roll  = roll
        self._pitch = pitch
        self._yaw   = yaw
        self._dirty = True

    def _flush(self):
        if self._dirty:
            self.web.page().runJavaScript(
                "updateAttitude({},{},{});".format(self._roll, self._pitch, self._yaw)
            )
            self._dirty = False
