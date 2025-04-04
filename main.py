import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QTimer, QRect
import threading
import json
import os

print("可用命令：")
print("notice -t [内容] - 修改文本")
print("notice -s [大小] - 修改字号")
print("notice -a [透明度] - 修改背景透明度")
print("exit - 退出程序")

class TransparentNotice(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # # 初始参数
        # self.text = "输入 notice -t 内容 修改文本\n输入 notice -s 数字 修改大小"
        # self.font_size = 20
        # self.opacity = 0.8  # 背景透明度

        # # 设置尺寸和位置（右下角）
        # screen = QApplication.primaryScreen().geometry()
        # self.setGeometry(screen.width() - 420, screen.height() - 180, 400, 150)

        # # 创建文字标签
        # self.label = QLabel(self.text, self)
        # self.label.setFont(QFont("Microsoft YaHei", self.font_size))
        # self.label.setStyleSheet("color: white;")
        # self.label.setAlignment(Qt.AlignCenter)
        # self.label.setGeometry(0, 0, 400, 150)

        # # 启动控制台线程
        # threading.Thread(target=self.console_handler, daemon=True).start()
                # 加载配置
        self.config_file = "config.json"
        self.load_config()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置尺寸和位置（右下角）
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 420, screen.height() - 180, 400, 150)

        # 创建文字标签
        self.label = QLabel(self.text, self)
        self.label.setFont(QFont("Microsoft YaHei", self.font_size))
        self.label.setStyleSheet("color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 400, 150)

        # 启动控制台线程
        threading.Thread(target=self.console_handler, daemon=True).start()

    def load_config(self):
        """从配置文件加载设置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.text = config.get("text", "输入 notice -t 内容 修改文本\n输入 notice -s 数字 修改大小")
                self.font_size = config.get("font_size", 20)
                self.opacity = config.get("opacity", 0.8)
        else:
            # 默认配置
            self.text = "输入 notice -t 内容 修改文本\n输入 notice -s 数字 修改大小"
            self.font_size = 20
            self.opacity = 0.8

    def save_config(self):
        """将设置保存到配置文件"""
        config = {
            "text": self.text,
            "font_size": self.font_size,
            "opacity": self.opacity
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def paintEvent(self, event):
        # 绘制半透明背景
        painter = QPainter(self)
        color = QColor(0, 0, 0, int(self.opacity * 255))
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False


    def update_display(self):
        self.label.setText(self.text)
        self.label.setFont(QFont("Microsoft YaHei", self.font_size))
        self.update()

    def console_handler(self):
        while True:
            try:
                cmd = input(">>> ").strip().lower()
                if cmd.startswith("notice -t "):
                    self.text = cmd[10:]
                    self.save_config()  # 每次更新后保存设置
                    QTimer.singleShot(0, self.update_display)
                elif cmd.startswith("notice -s "):
                    try:
                        self.font_size = int(cmd[10:])
                        self.save_config()  # 每次更新后保存设置
                        QTimer.singleShot(0, self.update_display)
                    except ValueError:
                        print("字体大小必须是整数")
                elif cmd.startswith("notice -a "):
                    try:
                        val = float(cmd[10:])
                        if 0.0 <= val <= 1.0:
                            self.opacity = val
                            self.save_config()  # 每次更新后保存设置
                            QTimer.singleShot(0, self.update)
                        else:
                            print("透明度必须在0.0到1.0之间")
                    except ValueError:
                        print("透明度必须是数字")
                elif cmd == "exit":
                    self.save_config()  # 程序退出前保存设置
                    QTimer.singleShot(0, self.close)
                    break
                else:
                    print("可用命令：\nnotice -t [内容] - 修改文本\nnotice -s [大小] - 修改字号\nnotice -a [透明度] - 修改背景透明度\nexit - 退出程序")
            except EOFError:
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    notice = TransparentNotice()
    notice.show()
    sys.exit(app.exec_())
