import yaml
import colorsys
import random


def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step

    return hls_colors


def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [int(x * 255.0) for x in (_r, _g, _b)]
        rgb_colors.append([r, g, b])

    return rgb_colors


if __name__ == '__main__':
    yaml_obj = {}
    num = 60
    with open('../color.yaml', 'w') as yaml_file:
        rgb_colors = ncolors(num)
        for i in range(num):
            yaml_obj[i] = rgb_colors[i]
        yaml.safe_dump(yaml_obj, yaml_file)

    with open('../color.yaml', 'r') as yaml_file:
        yaml_obj = yaml.safe_load(yaml_file.read())
        print(yaml_obj)
    pass
