#!/usr/bin/env python3
"""Isometric customer-journey SVG generator (iChain-style pseudo-3D).

Snake (S-shaped) layout: row 0 flows right-down, row 1 flows left-down.
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

def platform(x, y, w, d, h=14):
    return box(x, y, 0, w, d, h, '#ffffff', '#e3e9f1', '#c9d4e0')

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

def text(x, y, s, size=13, weight=700, fill='#11184F', anchor='middle'):
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
    """Parcel: cube + strap."""
    s = [box(x+6, y+6, z, 38, 38, 26, lighten(c,0.4), lighten(c,0.15), darken(c,0.15))]
    # straps on top
    t = iso(x+25, y+25, z+26)
    s.append(f'<line x1="{t[0]-14:.1f}" y1="{t[1]-3:.1f}" x2="{t[0]+14:.1f}" y2="{t[1]+3:.1f}" stroke="{darken(c,0.5)}" stroke-width="4"/>')
    s.append(f'<line x1="{t[0]+3:.1f}" y1="{t[1]-14:.1f}" x2="{t[0]-3:.1f}" y2="{t[1]+14:.1f}" stroke="{darken(c,0.5)}" stroke-width="4"/>')
    return s

ICONS = {'bulb': icon_bulb, 'doc': icon_doc, 'screen': icon_screen, 'stamp': icon_stamp,
         'truck': icon_truck, 'cycle': icon_cycle, 'shop': icon_shop, 'person': icon_person,
         'box': icon_box}


def snake_positions(n):
    """Return 3D (x, y) positions for a snake layout of n stages (row 0: 0..k, row 1: k..0)."""
    k = (n + 1) // 2  # row 0 length
    SP = 170  # spacing between platforms (3D units)
    pos = []
    for i in range(n):
        if i < k:
            pos.append((i * SP, 0))
        else:
            pos.append(((n - 1 - i) * SP, SP))
    return pos


def render_journey(stages, title, outfile):
    el = []
    n = len(stages)
    pos = snake_positions(n)
    bounds = []

    # platforms + icons + labels
    for i, st in enumerate(stages):
        x, y = pos[i]
        c = st['color']
        el.append(platform(x, y, 76, 76))
        for f in ICONS[st['icon']](x+2, y+2, 14, c):
            el.append(f)
        lbl = iso(x+38, y+38, 0)
        el.append(text(lbl[0], lbl[1] + 70, st['name'], 13, 700))
        for p in [iso(x,y,0), iso(x+76,y,0), iso(x,y+76,0), iso(x+76,y+76,0), iso(x,y,76)]:
            bounds.append(p)
        bounds.append((lbl[0], lbl[1]+70))

    # arrows: edge-to-edge between consecutive stage platforms
    for i in range(n - 1):
        x1, y1 = pos[i]; x2, y2 = pos[i+1]
        c1 = iso(x1+38, y1+38, 14)
        c2 = iso(x2+38, y2+38, 14)
        dx = c2[0]-c1[0]; dy = c2[1]-c1[1]
        L = math.hypot(dx, dy)
        ux, uy = dx/L, dy/L
        s = (c1[0]+ux*50, c1[1]+uy*50)
        e = (c2[0]-ux*50, c2[1]-uy*50)
        el.append(arrow(s, e, '#E1251B'))

    minx = min(p[0] for p in bounds) - 45
    maxx = max(p[0] for p in bounds) + 45
    miny = min(p[1] for p in bounds) - 95
    maxy = max(p[1] for p in bounds) + 30
    w, h = maxx - minx, maxy - miny

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx:.0f} {miny:.0f} {w:.0f} {h:.0f}">'
           + ''.join(el) + '</svg>')

    html = (f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>'
            f'<style>body{{margin:0;background:#eef1f6;font-family:Arial,sans-serif}}'
            f'.wrap{{max-width:1000px;margin:0 auto;padding:28px 20px}}'
            f'h1{{font-size:22px;color:#11184F;margin:0 0 4px;font-weight:800}}'
            f'.sub{{font-size:13px;color:#6b7280;margin:0 0 16px}}</style></head>'
            f'<body><div class="wrap"><h1>{title}</h1>'
            f'<p class="sub">Isometric customer journey · Service Dynamic Pricing</p>'
            f'{svg}</div></body></html>')
    open(outfile, 'w').write(html)
    print(f'saved {outfile} ({len(html):,} bytes)')


if __name__ == '__main__':
    OUT = '/root/ClaudeProjects/SSG_AI/Dynamic_Pricing/outputs/diagrams'

    enterprise = [
        {'name': 'Identify Need', 'icon': 'bulb', 'color': '#E1251B'},
        {'name': 'Get Quote', 'icon': 'doc', 'color': '#294E95'},
        {'name': 'Evaluate Price', 'icon': 'screen', 'color': '#4D144A'},
        {'name': 'Approve', 'icon': 'stamp', 'color': '#7A126B'},
        {'name': 'Deploy', 'icon': 'truck', 'color': '#11184F'},
        {'name': 'Renew', 'icon': 'cycle', 'color': '#059669'},
    ]
    render_journey(enterprise, 'Enterprise Customer Journey (B2B · LBPi)', f'{OUT}/journey-enterprise.html')

    channel = [
        {'name': 'Onboard', 'icon': 'shop', 'color': '#E1251B'},
        {'name': 'Get Quote', 'icon': 'doc', 'color': '#294E95'},
        {'name': 'Negotiate', 'icon': 'person', 'color': '#4D144A'},
        {'name': 'Resell', 'icon': 'truck', 'color': '#7A126B'},
        {'name': 'Support', 'icon': 'screen', 'color': '#11184F'},
        {'name': 'Renew', 'icon': 'cycle', 'color': '#059669'},
    ]
    render_journey(channel, 'Channel Partner Journey (B2B · LBPe)', f'{OUT}/journey-channel.html')

    consumer = [
        {'name': 'Browse', 'icon': 'screen', 'color': '#E1251B'},
        {'name': 'Select', 'icon': 'shop', 'color': '#294E95'},
        {'name': 'Checkout', 'icon': 'stamp', 'color': '#4D144A'},
        {'name': 'Receive', 'icon': 'box', 'color': '#7A126B'},
        {'name': 'Renew', 'icon': 'cycle', 'color': '#059669'},
    ]
    render_journey(consumer, 'Consumer Journey (B2C · eCommerce)', f'{OUT}/journey-consumer.html')
