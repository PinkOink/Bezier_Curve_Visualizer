import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAbstractButton
from PyQt5.QtGui import QPainter, QPen, QBrush, QMouseEvent
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widthApp, self.heightApp  = 800, 600

        self.border = 5
        self.button_border = self.border + 35
        self.radius = 5

        self.left_draw = self.border
        self.right_draw = self.widthApp - self.border
        self.up_draw = self.button_border
        self.down_draw = self.heightApp - self.border

        self.par_step = 0.001
        self.par_dir = 1
        self.par = 0

        self.pivot_points = [
            [100,200],
            [300,500],
            [300,150],
            [600,170]
        ]
        self.bezier_points = self.get_bezier_points()
        self.cur_move_point = -1

        self.initUI()

        self.my_timer = QTimer(self, timeout=self.draw_func, interval=100)
        self.my_timer.start()
        self.timer = 0


    def initUI(self):
        self.setMinimumSize(QSize(self.widthApp, self.heightApp))
        self.setMaximumSize(QSize(self.widthApp, self.heightApp))
        self.setGeometry(680, 400, self.widthApp, self.heightApp)
        self.setWindowTitle('Bezier Curve Visualizer')

        button = QPushButton('Add point', self)
        button.move(self.border,self.border)
        button.clicked.connect(self.click_add_point)

        button = QPushButton('Delete point', self)
        button.move(100 + self.border,self.border)
        button.clicked.connect(self.click_delete_point)

        button = QPushButton('Pause', self)
        button.move(200 + self.border,self.border)
        button.clicked.connect(self.click_pause)
        self.pause_button = button

        button = QPushButton('Play', self)
        button.move(300 + self.border,self.border)
        button.clicked.connect(self.click_play)
        button.setEnabled(False)
        self.play_button = button

        self.setMouseTracking(True)

        self.show()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            click_point = [event.pos().x(), event.pos().y()]
            for i in range(0, len(self.pivot_points)):
                if (click_point[0] >= self.pivot_points[i][0] and
                    click_point[0] <= (self.pivot_points[i][0] + 2 * self.radius) and
                        click_point[1] >= self.pivot_points[i][1] and
                        click_point[1] <= (self.pivot_points[i][1] + 2 * self.radius)):
                    self.cur_move_point = i
                    return


    def mouseMoveEvent(self, event):
        if self.cur_move_point != -1:
            mouse_point = [min(max(event.pos().x(), self.left_draw), self.right_draw),
                           min(max(event.pos().y(), self.up_draw), self.down_draw)]
            self.pivot_points[self.cur_move_point][0] = mouse_point[0] - self.radius
            self.pivot_points[self.cur_move_point][1] = mouse_point[1] - self.radius
            self.bezier_points = self.get_bezier_points()
            return


    def mouseReleaseEvent(self, event):
        if self.cur_move_point != -1:
            self.cur_move_point = -1


    def get_bezier_points(self):
        par = 0.0
        bezier_points = []
        while par < 1:
            buffer_points = self.pivot_points
            while len(buffer_points) != 1:
                next_points = []
                for i in range(0, len(buffer_points) - 1):
                    point = [buffer_points[i][0] + par * (buffer_points[i + 1][0] - buffer_points[i][0]),
                             buffer_points[i][1] + par * (buffer_points[i + 1][1] - buffer_points[i][1])]
                    next_points.append(point)
                buffer_points = next_points
            bezier_points.append(buffer_points[0])
            par = par + self.par_step
        return bezier_points


    def click_add_point(self):
        new_point = [(self.right_draw + self.left_draw) / 2,
                     (self.down_draw + self.up_draw) / 2]
        self.pivot_points.append(new_point)
        self.bezier_points = self.get_bezier_points()
        self.update()


    def click_delete_point(self):
        if len(self.pivot_points) > 2:
            self.pivot_points.pop(len(self.pivot_points) - 1)
            self.bezier_points = self.get_bezier_points()
            self.update()


    def click_pause(self):
        self.pause_button.setEnabled(False)
        self.play_button.setEnabled(True)
        self.par_dir = 0


    def click_play(self):
        self.pause_button.setEnabled(True)
        self.play_button.setEnabled(False)
        self.par_dir = 1


    def draw_func(self):
        painter = QPainter(self)
        painter.begin(self)

        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(self.left_draw, self.up_draw, self.right_draw - self.left_draw, self.down_draw - self.up_draw)

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        buffer_points = self.pivot_points
        while len(buffer_points) != 1:
            next_points = []
            for i in range(0, len(buffer_points) - 1):
                point = [buffer_points[i][0] + self.par * (buffer_points[i + 1][0] - buffer_points[i][0]),
                         buffer_points[i][1] + self.par * (buffer_points[i + 1][1] - buffer_points[i][1])]
                painter.drawLine(int(buffer_points[i][0] + self.radius), int(buffer_points[i][1] + self.radius),
                                 int(buffer_points[i + 1][0] + self.radius), int(buffer_points[i + 1][1] + self.radius))
                next_points.append(point)
            buffer_points = next_points

        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        for i in range(0, len(self.bezier_points) - 1):
            painter.drawLine(int(self.bezier_points[i][0] + self.radius), int(self.bezier_points[i][1] + self.radius),
                             int(self.bezier_points[i + 1][0] + self.radius), int(self.bezier_points[i + 1][1] + self.radius))

        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.blue))
        buffer_points = self.pivot_points
        while len(buffer_points) != 1:
            next_points = []
            for i in range(0, len(buffer_points) - 1):
                point = [buffer_points[i][0] + self.par * (buffer_points[i + 1][0] - buffer_points[i][0]),
                         buffer_points[i][1] + self.par * (buffer_points[i + 1][1] - buffer_points[i][1])]
                painter.drawEllipse(int(point[0]), int(point[1]), 2 * self.radius, 2 * self.radius)
                next_points.append(point)
            buffer_points = next_points

        painter.setBrush(QBrush(Qt.green))
        for point in self.pivot_points:
            painter.drawEllipse(int(point[0]), int(point[1]), 2 * self.radius, 2 * self.radius)

        painter.end()

        if self.par >= 1:
            self.par_dir = -1
        if self.par <= 0:
            self.par_dir = 1
        self.par = self.par + self.par_dir * self.par_step
        self.update()


    def paintEvent(self, e):
        self.draw_func()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())