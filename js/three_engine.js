/**
 * Heap Master Pro - Three.js 3D Engine Module
 * موتور سه‌بعدی صنعتی برای نمایش پدهای هیپ لیچینگ
 * شامل: ژئوممبران، لایه‌های رسی، انیمیشن جریان سیال، ابزارهای اندازه‌گیری
 */

/**
 * Heap Master Pro - Three.js 3D Engine Module
 * موتور سه‌بعدی صنعتی برای نمایش پدهای هیپ لیچینگ
 * شامل: ژئوممبران، لایه‌های رسی، انیمیشن جریان سیال، ابزارهای اندازه‌گیری
 */

// --- 3D ENGINE ---
const View3D = {
    scene: null, camera: null, renderer: null, controls: null,
    meshes: [], labels: [], rainSystem: null, isRaining: false,
    isWireframe: false, showLabels: false, isOpen: false,
    debugInfo: document.getElementById('debugInfo'),
    init() {
        this.setupCanvas();
        this.createScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupControls();
        this.addLights();
        this.addGrid();
        this.setupResizeHandler();

        // Initial render
        this.renderAll();

        this.updateDebugInfo('3D engine initialized');
    },
    setupCanvas() {
        const cont = document.getElementById('canvas-wrapper');
        if (!cont) return;
        cont.innerHTML = ''; // Clear placeholder
    },
    createScene() {
        this.scene = new THREE.Scene();
        const isDarkMode = document.body.classList.contains('dark-mode');
        this.scene.background = new THREE.Color(isDarkMode ? 0x111827 : 0xf8fafc);
    },
    setupCamera() {
        const cont = document.getElementById('canvas-wrapper');
        if (!cont) return;
        const width = cont.clientWidth || window.innerWidth;
        const height = cont.clientHeight || window.innerHeight;

        this.camera = new THREE.PerspectiveCamera(45, width/height, 1, 5000);
        this.camera.position.set(300, 250, 400);
        this.camera.lookAt(0, 0, 0);
    },
    setupRenderer() {
        const cont = document.getElementById('canvas-wrapper');
        if (!cont) return;
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.updateRendererSize();
        cont.appendChild(this.renderer.domElement);
    },
    updateRendererSize() {
        if(!this.renderer) return;

        const cont = document.getElementById('canvas-wrapper');
        if (!cont) return;
        const width = cont.clientWidth || window.innerWidth;
        const height = cont.clientHeight || window.innerHeight;

        this.renderer.setSize(width, height);
        if(this.camera) {
            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
        }
    },
    setupControls() {
        if(!this.camera || !this.renderer) return;

        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI/2 - 0.05; // Prevent going below ground
    },
    addLights() {
        const isDarkMode = document.body.classList.contains('dark-mode');

        // Ambient light
        this.scene.add(new THREE.AmbientLight(0xffffff, isDarkMode ? 0.5 : 0.3));

        // Directional light (sun)
        const sunLight = new THREE.DirectionalLight(0xffffff, isDarkMode ? 0.8 : 0.6);
        sunLight.position.set(200, 500, 200);
        sunLight.castShadow = true;

        // Configure shadow properties
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 0.5;
        sunLight.shadow.camera.far = 1000;
        sunLight.shadow.camera.left = -200;
        sunLight.shadow.camera.right = 200;
        sunLight.shadow.camera.top = 200;
        sunLight.shadow.camera.bottom = -200;

        this.scene.add(sunLight);
    },
    addGrid() {
        // Ground grid
        const gridSize = 500;
        const gridDivisions = 50;
        const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, 0x666666, 0x333333);
        gridHelper.position.y = -0.1; // Slightly below ground level
        gridHelper.material.opacity = 0.5;
        gridHelper.material.transparent = true;
        this.scene.add(gridHelper);

        // Add axes
        const axesHelper = new THREE.AxesHelper(50);
        this.scene.add(axesHelper);
    },
    setupResizeHandler() {
        window.addEventListener('resize', () => {
            this.updateRendererSize();
            if (this.controls) this.controls.update();
        });
    },
    updateTheme() {
        if(!this.scene) return;
        const isDarkMode = document.body.classList.contains('dark-mode');
        this.scene.background = new THREE.Color(isDarkMode ? 0x111827 : 0xf8fafc);
        if(this.renderer) {
            this.renderer.setClearColor(isDarkMode ? 0x111827 : 0xf8fafc);
        }
        this.renderAll();
    },
    open() {
        this.isOpen = true;
        document.getElementById('modal3D').classList.add('open');

        // Wait for modal to be fully visible before updating size
        setTimeout(() => {
            this.updateRendererSize();
            this.renderAll();
            this.animate();
            this.updateDebugInfo('3D view opened');
        }, 100);
    },
    close() {
        this.isOpen = false;
        document.getElementById('modal3D').classList.remove('open');
        this.updateDebugInfo('3D view closed');
    },
    renderAll() {
        if(!this.scene || !this.renderer) return;

        // Clear all existing meshes
        this.clearScene();

        // Rebuild the scene
        this.addGround();
        this.addPads();
        this.addLabels();

        if(this.isRaining) {
            this.createRain();
        }

        this.updateDebugInfo(`Rendered ${this.meshes.length} objects`);
    },
    clearScene() {
        // Remove all mesh objects from the scene
        this.meshes.forEach(mesh => {
            if(mesh.geometry) mesh.geometry.dispose();
            if(mesh.material) {
                if(Array.isArray(mesh.material)) {
                    mesh.material.forEach(mat => mat.dispose());
                } else {
                    mesh.material.dispose();
                }
            }
            this.scene.remove(mesh);
        });

        // Remove all labels
        this.labels.forEach(label => {
            this.scene.remove(label);
        });

        // Remove rain system if exists
        if(this.rainSystem) {
            this.scene.remove(this.rainSystem);
            this.rainSystem = null;
        }

        // Reset arrays
        this.meshes = [];
        this.labels = [];
    },
    addGround() {
        const size = 1000;
        const divisions = 100;

        const geometry = new THREE.PlaneGeometry(size, size, divisions, divisions);
        const material = new THREE.MeshStandardMaterial({
            color: 0x374151,
            wireframe: this.isWireframe,
            transparent: true,
            opacity: 0.3,
            roughness: 1.0
        });

        // Apply slope to the ground
        const positions = geometry.attributes.position.array;
        const sx = App.terrain.sx / 100;
        const sy = App.terrain.sy / 100;

        for(let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const z = positions[i + 1]; // Note: using z as y in plane geometry
            positions[i + 2] = (x * sx) + (-z * sy); // Apply slope
        }

        geometry.computeVertexNormals();

        const ground = new THREE.Mesh(geometry, material);
        ground.rotation.x = -Math.PI / 2; // Rotate to horizontal
        ground.position.y = -0.1; // Slightly below to avoid z-fighting

        this.scene.add(ground);
        this.meshes.push(ground);
    },
    addPads() {
        if(!App.pads || App.pads.length === 0) return;

        App.pads.forEach(pad => {
            this.addPad(pad);
        });
    },
    addPad(pad) {
        if(!pad) return;

        // Create pad geometry
        const padMesh = this.createPadGeometry(pad);
        if(!padMesh) return;

        // Add to scene
        this.scene.add(padMesh);
        this.meshes.push(padMesh);

        // Add piping if pad has irrigation
        if(pad.lat > 0 && pad.emit > 0) {
            const piping = this.createPiping(pad, padMesh);
            if(piping) {
                this.scene.add(piping);
                this.meshes.push(piping);
            }
        }
    },
    createPadGeometry(pad) {
        if(!pad || !pad.L || !pad.W || !pad.H) return null;

        const hL = pad.L / 2;
        const hW = pad.W / 2;
        const sx = App.terrain.sx / 100;
        const sy = App.terrain.sy / 100;
        const slope_ratio = 1 / Math.tan(pad.slopeDeg * Math.PI / 180);

        // Get adjacent pads
        const adjacent = App.getAdjacentPads(pad);

        // Function to get terrain height at point
        const getTerrainHeight = (x, z) => {
            return (x * sx) + (z * sy);
        };

        // Function to get slope run based on boundary type
        const getRun = (height, boundaryType, isAdjacent) => {
            if(boundaryType === 'wall') return 0;
            if(boundaryType === 'attach' && isAdjacent) {
                return height * slope_ratio * 0.5;
            }
            return height * slope_ratio;
        };

        // Calculate corner heights
        const getY = (x, z) => x * sx + z * sy;
        const crest_elev = pad.H;

        const heights = {
            TL: crest_elev - getY(-hL, -hW),
            TR: crest_elev - getY(hL, -hW),
            BR: crest_elev - getY(hL, hW),
            BL: crest_elev - getY(-hL, hW)
        };

        // Calculate runs
        const runs = {
            TL: getRun(heights.TL, pad.bounds.L, adjacent.left),
            TR: getRun(heights.TR, pad.bounds.R, adjacent.right),
            BR: getRun(heights.BR, pad.bounds.F, adjacent.front),
            BL: getRun(heights.BL, pad.bounds.B, adjacent.back)
        };

        // Base corners (bottom)
        const baseCorners = [
            new THREE.Vector3(-hL, getTerrainHeight(-hL, -hW), -hW),  // BL
            new THREE.Vector3(hL, getTerrainHeight(hL, -hW), -hW),   // BR
            new THREE.Vector3(hL, getTerrainHeight(hL, hW), hW),    // FR
            new THREE.Vector3(-hL, getTerrainHeight(-hL, hW), hW)    // FL
        ];

        // Offset by pad position
        baseCorners.forEach(corner => {
            corner.x += pad.x;
            corner.z += pad.z;
        });

        // Top corners
        const topCorners = [
            new THREE.Vector3(-hL + runs.TL, crest_elev, -hW + runs.TL), // BL
            new THREE.Vector3(hL - runs.TR, crest_elev, -hW + runs.TR),  // BR
            new THREE.Vector3(hL - runs.BR, crest_elev, hW - runs.BR),   // FR
            new THREE.Vector3(-hL + runs.BL, crest_elev, hW - runs.BL)   // FL
        ];

        // Offset by pad position
        topCorners.forEach(corner => {
            corner.x += pad.x;
            corner.z += pad.z;
        });

        // Check for overlaps with attached pads and adjust
        this.adjustForAttachedPads(pad, baseCorners, topCorners, adjacent);

        // Create geometry
        const geometry = new THREE.BufferGeometry();
        const vertices = [];

        // Add faces
        this.addSideFaces(vertices, baseCorners, topCorners);
        this.addTopFaces(vertices, topCorners);
        this.addBottomFaces(vertices, baseCorners);

        // Set geometry attributes
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.computeVertexNormals();

        // Create material
        const color = new THREE.Color(document.getElementById('colOre').value);
        if(pad.lift > 1) {
            // Darker color for higher lifts
            color.offsetHSL(0, 0, -0.1 * (pad.lift - 1));
        }

        const material = this.isWireframe ?
            new THREE.MeshBasicMaterial({
                color: color,
                wireframe: true,
                transparent: true,
                opacity: 0.8
            }) :
            new THREE.MeshStandardMaterial({
                color: color,
                roughness: 0.9,
                metalness: 0.1,
                flatShading: true
            });

        // Highlight selected pad
        if(pad.id == App.selectedId) {
            material.emissive = new THREE.Color(0x3333ff);
            material.emissiveIntensity = 0.3;
        }

        const mesh = new THREE.Mesh(geometry, material);
        mesh.userData = { padId: pad.id };
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        return mesh;
    },
    adjustForAttachedPads(pad, baseCorners, topCorners, adjacent) {
        // Adjust for attached pads to prevent overlap
        if(adjacent.left && pad.bounds.L === 'attach') {
            // Move left side slightly to the right
            const adjustment = 0.5;
            baseCorners[0].x += adjustment;
            baseCorners[3].x += adjustment;
            topCorners[0].x += adjustment;
            topCorners[3].x += adjustment;
        }

        if(adjacent.right && pad.bounds.R === 'attach') {
            // Move right side slightly to the left
            const adjustment = 0.5;
            baseCorners[1].x -= adjustment;
            baseCorners[2].x -= adjustment;
            topCorners[1].x -= adjustment;
            topCorners[2].x -= adjustment;
        }

        if(adjacent.front && pad.bounds.F === 'attach') {
            // Move front side slightly back
            const adjustment = 0.5;
            baseCorners[2].z -= adjustment;
            baseCorners[3].z -= adjustment;
            topCorners[2].z -= adjustment;
            topCorners[3].z -= adjustment;
        }

        if(adjacent.back && pad.bounds.B === 'attach') {
            // Move back side slightly forward
            const adjustment = 0.5;
            baseCorners[0].z += adjustment;
            baseCorners[1].z += adjustment;
            topCorners[0].z += adjustment;
            topCorners[1].z += adjustment;
        }
    },
    addSideFaces(vertices, baseCorners, topCorners) {
        // Create sides (4 faces, each made of 2 triangles)
        const sides = [
            [0, 3], // Left side
            [3, 2], // Front side
            [2, 1], // Right side
            [1, 0]  // Back side
        ];

        sides.forEach(side => {
            const i1 = side[0];
            const i2 = side[1];

            // First triangle: base1, base2, top2
            this.addTriangle(
                vertices,
                baseCorners[i1],
                baseCorners[i2],
                topCorners[i2]
            );

            // Second triangle: base1, top2, top1
            this.addTriangle(
                vertices,
                baseCorners[i1],
                topCorners[i2],
                topCorners[i1]
            );
        });
    },
    addTopFaces(vertices, topCorners) {
        // Create top face (2 triangles)
        this.addTriangle(
            vertices,
            topCorners[0],
            topCorners[1],
            topCorners[2]
        );
        this.addTriangle(
            vertices,
            topCorners[0],
            topCorners[2],
            topCorners[3]
        );
    },
    addBottomFaces(vertices, baseCorners) {
        // Create bottom face (2 triangles)
        this.addTriangle(
            vertices,
            baseCorners[0],
            baseCorners[2],
            baseCorners[1]
        );
        this.addTriangle(
            vertices,
            baseCorners[0],
            baseCorners[3],
            baseCorners[2]
        );
    },
    addTriangle(vertices, v1, v2, v3) {
        vertices.push(v1.x, v1.y, v1.z);
        vertices.push(v2.x, v2.y, v2.z);
        vertices.push(v3.x, v3.y, v3.z);
    },
    createPiping(pad, padMesh) {
        // Create group for all piping elements
        const pipingGroup = new THREE.Group();

        // Skip if top dimensions are too small
        const padBox = new THREE.Box3().setFromObject(padMesh);
        const topSize = {
            x: padBox.max.x - padBox.min.x,
            z: padBox.max.z - padBox.min.z
        };

        if(topSize.x < 5 || topSize.z < 5) return null;

        // Calculate top corners from pad mesh
        const topCorners = this.getTopCornersFromPadMesh(padMesh);
        if(!topCorners) return null;

        // Create main collector
        const collector = this.createCollector(topCorners);
        if(collector) pipingGroup.add(collector);

        // Create laterals
        const laterals = this.createLaterals(pad, topCorners);
        if(laterals) pipingGroup.add(laterals);

        // Add to scene
        if(pipingGroup.children.length > 0) {
            pipingGroup.position.y += 0.5; // Lift slightly above pad surface
            return pipingGroup;
        }

        return null;
    },
    getTopCornersFromPadMesh(padMesh) {
        // Extract top corners from the pad mesh geometry
        if(!padMesh.geometry || !padMesh.geometry.attributes.position) return null;

        const positions = padMesh.geometry.attributes.position.array;
        const vertices = [];

        for(let i = 0; i < positions.length; i += 3) {
            vertices.push(new THREE.Vector3(
                positions[i],
                positions[i+1],
                positions[i+2]
            ));
        }

        // Find top vertices (highest y values)
        vertices.sort((a, b) => b.y - a.y);
        const topVertices = vertices.slice(0, 4);

        // Sort them by x and z to get corners
        topVertices.sort((a, b) => a.x - b.x);

        return {
            BL: topVertices[0], // Back-left
            BR: topVertices[1], // Back-right
            FR: topVertices[2], // Front-right
            FL: topVertices[3]  // Front-left
        };
    },
    createCollector(topCorners) {
        if(!topCorners || !topCorners.BL || !topCorners.BR) return null;

        // Create line between back-left and back-right
        const points = [
            new THREE.Vector3(topCorners.BL.x, topCorners.BL.y, topCorners.BL.z),
            new THREE.Vector3(topCorners.BR.x, topCorners.BR.y, topCorners.BR.z)
        ];

        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: document.getElementById('colPipe').value,
            linewidth: 2
        });

        return new THREE.Line(geometry, material);
    },
    createLaterals(pad, topCorners) {
        if(!topCorners || !pad.lat || !pad.emit) return null;

        // Create group for all laterals
        const lateralGroup = new THREE.Group();

        // Calculate lateral spacing in meters
        const latSpacing = pad.lat / 100;
        const emitSpacing = pad.emit / 100;

        // Get bounding box of top surface
        const minX = Math.min(topCorners.BL.x, topCorners.BR.x, topCorners.FR.x, topCorners.FL.x);
        const maxX = Math.max(topCorners.BL.x, topCorners.BR.x, topCorners.FR.x, topCorners.FL.x);
        const minZ = Math.min(topCorners.BL.z, topCorners.BR.z, topCorners.FR.z, topCorners.FL.z);
        const maxZ = Math.max(topCorners.BL.z, topCorners.BR.z, topCorners.FR.z, topCorners.FL.z);

        // Create laterals along X axis
        const lengthX = maxX - minX;
        const numLaterals = Math.floor(lengthX / latSpacing) + 1;

        for(let i = 0; i < numLaterals; i++) {
            const x = minX + (i * latSpacing);

            // Find Z positions at this X (linear interpolation)
            const zBack = this.interpolateZ(x, minX, maxX, minZ, minZ);
            const zFront = this.interpolateZ(x, minX, maxX, maxZ, maxZ);

            const points = [
                new THREE.Vector3(x, topCorners.BL.y, zBack),
                new THREE.Vector3(x, topCorners.FL.y, zFront)
            ];

            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({
                color: document.getElementById('colPipe').value,
                linewidth: 1
            });

            lateralGroup.add(new THREE.Line(geometry, material));
        }

        return lateralGroup;
    },
    interpolateZ(x, x1, x2, z1, z2) {
        // Linear interpolation
        return z1 + ((x - x1) / (x2 - x1)) * (z2 - z1);
    },
    createRain() {
        if(this.rainSystem) {
            this.scene.remove(this.rainSystem);
            this.rainSystem = null;
        }

        // Find bounding box of all pads
        const boundingBox = new THREE.Box3();
        this.meshes.forEach(mesh => {
            if(mesh.userData && mesh.userData.padId) {
                boundingBox.expandByObject(mesh);
            }
        });

        if(boundingBox.isEmpty()) {
            // Default rain area if no pads
            boundingBox.set(
                new THREE.Vector3(-100, 0, -100),
                new THREE.Vector3(100, 100, 100)
            );
        }

        // Expand bounding box for rain area
        const padding = 50;
        boundingBox.min.x -= padding;
        boundingBox.min.y = boundingBox.max.y + 20; // Start above the highest pad
        boundingBox.min.z -= padding;
        boundingBox.max.x += padding;
        boundingBox.max.z += padding;

        // Create rain particles
        const particleCount = 2000;
        const positions = new Float32Array(particleCount * 3);

        for(let i = 0; i < particleCount; i++) {
            positions[i * 3] = boundingBox.min.x + Math.random() * (boundingBox.max.x - boundingBox.min.x);
            positions[i * 3 + 1] = boundingBox.min.y + Math.random() * 20;
            positions[i * 3 + 2] = boundingBox.min.z + Math.random() * (boundingBox.max.z - boundingBox.min.z);
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const material = new THREE.PointsMaterial({
            color: 0x0ea5e9,
            size: 1.5,
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true
        });

        this.rainSystem = new THREE.Points(geometry, material);
        this.scene.add(this.rainSystem);
    },
    addLabels() {
        if(!this.showLabels) return;

        App.pads.forEach(pad => {
            this.addPadLabel(pad);
        });
    },
    addPadLabel(pad) {
        // Create a canvas for the label
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;

        // Draw background
        context.fillStyle = 'rgba(0, 0, 0, 0.7)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.roundRect(0, 0, canvas.width, canvas.height, 10);
        context.fill();

        // Draw text
        context.fillStyle = 'white';
        context.font = '24px Arial';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(`${pad.name} - ${pad.lift}`, 128, 32);

        // Create texture and material
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({
            map: texture,
            transparent: true
        });

        // Create sprite
        const sprite = new THREE.Sprite(spriteMaterial);

        // Position above the pad
        sprite.position.set(
            pad.x,
            pad.H * pad.lift + 5,
            pad.z
        );

        // Scale to appropriate size
        sprite.scale.set(30, 10, 1);

        // Add to scene
        this.scene.add(sprite);
        this.labels.push(sprite);
    },
    highlightSelected() {
        if(!this.isOpen || !App.selectedId) return;

        // Reset all materials
        this.meshes.forEach(mesh => {
            if(mesh.material && mesh.material.emissive) {
                mesh.material.emissive.set(0x000000);
                mesh.material.emissiveIntensity = 0;
            }
        });

        // Highlight selected pad
        const selectedMesh = this.meshes.find(mesh =>
            mesh.userData && mesh.userData.padId === parseInt(App.selectedId)
        );

        if(selectedMesh && selectedMesh.material && selectedMesh.material.emissive) {
            selectedMesh.material.emissive.set(0x3333ff);
            selectedMesh.material.emissiveIntensity = 0.3;
        }
    },
    toggleRain() {
        this.isRaining = !this.isRaining;
        document.getElementById('btnRain').classList.toggle('active', this.isRaining);

        if(this.isRaining) {
            this.createRain();
        } else if(this.rainSystem) {
            this.scene.remove(this.rainSystem);
            this.rainSystem = null;
        }

        this.updateDebugInfo(`Rain ${this.isRaining ? 'enabled' : 'disabled'}`);
    },
    toggleWireframe() {
        this.isWireframe = !this.isWireframe;
        document.getElementById('btnWireframe').classList.toggle('active', this.isWireframe);
        this.renderAll();
        this.updateDebugInfo(`Wireframe ${this.isWireframe ? 'enabled' : 'disabled'}`);
    },
    toggleLabels() {
        this.showLabels = !this.showLabels;
        document.getElementById('btnLabels').classList.toggle('active', this.showLabels);
        this.renderAll();
        this.updateDebugInfo(`Labels ${this.showLabels ? 'enabled' : 'disabled'}`);
    },
    resetCam() {
        if(!this.controls || !this.camera) return;

        this.controls.reset();
        this.camera.position.set(300, 250, 400);
        this.camera.lookAt(0, 0, 0);
        this.updateDebugInfo('Camera reset');
    },
    animate() {
        if(!this.isOpen) return;

        requestAnimationFrame(() => this.animate());

        if(this.controls) {
            this.controls.update();
        }

        // Animate rain if active
        if(this.isRaining && this.rainSystem) {
            const positions = this.rainSystem.geometry.attributes.position.array;
            const maxY = this.rainSystem.position.y + 50;

            for(let i = 0; i < positions.length; i += 3) {
                positions[i + 1] -= 1.5; // Move down

                // Reset if below ground
                if(positions[i + 1] < 0) {
                    positions[i + 1] = maxY + Math.random() * 20;
                    positions[i] = this.rainSystem.position.x - 100 + Math.random() * 200;
                    positions[i + 2] = this.rainSystem.position.z - 100 + Math.random() * 200;
                }
            }

            this.rainSystem.geometry.attributes.position.needsUpdate = true;
        }

        if(this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    },
    updateDebugInfo(message) {
        if(this.debugInfo) {
            this.debugInfo.textContent = `3D: ${message} | Pads: ${App.pads.length} | Meshes: ${this.meshes.length}`;
        }
    }
};

class ThreeDEngine {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.meshes = [];
        this.labels = [];
        this.isRaining = false;
        this.rainSystem = null;
        this.isWireframe = false;
        this.showLabels = true;
        this.debugInfo = null;

        // رنگ‌های مواد
        this.colors = {
            geomembrane: 0x1a1a1a,
            gcl: 0x8B4513,
            ore: 0xC4A574,
            water: 0x4fc3f7,
            liner: 0x2d5016
        };
    }

    /**
     * راه‌اندازی صحنه Three.js
     */
    init(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container not found:', containerId);
            return false;
        }

        // ایجاد صحنه
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);
        this.scene.fog = new THREE.Fog(0x1a1a2e, 500, 1500);

        // دوربین
        this.camera = new THREE.PerspectiveCamera(
            60,
            container.clientWidth / container.clientHeight,
            0.1,
            5000
        );
        this.camera.position.set(300, 250, 400);

        // رندرر
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // پاک کردن محتوای قبلی و اضافه کردن رندرر
        container.innerHTML = '';
        container.appendChild(this.renderer.domElement);

        // کنترل‌ها
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2 + 0.1;

        // نورپردازی
        this.setupLighting();

        // زمین (Terrain)
        this.createGround();

        // رویداد تغییر اندازه
        window.addEventListener('resize', () => this.onResize());

        // شروع حلقه انیمیشن
        this.animate();

        return true;
    }

    /**
     * تنظیم نورپردازی صحنه
     */
    setupLighting() {
        // نور محیطی
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        // نور خورشید
        const sunLight = new THREE.DirectionalLight(0xffffff, 0.8);
        sunLight.position.set(200, 300, 200);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 50;
        sunLight.shadow.camera.far = 1000;
        sunLight.shadow.camera.left = -300;
        sunLight.shadow.camera.right = 300;
        sunLight.shadow.camera.top = 300;
        sunLight.shadow.camera.bottom = -300;
        this.scene.add(sunLight);

        // نور مکمل
        const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.3);
        fillLight.position.set(-200, 100, -200);
        this.scene.add(fillLight);
    }

    /**
     * ایجاد زمین پایه
     */
    createGround() {
        const groundGeo = new THREE.PlaneGeometry(1000, 1000, 50, 50);

        // ایجاد توپوگرافی ساده
        const vertices = groundGeo.attributes.position.array;
        for (let i = 0; i < vertices.length; i += 3) {
            const x = vertices[i];
            const y = vertices[i + 1];
            // ایجاد ناهمواری‌های ملایم
            vertices[i + 2] = Math.sin(x / 100) * 5 + Math.cos(y / 100) * 5;
        }
        groundGeo.computeVertexNormals();

        const groundMat = new THREE.MeshStandardMaterial({
            color: 0x3d5c3d,
            roughness: 0.9,
            metalness: 0.1
        });

        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
        this.meshes.push(ground);
    }

    /**
     * ایجاد پد هیپ لیچینگ با تمام لایه‌ها
     */
    createPad(padData) {
        const group = new THREE.Group();
        group.userData = { padId: padData.id, type: 'pad' };

        const { L, W, H, x, z, slopeDeg, bounds } = padData;
        const slopeRad = THREE.MathUtils.degToRad(slopeDeg);

        // 1. لایه ژئوممبران (Geomembrane) - کف پد
        const geomembraneGeo = new THREE.BoxGeometry(L + 4, 0.2, W + 4);
        const geomembraneMat = new THREE.MeshStandardMaterial({
            color: this.colors.geomembrane,
            roughness: 0.3,
            metalness: 0.7
        });
        const geomembrane = new THREE.Mesh(geomembraneGeo, geomembraneMat);
        geomembrane.position.set(x + L/2, -0.1, z + W/2);
        geomembrane.receiveShadow = true;
        group.add(geomembrane);

        // 2. لایه رسی (GCL - Geosynthetic Clay Liner)
        const gclGeo = new THREE.BoxGeometry(L + 2, 0.3, W + 2);
        const gclMat = new THREE.MeshStandardMaterial({
            color: this.colors.gcl,
            roughness: 0.8,
            metalness: 0.0
        });
        const gcl = new THREE.Mesh(gclGeo, gclMat);
        gcl.position.set(x + L/2, 0.15, z + W/2);
        gcl.receiveShadow = true;
        group.add(gcl);

        // 3. بدنه اصلی هیپ (Ore Heap) با شیب دیواره‌ها
        const heapShape = this.createHeapShape(L, W, H, slopeRad, bounds);
        const heapGeo = new THREE.ExtrudeGeometry(heapShape, {
            depth: H,
            bevelEnabled: false
        });

        const heapMat = new THREE.MeshStandardMaterial({
            color: this.colors.ore,
            roughness: 0.9,
            metalness: 0.1,
            wireframe: this.isWireframe
        });

        const heap = new THREE.Mesh(heapGeo, heapMat);
        heap.rotation.x = Math.PI; // معکوس کردن برای قرارگیری صحیح
        heap.position.set(x, 0.45, z);
        heap.castShadow = true;
        heap.receiveShadow = true;
        heap.userData = { padId: padData.id, type: 'heap' };
        group.add(heap);

        // 4. سیستم آبیاری (Laterals & Emitters)
        this.createIrrigationSystem(group, L, W, x, z, H, padData.lat, padData.emit);

        // 5. برچسب نام پد
        if (this.showLabels) {
            this.createLabel(group, padData.name || `پد ${padData.id}`, x + L/2, H + 5, z + W/2);
        }

        this.scene.add(group);
        this.meshes.push(group);

        return group;
    }

    /**
     * ایجاد شکل هندسی هیپ با شیب‌های مشخص
     */
    createHeapShape(L, W, H, slopeRad, bounds) {
        const shape = new THREE.Shape();

        // محاسبه offset ناشی از شیب
        const offsetX = H / Math.tan(slopeRad);
        const offsetZ = H / Math.tan(slopeRad);

        // شروع از گوشه پایین چپ
        shape.moveTo(0, 0);

        // ضلع چپ (بررسی نوع مرز)
        if (bounds?.L === 'attach') {
            shape.lineTo(0, W);
        } else if (bounds?.L === 'wall') {
            shape.lineTo(0, W);
        } else {
            shape.lineTo(offsetX, 0);
        }

        // ضلع بالا
        shape.lineTo(L, W);

        // ضلع راست
        if (bounds?.R === 'attach') {
            shape.lineTo(L, 0);
        } else if (bounds?.R === 'wall') {
            shape.lineTo(L, 0);
        } else {
            shape.lineTo(L - offsetX, W);
        }

        // بازگشت به نقطه شروع
        shape.lineTo(0, 0);

        return shape;
    }

    /**
     * ایجاد سیستم آبیاری (لاترال‌ها و امیترها)
     */
    createIrrigationSystem(group, L, W, x, z, H, lateralSpacing, emitterSpacing) {
        const lateralMat = new THREE.MeshStandardMaterial({
            color: 0x2196f3,
            roughness: 0.4,
            metalness: 0.3
        });

        const emitterMat = new THREE.MeshStandardMaterial({
            color: 0xff5722,
            emissive: 0xff5722,
            emissiveIntensity: 0.5
        });

        // ایجاد لاترال‌ها
        const numLaterals = Math.floor(W / lateralSpacing);
        for (let i = 0; i < numLaterals; i++) {
            const latZ = z + (i + 0.5) * lateralSpacing;

            // لوله لاترال
            const lateralGeo = new THREE.CylinderGeometry(0.1, 0.1, L, 8);
            const lateral = new THREE.Mesh(lateralGeo, lateralMat);
            lateral.rotation.z = Math.PI / 2;
            lateral.position.set(x + L/2, H + 0.5, latZ);
            group.add(lateral);

            // امیترها روی لاترال
            const numEmitters = Math.floor(L / emitterSpacing);
            for (let j = 0; j < numEmitters; j++) {
                const emitX = x + (j + 0.5) * emitterSpacing;

                const emitterGeo = new THREE.SphereGeometry(0.15, 8, 8);
                const emitter = new THREE.Mesh(emitterGeo, emitterMat);
                emitter.position.set(emitX, H + 0.65, latZ);
                group.add(emitter);
            }
        }
    }

    /**
     * ایجاد برچسب متنی برای پد
     */
    createLabel(group, text, x, y, z) {
        // ایجاد کانواس برای متن
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;

        context.fillStyle = '#ffffff';
        context.font = 'Bold 24px Vazirmatn, Arial';
        context.textAlign = 'center';
        context.fillText(text, 128, 40);

        const texture = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(20, 5, 1);
        sprite.position.set(x, y, z);

        group.add(sprite);
        this.labels.push(sprite);
    }

    /**
     * حذف پد از صحنه
     */
    removePad(padId) {
        const toRemove = this.meshes.filter(m => m.userData.padId === padId);
        toRemove.forEach(mesh => {
            this.scene.remove(mesh);
            if (mesh.geometry) mesh.geometry.dispose();
            if (mesh.material) mesh.material.dispose();
        });
        this.meshes = this.meshes.filter(m => m.userData.padId !== padId);
    }

    /**
     * پاک کردن تمام پدها
     */
    clearAll() {
        this.meshes.forEach(mesh => {
            this.scene.remove(mesh);
            if (mesh.geometry) mesh.geometry.dispose();
            if (mesh.material) mesh.material.dispose();
        });
        this.meshes = [];
        this.labels = [];
    }

    /**
     * ایجاد سیستم بارش (شبیه‌سازی جریان محلول)
     */
    createRain() {
        if (this.rainSystem) return;

        const rainCount = 5000;
        const rainGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(rainCount * 3);

        for (let i = 0; i < rainCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 400;
            positions[i + 1] = Math.random() * 100;
            positions[i + 2] = (Math.random() - 0.5) * 400;
        }

        rainGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const rainMat = new THREE.PointsMaterial({
            color: 0x4fc3f7,
            size: 0.3,
            transparent: true,
            opacity: 0.6
        });

        this.rainSystem = new THREE.Points(rainGeo, rainMat);
        this.rainSystem.position.y = 50;
        this.scene.add(this.rainSystem);
    }

    /**
     * بروزرسانی انیمیشن بارش
     */
    updateRain() {
        if (!this.rainSystem) return;

        const positions = this.rainSystem.geometry.attributes.position.array;
        const maxY = this.rainSystem.position.y + 50;

        for (let i = 0; i < positions.length; i += 3) {
            positions[i + 1] -= 1.5;

            if (positions[i + 1] < 0) {
                positions[i + 1] = maxY + Math.random() * 20;
                positions[i] = this.rainSystem.position.x - 100 + Math.random() * 200;
                positions[i + 2] = this.rainSystem.position.z - 100 + Math.random() * 200;
            }
        }

        this.rainSystem.geometry.attributes.position.needsUpdate = true;
    }

    /**
     * مدیریت تغییر اندازه پنجره
     */
    onResize() {
        const container = this.renderer.domElement.parentElement;
        if (!container) return;

        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }

    /**
     * بروزرسانی تم (شب/روز)
     */
    updateTheme(isDark) {
        if (isDark) {
            this.scene.background = new THREE.Color(0x1a1a2e);
            this.scene.fog.color.set(0x1a1a2e);
        } else {
            this.scene.background = new THREE.Color(0x87ceeb);
            this.scene.fog.color.set(0x87ceeb);
        }
    }

    /**
     * حلقه اصلی انیمیشن
     */
    animate() {
        requestAnimationFrame(() => this.animate());

        if (this.controls) {
            this.controls.update();
        }

        this.updateRain();

        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
}

// Export برای استفاده در ماژول‌های دیگر
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThreeDEngine;
}
