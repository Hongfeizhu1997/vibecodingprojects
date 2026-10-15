#!/usr/bin/env python3
"""Isometric customer-journey generator — combined 3-layer scene.

Three personas (Enterprise / Channel / Consumer) stacked in isometric space:
each persona lives on its own corridor (flat isometric slab), offset back-and-up
to create depth. Layers separated by colour theme + title label.
"""
import math

COS = math.cos(math.radians(30))
SIN = math.sin(math.radians(30))

def iso(x, y, z):
    return (x - y) * COS, (x + y) * SIN - z

def pts(ps):
    return ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in ps)

def darken(hexc, f):
    r = int(hexc[1:3], 16) * f; g = int(hexc[3:5], 16) * f; b = int(hexc[5:7], 16) * f
    return f'#{max(0,int(r)):02x}{max(0,int(g)):02x}{max(0,int(b)):02x}'

def lighten(hexc, f):
    r = int(hexc[1:3], 16); g = int(hexc[3:5], 16); b = int(hexc[5:7], 16)
    r += (255 - r) * f; g += (255 - g) * f; b += (255 - b) * f
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'

def box(x, y, z, w, d, h, tc, lc, rc):
    top = [iso(x, y, z+h), iso(x+w, y, z+h), iso(x+w, y+d, z+h), iso(x, y+d, z+h)]
    right = [iso(x, y, z), iso(x+w, y, z), iso(x+w, y, z+h), iso(x, y, z+h)]
    left = [iso(x, y, z), iso(x, y+d, z), iso(x, y+d, z+h), iso(x, y, z+h)]
    return (f'<polygon points="{pts(left)}" fill="{lc}"/>'
            f'<polygon points="{pts(right)}" fill="{rc}"/>'
            f'<polygon points="{pts(top)}" fill="{tc}"/>')

def platform(x, y, z, w, d, h=14):
    return box(x, y, z, w, d, h, '#ffffff', '#e3e9f1', '#c9d4e0')

def cylinder(cx, cy, z, r, h, tc, lc, rc, n=24):
    top = [iso(cx + r*math.cos(a), cy + r*math.sin(a), z+h) for a in [math.radians(t) for t in range(0, 360, 360//n)]]
    bot = [iso(cx + r*math.cos(a), cy + r*math.sin(a), z) for a in [math.radians(t) for t in range(0, 360, 360//n)]]
    top_pts = ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in top)
    side_pts = ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in (bot + top[::-1]))
    return (f'<polygon points="{side_pts}" fill="{rc}"/>'
            f'<polygon points="{top_pts}" fill="{tc}"/>')

def sphere(cx, cy, z, r, color):
    c = iso(cx, cy, z + r)
    return (f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r*1.12:.1f}" fill="{color}"/>'
            f'<circle cx="{(c[0]-r*0.3):.1f}" cy="{(c[1]-r*0.3):.1f}" r="{r*0.35:.1f}" fill="{lighten(color,0.45)}" opacity="0.85"/>')

def arrow(p1, p2, color, sw=3.5, head=11):
    dx = p2[0] - p1[0]; dy = p2[1] - p1[1]
    L = math.hypot(dx, dy)
    if L < 1: return ''
    ux, uy = dx/L, dy/L
    bx, by = p2[0] - ux*head, p2[1] - uy*head
    hx, hy = -uy, ux
    return (f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<polygon points="{p2[0]:.1f},{p2[1]:.1f} {bx+hx*head*0.55:.1f},{by+hy*head*0.55:.1f} {bx-hx*head*0.55:.1f},{by-hy*head*0.55:.1f}" fill="{color}"/>')

def text(x, y, s, size=12, weight=700, fill='#11184F', anchor='middle'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


# ---- icons ----
def icon_bulb(x, y, z, c):
    return [box(x+16, y+8, z, 18, 18, 8, darken(c,0.7), darken(c,0.55), darken(c,0.4)),
            sphere(x+25, y+25, z+8, 15, c)]

def icon_doc(x, y, z, c):
    s = [box(x+8, y+8, z, 34, 34, 7, lighten(c,0.55), lighten(c,0.35), lighten(c,0.2))]
    tc = iso(x+25, y+25, z+7)
    for dy in (-5, 1, 7):
        s.append(f'<line x1="{tc[0]-10:.1f}" y1="{tc[1]+dy:.1f}" x2="{tc[0]+10:.1f}" y2="{tc[1]+dy:.1f}" stroke="{darken(c,0.5)}" stroke-width="2.5"/>')
    return s

def icon_screen(x, y, z, c):
    return [box(x+20, y+20, z, 10, 10, 6, darken(c,0.6), darken(c,0.5), darken(c,0.4)),
            box(x+6, y+16, z+6, 38, 6, 26, lighten(c,0.6), darken(c,0.55), darken(c,0.45))]

def icon_stamp(x, y, z, c):
    t = iso(x+25, y+25, z+10)
    return [cylinder(x+25, y+25, z, 14, 10, c, lighten(c,0.2), darken(c,0.4)),
            f'<polyline points="{t[0]-8:.1f},{t[1]+1:.1f} {t[0]-2:.1f},{t[1]+6:.1f} {t[0]+9:.1f},{t[1]-6:.1f}" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>']

def icon_truck(x, y, z, c):
    s = [box(x+4, y+10, z, 30, 22, 18, c, darken(c,0.85), darken(c,0.65)),
         box(x+30, y+14, z, 14, 14, 12, lighten(c,0.3), darken(c,0.8), darken(c,0.6))]
    for wx in (10, 36):
        w = iso(x+wx, y+2, z)
        s.append(f'<circle cx="{w[0]:.1f}" cy="{w[1]:.1f}" r="6" fill="#1f2937"/>')
        s.append(f'<circle cx="{w[0]:.1f}" cy="{w[1]:.1f}" r="2.6" fill="#9ca3af"/>')
    return s

def icon_cycle(x, y, z, c):
    cc = iso(x+25, y+25, z+6)
    cx, cy_ = cc
    return [f'<path d="M {cx-16:.1f} {cy_-4:.1f} A 16 16 0 1 1 {cx+16:.1f} {cy_-4:.1f}" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/>',
            f'<polygon points="{cx+16:.1f},{cy_-4:.1f} {cx+11:.1f},{cy_-11:.1f} {cx+12:.1f},{cy_+2:.1f}" fill="{c}"/>']

def icon_shop(x, y, z, c):
    s = [box(x+6, y+8, z, 34, 26, 12, lighten(c,0.35), lighten(c,0.15), darken(c,0.2)),
         box(x+2, y+4, z+12, 6, 34, 14, darken(c,0.6), darken(c,0.5), darken(c,0.4))]
    for wx in (10, 36):
        w = iso(x+wx, y+6, z)
        s.append(f'<circle cx="{w[0]:.1f}" cy="{w[1]:.1f}" r="5" fill="#1f2937"/>')
    return s

def icon_person(x, y, z, c):
    return [box(x+18, y+16, z, 14, 14, 18, c, darken(c,0.85), darken(c,0.65)),
            sphere(x+25, y+25, z+18, 9, '#f1c27d')]

def icon_box(x, y, z, c):
    s = [box(x+6, y+6, z, 38, 38, 26, lighten(c,0.4), lighten(c,0.15), darken(c,0.15))]
    t = iso(x+25, y+25, z+26)
    s.append(f'<line x1="{t[0]-14:.1f}" y1="{t[1]-3:.1f}" x2="{t[0]+14:.1f}" y2="{t[1]+3:.1f}" stroke="{darken(c,0.5)}" stroke-width="4"/>')
    s.append(f'<line x1="{t[0]+3:.1f}" y1="{t[1]-14:.1f}" x2="{t[0]-3:.1f}" y2="{t[1]+14:.1f}" stroke="{darken(c,0.5)}" stroke-width="4"/>')
    return s

ICONS = {'bulb': icon_bulb, 'doc': icon_doc, 'screen': icon_screen, 'stamp': icon_stamp,
         'truck': icon_truck, 'cycle': icon_cycle, 'shop': icon_shop, 'person': icon_person,
         'box': icon_box}


# ---- scene dressing (grid, person silhouette, hologram, tree) ----
def ground_grid(x0, x1, y0, y1, step=80, color='#dfe5ef', sw=1.2):
    el = []
    y = y0
    while y <= y1:
        p1 = iso(x0, y, 0); p2 = iso(x1, y, 0)
        el.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{color}" stroke-width="{sw}"/>')
        y += step
    x = x0
    while x <= x1:
        p1 = iso(x, y0, 0); p2 = iso(x, y1, 0)
        el.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{color}" stroke-width="{sw}"/>')
        x += step
    return el

def person_figure(x, y, z, color, h=46):
    el = []
    el.append(box(x+8, y+10, z, 5, 5, h*0.4, darken(color,0.7), darken(color,0.6), darken(color,0.5)))
    el.append(box(x+15, y+10, z, 5, 5, h*0.4, darken(color,0.7), darken(color,0.6), darken(color,0.5)))
    el.append(box(x+6, y+7, z+h*0.4, 16, 12, h*0.3, color, darken(color,0.8), darken(color,0.6)))
    el.append(sphere(x+14, y+13, z+h*0.7, h*0.14, '#f1c27d'))
    return el

def hologram_panel(x, y, z, w, d, title, sub, color='#22d3ee'):
    el = []
    p1 = iso(x+w/2, y+d/2, z)
    p2 = iso(x+w/2, y+d/2, z-70)
    el.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{color}" stroke-width="1.4" stroke-dasharray="4,4" opacity="0.55"/>')
    top = [iso(x,y,z), iso(x+w,y,z), iso(x+w,y+d,z), iso(x,y+d,z)]
    el.append(f'<polygon points="{pts(top)}" fill="{color}" opacity="0.13" stroke="{color}" stroke-width="1.5" stroke-opacity="0.7"/>')
    c = iso(x+w/2, y+d/2, z)
    el.append(text(c[0], c[1]-2, title, 12, 800, color, 'middle'))
    el.append(text(c[0], c[1]+14, sub, 9, 600, '#475569', 'middle'))
    return el

def tree(x, y, z, h=55):
    el = []
    el.append(box(x+10, y+10, z, 6, 6, h*0.45, '#8b5a2b', darken('#8b5a2b',0.85), darken('#8b5a2b',0.65)))
    el.append(sphere(x+13, y+13, z+h*0.45, h*0.22, '#16a34a'))
    el.append(sphere(x+7, y+16, z+h*0.55, h*0.16, '#22c55e'))
    el.append(sphere(x+19, y+10, z+h*0.55, h*0.16, '#15803d'))
    return el

def building(x, y, z, w, d, h, color):
    el = []
    el.append(box(x, y, z, w, d, h, lighten(color,0.5), lighten(color,0.3), darken(color,0.2)))
    el.append(box(x, y, z+h, w, d, 3, lighten(color,0.72), lighten(color,0.55), lighten(color,0.42)))
    cols = max(1, int(d // 20))
    rows = max(1, int(h // 24))
    for ci in range(cols):
        for ri in range(rows):
            wy = y + d * (ci + 0.5) / cols
            wz = z + h * (ri + 0.5) / rows
            p = iso(x + w, wy, wz)
            el.append(f'<rect x="{p[0]-3.5:.1f}" y="{p[1]-2.5:.1f}" width="7" height="5" fill="#ffffff" opacity="0.4"/>')
    return el

def cloud(cx, cy, scale=1.0, color='#ffffff'):
    el = []
    el.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{32*scale:.1f}" ry="{14*scale:.1f}" fill="{color}" opacity="0.92"/>')
    el.append(f'<ellipse cx="{cx-22*scale:.1f}" cy="{cy+4*scale:.1f}" rx="{20*scale:.1f}" ry="{10*scale:.1f}" fill="{color}" opacity="0.82"/>')
    el.append(f'<ellipse cx="{cx+22*scale:.1f}" cy="{cy+4*scale:.1f}" rx="{23*scale:.1f}" ry="{11*scale:.1f}" fill="{color}" opacity="0.82"/>')
    return el

SPACING = 150  # x-spacing between stages on a corridor
PW = 72        # stage platform size

def render_scene(ox, oy, oz, stages, theme, title, subtitle, holo_title, holo_sub):
    """Render one persona scene: a corridor slab + horizontal journey + title."""
    el = []
    n = len(stages)
    corridor_w = (n - 1) * SPACING + PW + 50
    corridor_d = PW + 20
    # corridor slab
    el.append(box(ox, oy, oz, corridor_w, corridor_d, 12,
                  lighten(theme, 0.93), lighten(theme, 0.78), lighten(theme, 0.62)))
    # stages on corridor
    top_z = oz + 12
    for i, st in enumerate(stages):
        x = ox + 20 + i * SPACING
        el.append(platform(x, oy + 10, top_z, PW, PW, 12))
        for f in ICONS[st['icon']](x+2, oy+12, top_z+12, st['color']):
            el.append(f)
        lbl = iso(x + PW/2, oy + 10 + PW/2, top_z)
        el.append(text(lbl[0], lbl[1] + 58, st['name'], 11, 700, '#1a1d27'))
    # arrows between stages
    for i in range(n - 1):
        x1 = ox + 20 + i * SPACING + PW
        x2 = ox + 20 + (i+1) * SPACING
        c1 = iso(x1, oy + 10 + PW/2, top_z)
        c2 = iso(x2, oy + 10 + PW/2, top_z)
        dx = c2[0]-c1[0]; dy = c2[1]-c1[1]
        L = math.hypot(dx, dy); ux, uy = dx/L, dy/L
        el.append(arrow((c1[0]+ux*10, c1[1]+uy*10), (c2[0]-ux*10, c2[1]-uy*10), '#E1251B'))
    # title label anchored at the corridor back-left corner, extending LEFT (clear of stages)
    tpos = iso(ox, oy + corridor_d, oz)
    el.append(text(tpos[0] - 16, tpos[1] + 20, title, 15, 800, theme, 'end'))
    el.append(text(tpos[0] - 16, tpos[1] + 40, subtitle, 11, 400, '#6b7280', 'end'))
    # person silhouette at corridor entrance
    el += person_figure(ox + 2, oy + 44, top_z, theme)
    # hologram panel floating above the corridor
    el += hologram_panel(ox + 90, oy + 38, oz + 85, 132, 46, holo_title, holo_sub)
    return el


def main():
    OUT = '/root/ClaudeProjects/SSG_AI/Dynamic_Pricing/outputs/diagrams'

    enterprise = [
        {'name': 'Identify Need', 'icon': 'bulb', 'color': '#E1251B'},
        {'name': 'Get Quote', 'icon': 'doc', 'color': '#294E95'},
        {'name': 'Evaluate Price', 'icon': 'screen', 'color': '#4D144A'},
        {'name': 'Approve', 'icon': 'stamp', 'color': '#7A126B'},
        {'name': 'Deploy', 'icon': 'truck', 'color': '#11184F'},
        {'name': 'Renew', 'icon': 'cycle', 'color': '#059669'},
    ]
    channel = [
        {'name': 'Onboard', 'icon': 'shop', 'color': '#E1251B'},
        {'name': 'Get Quote', 'icon': 'doc', 'color': '#294E95'},
        {'name': 'Negotiate', 'icon': 'person', 'color': '#4D144A'},
        {'name': 'Resell', 'icon': 'truck', 'color': '#7A126B'},
        {'name': 'Support', 'icon': 'screen', 'color': '#11184F'},
        {'name': 'Renew', 'icon': 'cycle', 'color': '#059669'},
    ]
    consumer = [
        {'name': 'Browse', 'icon': 'screen', 'color': '#E1251B'},
        {'name': 'Select', 'icon': 'shop', 'color': '#294E95'},
        {'name': 'Checkout', 'icon': 'stamp', 'color': '#4D144A'},
        {'name': 'Receive', 'icon': 'box', 'color': '#7A126B'},
        {'name': 'Renew', 'icon': 'cycle', 'color': '#059669'},
    ]

    el = []
    # ground grid (bottom layer, behind everything)
    el += ground_grid(-300, 1020, -150, 650)
    # background buildings — strictly OUTSIDE the corridor band:
    #   upper-right (3D x large & y small → screen x>755) and lower-left (3D x small & y large → screen x<-409)
    el += building(900, -60, 0, 55, 42, 85, '#8ea3c0')
    el += building(970, -110, 0, 45, 34, 62, '#7d92b5')
    el += building(880, -20, 0, 50, 38, 70, '#93a7c4')
    el += building(-150, 560, 0, 55, 42, 85, '#8ea3c0')
    el += building(-250, 520, 0, 45, 34, 62, '#7d92b5')
    el += building(-100, 600, 0, 50, 38, 70, '#93a7c4')
    # trees — upper-right and lower-left
    el += tree(840, -70, 0, 50)
    el += tree(960, -40, 0, 55)
    el += tree(-220, 540, 0, 52)
    el += tree(-60, 590, 0, 48)
    # draw back-to-front so nearer layers correctly occlude farther ones
    el += render_scene(0, 380, 130, consumer, '#4D144A',
                       'Consumer', 'B2C · eCommerce',
                       'Live Pricing', 'real-time price')
    el += render_scene(0, 190, 65, channel, '#294E95',
                       'Channel Partner', 'B2B · LBPe indirect',
                       'Auto Margin', '+8% uplift')
    el += render_scene(0, 0, 0, enterprise, '#E1251B',
                       'Enterprise Customer', 'B2B · LBPi direct sale',
                       'Dynamic Quote', 'auto-priced')

    # bounds — cover grid, buildings, trees, corridors, personas, holograms, titles
    xs, ys = [], []
    for p in [iso(-300, -150, 0), iso(1020, -150, 0), iso(1020, 650, 0), iso(-300, 650, 0)]:
        xs.append(p[0]); ys.append(p[1])
    for b in ((900, -60, 0, 55, 42, 85), (970, -110, 0, 45, 34, 62), (880, -20, 0, 50, 38, 70),
              (-150, 560, 0, 55, 42, 85), (-250, 520, 0, 45, 34, 62), (-100, 600, 0, 50, 38, 70)):
        bx, by, bz, bw, bd, bh = b
        xs.append(iso(bx, by, bz)[0]); ys.append(iso(bx, by, bz)[1])
        xs.append(iso(bx + bw, by + bd, bz + bh)[0]); ys.append(iso(bx + bw, by + bd, bz + bh)[1])
    for oy, oz, n in ((0, 0, 6), (190, 65, 6), (380, 130, 5)):
        cw = (n - 1) * SPACING + PW + 50
        cd = PW + 20
        for x in (0, cw):
            for y in (0, cd):
                for z in (0, oz + 95):
                    p = iso(x, y, z)
                    xs.append(p[0]); ys.append(p[1])
    for oy, oz in ((0, 0), (190, 65), (380, 130)):
        p = iso(0, oy + PW + 20, oz)
        xs.append(p[0] - 175); ys.append(p[1] + 42)
    for tx, ty, th in ((840, -70, 50), (960, -40, 55), (-220, 540, 52), (-60, 590, 48)):
        xs.append(iso(tx, ty, 0)[0]); ys.append(iso(tx, ty, 0)[1])
        xs.append(iso(tx + 20, ty + 20, th)[0]); ys.append(iso(tx + 20, ty + 20, th)[1])
    minx, maxx = min(xs) - 12, max(xs) + 12
    miny, maxy = min(ys) - 12, max(ys) + 12
    w, h = maxx - minx, maxy - miny
    # clouds along the top edge (screen-space, decorative sky)
    el += cloud(minx + w*0.22, miny + 50, 1.0)
    el += cloud(minx + w*0.52, miny + 30, 1.25)
    el += cloud(minx + w*0.78, miny + 55, 0.9)

    SCALE = 1.28
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx*SCALE:.0f} {miny*SCALE:.0f} {w*SCALE:.0f} {h*SCALE:.0f}">'
           f'<g transform="scale({SCALE})">'
           + ''.join(el) + '</g></svg>')

    html = (f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Dynamic Pricing Customer Journeys</title>'
            f'<style>body{{margin:0;background:#eef1f6;font-family:Arial,sans-serif}}'
            f'.wrap{{max-width:1300px;margin:0 auto;padding:24px 16px}}'
            f'h1{{font-size:22px;color:#11184F;margin:0 0 4px;font-weight:800}}'
            f'.sub{{font-size:13px;color:#6b7280;margin:0 0 16px}}</style></head>'
            f'<body><div class="wrap"><h1>Service Dynamic Pricing — Customer Journeys</h1>'
            f'<p class="sub">Three personas · Isometric layered view</p>'
            f'{svg}</div></body></html>')
    open(f'{OUT}/journey-combined.html', 'w').write(html)
    print(f'saved journey-combined.html ({len(html):,} bytes)')


if __name__ == '__main__':
    main()
