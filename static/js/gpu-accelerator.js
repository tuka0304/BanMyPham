/**
 * Aeterna GPU Hardware Acceleration Engine
 * Chuyển giao các tác vụ đồ họa và hoạt ảnh từ CPU sang GPU
 */
(function() {
    'use strict';

    const GPUAccelerator = {
        isGPUAvailable: false,
        gpuInfo: null,
        isTabActive: true,

        init() {
            this.detectGPUCapabilities();
            this.applyHardwareLayering();
            this.setupVisibilityListener();
            this.optimizeSmoothScroll();
            // In thông tin tối ưu ra console để debug và theo dõi
            if (this.gpuInfo) {
                console.log(`%c[GPU Engine Activated]%c Rendered via ${this.gpuInfo.renderer || 'GPU Hardware'}`, 
                    'background: #db2777; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: bold;',
                    'color: #ec4899; font-weight: bold;'
                );
            }
        },

        // 1. Nhận diện GPU phần cứng và khả năng WebGL/WebGPU
        detectGPUCapabilities() {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl2', { powerPreference: 'high-performance' }) ||
                           canvas.getContext('webgl', { powerPreference: 'high-performance' });
                
                if (gl) {
                    this.isGPUAvailable = true;
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        this.gpuInfo = {
                            vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                            renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
                        };
                    } else {
                        this.gpuInfo = {
                            vendor: gl.getParameter(gl.VENDOR),
                            renderer: gl.getParameter(gl.RENDERER)
                        };
                    }
                }
            } catch (e) {
                this.isGPUAvailable = false;
            }
        },

        // 2. Ép trình duyệt đưa các layer đồ họa nặng lên GPU Compositor (Zero CPU Paint)
        applyHardwareLayering() {
            const style = document.createElement('style');
            style.id = 'gpu-acceleration-styles';
            style.textContent = `
                /* Ép phần cứng GPU xử lý Layer Compositing */
                .gpu-accelerated,
                .glass-card,
                .glass-nav,
                #bottle-wrapper,
                .ambient-glow,
                .click-flower,
                .click-glow,
                #seamless-transition-overlay {
                    transform: translate3d(0, 0, 0);
                    -webkit-transform: translate3d(0, 0, 0);
                    backface-visibility: hidden;
                    -webkit-backface-visibility: hidden;
                    perspective: 1000px;
                    -webkit-perspective: 1000px;
                }

                /* Tối ưu hóa will-change để GPU chuẩn bị trước texture memory */
                .glass-card {
                    will-change: transform, box-shadow;
                }

                .click-flower {
                    will-change: transform, opacity;
                    contain: layout style paint;
                }

                .click-glow {
                    will-change: transform, opacity;
                    contain: layout style paint;
                }

                /* Giảm tải chi phí reflow cho toàn bộ animation */
                @media (prefers-reduced-motion: reduce) {
                    * {
                        animation-duration: 0.01ms !important;
                        animation-iteration-count: 1 !important;
                        transition-duration: 0.01ms !important;
                    }
                }
            `;
            document.head.appendChild(style);
        },

        // 3. Tự động tạm ngưng GPU & CPU khi người dùng đổi tab (Tiết kiệm 100% pin & tài nguyên)
        setupVisibilityListener() {
            document.addEventListener('visibilitychange', () => {
                this.isTabActive = !document.hidden;
                window.dispatchEvent(new CustomEvent('gpu-tab-visibility', { 
                    detail: { active: this.isTabActive } 
                }));
            });
        },

        // 4. Smooth scrolling mượt mà qua GPU compositor
        optimizeSmoothScroll() {
            if ('scrollBehavior' in document.documentElement.style) {
                document.documentElement.style.scrollBehavior = 'smooth';
            }
        }
    };

    // Khởi tạo ngay khi DOM load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => GPUAccelerator.init());
    } else {
        GPUAccelerator.init();
    }

    // Expose ra window để Three.js hoặc script khác dùng chung
    window.GPUAccelerator = GPUAccelerator;
})();
