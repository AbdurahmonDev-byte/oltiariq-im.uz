/* OLTIARIQ IM — Geometrik Lattice fon animatsiyasi (sof JS, framework'siz)
   Kursor va teginish reaksiyasi, doim harakatlanuvchi zarralar. */
(function () {
    var canvas = document.getElementById('lattice-canvas');
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var W = 0, H = 0, dpr = 1;
    var points = [];
    var mouse = { x: -1000, y: -1000, tx: -1000, ty: -1000 };
    var maxDist = 140;
    var maxDistSq = maxDist * maxDist;

    function isDark() {
        return document.documentElement.classList.contains('dark');
    }

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W * dpr;
        canvas.height = H * dpr;
        canvas.style.width = W + 'px';
        canvas.style.height = H + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        var density = Math.floor((W * H) / 11000);
        var count = Math.min(Math.max(density, 40), 110);
        points = [];
        for (var i = 0; i < count; i++) {
            points.push({
                x: Math.random() * W,
                y: Math.random() * H,
                vx: (Math.random() - 0.5) * 0.7,
                vy: (Math.random() - 0.5) * 0.7,
                pulse: Math.random() * Math.PI * 2,
                ps: 1 + Math.random() * 1.5
            });
        }
    }

    window.addEventListener('resize', resize);

    window.addEventListener('mousemove', function (e) {
        mouse.tx = e.clientX;
        mouse.ty = e.clientY;
    }, { passive: true });
    window.addEventListener('mouseleave', function () {
        mouse.tx = -1000;
        mouse.ty = -1000;
    }, { passive: true });
    window.addEventListener('touchstart', function (e) {
        var t = e.touches[0];
        mouse.tx = t.clientX;
        mouse.ty = t.clientY;
    }, { passive: true });
    window.addEventListener('touchmove', function (e) {
        var t = e.touches[0];
        mouse.tx = t.clientX;
        mouse.ty = t.clientY;
    }, { passive: true });
    window.addEventListener('touchend', function () {
        mouse.tx = -1000;
        mouse.ty = -1000;
    }, { passive: true });

    var lastTime = performance.now();

    function render(now) {
        var dt = Math.min((now - lastTime) / 1000, 0.033);
        lastTime = now;
        var dark = isDark();

        mouse.x += (mouse.tx - mouse.x) * 0.1;
        mouse.y += (mouse.ty - mouse.y) * 0.1;

        ctx.fillStyle = dark ? '#080c1a' : '#f8fafc';
        ctx.fillRect(0, 0, W, H);

        var strokeRGB = dark ? '148, 163, 184' : '71, 85, 105';

        var pCount = points.length;
        var i, j, k;

        for (i = 0; i < pCount; i++) {
            var p = points[i];
            p.pulse += dt * p.ps;
            p.x += p.vx * dt * 60;
            p.y += p.vy * dt * 60;
            if (p.x < 0) { p.x = 0; p.vx *= -1; } else if (p.x > W) { p.x = W; p.vx *= -1; }
            if (p.y < 0) { p.y = 0; p.vy *= -1; } else if (p.y > H) { p.y = H; p.vy *= -1; }

            var dx = mouse.x - p.x;
            var dy = mouse.y - p.y;
            var distSq = dx * dx + dy * dy;
            if (distSq < 40000 && distSq > 0) {
                var dist = Math.sqrt(distSq);
                var force = (1 - dist / 200) * 35;
                p.x -= (dx / dist) * force * dt * 6;
                p.y -= (dy / dist) * force * dt * 6;
            }
        }

        var cellSize = maxDist;
        var cols = Math.max(1, Math.ceil(W / cellSize));
        var rows = Math.max(1, Math.ceil(H / cellSize));
        var grid = [];
        for (var c = 0; c < cols; c++) {
            grid.push([]);
            for (var r = 0; r < rows; r++) grid[c].push([]);
        }
        for (i = 0; i < pCount; i++) {
            var gc = Math.min(cols - 1, Math.max(0, Math.floor(points[i].x / cellSize)));
            var gr = Math.min(rows - 1, Math.max(0, Math.floor(points[i].y / cellSize)));
            grid[gc][gr].push(i);
        }

        for (c = 0; c < cols; c++) {
            for (r = 0; r < rows; r++) {
                var cellPoints = grid[c][r];
                var neighbors = [];
                for (var nc = Math.max(0, c - 1); nc <= Math.min(cols - 1, c + 1); nc++) {
                    for (var nr = Math.max(0, r - 1); nr <= Math.min(rows - 1, r + 1); nr++) {
                        var nList = grid[nc][nr];
                        for (var nk = 0; nk < nList.length; nk++) neighbors.push(nList[nk]);
                    }
                }
                var neighborCount = neighbors.length;

                for (i = 0; i < cellPoints.length; i++) {
                    var idx1 = cellPoints[i];
                    var p1 = points[idx1];
                    for (j = 0; j < neighborCount; j++) {
                        var idx2 = neighbors[j];
                        if (idx1 >= idx2) continue;
                        var p2 = points[idx2];
                        var dx12 = p1.x - p2.x, dy12 = p1.y - p2.y;
                        if (dx12 * dx12 + dy12 * dy12 > maxDistSq) continue;
                        for (k = j + 1; k < neighborCount; k++) {
                            var idx3 = neighbors[k];
                            if (idx2 >= idx3) continue;
                            var p3 = points[idx3];
                            var dx23 = p2.x - p3.x, dy23 = p2.y - p3.y;
                            if (dx23 * dx23 + dy23 * dy23 > maxDistSq) continue;
                            var dx31 = p3.x - p1.x, dy31 = p3.y - p1.y;
                            if (dx31 * dx31 + dy31 * dy31 > maxDistSq) continue;

                            var avgX = (p1.x + p2.x + p3.x) * 0.3333;
                            var avgY = (p1.y + p2.y + p3.y) * 0.3333;

                            ctx.fillStyle = 'rgba(' + strokeRGB + ', 0.04)';
                            ctx.strokeStyle = 'rgba(' + strokeRGB + ', 0.07)';
                            ctx.lineWidth = 0.4;

                            ctx.beginPath();
                            ctx.moveTo(p1.x, p1.y);
                            ctx.lineTo(p2.x, p2.y);
                            ctx.lineTo(p3.x, p3.y);
                            ctx.closePath();
                            ctx.fill();
                            ctx.stroke();
                        }
                    }
                }
            }
        }

        for (i = 0; i < pCount; i++) {
            var pt = points[i];
            var pulseRadius = 1.8 + Math.sin(pt.pulse) * 1.0;
            ctx.fillStyle = 'rgba(' + strokeRGB + ', 0.4)';
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, pulseRadius, 0, Math.PI * 2);
            ctx.fill();
        }

        requestAnimationFrame(render);
    }

    resize();
    requestAnimationFrame(render);
})();
