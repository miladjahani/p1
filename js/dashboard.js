/**
 * Heap Master Pro - Dashboard & Charts Module
 * مدیریت داشبورد، نمودارها و گزارش‌ها
 * استفاده از Chart.js برای رسم نمودارهای پیشرفت تولید و مصرف اسید
 */

/**
 * Heap Master Pro - Dashboard & Charts Module
 * مدیریت داشبورد، نمودارها و گزارش‌ها
 * استفاده از Chart.js برای رسم نمودارهای پیشرفت تولید و مصرف اسید
 */

// --- CORE APP LOGIC ---
const App = {
    pads: [],
    selectedId: null,
    terrain: { sx: -2, sy: 1 },
    init() {
        const savedTheme = localStorage.getItem('heapMasterTheme');
        if(savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
            document.getElementById('themeToggle').innerHTML = '<i class="fas fa-sun"></i>';
        }

        document.getElementById('themeToggle').addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('heapMasterTheme', isDark ? 'dark' : 'light');
            document.getElementById('themeToggle').innerHTML = isDark ?
                '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
            View3D.updateTheme();
        });

        document.getElementById('menuToggle').addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('open');
        });

        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
            });
        });

        const inputs = ['inpName','inpL','inpW','inpH','inpX','inpZ','inpLat','inpEmit','inpIrrRate','inpSlopeDeg','inpGrade','inpRec','inpDens'];
        inputs.forEach(id => document.getElementById(id).addEventListener('input', () => this.updateFromDOM()));
        const selects = ['bTypeL', 'bTypeR', 'bTypeF', 'bTypeB'];
        selects.forEach(id => document.getElementById(id).addEventListener('change', () => this.updateFromDOM()));

        // Add debug info toggle
        document.querySelector('.fab-help').addEventListener('click', () => {
            const debug = document.getElementById('debugInfo');
            debug.style.display = debug.style.display === 'none' || !debug.style.display ? 'block' : 'none';
        });

        this.createPad({
            x:0, z:0, L:200, W:100, H:15, lift:1,
            slopeDeg: 37,
            grade: 0.7,
            rec: 80,
            dens: 1.7,
            irrRate: 80,
            lat: 50,
            emit: 40
        });

        document.getElementById('inpSx').value = this.terrain.sx;
        document.getElementById('inpSy').value = this.terrain.sy;

        View3D.init();
    },
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        document.getElementById('toast-message').textContent = message;
        toast.className = 'toast ' + type;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    },
    createPad(props) {
        const id = Date.now() + Math.floor(Math.random() * 1000);
        const p = {
            id: id,
            name: props.name || `پد ${this.pads.length + 1}`,
            x: props.x, z: props.z,
            L: props.L, W: props.W, H: props.H,
            lift: props.lift,
            slopeDeg: props.slopeDeg || 37,
            bounds: {
                L: props.bounds?.L || 'free',
                R: props.bounds?.R || 'free',
                F: props.bounds?.F || 'free',
                B: props.bounds?.B || 'free'
            },
            lat: props.lat || 50,
            emit: props.emit || 40,
            irrRate: props.irrRate || 80,
            grade: props.grade || 0.7,
            rec: props.rec || 80,
            dens: props.dens || 1.7
        };
        this.pads.push(p);
        this.renderPadSelect();
        this.selectPad(id.toString());

        // Add a small delay before rendering 3D to ensure DOM is updated
        setTimeout(() => {
            if(View3D.scene) View3D.renderAll();
        }, 100);

        const padSelect = document.getElementById('padSelect');
        padSelect.classList.add('pulse');
        setTimeout(() => padSelect.classList.remove('pulse'), 500);

        this.showToast(`پد "${p.name}" با موفقیت ایجاد شد`);
    },
    addPad(mode) {
        if(!this.selectedId) return;
        const ref = this.pads.find(p => p.id == this.selectedId);
        if(!ref) return;

        // Determine the bounds for the new pad based on adjacency
        let newBounds = { L: 'free', R: 'free', F: 'free', B: 'free' };

        if(mode === 'right') {
            newBounds.L = 'attach'; // Left side attaches to reference pad
        } else if(mode === 'front') {
            newBounds.B = 'attach'; // Back side attaches to reference pad
        }

        let props = {
            ...ref, name: '',
            bounds: newBounds,
            slopeDeg: ref.slopeDeg,
            grade: ref.grade,
            rec: ref.rec,
            dens: ref.dens,
            irrRate: ref.irrRate,
            lat: ref.lat,
            emit: ref.emit
        };

        if(mode === 'right') {
            props.x = ref.x + ref.L;
            props.z = ref.z;
            props.lift = 1;
            props.name = `${ref.name} - راست`;
        } else if(mode === 'front') {
            props.x = ref.x;
            props.z = ref.z + ref.W;
            props.lift = 1;
            props.name = `${ref.name} - جلو`;
        } else if(mode === 'top') {
            props.x = ref.x;
            props.z = ref.z;
            props.lift = ref.lift + 1;
            props.name = `طبقه ${props.lift} - ${ref.name}`;
        }

        // Update reference pad boundaries if attaching
        if(mode === 'right' || mode === 'front') {
            const updatedRef = {...ref};
            if(mode === 'right') {
                updatedRef.bounds.R = 'attach'; // Right side now attaches to new pad
            } else if(mode === 'front') {
                updatedRef.bounds.F = 'attach'; // Front side now attaches to new pad
            }
            const refIndex = this.pads.findIndex(p => p.id === ref.id);
            if(refIndex !== -1) {
                this.pads[refIndex] = updatedRef;
            }
        }

        this.createPad(props);
    },
    deletePad() {
        if(this.pads.length <= 1) {
            this.showToast('حداقل یک پد باید وجود داشته باشد', 'error');
            return;
        }

        if(!confirm("آیا مطمئن هستید که می‌خواهید این پد را حذف کنید؟")) return;

        const padToDelete = this.pads.find(p => p.id == this.selectedId);
        if(!padToDelete) return;

        const padName = padToDelete.name;

        // Find adjacent pads that might need boundary updates
        this.pads.forEach(p => {
            if(p.id === padToDelete.id || p.lift !== padToDelete.lift) return;

            // Check if p is attached to padToDelete and update boundaries
            if(p.x + p.L === padToDelete.x && p.z === padToDelete.z && p.bounds.R === 'attach') {
                const idx = this.pads.findIndex(x => x.id === p.id);
                if(idx !== -1) {
                    const updatedP = {...this.pads[idx]};
                    updatedP.bounds.R = 'free';
                    this.pads[idx] = updatedP;
                }
            }
            if(p.x === padToDelete.x + padToDelete.L && p.z === padToDelete.z && p.bounds.L === 'attach') {
                const idx = this.pads.findIndex(x => x.id === p.id);
                if(idx !== -1) {
                    const updatedP = {...this.pads[idx]};
                    updatedP.bounds.L = 'free';
                    this.pads[idx] = updatedP;
                }
            }
            if(p.x === padToDelete.x && p.z + p.W === padToDelete.z && p.bounds.F === 'attach') {
                const idx = this.pads.findIndex(x => x.id === p.id);
                if(idx !== -1) {
                    const updatedP = {...this.pads[idx]};
                    updatedP.bounds.F = 'free';
                    this.pads[idx] = updatedP;
                }
            }
            if(p.x === padToDelete.x && p.z === padToDelete.z + padToDelete.W && p.bounds.B === 'attach') {
                const idx = this.pads.findIndex(x => x.id === p.id);
                if(idx !== -1) {
                    const updatedP = {...this.pads[idx]};
                    updatedP.bounds.B = 'free';
                    this.pads[idx] = updatedP;
                }
            }
        });

        this.pads = this.pads.filter(p => p.id != this.selectedId);
        this.renderPadSelect();
        if(this.pads.length > 0) {
            this.selectPad(this.pads[this.pads.length-1].id.toString());
        }
        View3D.renderAll();

        this.showToast(`پد "${padName}" با موفقیت حذف شد`);
    },
    selectPad(id) {
        this.selectedId = id;
        const p = this.pads.find(x => x.id == id);
        if(!p) return;

        const set = (k, v) => document.getElementById(k).value = v;
        set('inpName', p.name);
        set('inpL', p.L); set('inpW', p.W); set('inpH', p.H);
        set('inpX', p.x); set('inpZ', p.z);
        set('inpLift', p.lift);
        set('inpLat', p.lat); set('inpEmit', p.emit);
        set('inpIrrRate', p.irrRate);
        set('inpSlopeDeg', p.slopeDeg);
        set('inpGrade', p.grade);
        set('inpRec', p.rec);
        set('inpDens', p.dens);
        set('bTypeL', p.bounds.L); set('bTypeR', p.bounds.R);
        set('bTypeF', p.bounds.F); set('bTypeB', p.bounds.B);
        document.getElementById('padSelect').value = id;

        this.calcStats();

        // Update 3D view highlighting
        if(View3D.scene) {
            View3D.renderAll();
            View3D.highlightSelected();
        }
    },
    renderPadSelect() {
        const sel = document.getElementById('padSelect');
        sel.innerHTML = '';
        this.pads.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.text = `[${p.lift}] ${p.name} (${p.L}×${p.W}×${p.H}m)`;
            if(p.id == this.selectedId) opt.selected = true;
            sel.appendChild(opt);
        });
    },
    updateFromDOM() {
        if(!this.selectedId) return;
        const p = this.pads.find(x => x.id == this.selectedId);
        if(!p) return;

        const get = (k) => document.getElementById(k).value;
        const num = (k) => parseFloat(get(k)) || 0;

        p.name = get('inpName');
        p.L = num('inpL'); p.W = num('inpW'); p.H = num('inpH');
        p.x = num('inpX'); p.z = num('inpZ');
        p.lat = num('inpLat'); p.emit = num('inpEmit');
        p.irrRate = num('inpIrrRate');
        p.slopeDeg = num('inpSlopeDeg');
        p.grade = num('inpGrade');
        p.rec = num('inpRec');
        p.dens = num('inpDens');
        p.bounds.L = get('bTypeL'); p.bounds.R = get('bTypeR');
        p.bounds.F = get('bTypeF'); p.bounds.B = get('bTypeB');

        this.renderPadSelect();
        this.calcStats();

        if(View3D.scene) {
            View3D.renderAll();
        }
    },
    updateGlobalSlope() {
        this.terrain.sx = parseFloat(document.getElementById('inpSx').value) || 0;
        this.terrain.sy = parseFloat(document.getElementById('inpSy').value) || 0;
        this.calcStats();
        if(View3D.scene) {
            View3D.renderAll();
        }
    },
    getAdjacentPads(pad) {
        const adjacent = {
            left: null,
            right: null,
            front: null,
            back: null
        };

        this.pads.forEach(p => {
            if(p.id === pad.id || p.lift !== pad.lift) return;

            // Check if p is to the left of pad
            if(p.x + p.L === pad.x && p.z === pad.z && p.W === pad.W) {
                adjacent.left = p;
            }

            // Check if p is to the right of pad
            if(p.x === pad.x + pad.L && p.z === pad.z && p.W === pad.W) {
                adjacent.right = p;
            }

            // Check if p is in front of pad (positive z direction)
            if(p.x === pad.x && p.z === pad.z + pad.W && p.L === pad.L) {
                adjacent.front = p;
            }

            // Check if p is behind pad (negative z direction)
            if(p.x === pad.x && p.z + p.W === pad.z && p.L === pad.L) {
                adjacent.back = p;
            }
        });

        return adjacent;
    },
    calcStats() {
        if(!this.selectedId) return;
        const p = this.pads.find(x => x.id == this.selectedId);
        if(!p) return;

        const num = id => parseFloat(document.getElementById(id).value) || 0;
        const adjacent = this.getAdjacentPads(p);

        const H_avg = p.H;
        const slope_deg = p.slopeDeg;
        const L = p.L;
        const W = p.W;
        const sx = this.terrain.sx / 100;
        const sy = this.terrain.sy / 100;
        const dens = p.dens;
        const grade = p.grade / 100;
        const rec = p.rec / 100;
        const irrRate = p.irrRate;
        const latSpace = p.lat / 100;
        const emitSpace = p.emit / 100;

        const slope_ratio = 1 / Math.tan(slope_deg * Math.PI / 180);
        const crest_elev = H_avg;
        const hL = L/2, hW = W/2;

        const getY = (x, z) => x * sx + z * sy;

        // Corner ground heights
        const hTL = crest_elev - getY(-hL, -hW);
        const hTR = crest_elev - getY(hL, -hW);
        const hBR = crest_elev - getY(hL, hW);
        const hBL = crest_elev - getY(-hL, hW);

        // Runs based on boundary types and adjacent pads
        const getRun = (height, boundaryType, isAdjacent) => {
            if(boundaryType === 'wall') return 0;
            if(boundaryType === 'attach' && isAdjacent) {
                // Reduced slope effect when attached to another pad
                return height * slope_ratio * 0.5;
            }
            return height * slope_ratio;
        };

        const runTL = getRun(hTL, p.bounds.L, adjacent.left);
        const runTR = getRun(hTR, p.bounds.R, adjacent.right);
        const runBR = getRun(hBR, p.bounds.F, adjacent.front);
        const runBL = getRun(hBL, p.bounds.B, adjacent.back);

        // Top dimensions
        let topL = Math.max(0, L - (runTL + runTR));
        let topW = Math.max(0, W - (runBL + runBR));

        // Adjust for attached boundaries
        if(p.bounds.L === 'attach' && adjacent.left) {
            // Additional adjustment needed for attached pads
            topL = Math.min(topL, L - 0.1); // Small reduction
        }

        if(p.bounds.R === 'attach' && adjacent.right) {
            topL = Math.min(topL, L - 0.1);
        }

        if(p.bounds.F === 'attach' && adjacent.front) {
            topW = Math.min(topW, W - 0.1);
        }

        if(p.bounds.B === 'attach' && adjacent.back) {
            topW = Math.min(topW, W - 0.1);
        }

        // Calculate areas
        const baseArea = L * W;
        const topArea = topL * topW;

        // Prismoidal formula for volume
        const midL = (L + topL) / 2;
        const midW = (W + topW) / 2;
        const midArea = midL * midW;
        const vol = (H_avg / 6) * (baseArea + topArea + 4 * midArea);

        // Calculate mass and recoverable copper
        const mass = vol * dens;
        const cu = mass * grade * rec;
        const acid = mass * 0.015;

        // Piping calculations
        const numLat = latSpace > 0 ? Math.floor(topL / latSpace) : 0;
        const latLen = numLat * topW;
        const emitCount = emitSpace > 0 ? Math.floor(latLen / emitSpace) : 0;
        const flow_m3_hr = (emitCount * irrRate * 60) / 1000000;
        const pipeLen = topL + latLen;

        // Hip (edge) lengths
        const dist = (dx, dz, dy) => Math.sqrt(dx*dx + dz*dz + dy*dy);

        const hipFL = dist(runBL, runTL, hTL);
        const hipFR = dist(runBR, runTR, hTR);
        const hipBL = dist(runBL, runTL, hBL);
        const hipBR = dist(runBR, runTR, hBR);

        // UI Update functions
        const f = n => Math.round(n).toLocaleString('fa');
        const f2 = n => n.toFixed(2);

        // Summary Tab
        document.getElementById('resCu').innerText = f2(cu);
        document.getElementById('resVol').innerText = f(vol);
        document.getElementById('resAcid').innerText = f(acid);
        document.getElementById('resFlow').innerText = f2(flow_m3_hr);

        document.getElementById('tblMass').innerText = f(mass) + " تن";
        document.getElementById('tblBaseArea').innerText = f(baseArea) + " متر مربع";
        document.getElementById('tblTopArea').innerText = f(topArea) + " متر مربع";
        document.getElementById('tblTopDims').innerText = `${f2(topL)} × ${f2(topW)} متر`;
        document.getElementById('tblEmit').innerText = f(emitCount) + " عدد";

        // Geometry Tab
        document.getElementById('resH_FL').innerText = f2(hTL) + " متر";
        document.getElementById('resH_FR').innerText = f2(hTR) + " متر";
        document.getElementById('resH_BL').innerText = f2(hBL) + " متر";
        document.getElementById('resH_BR').innerText = f2(hBR) + " متر";

        document.getElementById('resHip_FL').innerText = f2(hipFL) + " متر";
        document.getElementById('resHip_FR').innerText = f2(hipFR) + " متر";
        document.getElementById('resHip_BL').innerText = f2(hipBL) + " متر";
        document.getElementById('resHip_BR').innerText = f2(hipBR) + " متر";

        // Visual corners
        document.getElementById('corner-FL').innerText = f2(hTL) + " متر";
        document.getElementById('corner-FR').innerText = f2(hTR) + " متر";
        document.getElementById('corner-BL').innerText = f2(hBL) + " متر";
        document.getElementById('corner-BR').innerText = f2(hBR) + " متر";

        // Technical Tab
        document.getElementById('tblMassTech').innerText = f(mass) + " تن";
        document.getElementById('tblVol').innerText = f(vol) + " متر مکعب";
        document.getElementById('tblCu').innerText = f2(cu) + " تن";
        document.getElementById('tblAcid').innerText = f(acid) + " تن";
        document.getElementById('tblGrade').innerText = p.grade * 100 + "%";
        document.getElementById('tblRec').innerText = p.rec * 100 + "%";
        document.getElementById('tblDens').innerText = p.dens + " تن/متر مکعب";

        // Irrigation Tab
        document.getElementById('tblFlow').innerText = f2(flow_m3_hr) + " متر مکعب/ساعت";
        document.getElementById('tblEmitterCount').innerText = f(emitCount) + " عدد";
        document.getElementById('tblCol').innerText = f(topL) + " متر";
        document.getElementById('tblLat').innerText = f(latLen) + " متر";
        document.getElementById('tblPipe').innerText = f(pipeLen) + " متر";
        document.getElementById('tblLatSpace').innerText = p.lat + " سانتی‌متر";
        document.getElementById('tblEmitSpace').innerText = p.emit + " سانتی‌متر";
        document.getElementById('tblIrrRate').innerText = p.irrRate + " میلی‌لیتر/دقیقه";

        return {
            L, W, H_avg, slope_deg, baseArea, topArea, topL, topW, vol, mass, cu, acid,
            hTL, hTR, hBR, hBL,
            flow_m3_hr, pipeLen, emitCount
        };
    }
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    App.init();

    // Set up toast dismissal
    document.getElementById('toast').addEventListener('click', function() {
        this.classList.remove('show');
    });

    // Initial debug info
    if (document.getElementById('debugInfo')) {
        document.getElementById('debugInfo').textContent = '3D engine ready';
    }
});

class DashboardManager {
    constructor() {
        this.charts = {};
        this.currentPadId = null;
    }

    /**
     * راه‌اندازی داشبورد
     */
    init() {
        console.log('Dashboard initialized');
    }

    /**
     * ایجاد نمودار پیشرفت تولید ماهانه
     */
    createProductionChart(canvasId, monthlyData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart if any
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const months = monthlyData.map(d => `ماه ${d.month}`);
        const cathodeValues = monthlyData.map(d => d.cathode_tonnes);
        const oreValues = monthlyData.map(d => d.ore_processed_tonnes);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'کاتد مس (تن)',
                        data: cathodeValues,
                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'سنگ معدن پردازش شده (هزار تن)',
                        data: oreValues,
                        type: 'line',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    tooltip: {
                        rtl: true,
                        titleFont: {
                            family: 'Vazirmatn'
                        },
                        bodyFont: {
                            family: 'Vazirmatn'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'کاتد مس (تن)',
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        },
                        title: {
                            display: true,
                            text: 'سنگ معدن (هزار تن)',
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * ایجاد نمودار مصرف اسید
     */
    createAcidConsumptionChart(canvasId, dailyData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const days = dailyData.map((_, i) => `روز ${i + 1}`);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: days,
                datasets: [{
                    label: 'مصرف اسید (تن)',
                    data: dailyData,
                    borderColor: 'rgba(244, 63, 94, 1)',
                    backgroundColor: 'rgba(244, 63, 94, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    tooltip: {
                        rtl: true,
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y.toFixed(2) + ' تن';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'مصرف اسید (تن)',
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * ایجاد نمودار بازیابی بر اساس پارامترها
     */
    createRecoveryChart(canvasId, flowRates, recoveries) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: flowRates.map(f => f + ' L/m²/h'),
                datasets: [{
                    label: 'بازیابی مس (%)',
                    data: recoveries,
                    borderColor: 'rgba(245, 158, 11, 1)',
                    backgroundColor: 'rgba(245, 158, 11, 0.2)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(245, 158, 11, 1)',
                    pointRadius: 5,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    tooltip: {
                        rtl: true,
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y.toFixed(2) + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'دبی آبیاری',
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'بازیابی (%)',
                            font: {
                                family: 'Vazirmatn'
                            }
                        },
                        min: 70,
                        max: 95
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * بروزرسانی KPI های داشبورد
     */
    updateKPIs(kpiData) {
        const kpiElements = {
            'kpi-tonnage': kpiData.tonnage,
            'kpi-recovery': kpiData.recovery,
            'kpi-cathode': kpiData.cathode,
            'kpi-opex': kpiData.opex
        };

        for (const [id, value] of Object.entries(kpiElements)) {
            const el = document.getElementById(id);
            if (el && value !== undefined) {
                el.textContent = this.formatNumber(value);

                // Add animation
                el.classList.add('pulse');
                setTimeout(() => el.classList.remove('pulse'), 500);
            }
        }
    }

    /**
     * فرمت کردن اعداد بزرگ
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(2) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toFixed(2);
    }

    /**
     * Export داده‌های پروژه به JSON
     */
    exportProject(pads, settings) {
        const projectData = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            pads: pads,
            settings: settings,
            metadata: {
                totalPads: pads.length,
                projectName: settings.projectName || 'Heap Master Project'
            }
        };

        const jsonString = JSON.stringify(projectData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `heap-master-project-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        return true;
    }

    /**
     * Import داده‌های پروژه از JSON
     */
    importProject(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                try {
                    const projectData = JSON.parse(e.target.result);

                    // Validate structure
                    if (!projectData.pads || !Array.isArray(projectData.pads)) {
                        throw new Error('Invalid project file structure');
                    }

                    resolve(projectData);
                } catch (error) {
                    reject(new Error('Failed to parse project file: ' + error.message));
                }
            };

            reader.onerror = () => {
                reject(new Error('Failed to read file'));
            };

            reader.readAsText(file);
        });
    }

    /**
     * ذخیره تنظیمات در localStorage
     */
    saveSettings(settings) {
        try {
            localStorage.setItem('heapMasterSettings', JSON.stringify(settings));
            return true;
        } catch (error) {
            console.error('Failed to save settings:', error);
            return false;
        }
    }

    /**
     * بارگذاری تنظیمات از localStorage
     */
    loadSettings() {
        try {
            const saved = localStorage.getItem('heapMasterSettings');
            return saved ? JSON.parse(saved) : null;
        } catch (error) {
            console.error('Failed to load settings:', error);
            return null;
        }
    }

    /**
     * پاک کردن تمام نمودارها
     */
    destroyAllCharts() {
        for (const chartId in this.charts) {
            if (this.charts[chartId]) {
                this.charts[chartId].destroy();
            }
        }
        this.charts = {};
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}
