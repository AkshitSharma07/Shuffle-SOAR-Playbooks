"""
build_flow.py
==============
Small helper to generate consistent vertical flowchart SVGs for each
playbook diagram, matching the visual style of architecture.svg.

Each playbook is defined as a list of "nodes", where a node is either:
  - a single box: {"title": ..., "sub": ..., "color": ...}
  - a branch: {"branch": True, "left": {...}, "right": {...}, "left_label": ..., "right_label": ...}
    (after a branch, flow continues from a merge point below both boxes)

Colors follow the same flat palette used in architecture.svg.
"""

import cairosvg

COLORS = {
    "gray": "#5F5E5A",
    "teal": "#0F6E56",
    "blue": "#185FA5",
    "purple": "#534AB7",
    "rust": "#993C1D",
    "darkred": "#791F1F",
    "green": "#27500A",
    "darkgray": "#444441",
    "maroon": "#99352B",
}

WIDTH = 680
BOX_W_FULL = 320
BOX_W_HALF = 150
PAD_X = (WIDTH - BOX_W_FULL) // 2


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_box(x, w, y, h, title, sub_lines, color, title_size=14):
    cx = x + w / 2
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{color}"/>']
    title_y = y + 22 if sub_lines else y + h / 2 + 5
    parts.append(
        f'<text x="{cx}" y="{title_y}" text-anchor="middle" '
        f'style="font-family:Arial,Helvetica,sans-serif;font-size:{title_size}px;font-weight:700;fill:#FFFFFF">{esc(title)}</text>'
    )
    sy = title_y + 18
    for line in sub_lines:
        parts.append(
            f'<text x="{cx}" y="{sy}" text-anchor="middle" '
            f'style="font-family:Arial,Helvetica,sans-serif;font-size:11px;fill:#FFFFFF;opacity:0.92">{esc(line)}</text>'
        )
        sy += 16
    return "\n".join(parts), y + h


def build_flow(title_text, desc_text, nodes, out_svg, out_png):
    y = 30
    elements = []
    last_cx = WIDTH / 2

    for i, node in enumerate(nodes):
        if node.get("branch"):
            left, right = node["left"], node["right"]
            box_h = 70
            gap = 40
            total_w = BOX_W_HALF * 2 + gap
            lx = (WIDTH - total_w) / 2
            rx = lx + BOX_W_HALF + gap

            # connector down to branch point
            elements.append(f'<line x1="{last_cx}" y1="{y}" x2="{last_cx}" y2="{y+24}" class="arr"/>')
            y += 24
            # horizontal split line
            elements.append(f'<line x1="{lx + BOX_W_HALF/2}" y1="{y}" x2="{rx + BOX_W_HALF/2}" y2="{y}" class="arr"/>')
            elements.append(
                f'<text x="{lx + BOX_W_HALF/2}" y="{y-6}" text-anchor="middle" class="label">{esc(node.get("left_label",""))}</text>'
            )
            elements.append(
                f'<text x="{rx + BOX_W_HALF/2}" y="{y-6}" text-anchor="middle" class="label">{esc(node.get("right_label",""))}</text>'
            )
            elements.append(f'<line x1="{lx + BOX_W_HALF/2}" y1="{y}" x2="{lx + BOX_W_HALF/2}" y2="{y+16}" class="arr" marker-end="url(#arrow)"/>')
            elements.append(f'<line x1="{rx + BOX_W_HALF/2}" y1="{y}" x2="{rx + BOX_W_HALF/2}" y2="{y+16}" class="arr" marker-end="url(#arrow)"/>')
            y += 16

            lb_svg, lb_bottom = render_box(lx, BOX_W_HALF, y, box_h, left["title"], left["sub"], COLORS[left["color"]], 13)
            rb_svg, rb_bottom = render_box(rx, BOX_W_HALF, y, box_h, right["title"], right["sub"], COLORS[right["color"]], 13)
            elements.append(lb_svg)
            elements.append(rb_svg)

            bottom = max(lb_bottom, rb_bottom)
            # merge back to center if there's a next node
            if i < len(nodes) - 1:
                merge_y = bottom + 20
                elements.append(f'<line x1="{lx + BOX_W_HALF/2}" y1="{bottom}" x2="{lx + BOX_W_HALF/2}" y2="{merge_y}" class="arr"/>')
                elements.append(f'<line x1="{lx + BOX_W_HALF/2}" y1="{merge_y}" x2="{WIDTH/2}" y2="{merge_y}" class="arr"/>')
                elements.append(f'<line x1="{WIDTH/2}" y1="{merge_y}" x2="{WIDTH/2}" y2="{merge_y+20}" class="arr" marker-end="url(#arrow)"/>')
                y = merge_y + 20
            else:
                y = bottom
            last_cx = WIDTH / 2
        else:
            box_h = 50 if not node.get("sub") else (50 if len(node["sub"]) <= 1 else 50 + 14 * (len(node["sub"]) - 1))
            if i > 0:
                elements.append(f'<line x1="{last_cx}" y1="{y}" x2="{last_cx}" y2="{y+24}" class="arr" marker-end="url(#arrow)"/>')
                y += 24
            box_svg, bottom = render_box(PAD_X, BOX_W_FULL, y, box_h, node["title"], node.get("sub", []), COLORS[node["color"]])
            elements.append(box_svg)
            y = bottom
            last_cx = WIDTH / 2

    total_height = y + 30

    style = """
  <style>
    text { font-family: Arial, Helvetica, sans-serif; }
    .arr { stroke: #5F5E5A; stroke-width: 1.5; fill: none; }
    .label { font-size: 11px; fill: #5F5E5A; font-family: Arial, Helvetica, sans-serif; }
  </style>
"""
    defs = """
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
"""

    svg = (
        f'<svg width="{WIDTH}" height="{total_height}" viewBox="0 0 {WIDTH} {total_height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img">\n'
        f'<title>{esc(title_text)}</title>\n<desc>{esc(desc_text)}</desc>\n'
        f"{defs}{style}\n" + "\n".join(elements) + "\n</svg>"
    )

    with open(out_svg, "w") as f:
        f.write(svg)
    cairosvg.svg2png(url=out_svg, write_to=out_png, output_width=900)
    print(f"Built {out_svg} -> {out_png} (height={total_height})")
