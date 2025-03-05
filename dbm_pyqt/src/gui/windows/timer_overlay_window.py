# src/gui/windows/timer_overlay_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint

class TimerOverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("技能倒计时显示")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 300, 200)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.skill_timers = []
        self.is_edit_mode = False
        self.drag_start_position = None #  记录窗口拖拽开始时的鼠标位置 (在窗口内)


    def set_edit_mode(self, enabled):
        """
        设置编辑模式状态。
        """
        self.is_edit_mode = enabled
        print(f"Overlay Window 编辑模式: {'启用' if self.is_edit_mode else '禁用'}")
        if enabled:
            self.setCursor(Qt.SizeFDiagCursor) #  编辑模式下，设置窗口鼠标光标为尺寸调整斜箭头，表示可拖拽窗口
        else:
            self.setCursor(Qt.ArrowCursor) #  正常模式下，恢复默认鼠标光标


    def add_timer_progress_bar(self, skill_timer):
        """
        将 SkillTimer 的进度条添加到 Overlay 窗口的布局中。
        """
        self.main_layout.addWidget(skill_timer.progress_bar)
        skill_timer.progress_bar.show()
        self.skill_timers.append(skill_timer)

    def remove_timer_progress_bar(self, skill_timer):
        """
        从 Overlay 窗口的布局中移除 SkillTimer 的进度条。
        """
        self.main_layout.removeWidget(skill_timer.progress_bar)
        #skill_timer.progress_bar.hide()
        self.skill_timers.remove(skill_timer)

    def clear_all_timers(self):
        """
        清除所有计时器和进度条。
        """
        for timer in list(self.skill_timers):
            self.remove_timer_progress_bar(timer)
            timer.stop_timer()


    # ---- 窗口拖拽事件处理 ----
    def mousePressEvent(self, event):
        """
        鼠标按下事件处理 (窗口拖拽开始)。
        """
        if self.is_edit_mode and event.button() == Qt.LeftButton: #  只有在编辑模式且按下鼠标左键时才开始拖拽窗口
            self.drag_start_position = event.pos() #  记录鼠标相对于窗口的初始位置
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件处理 (窗口拖拽移动)。
        """
        if self.is_edit_mode and self.drag_start_position: #  只有在编辑模式且拖拽已开始时才处理鼠标移动
            current_pos = event.pos() #  获取鼠标相对于窗口的当前位置
            offset = current_pos - self.drag_start_position #  计算鼠标偏移量
            self.move(self.frameGeometry().topLeft() + offset) #  移动窗口， frameGeometry().topLeft() 获取窗口在屏幕上的左上角坐标
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件处理 (窗口拖拽结束)。
        """
        if self.is_edit_mode and event.button() == Qt.LeftButton: #  只有在编辑模式且释放鼠标左键时才处理
            self.drag_start_position = None #  拖拽结束，清除拖拽开始位置
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def get_window_position(self):
        """
        获取窗口当前位置 (左上角坐标)。
        """
        return self.frameGeometry().topLeft()


class SkillTimer:
    def __init__(self, skill_name, duration_seconds, overlay_window, progress_bar_text="", progress_bar_color=None): # 添加 progress_bar_color 参数，默认值为 None
        self.duration_update_scale = 10;
        self.timer_interval = 10

        self.skill_name = skill_name
        self.duration_seconds = duration_seconds
        self.overlay_window = overlay_window
        self.progress_bar_text = progress_bar_text

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, duration_seconds * 1000)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(100)
        self.progress_bar.setFixedWidth(500)

        self._update_progress_bar_format()
 

        if progress_bar_color: # 如果 progress_bar_color 参数有效
            self.set_progress_bar_color(progress_bar_color) # 调用新的方法设置颜色

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.elapsed_seconds = 0
        self.is_running = False

    def set_progress_bar_color(self, color):
        """
        设置进度条颜色。
        """
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #E0E0E0; /* 背景色，可以根据需要调整 */
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background-color: {color}; /* 前景色，使用传入的颜色 */
                border-radius: 5px;
            }}
        """)

    def start_timer(self):
        """
        启动计时器，并将进度条添加到 Overlay 窗口。
        """
        if not self.is_running:
            self.is_running = True
            self.elapsed_seconds = 0
            self.elapsed_milliseconds = 0
            self.overlay_window.add_timer_progress_bar(self)
            self.timer.start(self.timer_interval)

    def update_progress(self):
        """
        更新进度条。
        """
        if not self.is_running:
            return

        self.elapsed_seconds += self.timer_interval/1000 # 增加计时器的计时间隔对应的秒数
        self.elapsed_milliseconds += self.timer_interval
        remaining_milliseconds = max(0, int(self.duration_seconds * 1000 - self.elapsed_milliseconds)) # 计算剩余秒数，确保不为负数
        progress_value = self.elapsed_milliseconds # 进度值增加毫秒数对应的数值 (duration_seconds * 10)
        self.progress_bar.setValue(progress_value) # 设置进度条值
        self._update_progress_bar_format(remaining_milliseconds) # 更新进度条格式，传入剩余秒数

        if self.elapsed_seconds >= self.duration_seconds:
            self.stop_timer()

    def stop_timer(self):
        """
        停止计时器，从 Overlay 窗口移除进度条并清理。
        """
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self._update_progress_bar_format(0, completed=True) # 计时结束时更新进度条格式，传入剩余秒数 0 和 completed=True
            self.overlay_window.remove_timer_progress_bar(self)

    def _update_progress_bar_format(self, remaining_milliseconds=None, completed=False):
        """
        更新进度条的文本格式。
        """
        if completed:
            format_text = f"{self.skill_name} - 完成" # 计时结束后显示 "完成"
        elif remaining_milliseconds is not None:
            format_text = f"{self.skill_name} - {self.progress_bar_text} - {remaining_milliseconds/1000:.2f} 秒" # 显示技能名，提示文字，剩余秒数
        else: # 初始格式，不显示秒数
            format_text = f"{self.skill_name} - {self.progress_bar_text}"

        self.progress_bar.setFormat(format_text) # 设置新的进度条格式


import time # 导入 time 模块

class ProgressBarWorkerThread(QThread):
    """
    工作线程，负责后台更新进度条的值。
    """
    progress_updated = pyqtSignal(int) # 定义信号，用于通知 SkillTimer 进度更新

    def __init__(self, duration_seconds):
        super().__init__()
        self.duration_seconds = duration_seconds
        self.max_value = duration_seconds * 10 # 对应 SkillTimer 中进度条的 range 设置
        self.current_value = 0
        self.is_running = False
        self.elapsed_seconds = 0.0 # 线程内部计时

    def run(self):
        """
        线程运行函数，执行后台进度更新任务。
        """
        self.is_running = True
        start_time = time.time() # 记录开始时间
        while self.is_running and self.elapsed_seconds < self.duration_seconds:
            time.sleep(0.02) # 模拟耗时操作，减少 CPU 占用，20ms 间隔，与新的定时器间隔一致
            self.elapsed_seconds = time.time() - start_time # 计算已逝去的时间
            progress_value = int(self.elapsed_seconds * 10) # 根据时间计算进度值
            if progress_value > self.max_value:
                progress_value = self.max_value # 确保不超过最大值
            self.progress_updated.emit(progress_value) # 发射信号，传递当前进度值

        self.is_running = False
        self.progress_updated.emit(self.max_value) # 确保最后进度达到 100%


    def stop_worker(self):
        """
        停止工作线程。
        """
        self.is_running = False
        self.wait() # 等待线程安全退出