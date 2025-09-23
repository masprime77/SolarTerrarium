def scale_rgb(color, scale):
    cr = int(color[0] * scale)
    r = cr if cr <= 255 and cr >= 0 else 255
    cg = int(color[1] * scale)
    g = cg if cg <= 255 and cg >= 0 else 255
    cb = int(color[2] * scale)
    b = cb if cb <= 255 and cb >= 0 else 255
    return (r, g, b)