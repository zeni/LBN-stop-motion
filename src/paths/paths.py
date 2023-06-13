from enums import PathType, PathMotion
import numpy as np
import cv2


class Path:
    def __init__(self, r, min_l, seg, col, type, motion):
        self.ratio = r
        self.min_length = min_l
        self.segments = seg
        self.color = col
        self.type = type
        self.motion = motion
        self.pos_xy = []


class Paths:
    def __init__(self):
        self.paths = []
        self.new = True
        self.current_path = []

    def new_path(self, r, min_l, seg, col, type, motion):
        self.new = False
        self.current_path = Path(r, min_l, seg, col, type, motion)

    def append_pos(self, xy):
        self.current_path.pos_xy.append(xy)

    def end_path(self):
        self.new = True
        p = Path(
            self.current_path.ratio,
            self.current_path.min_length,
            self.current_path.segments,
            self.current_path.color,
            self.current_path.type,
            self.current_path.motion,
        )
        p.pos_xy = self.current_path.pos_xy
        self.paths.append(p)
        self.current_path.pos_xy = []

    def display_current_path(self, img, xy):
        if not self.new:
            # if self.current_path is not None:
            col = self.current_path.color
            col = [col[2], col[1], col[0]]
            if len(self.current_path.pos_xy) >= 2:
                for i in range(len(self.current_path.pos_xy) - 1):
                    pA = (
                        self.current_path.pos_xy[i][0],
                        self.current_path.pos_xy[i][1],
                    )
                    pB = (
                        self.current_path.pos_xy[i + 1][0],
                        self.current_path.pos_xy[i + 1][1],
                    )
                    cv2.line(img, pA, pB, col, 2)
            if len(self.current_path.pos_xy) > 0:
                if len(self.current_path.pos_xy) > 0 and not self.new and len(xy) > 0:
                    cv2.line(
                        img,
                        self.current_path.pos_xy[-1],
                        xy,
                        col,
                        2,
                    )
        return img

    def display_paths(self, img):
        for p in self.paths:
            if p.type == PathType.LINEAR:
                img = self.display_path_linear(img, p)
            elif p.type == PathType.HALF:
                img = self.display_path_half(img, p)
            elif p.type == PathType.RATIO:
                img = self.display_path_ratio(img, p)
        return img

    def display_path_linear(self, img, path):
        col = path.color
        col = [col[2], col[1], col[0]]
        if len(path.pos_xy) >= 2:
            d = 5
            n = path.segments
            le = 0
            for i in range(len(path.pos_xy) - 1):
                pA = (path.pos_xy[i][0], path.pos_xy[i][1])
                pB = (path.pos_xy[i + 1][0], path.pos_xy[i + 1][1])
                le += np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
            l = int(le / n)
            l0 = 0
            for i in range(len(path.pos_xy) - 1):
                if path.pos_xy[i][0] == path.pos_xy[i + 1][0]:
                    x = path.pos_xy[i][0]
                    pA = (x, path.pos_xy[i][1])
                    pB = (x, path.pos_xy[i + 1][1])
                    if path.pos_xy[i][1] < path.pos_xy[i + 1][1]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    nl = int((ls - l0) / l)
                    for k in range(nl + 1):
                        p1 = (x - d, pA[1] + inc * (k * l + l0))
                        p2 = (x + d, pA[1] + inc * (k * l + l0))
                        cv2.line(img, p1, p2, col, 2)
                    y = pA[1] + inc * ((nl + 1) * l + l0)
                    l0 = int(np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2) - ls)
                elif path.pos_xy[i][1] == path.pos_xy[i + 1][1]:
                    y = path.pos_xy[i][1]
                    pA = (path.pos_xy[i][0], y)
                    pB = (path.pos_xy[i + 1][0], y)
                    if path.pos_xy[i][0] < path.pos_xy[i + 1][0]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    nl = int((ls - l0) / l)
                    for k in range(nl + 1):
                        p1 = (pA[0] + inc * (k * l + l0), y - d)
                        p2 = (pA[0] + inc * (k * l + l0), y + d)
                        cv2.line(img, p1, p2, col, 2)
                    x = pA[0] + inc * ((nl + 1) * l + l0)
                    l0 = int(np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2) - ls)
                else:
                    pA = (path.pos_xy[i][0], path.pos_xy[i][1])
                    pB = (path.pos_xy[i + 1][0], path.pos_xy[i + 1][1])
                    if path.pos_xy[i][0] < path.pos_xy[i + 1][0]:
                        inc = 1
                    else:
                        inc = -1
                    a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                    b = pA[1] - a * pA[0]
                    b1 = b + d * np.sqrt(1 + a * a)
                    b2 = b - d * np.sqrt(1 + a * a)
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    nl = int((ls - l0) / l)
                    for k in range(nl + 1):
                        x = pA[0] + inc * (l * k + l0) / np.sqrt(1 + a * a)
                        y = a * x + b
                        b3 = y + 1 / a * x
                        x1 = (b3 - b1) * a / (1 + a * a)
                        x2 = (b3 - b2) * a / (1 + a * a)
                        y1 = a * x1 + b1
                        y2 = a * x2 + b2
                        p1 = (int(x1), int(y1))
                        p2 = (int(x2), int(y2))
                        cv2.line(img, p1, p2, col, 2)
                    x = pA[0] + inc * (l * (nl + 1) + l0) / np.sqrt(1 + a * a)
                    y = a * x + b
                    l0 = int(np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2) - ls)
        return img

    def display_path_ratio(self, img, path):
        col = path.color
        col = [col[2], col[1], col[0]]
        r = path.ratio
        li = path.min_length
        if len(path.pos_xy) >= 2:
            d = 5
            n = path.segments
            le = 0
            for i in range(len(path.pos_xy) - 1):
                pA = (path.pos_xy[i][0], path.pos_xy[i][1])
                pB = (path.pos_xy[i + 1][0], path.pos_xy[i + 1][1])
                le += np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
            l = int(le / n)
            l0 = 0
            k = 0
            if path.motion == PathMotion.DEC:
                s = len(path.pos_xy) - 1
                e = 0
                dir = -1
            else:
                s = 0
                e = len(path.pos_xy) - 1
                dir = 1
            for i in range(s, e, dir):
                # for i in range(len(path.pos_xy) - 1, 0, -1): for reverse with i-1
                if path.pos_xy[i][0] == path.pos_xy[i + dir][0]:
                    x = path.pos_xy[i][0]
                    pA = (x, path.pos_xy[i][1])
                    pB = (x, path.pos_xy[i + dir][1])
                    if path.pos_xy[i][1] < path.pos_xy[i + dir][1]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l_current = 0
                    l = 0
                    while l_current <= ls:
                        l_current = l + l0
                        if l_current <= ls:
                            p1 = (x - d, int(pA[1] + inc * int(l_current)))
                            p2 = (x + d, int(pA[1] + inc * int(l_current)))
                            cv2.line(img, p1, p2, col, 2)
                            k += 1
                            l += li * r**k
                        else:
                            l0 = l_current - ls
                elif path.pos_xy[i][1] == path.pos_xy[i + dir][1]:
                    y = path.pos_xy[i][1]
                    pA = (path.pos_xy[i][0], y)
                    pB = (path.pos_xy[i + dir][0], y)
                    if path.pos_xy[i][0] < path.pos_xy[i + dir][0]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l_current = 0
                    l = 0
                    while l_current <= ls:
                        l_current = l + l0
                        if l_current <= ls:
                            p1 = (int(pA[0] + inc * int(l_current)), y - d)
                            p2 = (int(pA[0] + inc * int(l_current)), y + d)
                            cv2.line(img, p1, p2, col, 2)
                            k += 1
                            l += li * r**k
                        else:
                            l0 = l_current - ls
                else:
                    pA = (path.pos_xy[i][0], path.pos_xy[i][1])
                    pB = (path.pos_xy[i + dir][0], path.pos_xy[i + dir][1])
                    if path.pos_xy[i][0] < path.pos_xy[i + dir][0]:
                        inc = 1
                    else:
                        inc = -1
                    a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                    b = pA[1] - a * pA[0]
                    b1 = b + d * np.sqrt(1 + a * a)
                    b2 = b - d * np.sqrt(1 + a * a)
                    cv2.line(img, pA, pB, col, 2)
                    ls = np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                    l_current = 0
                    l = 0
                    while l_current <= ls:
                        x = pA[0] + inc * (l + l0) / np.sqrt(1 + a * a)
                        y = a * x + b
                        l_current = np.sqrt((pA[0] - x) ** 2 + (pA[1] - y) ** 2)
                        if l_current <= ls:
                            b3 = y + 1 / a * x
                            x1 = (b3 - b1) * a / (1 + a * a)
                            x2 = (b3 - b2) * a / (1 + a * a)
                            y1 = a * x1 + b1
                            y2 = a * x2 + b2
                            p1 = (int(x1), int(y1))
                            p2 = (int(x2), int(y2))
                            cv2.line(img, p1, p2, col, 2)
                            k += 1
                            l += li * r**k
                        else:
                            l0 = l_current - ls
        return img

    def display_path_half(self, img, path):
        col = path.color
        col = [col[2], col[1], col[0]]
        li = path.min_length
        if len(path.pos_xy) >= 2:
            d = 5
            le = 0
            parts_l = []
            parts_l.append(0)
            for i in range(len(path.pos_xy) - 1):
                pA = (path.pos_xy[i][0], path.pos_xy[i][1])
                pB = (path.pos_xy[i + 1][0], path.pos_xy[i + 1][1])
                le += np.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2)
                parts_l.append(le)
            lm = parts_l[-1]
            l_half = parts_l[-1]
            while l_half > li:
                l_half = l_half / 2
                if path.motion == PathMotion.DEC:
                    lm = parts_l[-1] - l_half
                else:
                    lm = l_half
                current_part = 0
                for i in range(len(parts_l) - 1):
                    if lm >= parts_l[i] and lm < parts_l[i + 1]:
                        current_part = i
                        break
                l = lm - parts_l[current_part]
                if path.pos_xy[i][0] == path.pos_xy[i + 1][0]:
                    x = path.pos_xy[i][0]
                    pA = (x, path.pos_xy[i][1])
                    pB = (x, path.pos_xy[i + 1][1])
                    if path.pos_xy[i][1] < path.pos_xy[i + 1][1]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    p1 = (x - d, int(pA[1] + inc * int(l)))
                    p2 = (x + d, int(pA[1] + inc * int(l)))
                    cv2.line(img, p1, p2, col, 2)
                elif path.pos_xy[i][1] == path.pos_xy[i + 1][1]:
                    y = path.pos_xy[i][1]
                    pA = (path.pos_xy[i][0], y)
                    pB = (path.pos_xy[i + 1][0], y)
                    if path.pos_xy[i][0] < path.pos_xy[i + 1][0]:
                        inc = 1
                    else:
                        inc = -1
                    cv2.line(img, pA, pB, col, 2)
                    p1 = (int(pA[0] + inc * int(l)), y - d)
                    p2 = (int(pA[0] + inc * int(l)), y + d)
                    cv2.line(img, p1, p2, col, 2)

                else:
                    pA = (path.pos_xy[current_part][0], path.pos_xy[current_part][1])
                    pB = (
                        path.pos_xy[current_part + 1][0],
                        path.pos_xy[current_part + 1][1],
                    )
                    if path.pos_xy[current_part][0] < path.pos_xy[current_part + 1][0]:
                        inc = 1
                    else:
                        inc = -1
                    a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                    b = pA[1] - a * pA[0]
                    b1 = b + d * np.sqrt(1 + a * a)
                    b2 = b - d * np.sqrt(1 + a * a)
                    cv2.line(img, pA, pB, col, 2)
                    x = pA[0] + inc * l / np.sqrt(1 + a * a)
                    y = a * x + b
                    b3 = y + 1 / a * x
                    x1 = (b3 - b1) * a / (1 + a * a)
                    x2 = (b3 - b2) * a / (1 + a * a)
                    y1 = a * x1 + b1
                    y2 = a * x2 + b2
                    p1 = (int(x1), int(y1))
                    p2 = (int(x2), int(y2))
                    cv2.line(img, p1, p2, col, 2)
            pA = (path.pos_xy[-2][0], path.pos_xy[-2][1])
            pB = (path.pos_xy[-1][0], path.pos_xy[-1][1])
            cv2.line(img, pA, pB, col, 2)
            if path.pos_xy[0][0] == path.pos_xy[1][0]:
                x = path.pos_xy[0][0]
                y = path.pos_xy[0][1]
                p1 = (int(x - d), int(y))
                p2 = (int(x + d), int(y))
                cv2.line(img, p1, p2, col, 2)
            elif path.pos_xy[0][1] == path.pos_xy[1][1]:
                x = path.pos_xy[0][0]
                y = path.pos_xy[0][1]
                p1 = (int(x), int(y - d))
                p2 = (int(x), int(y + d))
                cv2.line(img, p1, p2, col, 2)
            else:
                pA = (path.pos_xy[0][0], path.pos_xy[0][1])
                pB = (path.pos_xy[1][0], path.pos_xy[1][1])
                a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                b = pA[1] - a * pA[0]
                b1 = b + d * np.sqrt(1 + a * a)
                b2 = b - d * np.sqrt(1 + a * a)
                x = pA[0]
                y = a * x + b
                b3 = y + 1 / a * x
                x1 = (b3 - b1) * a / (1 + a * a)
                x2 = (b3 - b2) * a / (1 + a * a)
                y1 = a * x1 + b1
                y2 = a * x2 + b2
                p1 = (int(x1), int(y1))
                p2 = (int(x2), int(y2))
                cv2.line(img, p1, p2, col, 2)
            if path.pos_xy[-2][0] == path.pos_xy[-1][0]:
                x = path.pos_xy[-1][0]
                y = path.pos_xy[-1][1]
                p1 = (int(x - d), int(y))
                p2 = (int(x + d), int(y))
                cv2.line(img, p1, p2, col, 2)
            elif path.pos_xy[-2][1] == path.pos_xy[-1][1]:
                x = path.pos_xy[-1][0]
                y = path.pos_xy[-1][1]
                p1 = (int(x), int(y - d))
                p2 = (int(x), int(y + d))
                cv2.line(img, p1, p2, col, 2)
            else:
                pA = (path.pos_xy[-2][0], path.pos_xy[-2][1])
                pB = (path.pos_xy[-1][0], path.pos_xy[-1][1])
                # cv2.line(img, pA, pB, col, 2)
                a = (pA[1] - pB[1]) / (pA[0] - pB[0])
                b = pA[1] - a * pA[0]
                b1 = b + d * np.sqrt(1 + a * a)
                b2 = b - d * np.sqrt(1 + a * a)
                x = pB[0]
                y = a * x + b
                b3 = y + 1 / a * x
                x1 = (b3 - b1) * a / (1 + a * a)
                x2 = (b3 - b2) * a / (1 + a * a)
                y1 = a * x1 + b1
                y2 = a * x2 + b2
                p1 = (int(x1), int(y1))
                p2 = (int(x2), int(y2))
                cv2.line(img, p1, p2, col, 2)
        return img
