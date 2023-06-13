import cv2


class Annotation:
    def __init__(self, col):
        self.pos_xy = []
        self.color = col


class Annotations:
    def __init__(self):
        self.annos = []
        self.new = True
        self.current_annotation = []

    def new_annotation(self, col):
        self.new = False
        self.current_annotation = Annotation(col)

    def append_pos(self, xy):
        self.current_annotation.pos_xy.append(xy)

    def end_annotation(self):
        self.new = True
        a = Annotation(
            self.current_annotation.color,
        )
        a.pos_xy = self.current_annotation.pos_xy
        self.annos.append(a)
        self.current_annotation.pos_xy = []

    def display_current_annotation(self, img):
        if not self.new:
            # if self.current_path is not None:
            col = self.current_annotation.color
            col = [col[2], col[1], col[0]]
            # col = (self.draw_color[2], self.draw_color[1], self.draw_color[0])
            if len(self.current_annotation.pos_xy) > 1:
                for i in range(len(self.current_annotation.pos_xy) - 1):
                    cv2.line(
                        img,
                        self.current_annotation.pos_xy[i],
                        self.current_annotation.pos_xy[i + 1],
                        color=col,
                        thickness=2,
                    )
            """for a in self.mouse_coords_annotations:
                if len(a) > 1:
                    for i in range(len(a) - 1):
                        cv2.line(
                            img,
                            a[i],
                            a[i + 1],
                            color=col,
                            thickness=2,
                        )"""
        return img

    def display_annotations(self, img):
        for a in self.annos:
            col = a.color
            col = [col[2], col[1], col[0]]
            if len(a.pos_xy) > 1:
                for i in range(len(a.pos_xy) - 1):
                    cv2.line(
                        img,
                        a.pos_xy[i],
                        a.pos_xy[i + 1],
                        color=col,
                        thickness=2,
                    )
        return img
