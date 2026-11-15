import json

def get_spotify_player_html(dc1, dc2, dc3, daccent, dglow, dgrad, dsai, dartist, playlist_items, start_index=0):
    """
    Renders the Spotify-style YouTube player with queue support, track auto-switch,
    scrubbing seeker, shuffle, repeat, volume, and interactive queue management.
    """
    items_json = json.dumps(playlist_items)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }}

body {{
    font-family: 'Inter', sans-serif;
    background: transparent;
    color: white;
    overflow-x: hidden;
    overflow-y: auto;
    padding: 0 0 20px 0;
    user-select: none;
}}

/* ── Orbital visualizer canvas ── */
.vis-canvas-wrap {{
    width: 100%;
    height: 70px;
    position: relative;
    margin-bottom: -4px;
}}

#visCanvas {{
    display: block;
    width: 100%;
    height: 100%;
}}

/* ── Player card ── */
.player-card {{
    position: relative;
    background: rgba(10, 10, 24, 0.82);
    backdrop-filter: blur(40px) saturate(190%);
    -webkit-backdrop-filter: blur(40px) saturate(190%);
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.08);
    padding: 22px 22px 18px;
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba({dc1}, 0.1),
        0 30px 80px rgba(0,0,0,0.85),
        0 0 60px rgba({dc1}, 0.08),
        inset 0 1px 0 rgba(255,255,255,0.1);
}}

/* Top shimmer */
.card-shimmer {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba({dc1}, 0.7) 30%,
        rgba({dc2}, 0.7) 60%,
        transparent 100%
    );
}}

/* Ambient glow */
.card-ambient {{
    position: absolute;
    top: -60px; left: -40px; right: -40px;
    height: 140px;
    background: radial-gradient(ellipse at 50% 100%, rgba({dc1}, 0.12) 0%, transparent 70%);
    pointer-events: none;
}}

/* ── Track info row ── */
.track-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 18px;
}}

/* Animated album art */
.album-art {{
    position: relative;
    width: 52px;
    height: 52px;
    flex-shrink: 0;
}}

.album-ring-outer {{
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 1.5px solid rgba({dc1}, 0.4);
    animation: albumSpin 8s linear infinite;
}}

.album-ring-inner {{
    position: absolute;
    inset: 5px;
    border-radius: 50%;
    background: {dgrad};
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 22px rgba({dc1}, 0.55),
        inset 0 1px 0 rgba(255,255,255,0.3);
}}

.album-center-hole {{
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: rgba(8,8,20,0.92);
    border: 1.5px solid rgba(255,255,255,0.4);
}}

@keyframes albumSpin {{ to {{ transform: rotate(360deg); }} }}
.album-ring-outer.paused {{ animation-play-state: paused; }}

/* Track text */
.track-meta {{ flex: 1; overflow: hidden; }}

.track-title {{
    font-size: 14px;
    font-weight: 700;
    color: rgba(255,255,255,0.95);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    letter-spacing: -0.2px;
    line-height: 1.2;
    margin-bottom: 4px;
}}

.track-artist {{
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.38);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* Live & Queue buttons badge */
.track-actions {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.live-badge {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    background: rgba({dc1}, 0.12);
    border: 1px solid rgba({dc1}, 0.3);
    border-radius: 100px;
    flex-shrink: 0;
    backdrop-filter: blur(10px);
}}

.live-dot {{
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: {daccent};
    box-shadow: 0 0 8px {daccent};
    animation: livePulse 1.6s ease-in-out infinite;
}}

.live-text {{
    font-family: 'Space Mono', monospace;
    font-size: 7.5px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba({dc1}, 0.9);
}}

@keyframes livePulse {{
    0%, 100% {{ opacity: 1;   transform: scale(1);   }}
    50%       {{ opacity: 0.3; transform: scale(0.65); }}
}}

.queue-pill-btn {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 100px;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.queue-pill-btn:hover {{
    background: rgba({dc1}, 0.15);
    border-color: rgba({dc1}, 0.4);
}}

.queue-pill-btn svg {{
    width: 12px;
    height: 12px;
    fill: rgba(255,255,255,0.7);
}}

.queue-pill-btn span {{
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.85);
}}

/* ── Seeker (progress + seek) ── */
.seeker-wrap {{
    margin-bottom: 18px;
}}

.time-row {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}}

.time-label {{
    font-family: 'Space Mono', monospace;
    font-size: 9.5px;
    font-weight: 400;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.5px;
}}

.seek-track {{
    position: relative;
    height: 5px;
    border-radius: 5px;
    background: rgba(255,255,255,0.08);
    cursor: pointer;
    overflow: visible;
}}

.seek-buffer {{
    position: absolute;
    left: 0; top: 0;
    height: 100%;
    border-radius: 5px;
    background: rgba(255,255,255,0.08);
    pointer-events: none;
    transition: width 1s linear;
}}

.seek-fill {{
    position: absolute;
    left: 0; top: 0;
    height: 100%;
    border-radius: 5px;
    background: linear-gradient(90deg, rgba({dc1},0.95), rgba({dc2},0.9));
    pointer-events: none;
    transition: width 0.25s linear;
    box-shadow: 0 0 10px rgba({dc1}, 0.5);
}}

.seek-thumb {{
    position: absolute;
    top: 50%;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: white;
    border: 2px solid rgba({dc1}, 0.95);
    transform: translate(-50%, -50%) scale(0);
    box-shadow: 0 0 12px rgba({dc1}, 0.7), 0 2px 6px rgba(0,0,0,0.6);
    pointer-events: none;
    transition: transform 0.15s ease;
}}

.seek-track:hover .seek-thumb {{
    transform: translate(-50%, -50%) scale(1);
}}

.seek-track:active .seek-thumb {{
    transform: translate(-50%, -50%) scale(1.25);
}}

/* ── Spotify Style Controls ── */
.controls-row {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-bottom: 16px;
}}

.ctrl-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1);
    flex-shrink: 0;
    border: none;
    outline: none;
    position: relative;
    overflow: hidden;
}}

.ctrl-btn::before {{
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: rgba({dc1}, 0);
    transition: background 0.2s ease;
}}

.ctrl-btn:hover::before {{
    background: rgba({dc1}, 0.12);
}}

.ctrl-sm {{
    width: 38px;
    height: 38px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}}

.ctrl-sm:hover {{
    transform: scale(1.12);
    border-color: rgba({dc1}, 0.4);
}}

.ctrl-sm:active {{ transform: scale(0.9); }}

.ctrl-sm svg {{
    width: 15px;
    height: 15px;
    fill: rgba(255,255,255,0.65);
    position: relative;
    z-index: 1;
}}

.ctrl-play-btn {{
    width: 56px;
    height: 56px;
    background: {dgrad};
    border: none;
    box-shadow:
        0 6px 28px rgba({dc1}, 0.5),
        0 0 60px rgba({dc1}, 0.2),
        inset 0 1px 0 rgba(255,255,255,0.35);
}}

.ctrl-play-btn:hover {{
    transform: scale(1.1);
    box-shadow:
        0 10px 38px rgba({dc1}, 0.65),
        0 0 80px rgba({dc1}, 0.25),
        inset 0 1px 0 rgba(255,255,255,0.4);
}}

.ctrl-play-btn:active {{ transform: scale(0.92); }}

.ctrl-play-btn svg {{
    width: 20px;
    height: 20px;
    fill: white;
    position: relative;
    z-index: 1;
    filter: drop-shadow(0 1px 3px rgba(0,0,0,0.3));
}}

#playIcon {{ margin-left: 2px; }}

/* ── Volume row ── */
.volume-row {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.vol-icon {{
    width: 14px;
    height: 14px;
    fill: rgba(255,255,255,0.35);
    flex-shrink: 0;
}}

.vol-track {{
    flex: 1;
    position: relative;
    height: 4px;
    border-radius: 4px;
    background: rgba(255,255,255,0.08);
    cursor: pointer;
    overflow: hidden;
}}

.vol-fill {{
    position: absolute;
    left: 0; top: 0;
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, rgba({dc1},0.85), rgba({dc2},0.85));
    width: 80%;
    transition: width 0.1s ease;
}}

.vol-label {{
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 1px;
    width: 28px;
    text-align: right;
    flex-shrink: 0;
}}

/* ── Interactive Queue Section (Spotify Drawer) ── */
.queue-container {{
    margin-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.08);
    padding-top: 14px;
    display: none;
    animation: fadeIn 0.3s ease;
}}

.queue-container.open {{
    display: block;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(-6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.queue-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}}

.queue-title {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.6);
}}

.queue-count {{
    font-family: 'Space Mono', monospace;
    font-size: 9.5px;
    color: rgba({dc1}, 0.9);
}}

.queue-list {{
    max-height: 180px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-right: 4px;
}}

.queue-list::-webkit-scrollbar {{
    width: 4px;
}}
.queue-list::-webkit-scrollbar-thumb {{
    background: rgba(255,255,255,0.15);
    border-radius: 4px;
}}

.queue-item {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.queue-item:hover {{
    background: rgba(255,255,255,0.08);
    border-color: rgba({dc1}, 0.3);
    transform: translateX(3px);
}}

.queue-item.active {{
    background: rgba({dc1}, 0.15);
    border-color: rgba({dc1}, 0.5);
}}

.queue-item-info {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow: hidden;
}}

.qi-title {{
    font-size: 11.5px;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.qi-artist {{
    font-size: 9px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 1px;
    text-transform: uppercase;
}}

.qi-now-playing {{
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: {daccent};
    text-transform: uppercase;
    display: none;
}}

.queue-item.active .qi-now-playing {{
    display: inline-block;
}}

/* Add track inline mini-form */
.add-queue-box {{
    margin-top: 10px;
    display: flex;
    gap: 8px;
}}

.queue-input {{
    flex: 1;
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 6px 12px;
    color: white;
    font-size: 10.5px;
    outline: none;
}}
.queue-input:focus {{
    border-color: rgba({dc1}, 0.5);
}}

.queue-add-btn {{
    padding: 6px 12px;
    background: rgba({dc1}, 0.2);
    border: 1px solid rgba({dc1}, 0.4);
    border-radius: 10px;
    color: white;
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s ease;
}}
.queue-add-btn:hover {{
    background: rgba({dc1}, 0.35);
}}

/* Hidden YT iframe */
.yt-shell {{
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0.001;
    z-index: -999;
    pointer-events: none;
    overflow: hidden;
    top: 0; left: 0;
}}
</style>
</head>
<body>

<div class="vis-canvas-wrap">
    <canvas id="visCanvas"></canvas>
</div>

<div class="player-card">
    <div class="card-shimmer"></div>
    <div class="card-ambient"></div>

    <!-- Track info -->
    <div class="track-row">
        <div class="album-art">
            <div class="album-ring-outer" id="albumRing"></div>
            <div class="album-ring-inner">
                <div class="album-center-hole"></div>
            </div>
        </div>
        <div class="track-meta">
            <div class="track-title" id="trackTitleDisplay">{dsai}</div>
            <div class="track-artist" id="trackArtistDisplay">{dartist}</div>
        </div>
        <div class="track-actions">
            <div class="queue-pill-btn" onclick="toggleQueueDrawer()" title="View & Manage Queue">
                <svg viewBox="0 0 24 24"><path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/></svg>
                <span id="queueBadgeText">Queue</span>
            </div>
            <div class="live-badge">
                <div class="live-dot"></div>
                <div class="live-text">Live</div>
            </div>
        </div>
    </div>

    <!-- Seeker -->
    <div class="seeker-wrap">
        <div class="time-row">
            <span class="time-label" id="timeNow">0:00</span>
            <span class="time-label" id="timeDur">—:——</span>
        </div>
        <div class="seek-track" id="seekTrack">
            <div class="seek-buffer" id="seekBuffer" style="width:0%"></div>
            <div class="seek-fill"   id="seekFill"   style="width:0%"></div>
            <div class="seek-thumb"  id="seekThumb"  style="left:0%"></div>
        </div>
    </div>

    <!-- Spotify Style Controls -->
    <div class="controls-row">
        <div class="ctrl-btn ctrl-sm" onclick="shuffleToggle()" id="shuffleBtn" title="Shuffle">
            <svg viewBox="0 0 24 24"><path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17zm4.76-.82l3.15 3.15-3.15 3.15L17 16l4.45-4.45-4.45-4.45zm-.82 8.16L9.17 10.59 4 15.76 5.41 17.17l4.18-4.18 5.35 5.35z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-sm" onclick="prevTrack()" title="Previous Track">
            <svg viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6 8.5 6V6z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-play-btn" onclick="togglePlay()" id="playBtnEl" title="Play/Pause">
            <svg id="playIcon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-sm" onclick="nextTrack()" title="Next Track">
            <svg viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zm2.5-6 8.5 6V6z"/></svg>
        </div>
        <div class="ctrl-btn ctrl-sm" onclick="repeatToggle()" id="repeatBtn" title="Repeat Current Song">
            <svg viewBox="0 0 24 24"><path d="M7 7h10v3l4-4-4-4v3H5v6h2zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2z"/></svg>
        </div>
    </div>

    <!-- Volume -->
    <div class="volume-row">
        <svg class="vol-icon" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
        <div class="vol-track" id="volTrack">
            <div class="vol-fill" id="volFill"></div>
        </div>
        <span class="vol-label" id="volLabel">80%</span>
    </div>

    <!-- Up Next & Queue Drawer -->
    <div class="queue-container" id="queueDrawer">
        <div class="queue-header">
            <div class="queue-title">Now Playing Queue</div>
            <div class="queue-count" id="queueCountDisplay">0 tracks</div>
        </div>
        <div class="queue-list" id="queueList"></div>
        <div class="add-queue-box">
            <input type="text" class="queue-input" id="quickAddInput" placeholder="Add YouTube Video/Playlist URL..." />
            <button class="queue-add-btn" onclick="quickAddToQueue()">+ Add</button>
        </div>
    </div>
</div>

<div class="yt-shell"><div id="yt-player"></div></div>

<script>
// ── Palette ──────────────────────────────────────────────────────────────────
var C1 = [{dc1}];
var C2 = [{dc2}];
var C3 = [{dc3}];
var palRGB = [
    'rgba(' + C1.join(',') + ',',
    'rgba(' + C2.join(',') + ',',
    'rgba(' + C3.join(',') + ','
];

// ── Visualizer ───────────────────────────────────────────────────────────────
var canvas = document.getElementById('visCanvas');
var ctx    = canvas.getContext('2d');
var DPR    = window.devicePixelRatio || 1;
var W, H;

function resizeCanvas() {{
    var wrap = canvas.parentElement;
    W = wrap.offsetWidth;
    H = wrap.offsetHeight;
    canvas.width  = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width  = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Particles
var particles = [];
for (var i = 0; i < 20; i++) {{
    particles.push({{
        x: Math.random() * 600,
        y: Math.random() * H,
        r: 3 + Math.random() * 14,
        maxR: 8 + Math.random() * 24,
        phase: Math.random() * Math.PI * 2,
        speed: 0.008 + Math.random() * 0.016,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.25,
        ci: Math.floor(Math.random() * 3)
    }});
}}

// Bars
var BAR_COUNT = 44;
var bars = Array.from({{ length: BAR_COUNT }}, function(_, i) {{
    return {{
        h: 0.2 + Math.random() * 0.6,
        target: 0.2 + Math.random() * 0.6,
        speed: 0.05 + Math.random() * 0.08,
        phase: (i / BAR_COUNT) * Math.PI * 2
    }};
}});

var tick = 0;
var isPlayingVis = false;

function drawVisualizer() {{
    requestAnimationFrame(drawVisualizer);
    ctx.clearRect(0, 0, W, H);
    tick += isPlayingVis ? 0.025 : 0.008;

    var barW  = W / BAR_COUNT;
    var barMaxH = H * 0.55;
    var barY  = H * 0.88;

    for (var i = 0; i < BAR_COUNT; i++) {{
        var b = bars[i];
        if (isPlayingVis) {{
            b.target = 0.15 + 0.85 * Math.abs(
                0.5 * Math.sin(tick * 2.1 + b.phase) +
                0.3 * Math.sin(tick * 3.7 + b.phase * 1.4) +
                0.2 * Math.sin(tick * 1.3 + b.phase * 0.7)
            );
        }} else {{
            b.target = 0.05 + 0.08 * Math.abs(Math.sin(tick * 0.8 + b.phase));
        }}
        b.h += (b.target - b.h) * b.speed;

        var bh  = b.h * barMaxH;
        var bx  = i * barW + barW * 0.15;
        var bww = barW * 0.55;
        var ci  = i % 3;
        var opa = 0.15 + b.h * 0.5;

        var grd = ctx.createLinearGradient(bx, barY - bh, bx, barY);
        grd.addColorStop(0,   palRGB[ci] + opa + ')');
        grd.addColorStop(0.5, palRGB[(ci+1)%3] + (opa * 0.7) + ')');
        grd.addColorStop(1,   palRGB[ci] + '0)');

        ctx.beginPath();
        ctx.roundRect(bx, barY - bh, bww, bh, [2, 2, 0, 0]);
        ctx.fillStyle = grd;
        ctx.fill();
    }}

    for (var j = 0; j < particles.length; j++) {{
        var p = particles[j];
        p.phase += p.speed * (isPlayingVis ? 1.8 : 0.5);
        var pulse = 0.5 + 0.5 * Math.sin(p.phase);
        var cr = p.r + (p.maxR - p.r) * pulse;

        p.x += p.vx * (isPlayingVis ? 1.2 : 0.4);
        p.y += p.vy * (isPlayingVis ? 1.2 : 0.4);
        if (p.x < -p.maxR)  p.x = W + p.maxR;
        if (p.x > W+p.maxR) p.x = -p.maxR;
        if (p.y < -p.maxR)  p.y = H + p.maxR;
        if (p.y > H+p.maxR) p.y = -p.maxR;

        var pg = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, cr);
        var opa2 = (0.18 + 0.18 * pulse) * (isPlayingVis ? 1 : 0.4);
        pg.addColorStop(0, palRGB[p.ci] + opa2 + ')');
        pg.addColorStop(1, palRGB[p.ci] + '0)');
        ctx.beginPath();
        ctx.arc(p.x, p.y, cr, 0, Math.PI * 2);
        ctx.fillStyle = pg;
        ctx.fill();
    }}
}}
drawVisualizer();

// ── Queue & Player State ──────────────────────────────────────────────────────
var queueItems = {items_json};
var currentIndex = {start_index};
var player;
var isPlaying    = false;
var isSeeking    = false;
var seekInterval = null;
var volLevel     = 80;
var isShuffled   = false;
var isRepeat     = false;

function renderQueueUI() {{
    var listEl = document.getElementById('queueList');
    listEl.innerHTML = '';
    document.getElementById('queueCountDisplay').textContent = queueItems.length + ' tracks';
    document.getElementById('queueBadgeText').textContent = 'Queue (' + queueItems.length + ')';

    queueItems.forEach(function(item, idx) {{
        var itemDiv = document.createElement('div');
        itemDiv.className = 'queue-item' + (idx === currentIndex ? ' active' : '');
        itemDiv.onclick = function() {{
            playQueueIndex(idx);
        }};

        var infoDiv = document.createElement('div');
        infoDiv.className = 'queue-item-info';

        var titleSpan = document.createElement('span');
        titleSpan.className = 'qi-title';
        titleSpan.textContent = (idx + 1) + '. ' + item.title;

        var artistSpan = document.createElement('span');
        artistSpan.className = 'qi-artist';
        artistSpan.textContent = item.artist || (item.source_type === 'playlist' ? 'Playlist' : 'Single Track');

        infoDiv.appendChild(titleSpan);
        infoDiv.appendChild(artistSpan);

        var nowPlayingBadge = document.createElement('span');
        nowPlayingBadge.className = 'qi-now-playing';
        nowPlayingBadge.textContent = 'PLAYING';

        itemDiv.appendChild(infoDiv);
        itemDiv.appendChild(nowPlayingBadge);
        listEl.appendChild(itemDiv);
    }});
}}

function toggleQueueDrawer() {{
    var drawer = document.getElementById('queueDrawer');
    drawer.classList.toggle('open');
}}

function quickAddToQueue() {{
    var input = document.getElementById('quickAddInput');
    var val = input.value.trim();
    if (!val) return;

    var sId = val;
    var sType = 'playlist';
    if (val.indexOf('list=') !== -1) {{
        sId = val.split('list=')[1].split('&')[0];
        sType = 'playlist';
    }} else if (val.indexOf('v=') !== -1) {{
        sId = val.split('v=')[1].split('&')[0];
        sType = 'video';
    }} else if (val.indexOf('youtu.be/') !== -1) {{
        sId = val.split('youtu.be/')[1].split('?')[0];
        sType = 'video';
    }}

    queueItems.push({{
        title: 'User Added #' + (queueItems.length + 1),
        artist: 'Queue Entry',
        source_type: sType,
        source_id: sId
    }});

    input.value = '';
    renderQueueUI();
}}

// ── YouTube Player Setup ─────────────────────────────────────────────────────
var tag = document.createElement('script');
tag.src = 'https://www.youtube.com/iframe_api';
document.body.appendChild(tag);

function getInitPlayerVars() {{
    var cur = queueItems[currentIndex];
    if (!cur) return {{ autoplay: 1, controls: 0, playsinline: 1, rel: 0 }};

    if (cur.source_type === 'playlist') {{
        return {{
            autoplay: 1,
            controls: 0,
            playsinline: 1,
            rel: 0,
            listType: 'playlist',
            list: cur.source_id,
            index: 0
        }};
    }} else {{
        return {{
            autoplay: 1,
            controls: 0,
            playsinline: 1,
            rel: 0,
            videoId: cur.source_id
        }};
    }}
}}

function onYouTubeIframeAPIReady() {{
    renderQueueUI();
    var pVars = getInitPlayerVars();

    player = new YT.Player('yt-player', {{
        height: '1', width: '1',
        playerVars: pVars,
        events: {{
            onReady:       onPlayerReady,
            onStateChange: onStateChange
        }}
    }});
}}

function onPlayerReady(e) {{
    e.target.setVolume(volLevel);
    e.target.playVideo();
    updateTrackLabels();
}}

function updateTrackLabels() {{
    var cur = queueItems[currentIndex];
    if (cur) {{
        document.getElementById('trackTitleDisplay').textContent = cur.title;
        document.getElementById('trackArtistDisplay').textContent = cur.artist;
    }}
    renderQueueUI();
}}

function playQueueIndex(idx) {{
    if (idx < 0 || idx >= queueItems.length) return;
    currentIndex = idx;
    var cur = queueItems[currentIndex];
    if (!cur || !player) return;

    updateTrackLabels();

    if (cur.source_type === 'playlist') {{
        player.loadPlaylist({{
            listType: 'playlist',
            list: cur.source_id,
            index: 0
        }});
    }} else {{
        player.loadVideoById(cur.source_id);
    }}
    player.playVideo();
}}

function onStateChange(e) {{
    var icon = document.getElementById('playIcon');
    var ring = document.getElementById('albumRing');

    if (e.data === YT.PlayerState.PLAYING) {{
        isPlaying = true;
        isPlayingVis = true;
        icon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
        ring.classList.remove('paused');
        startSeeker();
        
        // Auto update video title from YouTube if available
        if (player.getVideoData && player.getVideoData().title) {{
            var realTitle = player.getVideoData().title;
            var realAuthor = player.getVideoData().author;
            if (realTitle) {{
                document.getElementById('trackTitleDisplay').textContent = realTitle;
                if (realAuthor) document.getElementById('trackArtistDisplay').textContent = realAuthor;
            }}
        }}
    }} else if (e.data === YT.PlayerState.ENDED) {{
        // Auto-switch to next in queue
        if (isRepeat) {{
            player.seekTo(0, true);
            player.playVideo();
        }} else {{
            nextTrack();
        }}
    }} else {{
        isPlaying = false;
        isPlayingVis = false;
        icon.innerHTML = '<path d="M8 5v14l11-7z"/>';
        ring.classList.add('paused');
        clearInterval(seekInterval);
    }}
}}

// ── Seeker logic ─────────────────────────────────────────────────────────────
function formatTime(s) {{
    if (!s || isNaN(s)) return '0:00';
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
}}

function updateSeeker() {{
    if (!player || !player.getDuration || isSeeking) return;
    var dur = player.getDuration()     || 0;
    var cur = player.getCurrentTime()  || 0;
    var pct = dur > 0 ? (cur / dur) * 100 : 0;

    document.getElementById('seekFill').style.width   = pct + '%';
    document.getElementById('seekThumb').style.left   = pct + '%';
    document.getElementById('seekBuffer').style.width = Math.min(pct + 8, 100) + '%';
    document.getElementById('timeNow').textContent    = formatTime(cur);
    document.getElementById('timeDur').textContent    = formatTime(dur);
}}

function startSeeker() {{
    clearInterval(seekInterval);
    seekInterval = setInterval(updateSeeker, 350);
}}

// Clickable & Draggable Seek
var seekTrack = document.getElementById('seekTrack');
var seeking   = false;

function seekTo(e) {{
    if (!player || !player.getDuration) return;
    var rect = seekTrack.getBoundingClientRect();
    var x    = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    var pct  = Math.max(0, Math.min(1, x / rect.width));
    var dur  = player.getDuration() || 0;
    player.seekTo(pct * dur, true);
    document.getElementById('seekFill').style.width  = (pct * 100) + '%';
    document.getElementById('seekThumb').style.left  = (pct * 100) + '%';
    document.getElementById('timeNow').textContent   = formatTime(pct * dur);
}}

seekTrack.addEventListener('mousedown',  function(e) {{ seeking = true; isSeeking = true; seekTo(e); }});
seekTrack.addEventListener('touchstart', function(e) {{ seeking = true; isSeeking = true; seekTo(e); }}, {{ passive: true }});
document.addEventListener('mousemove',   function(e) {{ if (seeking) seekTo(e); }});
document.addEventListener('touchmove',   function(e) {{ if (seeking) seekTo(e); }}, {{ passive: true }});
document.addEventListener('mouseup',     function()  {{ if (seeking) {{ seeking = false; setTimeout(function() {{ isSeeking = false; }}, 300); }} }});
document.addEventListener('touchend',    function()  {{ if (seeking) {{ seeking = false; setTimeout(function() {{ isSeeking = false; }}, 300); }} }});

// ── Volume ────────────────────────────────────────────────────────────────────
var volTrack   = document.getElementById('volTrack');
var volFill    = document.getElementById('volFill');
var volLabel   = document.getElementById('volLabel');
var volDragging = false;

function setVolume(e) {{
    var rect = volTrack.getBoundingClientRect();
    var x    = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
    volLevel = Math.round(Math.max(0, Math.min(100, (x / rect.width) * 100)));
    volFill.style.width    = volLevel + '%';
    volLabel.textContent   = volLevel + '%';
    if (player && player.setVolume) player.setVolume(volLevel);
}}

volTrack.addEventListener('mousedown',  function(e) {{ volDragging = true; setVolume(e); }});
volTrack.addEventListener('touchstart', function(e) {{ volDragging = true; setVolume(e); }}, {{ passive: true }});
document.addEventListener('mousemove',  function(e) {{ if (volDragging) setVolume(e); }});
document.addEventListener('touchmove',  function(e) {{ if (volDragging) setVolume(e); }}, {{ passive: true }});
document.addEventListener('mouseup',    function()  {{ volDragging = false; }});
document.addEventListener('touchend',   function()  {{ volDragging = false; }});

// ── Spotify Style Controls ───────────────────────────────────────────────────
function togglePlay() {{
    if (!player) return;
    if (isPlaying) {{ player.pauseVideo(); }} else {{ player.playVideo(); }}
}}

function nextTrack()  {{
    if (isShuffled && queueItems.length > 1) {{
        var nextIdx = Math.floor(Math.random() * queueItems.length);
        if (nextIdx === currentIndex) nextIdx = (currentIndex + 1) % queueItems.length;
        playQueueIndex(nextIdx);
    }} else if (currentIndex < queueItems.length - 1) {{
        playQueueIndex(currentIndex + 1);
    }} else if (player && player.nextVideo) {{
        // If it's a YouTube playlist, trigger internal next
        player.nextVideo();
    }} else {{
        // Loop back to start
        playQueueIndex(0);
    }}
}}

function prevTrack()  {{
    if (player && player.getCurrentTime && player.getCurrentTime() > 4) {{
        player.seekTo(0, true);
    }} else if (currentIndex > 0) {{
        playQueueIndex(currentIndex - 1);
    }} else if (player && player.previousVideo) {{
        player.previousVideo();
    }}
}}

function shuffleToggle() {{
    isShuffled = !isShuffled;
    if (player && player.setShuffle) player.setShuffle(isShuffled);
    var btn = document.getElementById('shuffleBtn');
    btn.style.opacity = isShuffled ? '1' : '0.4';
    btn.querySelector('svg').style.fill = isShuffled ? 'rgba({dc1},0.95)' : 'rgba(255,255,255,0.45)';
}}

function repeatToggle() {{
    isRepeat = !isRepeat;
    var btn = document.getElementById('repeatBtn');
    btn.style.opacity = isRepeat ? '1' : '0.4';
    btn.querySelector('svg').style.fill = isRepeat ? 'rgba({dc1},0.95)' : 'rgba(255,255,255,0.45)';
}}

// Keyboard shortcuts (Spotify style)
document.addEventListener('keydown', function(e) {{
    if (e.target.tagName === 'INPUT') return; // Don't trigger when typing
    if (e.code === 'Space')       {{ e.preventDefault(); togglePlay(); }}
    if (e.code === 'ArrowRight')  {{ if (player && player.getCurrentTime) player.seekTo(player.getCurrentTime() + 10, true); }}
    if (e.code === 'ArrowLeft')   {{ if (player && player.getCurrentTime) player.seekTo(Math.max(0, player.getCurrentTime() - 10), true); }}
    if (e.code === 'ArrowUp')     {{ volLevel = Math.min(100, volLevel + 5); if (player) player.setVolume(volLevel); volFill.style.width = volLevel + '%'; volLabel.textContent = volLevel + '%'; }}
    if (e.code === 'ArrowDown')   {{ volLevel = Math.max(0,   volLevel - 5); if (player) player.setVolume(volLevel); volFill.style.width = volLevel + '%'; volLabel.textContent = volLevel + '%'; }}
}});
</script>
</body>
</html>"""
    return html

