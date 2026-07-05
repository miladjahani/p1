/**
 * Heap Master Pro - Three.js 3D Engine Module
 * موتور سه‌بعدی صنعتی برای نمایش پدهای هیپ لیچینگ
 * شامل: ژئوممبران، لایه‌های رسی، انیمیشن جریان سیال، ابزارهای اندازه‌گیری
 */

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
