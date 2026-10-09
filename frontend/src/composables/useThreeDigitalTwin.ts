import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import type { SiteNode, WorkerInfo, EvacuationRoute, ActType, SensorItem } from '@/types/emergency';

export function useThreeDigitalTwin() {
  let scene: THREE.Scene | null = null;
  let camera: THREE.PerspectiveCamera | null = null;
  let renderer: THREE.WebGLRenderer | null = null;
  let controls: OrbitControls | null = null;
  let animationFrameId: number | null = null;
  let cameraMoveFrameId: number | null = null;

  // 场景分组
  let buildingGroup: THREE.Group;
  let fireMeshGroup: THREE.Group;
  let smokeParticles: THREE.Points | null = null;
  let pathTubesGroup: THREE.Group;
  let workerAvatarsGroup: THREE.Group;
  let labelSpritesGroup: THREE.Group;
  let obstacleGroup: THREE.Group;
  let sensorMarkersGroup: THREE.Group;

  // 空间坐标归一化映射 (原图尺寸 840x560 -> 以核心筒为中心 (0, 0, 0))
  function mapTo3D(gx: number, gy: number) {
    return {
      x: (gx - 420) * 0.95,
      y: 0,
      z: (gy - 280) * 0.95,
    };
  }

  // 高清 3D Canvas 文字标牌 (Sprite)
  function createTextSprite(
    text: string,
    bgColor: string = 'rgba(15, 23, 42, 0.88)',
    textColor: string = '#ffffff',
    borderColor: string = '#38bdf8'
  ) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    const ctx = canvas.getContext('2d')!;

    ctx.fillStyle = bgColor;
    ctx.roundRect(4, 4, 248, 56, 12);
    ctx.fill();

    ctx.strokeStyle = borderColor;
    ctx.lineWidth = 3;
    ctx.stroke();

    ctx.fillStyle = textColor;
    ctx.font = 'bold 22px "Inter", "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 128, 32, 228);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({
      map: texture,
      depthTest: true,
      depthWrite: false,
      transparent: true,
    });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(45, 11.25, 1);
    return sprite;
  }

  // 构建高精度 BIM 实体结构
  function buildRealisticBIMGeometry() {
    // 1. 楼层主体底板
    const slabGeo = new THREE.BoxGeometry(720, 14, 520);
    const slabMat = new THREE.MeshStandardMaterial({ color: 0x111c2b, roughness: 0.82, metalness: 0.12 });
    const slab = new THREE.Mesh(slabGeo, slabMat);
    slab.position.set(0, -7, 0);
    buildingGroup.add(slab);

    const grid = new THREE.GridHelper(720, 36, 0x25466a, 0x17283b);
    grid.position.set(0, 0.5, 0);
    buildingGroup.add(grid);

    // 施工分区与疏散通道铺在地面上，让俯视时能读懂楼层布局。
    const addZone = (name: string, x: number, z: number, width: number, depth: number, color: number) => {
      const zone = new THREE.Mesh(
        new THREE.PlaneGeometry(width, depth),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.13, side: THREE.DoubleSide, depthWrite: false })
      );
      zone.name = name;
      zone.rotation.x = -Math.PI / 2;
      zone.position.set(x, 0.72, z);
      buildingGroup.add(zone);
      const outline = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(width, 0.2, depth)),
        new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.65 })
      );
      outline.position.set(x, 0.8, z);
      buildingGroup.add(outline);
    };
    const addAisle = (x: number, z: number, width: number, depth: number) => {
      const aisle = new THREE.Mesh(
        new THREE.BoxGeometry(width, 0.35, depth),
        new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.16, depthWrite: false })
      );
      aisle.position.set(x, 0.76, z);
      buildingGroup.add(aisle);
      const edgeMat = new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.45 });
      const edgeGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(width, 0.25, depth));
      const edges = new THREE.LineSegments(edgeGeo, edgeMat);
      edges.position.copy(aisle.position);
      buildingGroup.add(edges);
    };

    addZone('zone-wood', -247, -133, 92, 74, 0xf59e0b);
    addZone('zone-rebar', 152, -133, 100, 76, 0x60a5fa);
    addZone('zone-core', -38, 0, 170, 148, 0x38bdf8);
    addZone('zone-storage', 266, 95, 90, 72, 0xfb7185);
    addAisle(-38, -152, 390, 22);  // 北侧主通道
    addAisle(228, -38, 22, 182);   // 东侧转运通道
    addAisle(-228, 38, 22, 110);  // 西侧防护通道
    addAisle(-19, 133, 245, 22);  // 南侧连通通道

    // 2. 核心筒剪力墙
    const coreMat = new THREE.MeshStandardMaterial({ color: 0x33465c, roughness: 0.58, metalness: 0.18 });
    const wallN = new THREE.Mesh(new THREE.BoxGeometry(150, 75, 12), coreMat);
    wallN.position.set(0, 37.5, -60);
    const wallS = new THREE.Mesh(new THREE.BoxGeometry(150, 75, 12), coreMat);
    wallS.position.set(0, 37.5, 60);
    const wallW = new THREE.Mesh(new THREE.BoxGeometry(12, 75, 120), coreMat);
    wallW.position.set(-75, 37.5, 0);
    buildingGroup.add(wallN, wallS, wallW);

    // 核心筒竖向烟囱效应气流光柱
    const stackCyl = new THREE.Mesh(
      new THREE.CylinderGeometry(24, 24, 200, 16),
      new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.12, wireframe: true })
    );
    stackCyl.position.set(0, 100, 0);
    buildingGroup.add(stackCyl);

    // 3. 结构方柱立柱阵列
    const colGeo = new THREE.BoxGeometry(18, 75, 18);
    const colMat = new THREE.MeshStandardMaterial({ color: 0x52677e, roughness: 0.52, metalness: 0.12 });
    const pillarPositions = [
      [-260, -160], [0, -160], [260, -160],
      [-260, 0], [260, 0],
      [-260, 160], [0, 160], [260, 160]
    ];
    pillarPositions.forEach(p => {
      const col = new THREE.Mesh(colGeo, colMat);
      col.position.set(p[0], 37.5, p[1]);
      buildingGroup.add(col);
    });

    // 4. 外立面脚手架刚性钢管网
    const scaffoldMat = new THREE.MeshStandardMaterial({ color: 0x7890a8, metalness: 0.62, roughness: 0.4 });
    for (let x = -350; x <= 350; x += 50) {
      const poleN = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 95, 6), scaffoldMat);
      poleN.position.set(x, 47.5, -255);
      const poleS = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 95, 6), scaffoldMat);
      poleS.position.set(x, 47.5, 255);
      buildingGroup.add(poleN, poleS);
    }
    for (let z = -250; z <= 250; z += 50) {
      const poleW = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 95, 6), scaffoldMat);
      poleW.position.set(-355, 47.5, z);
      const poleE = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 95, 6), scaffoldMat);
      poleE.position.set(355, 47.5, z);
      buildingGroup.add(poleW, poleE);
    }

    // 5. 重点功能区域构件
    // 木模板加工区
    const woodP = mapTo3D(160, 140);
    const lumber = new THREE.Mesh(
      new THREE.BoxGeometry(40, 10, 30),
      new THREE.MeshStandardMaterial({ color: 0x92400e })
    );
    lumber.position.set(woodP.x, 5, woodP.z);
    buildingGroup.add(lumber);

    // 钢筋加工区
    const rebarP = mapTo3D(580, 140);
    const rebarCage = new THREE.Mesh(
      new THREE.BoxGeometry(45, 15, 30),
      new THREE.MeshStandardMaterial({ color: 0x1e3a8a, wireframe: true })
    );
    rebarCage.position.set(rebarP.x, 7.5, rebarP.z);
    buildingGroup.add(rebarCage);

    // 出口A门框 (东现浇楼梯)
    const exitAP = mapTo3D(760, 140);
    const archA = new THREE.Mesh(
      new THREE.BoxGeometry(10, 45, 35),
      new THREE.MeshStandardMaterial({ color: 0x10b981, transparent: true, opacity: 0.6 })
    );
    archA.position.set(exitAP.x, 22.5, exitAP.z);
    buildingGroup.add(archA);

    // 出口B外架爬梯 (西外挂爬梯)
    const exitBP = mapTo3D(80, 380);
    const ladderB = new THREE.Mesh(
      new THREE.BoxGeometry(8, 75, 20),
      new THREE.MeshStandardMaterial({ color: 0x10b981, wireframe: true })
    );
    ladderB.position.set(exitBP.x, 37.5, exitBP.z);
    buildingGroup.add(ladderB);

    // 避难平台C (南悬挑平台)
    const exitCP = mapTo3D(320, 490);
    const platC = new THREE.Mesh(
      new THREE.BoxGeometry(60, 6, 45),
      new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.5 })
    );
    platC.position.set(exitCP.x, 3, exitCP.z);
    buildingGroup.add(platC);

    // 出口识别标记：高对比地面信标与立式指示牌。
    [
      { p: exitAP, color: 0x34d399, text: 'A' },
      { p: exitBP, color: 0x34d399, text: 'B' },
      { p: exitCP, color: 0xfbbf24, text: 'C' },
    ].forEach(({ p, color, text }) => {
      const beacon = new THREE.Mesh(
        new THREE.RingGeometry(11, 15, 32),
        new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide, transparent: true, opacity: 0.95 })
      );
      beacon.rotation.x = -Math.PI / 2;
      beacon.position.set(p.x, 1.2, p.z);
      buildingGroup.add(beacon);
      const badge = createTextSprite(`安全出口 ${text}`, 'rgba(5, 150, 105, 0.95)', '#ecfdf5', '#6ee7b7');
      badge.scale.set(32, 8, 1);
      badge.position.set(p.x, 56, p.z);
      buildingGroup.add(badge);
    });
  }

  // 构造火情粒子与浓烟
  function buildFireAndSmokeParticleSystems() {
    const fireCount = 220;
    const fireGeo = new THREE.BufferGeometry();
    const firePos = new Float32Array(fireCount * 3);
    const fireP = mapTo3D(580, 140);

    for (let i = 0; i < fireCount; i++) {
      firePos[i * 3] = fireP.x + (Math.random() - 0.5) * 40;
      firePos[i * 3 + 1] = Math.random() * 55;
      firePos[i * 3 + 2] = fireP.z + (Math.random() - 0.5) * 40;
    }
    fireGeo.setAttribute('position', new THREE.BufferAttribute(firePos, 3));
    const fireMat = new THREE.PointsMaterial({
      color: 0xf59e0b,
      size: 16,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending,
    });
    const particles = new THREE.Points(fireGeo, fireMat);
    particles.name = 'fireParticles';
    fireMeshGroup.add(particles);

    // 地面红色火警隔离圈
    const ringGeo = new THREE.RingGeometry(25, 45, 32);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xef4444, side: THREE.DoubleSide, transparent: true, opacity: 0.45 });
    const dangerRing = new THREE.Mesh(ringGeo, ringMat);
    dangerRing.rotation.x = Math.PI / 2;
    dangerRing.position.set(fireP.x, 0.8, fireP.z);
    fireMeshGroup.add(dangerRing);

    // 火焰顶部立体警告牌
    const fireLabel = createTextSprite('火源中心 · 配电箱短路', 'rgba(239, 68, 68, 0.92)', '#ffffff', '#fca5a5');
    fireLabel.position.set(fireP.x, 65, fireP.z);
    fireMeshGroup.add(fireLabel);

    // 粒子浓烟
    const smokeCount = 300;
    const smokeGeo = new THREE.BufferGeometry();
    const smokePos = new Float32Array(smokeCount * 3);
    for (let i = 0; i < smokeCount; i++) {
      smokePos[i * 3] = fireP.x + (Math.random() - 0.5) * 60;
      smokePos[i * 3 + 1] = 20 + Math.random() * 100;
      smokePos[i * 3 + 2] = fireP.z + (Math.random() - 0.5) * 60;
    }
    smokeGeo.setAttribute('position', new THREE.BufferAttribute(smokePos, 3));
    const smokeMat = new THREE.PointsMaterial({
      color: 0x64748b,
      size: 24,
      transparent: true,
      opacity: 0.45,
    });
    smokeParticles = new THREE.Points(smokeGeo, smokeMat);
    fireMeshGroup.add(smokeParticles);

    fireMeshGroup.visible = false;
  }

  function animateParticles() {
    if (!fireMeshGroup.visible) return;

    const fPart = fireMeshGroup.getObjectByName('fireParticles') as THREE.Points;
    if (fPart) {
      const pos = fPart.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < pos.length; i += 3) {
        pos[i + 1] += 1.6;
        pos[i] += (Math.random() - 0.5) * 0.7;
        if (pos[i + 1] > 65) pos[i + 1] = 2;
      }
      fPart.geometry.attributes.position.needsUpdate = true;
    }

    if (smokeParticles) {
      const sPos = smokeParticles.geometry.attributes.position.array as Float32Array;
      const fp = mapTo3D(580, 140);
      for (let i = 0; i < sPos.length; i += 3) {
        sPos[i + 1] += 1.1;
        sPos[i] += 0.8; // 向东蔓延
        if (sPos[i + 1] > 140) {
          sPos[i + 1] = 20;
          sPos[i] = fp.x + (Math.random() - 0.5) * 40;
        }
      }
      smokeParticles.geometry.attributes.position.needsUpdate = true;
    }
  }

  // 初始化 Three.js 场景
  function init(container: HTMLElement) {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050914);
    // 关键：杜绝黑雾，缩放拉远永不消失
    scene.fog = null;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 520;

    camera = new THREE.PerspectiveCamera(45, width / height, 5, 8000);
    camera.position.set(0, 380, 440);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    renderer.shadowMap.enabled = true;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.target.set(0, 0, 0);
    controls.minDistance = 60;
    controls.maxDistance = 2500;
    controls.screenSpacePanning = true;
    controls.maxPolarAngle = Math.PI / 2.05;

    // 灯光
    const ambientLight = new THREE.HemisphereLight(0xdbeafe, 0x18263a, 1.25);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xc9e8ff, 2.1);
    dirLight1.position.set(150, 400, 250);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x6ee7b7, 1.0);
    dirLight2.position.set(-200, 300, -200);
    scene.add(dirLight2);

    // 图元分组
    buildingGroup = new THREE.Group();
    fireMeshGroup = new THREE.Group();
    pathTubesGroup = new THREE.Group();
    workerAvatarsGroup = new THREE.Group();
    labelSpritesGroup = new THREE.Group();
    obstacleGroup = new THREE.Group();
    sensorMarkersGroup = new THREE.Group();

    scene.add(buildingGroup);
    scene.add(fireMeshGroup);
    scene.add(pathTubesGroup);
    scene.add(workerAvatarsGroup);
    scene.add(labelSpritesGroup);
    scene.add(obstacleGroup);
    scene.add(sensorMarkersGroup);

    buildRealisticBIMGeometry();
    buildFireAndSmokeParticleSystems();

    function animate() {
      animationFrameId = requestAnimationFrame(animate);
      controls?.update();
      animateParticles();
      if (renderer && scene && camera) {
        renderer.render(scene, camera);
      }
    }
    animate();
  }

  // 响应式更新 3D 态势
  function updateScene(
    act: ActType,
    nodes: SiteNode[],
    workers: WorkerInfo[],
    routes: EvacuationRoute[],
    sensors?: SensorItem[]
  ) {
    if (!scene) return;

    const isFire = (act === 'ACT_2_FIRE' || act === 'ACT_3_BLOCKAGE');
    fireMeshGroup.visible = isFire;

    // 清空动态图元并释放 GPU 资源，避免连续切换演练时纹理和网格累积。
    const clearGroup = (group: THREE.Group) => {
      [...group.children].forEach(child => {
        child.traverse(object => {
          const mesh = object as THREE.Mesh;
          mesh.geometry?.dispose?.();
          const materials = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : [];
          materials.forEach(material => {
            const map = (material as THREE.MeshBasicMaterial).map;
            map?.dispose();
            material.dispose();
          });
        });
        group.remove(child);
      });
    };
    clearGroup(labelSpritesGroup);
    clearGroup(workerAvatarsGroup);
    clearGroup(pathTubesGroup);
    clearGroup(obstacleGroup);
    clearGroup(sensorMarkersGroup);

    // 1. 中文位置标牌
    nodes.forEach(n => {
      const p = mapTo3D(n.coords.x, n.coords.y);
      const isExit = (n.zone_type === 'safe_exit' || n.zone_type === 'refuge_platform');
      const isHazard = n.zone_type === 'hazard_storage';
      const borderC = isExit ? '#34d399' : isHazard ? '#fb7185' : '#7dd3fc';
      const bgC = isExit ? 'rgba(6, 78, 59, 0.96)' : isHazard ? 'rgba(136, 19, 55, 0.94)' : 'rgba(15, 23, 42, 0.92)';

      const sprite = createTextSprite(n.name, bgC, '#ffffff', borderC);
      sprite.scale.set(isExit ? 54 : 48, isExit ? 13.5 : 12, 1);
      sprite.position.set(p.x, isExit ? 48 : 33, p.z);
      labelSpritesGroup.add(sprite);

      // 地面光圈
      const disc = new THREE.Mesh(
        new THREE.CircleGeometry(isExit ? 17 : isHazard ? 14 : 10, 32),
        new THREE.MeshBasicMaterial({ color: isExit ? 0x10b981 : isHazard ? 0xf43f5e : 0x38bdf8, transparent: true, opacity: isExit ? 0.8 : 0.55 })
      );
      disc.rotation.x = -Math.PI / 2;
      disc.position.set(p.x, 0.6, p.z);
      labelSpritesGroup.add(disc);
    });

    // 2. 工友小人立体模型
    workers.forEach(w => {
      const n = nodes.find(item => item.id === w.current_node);
      if (!n) return;
      const p = mapTo3D(n.coords.x, n.coords.y);
      const wGroup = new THREE.Group();

      const statusColor = w.status === 'safe' ? 0x34d399 : w.status === 'trapped' ? 0xfb7185 : 0x38bdf8;
      const body = new THREE.Mesh(
        new THREE.CapsuleGeometry(4.3, 8, 4, 8),
        new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.48, metalness: 0.04 })
      );
      body.position.set(0, 10, 0);
      const head = new THREE.Mesh(new THREE.SphereGeometry(3.5, 16, 12), new THREE.MeshStandardMaterial({ color: 0xf1c7a2, roughness: 0.8 }));
      head.position.set(0, 18, 0);
      const helmet = new THREE.Mesh(new THREE.SphereGeometry(4.4, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xfacc15, roughness: 0.35, metalness: 0.12 }));
      helmet.position.set(0, 20, 0);
      const helmetBrim = new THREE.Mesh(new THREE.CylinderGeometry(4.9, 4.9, 1.2, 16), new THREE.MeshStandardMaterial({ color: 0xfbbf24, roughness: 0.4 }));
      helmetBrim.position.set(0, 19.6, 0);
      const beacon = new THREE.Mesh(new THREE.SphereGeometry(1.4, 10, 8), new THREE.MeshBasicMaterial({ color: statusColor }));
      beacon.position.set(0, 23.5, 0);

      const nameSprite = createTextSprite(`${w.name} (${w.id})`, 'rgba(2, 132, 199, 0.92)', '#ffffff', '#38bdf8');
      nameSprite.scale.set(38, 9.5, 1);
      nameSprite.position.set(0, 26, 0);

      const ring = new THREE.Mesh(
        new THREE.RingGeometry(7, 9, 32),
        new THREE.MeshBasicMaterial({ color: statusColor, side: THREE.DoubleSide, transparent: true, opacity: 0.95 })
      );
      ring.rotation.x = Math.PI / 2;
      ring.position.set(0, 0.7, 0);

      wGroup.add(body, head, helmet, helmetBrim, beacon, nameSprite, ring);
      wGroup.position.set(p.x, 0, p.z);
      workerAvatarsGroup.add(wGroup);
    });

    // 3. 逃生导向发光管道 (Tube)
    if (isFire) {
      routes.forEach(r => {
        if (!r.path || r.path.length < 2) return;
        const points: THREE.Vector3[] = [];
        r.path.forEach(nid => {
          const node = nodes.find(item => item.id === nid);
          if (node) {
            const p = mapTo3D(node.coords.x, node.coords.y);
            points.push(new THREE.Vector3(p.x, 6, p.z));
          }
        });

        if (points.length >= 2) {
          const curve = new THREE.CatmullRomCurve3(points);
          const tubeGeo = new THREE.TubeGeometry(curve, 32, 4.2, 8, false);
          const colorHex = r.target_exit === 'EXIT_REFUGE' ? 0x22d3ee : 0x34d399;
          const tubeMat = new THREE.MeshBasicMaterial({
            color: colorHex,
            transparent: true,
            opacity: 0.92,
          });
          const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
          pathTubesGroup.add(tubeMesh);

          // 沿路线放置方向箭头，避免只看到一条无法判断起终点的发光线。
          const arrowGeo = new THREE.ConeGeometry(5.5, 13, 10);
          const arrowMat = new THREE.MeshBasicMaterial({ color: colorHex });
          for (let i = 0; i < points.length - 1; i++) {
            const start = points[i];
            const end = points[i + 1];
            const direction = new THREE.Vector3().subVectors(end, start);
            if (direction.length() < 24) continue;
            direction.normalize();
            const arrow = new THREE.Mesh(arrowGeo, arrowMat);
            arrow.position.copy(start).lerp(end, 0.72);
            arrow.position.y = 8.5;
            arrow.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction);
            pathTubesGroup.add(arrow);
          }
        }
      });

      // 东侧主干道断流隔离墙
      const eastBlockP = mapTo3D(660, 240);
      const blockWall = new THREE.Mesh(
        new THREE.BoxGeometry(35, 30, 6),
        new THREE.MeshBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.75 })
      );
      blockWall.position.set(eastBlockP.x, 15, eastBlockP.z);
      const blockLabel = createTextSprite('东侧火情封锁', 'rgba(239, 68, 68, 0.95)', '#ffffff', '#ffffff');
      blockLabel.scale.set(45, 11, 1);
      blockLabel.position.set(eastBlockP.x, 38, eastBlockP.z);
      pathTubesGroup.add(blockWall, blockLabel);
    }

    // 4. 次生脚手架坍塌障碍物
    if (act === 'ACT_3_BLOCKAGE') {
      const obsP = mapTo3D(80, 380);
      const pipe1 = new THREE.Mesh(
        new THREE.CylinderGeometry(2, 2, 45, 8),
        new THREE.MeshStandardMaterial({ color: 0xf97316 })
      );
      pipe1.rotation.z = Math.PI / 3;
      pipe1.position.set(obsP.x + 20, 10, obsP.z - 20);

      const pipe2 = new THREE.Mesh(
        new THREE.CylinderGeometry(2, 2, 40, 8),
        new THREE.MeshStandardMaterial({ color: 0xf97316 })
      );
      pipe2.rotation.x = Math.PI / 4;
      pipe2.position.set(obsP.x + 25, 8, obsP.z - 15);

      const obsLabel = createTextSprite('支架坍塌 · 净宽 0.35 m', 'rgba(249, 115, 22, 0.95)', '#ffffff', '#ffffff');
      obsLabel.scale.set(58, 14, 1);
      obsLabel.position.set(obsP.x + 20, 35, obsP.z - 20);

      obstacleGroup.add(pipe1, pipe2, obsLabel);
    }

    // 5. IoT 传感器实时 3D 浮动标牌
    if (sensors && sensors.length > 0) {
      sensors.forEach(s => {
        // 仅对异常/警示状态或处于火灾/阻断关键位置的传感器在 3D 空间进行醒目标注
        if (s.status === 'NORMAL') return;

        const coords = s.coords || nodes.find(n => n.id === s.node_id)?.coords;
        if (!coords) return;
        const p = mapTo3D(coords.x, coords.y);
        const isAlarm = (s.status === 'ALARM' || s.status === 'BLOCKED');
        const bgC = isAlarm ? 'rgba(225, 29, 72, 0.95)' : 'rgba(217, 119, 6, 0.92)';
        const borderC = isAlarm ? '#fda4af' : '#fde68a';
        const icon = isAlarm ? '!' : '·';

        const sprite = createTextSprite(
          `${icon} ${s.name}: ${s.current_value}${s.unit}`,
          bgC,
          '#ffffff',
          borderC
        );
        sprite.scale.set(isAlarm ? 58 : 50, isAlarm ? 14.5 : 12.5, 1);
        sprite.position.set(p.x, isAlarm ? 62 : 44, p.z + 10);
        sensorMarkersGroup.add(sprite);

        // 传感器地面警示光圈
        const disc = new THREE.Mesh(
          new THREE.CircleGeometry(isAlarm ? 14 : 9, 24),
          new THREE.MeshBasicMaterial({
            color: isAlarm ? 0xf43f5e : 0xf59e0b,
            transparent: true,
            opacity: isAlarm ? 0.85 : 0.6,
          })
        );
        disc.rotation.x = -Math.PI / 2;
        disc.position.set(p.x, 0.7, p.z);
        sensorMarkersGroup.add(disc);
      });
    }
  }

  function setCameraPreset(preset: 'iso' | 'fire' | 'exitB') {
    if (!camera || !controls) return;
    let nextPosition: THREE.Vector3;
    let nextTarget: THREE.Vector3;
    if (preset === 'iso') {
      nextPosition = new THREE.Vector3(0, 380, 440);
      nextTarget = new THREE.Vector3(0, 0, 0);
    } else if (preset === 'fire') {
      const fp = mapTo3D(580, 140);
      nextPosition = new THREE.Vector3(fp.x + 80, 160, fp.z + 120);
      nextTarget = new THREE.Vector3(fp.x, 20, fp.z);
    } else if (preset === 'exitB') {
      const bp = mapTo3D(80, 380);
      nextPosition = new THREE.Vector3(bp.x + 100, 140, bp.z + 100);
      nextTarget = new THREE.Vector3(bp.x, 15, bp.z);
    }
    if (cameraMoveFrameId !== null) cancelAnimationFrame(cameraMoveFrameId);
    const startPosition = camera.position.clone();
    const startTarget = controls.target.clone();
    const startedAt = performance.now();
    const moveCamera = (now: number) => {
      const progress = Math.min((now - startedAt) / 620, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      camera!.position.lerpVectors(startPosition, nextPosition, eased);
      controls!.target.lerpVectors(startTarget, nextTarget, eased);
      controls!.update();
      if (progress < 1) cameraMoveFrameId = requestAnimationFrame(moveCamera);
      else cameraMoveFrameId = null;
    };
    cameraMoveFrameId = requestAnimationFrame(moveCamera);
  }

  function handleResize(width: number, height: number) {
    if (!camera || !renderer) return;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  function destroy() {
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
    }
    if (cameraMoveFrameId !== null) cancelAnimationFrame(cameraMoveFrameId);
    renderer?.dispose();
  }

  return {
    init,
    updateScene,
    setCameraPreset,
    handleResize,
    destroy,
  };
}
