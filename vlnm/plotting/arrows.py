"""
Fancier arrows for matplotlib.
"""

import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib.bezier import (
    concatenate_paths, make_path_regular, split_de_casteljau)
from matplotlib.transforms import Affine2D, IdentityTransform


import matplotlib.colors as colors
import numpy as np

from scipy.special import binom

# pylint: disable=protected-access

def bezier_point_at_t(bezier: np.ndarray, t: float) -> np.ndarray:
    """
    Return the point on a bezier curve at the specified time.
    """
    n = len(bezier) - 1
    return sum(bezier[i] * (1 - t) ** (n - i) * (t ** i) * binom(n, i) for i in range(0, n + 1))


def shorten_bezier(
        bezier: np.ndarray, shorten: float, left: bool = True, eps: float = 1e-6) -> np.ndarray:
    """
    Shorten a bezier curve by the specifed distance from the left or right of the curve.
    """
    bezier = np.array(bezier)
    reference = bezier[0] if left else bezier[-1]
    target = shorten ** 2
    t1, t2 = 0, 1
    x = 1
    while np.abs(x) > eps:
        t = (t1 + t2) * 0.5
        q = bezier_point_at_t(bezier, t) - reference
        x = np.sum(q ** 2) - target
        if x > 0:
            t2 = t
        else:
            t1 = t
    left_bezier, right_bezier = split_de_casteljau(bezier, t)
    if left:
        return right_bezier
    return left_bezier


def shorten_line(p1, p2, d):
    """
    Shorten a line by a distance.
    """
    p1 = np.array(p1)
    p2 = np.array(p2)
    hyp = np.hypot(*(p2 - p1))
    return bezier_point_at_t(np.array([p2, p1]), d / hyp)


def shorten_path(path: Path, begin: float = None, end: float = None):
    """
    Shorten a path from th
    """
    vertices = path.vertices[:]
    codes = path.codes[:]
    if codes[-1] == Path.LINETO:
        if end:
            x, y = shorten_line(vertices[-2], vertices[-1], end)
            vertices[-1] = (x, y)
        if begin:
            x, y = shorten_line(vertices[1], vertices[0], begin)
            vertices[0] = (x, y)
    elif codes[-1] in [Path.CURVE3, Path.CURVE4]:
        vertices = vertices[-3:] if codes[-1] == Path.CURVE3 else vertices[-4:]
        if end:
            vertices = shorten_bezier(vertices, end, left=False)
        if begin:
            vertices = shorten_bezier(vertices, begin, left=True)

    return Path(vertices=vertices, codes=codes)


class FancierArrowFactory:
    """
    Factory class for use with arrow style in FancyArrowPatch.
    """
    def __init__(self, cls, **kwargs):
        self.cls = cls
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        props = self.kwargs.copy()
        props.update(kwargs)
        return self.cls(*args, **props)


def _register_style(name, **kwargs):
    def _register(cls):
        mpatches.ArrowStyle._style_list[name.lower()] = FancierArrowFactory(cls, **kwargs)
    return _register

@_register_style('Fancier')
class FancierArrowStyle(mpatches.ArrowStyle._Base):
    """
    """

    def __init__(self, begin=None, end=None):
        self.begin = begin
        self.end = end

    def transmute(self, path, mutation_size, linewidth):

        shorten_begin = shorten_end = 0
        begin_x, begin_y = path.vertices[0]
        end_x, end_y = path.vertices[-1]

        # begin arrow
        x0, y0 = path.vertices[0]
        x1, y1 = path.vertices[1]

        # If there is no room for an arrow and a line, then skip the arrow
        has_begin_arrow = self.begin and (x0, y0) != (x1, y1)
        if has_begin_arrow:
            begin_arrow, shorten_begin = self.begin.get_arrow_head(linewidth, mutation_size)

        # end arrow
        x2, y2 = path.vertices[-2]
        x3, y3 = path.vertices[-1]

        # If there is no room for an arrow and a line, then skip the arrow
        has_end_arrow = self.end and (x2, y2) != (x3, y3)
        if has_end_arrow:
            end_arrow_path, shorten_end = self.end.get_arrow_head(linewidth, mutation_size)

        paths = [shorten_path(path, begin=shorten_begin, end=shorten_end)]
        fillables = [False]
        styles = [None]

        if has_begin_arrow:
            if shorten_begin:
                x0, y0 = paths[0].vertices[0]
                x1, y1 = begin_x, begin_y
            else:
                x0, y0 = paths[0].vertices[1]
                x1, y1 = paths[0].vertices[0]
            angle = np.arctan2(y1 - y0, x1 - x0)
            begin_arrow = Affine2D().rotate(angle).translate(
                begin_x, begin_y).transform_path(begin_arrow)
            paths.append(begin_arrow)
            fillables.append(self.begin.fill)
            styles.append(self.begin.style)

        if has_end_arrow:
            if shorten_end:
                x0, y0 = paths[0].vertices[-1]
                x1, y1 = end_x, end_y
            else:
                x0, y0 = paths[0].vertices[-2]
                x1, y1 = paths[0].vertices[-1]
            angle = np.arctan2(y1 - y0, x1 - x0)

            end_arrow_path = Affine2D().rotate(angle).translate(
                end_x, end_y).transform_path(end_arrow_path)
            paths.append(end_arrow_path)
            fillables.append(self.end.fill)
            styles.append(self.end.style)

        return paths, fillables, styles

    def __call__(self, path, mutation_size, linewidth, aspect_ratio=1.):
        """
        The __call__ method is a thin wrapper around the transmute method
        and takes care of the aspect ratio.
        """

        path = make_path_regular(path)

        if aspect_ratio is not None:
            # Squeeze the given height by the aspect_ratio

            vertices, codes = path.vertices[:], path.codes[:]
            # Squeeze the height
            vertices[:, 1] = vertices[:, 1] / aspect_ratio
            path_shrunk = Path(vertices, codes)
            # call transmute method with squeezed height.
            path_mutated, fillable, style = self.transmute(
                path_shrunk, linewidth, mutation_size)
            if np.iterable(fillable):
                path_list = []
                for p in zip(path_mutated):
                    v, c = p.vertices, p.codes
                    # Restore the height
                    v[:, 1] = v[:, 1] * aspect_ratio
                    path_list.append(Path(v, c))
                return path_list, fillable, style
            return path_mutated, fillable, style
        return self.transmute(path, mutation_size, linewidth)


class FancierArrowPatch(mpatches.FancyArrowPatch):
    """
    Fancier version of FancyArrowPatch.
    """

    def get_path(self):
        """
        Return the path of the arrow in the data coordinates. Use
        get_path_in_displaycoord() method to retrieve the arrow path
        in display coordinates.
        """
        _path, fillable, _styles = self.get_path_in_displaycoord()

        if np.iterable(fillable):
            _path = concatenate_paths(_path)

        return self.get_transform().inverted().transform_path(_path)

    def get_path_in_displaycoord(self):
        """
        Return the mutated path of the arrow in display coordinates.
        """

        dpi_cor = self.get_dpi_cor()

        if self._posA_posB is not None:
            posA = self.get_transform().transform_point(self._posA_posB[0])
            posB = self.get_transform().transform_point(self._posA_posB[1])
            _path = self.get_connectionstyle()(
                posA, posB, patchA=self.patchA, patchB=self.patchB,
                shrinkA=self.shrinkA * dpi_cor, shrinkB=self.shrinkB * dpi_cor)
        else:
            _path = self.get_transform().transform_path(self._path_original)

        paths, fillables, styles = self.get_arrowstyle()(
            _path,
            self.get_mutation_scale() * dpi_cor,
            self.get_linewidth() * dpi_cor,
            self.get_mutation_aspect())


        return paths, fillables, styles

    def draw(self, renderer):

        if not self.get_visible():
            return

        self.set_dpi_cor(renderer.points_to_pixels(1.))

        paths, fillables, styles = self.get_path_in_displaycoord()

        affine = IdentityTransform()

        default_style = dict(
            edgecolor=self._edgecolor,
            facecolor=self._facecolor,
            linewidth=self._linewidth,
            capstyle=self._capstyle,
            joinstyle=self._joinstyle,
            dashoffset=self._dashoffset,
            dashes=self._dashes,
            snap=self.get_snap(),
            alpha=self._alpha)

        if any(styles):
            for path, fillable, style in zip(paths, fillables, styles):
                with PatchContext(renderer) as patch:
                    gc_style = default_style.copy()
                    gc_style.update(style or {})
                    patch.gc(**gc_style)
                    if fillable:
                        patch.draw_path(path, affine)
                    else:
                        patch.draw_path(path, affine, False)
        else:
            with PatchContext(renderer) as patch:
                gc_style = default_style.copy()
                gc_style.update(style or {})
                patch.gc(**gc_style)
                for path, fillable in zip(paths, fillables):
                    if fillable:
                        patch.draw_path(path, affine)
                    else:
                        patch.draw_path(path, affine, False)

        self.stale = False


class PatchContext:
    """
    Class for managing rendering of patches.
    """
    def __init__(self, renderer, gid=None):
        self.renderer = renderer
        self._patch = None
        self._gc = None
        self._gid = gid
        self._rgbFace = None

    def begin_patch(self):
        self._patch = self.renderer.open_group('patch', self._gid)
        self._gc = self.renderer.new_gc()
        self._rgbFace = None

    def draw_path(self, path, transform, fill=True):
        if fill:
            self.renderer.draw_path(self._gc, path, transform, self._rgbFace)
        else:
            self.renderer.draw_path(self._gc, path, transform, None)

    def get_gc(self):
        return self._gc

    def gc(self, linewidth=1., edgecolor=None, facecolor=None, capstyle=None, joinstyle='round',
           dashoffset=None, dashes=None, snap=None, alpha=None, color=None):

        edgecolor = colors.to_rgba(edgecolor or color)
        facecolor = colors.to_rgba(facecolor or color)

        gc = self._gc

        gc.set_foreground(edgecolor, isRGBA=True)
        gc.set_linewidth(0 if edgecolor and edgecolor[3] == 0 else linewidth)
        gc.set_antialiased(True)
        gc.set_capstyle(capstyle)
        gc.set_joinstyle(joinstyle)
        gc.set_snap(snap)
        gc.set_dashes(dashoffset, dashes)
        gc.set_alpha(alpha)

        self._rgbFace = None if facecolor and facecolor[3] == 0 else facecolor

    def end_patch(self):
        self._gc.restore()
        self.renderer.close_group('patch')

    def __enter__(self):
        self.begin_patch()
        return self

    def __exit__(self, *args):
        self.end_patch()


class FancierArrow:
    """
    Base class for fancier arrows.
    """
    LEFT = 'l'
    RIGHT = 'r'

    def __init__(self, fill=False, width=1., length=1., angle=None, side=None, inset=0.5, **style):
        self.fill = fill
        self.width = 2 * length / np.radians(angle) if angle else width
        self.length = length
        self.angle = angle if angle else np.arctan2(width / 2, length)
        self.side = side.lower()[0] if side else None
        self.inset = inset
        self.style = style

        hyp = np.hypot(width / 2, length)
        self.tan_a = width / 2 / length
        self.sin_a = width / 2 / hyp
        self.cos_a = length / hyp


class Kite(FancierArrow):
    """
    Kite shaped arrow.
    """
    def __init__(self, width=1., length=1., inset=0.75, side=None, fill=False, **kwargs):
        super().__init__(
            width=width,
            length=length,
            inset=inset,
            side=side,
            fill=fill,
            **kwargs)


    def get_arrow_head(self, linewidth, scale):

        side = self.side
        length, width = self.length, self.width
        inset = self.inset * length
        angle = np.arctan2(width / 2, length)

        xscale = yscale = scale

        if side and side in [FancierArrow.LEFT, FancierArrow.RIGHT]:
            miter = 0.5 * linewidth / np.tan(angle)
            path = Path(
                vertices=[(-length, 0), (-inset, -width / 2), (0, 0), (-length, 0)],
                codes=[Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
            if side == FancierArrow.LEFT:
                yscale = -yscale
        else:
            miter = 0.5 * linewidth / np.sin(angle)
            path = Path(
                vertices=[(-length, 0), (-inset, -width / 2),
                          (0, 0),
                          (-inset, width / 2), (-length, 0)],
                codes=[Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
        shorten = inset * scale + miter

        transform = Affine2D().scale(xscale, yscale).translate(-miter, 0)
        arrow_head = transform.transform_path(path)
        return arrow_head, shorten

class Stealth(FancierArrow):
    """
    Stealth-like arrow.
    """
    def __init__(
            self, width=1., length=1., inset=0.75, side=None, angle=None, fill=False, **kwargs):
        super().__init__(
            width=width,
            length=length,
            inset=inset,
            angle=angle,
            side=side,
            fill=fill,
            **kwargs)

    def get_arrow_head(self, linewidth, scale):
        side = self.side
        length, width = self.length, self.width
        inset = self.inset * length


        xscale = yscale = scale

        if side and side in [FancierArrow.LEFT, FancierArrow.RIGHT]:
            miter = 0.5 * linewidth / self.tan_a
            path = Path(
                vertices=[(-inset, 0), (0, 0), (-length, -width / 2), (-inset, 0)],
                codes=[Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
            if side == FancierArrow.LEFT:
                yscale = -yscale
        else:
            miter = 0.5 * linewidth / self.sin_a
            path = Path(
                vertices=[(-inset, 0), (-length, -width / 2),
                          (0, 0), (-length, width / 2),
                          (-inset, 0)],
                codes=[Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
        shorten = inset * scale + miter

        transform = Affine2D().scale(xscale, yscale).translate(-miter, 0)
        arrow_head = transform.transform_path(path)
        return arrow_head, shorten
