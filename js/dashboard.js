/**
 * Heap Master Pro - Dashboard & Charts Module
 * مدیریت داشبورد، نمودارها و گزارش‌ها
 * استفاده از Chart.js برای رسم نمودارهای پیشرفت تولید و مصرف اسید
 */

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
