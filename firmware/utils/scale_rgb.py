def scale_rgb(color, scale):
    r = int(color[0] * scale)
    g = int(color[1] * scale)
    b = int(color[2] * scale)
    return (r, g, b)