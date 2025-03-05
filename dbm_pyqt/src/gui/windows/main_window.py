# src/gui/windows/main_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QCheckBox, QComboBox
from PyQt5.QtCore import Qt, QPoint
import json  # 导入 json 模块
import os    # 导入 os 模块

from src.core.data_manager import DataManager
from src.gui.windows.timer_overlay_window import TimerOverlayWindow, SkillTimer

class DBMWindow(QWidget):
    # 配置文件路径
    WINDOW_CONFIG_FILE = os.path.join("resources", "data", "window_config.json")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBM 应用程序")
        self.setGeometry(300, 300, 800, 600)

        self.data_manager = DataManager()
        self.data_manager.load_boss_data()

        # ---- UI 布局调整 ---- (保持不变) ----
        main_layout = QHBoxLayout(self)
        boss_list_layout = QVBoxLayout()
        boss_list_layout.addWidget(QLabel("Boss 列表"))
        self.boss_list_widget = QListWidget()
        boss_list_layout.addWidget(self.boss_list_widget)
        self.boss_description_label = QLabel("Boss 描述将显示在这里")
        boss_list_layout.addWidget(self.boss_description_label)
        main_layout.addLayout(boss_list_layout)
        timer_control_layout = QVBoxLayout()
        timer_control_layout.addWidget(QLabel("技能倒计时控制"))
        self.boss_selection_combobox = QComboBox()
        self.boss_selection_combobox.addItem("请选择 Boss")
        boss_names = self.data_manager.get_boss_names()
        self.boss_selection_combobox.addItems(boss_names)
        self.boss_selection_combobox.currentIndexChanged.connect(self.on_boss_selected)
        timer_control_layout.addWidget(self.boss_selection_combobox)
        self.edit_mode_checkbox = QCheckBox("编辑模式")
        self.edit_mode_checkbox.stateChanged.connect(self.toggle_edit_mode)
        timer_control_layout.addWidget(self.edit_mode_checkbox)
        self.start_timer_button = QPushButton("触发技能倒计时")
        self.start_timer_button.clicked.connect(self.start_skill_timer)
        timer_control_layout.addWidget(self.start_timer_button)
        main_layout.addLayout(timer_control_layout)
        # ---- 布局调整结束 ----

        self.populate_boss_list()

        self.overlay_window = TimerOverlayWindow()
        self.skill_timers = []

        self.load_window_position() # 加载窗口位置
        self.overlay_window.show()
        self.is_edit_mode_enabled = False

    def closeEvent(self, event):
        self.save_window_position() # 保存窗口位置
        self.overlay_window.close()
        event.accept()

    def populate_boss_list(self):
        # ... (populate_boss_list 方法保持不变) ...
        self.boss_list_widget.itemClicked.connect(self.on_boss_item_clicked)

    def on_boss_item_clicked(self, item):
        # ... (on_boss_item_clicked 方法保持不变) ...
        self.boss_description_label.setTextFormat(Qt.RichText)

    def on_boss_selected(self, index):
        """
        当 Boss 选择下拉框选项改变时触发。
        """
        boss_name = self.boss_selection_combobox.currentText() # 获取当前选中的 Boss 名称
        if boss_name != "请选择 Boss": #  忽略默认提示选项
            print(f"选定的 Boss: {boss_name}") #  控制台输出选定的 Boss 名称
            #  (后续可以在这里根据选定的 Boss 加载技能列表或执行其他操作)
        else:
            print("未选择 Boss")

    def start_skill_timer(self):
        """
        触发选定 Boss 的技能倒计时 (临时实现：触发所有技能的无条件倒计时)。
        """
        selected_boss_name = self.boss_selection_combobox.currentText() # 获取选定的 Boss 名称
        if selected_boss_name == "请选择 Boss":
            print("请先选择 Boss")
            return

        skill_data_list = self.data_manager.get_boss_skill_data(selected_boss_name) # 获取选定 Boss 的技能数据
        if skill_data_list:
            for skill_data in skill_data_list:
                skill_name = skill_data.get('name')
                duration_seconds = skill_data.get('countdown_duration')
                progress_bar_text = skill_data.get('progress_bar_text', "")
                trigger_condition = skill_data.get('trigger_condition')
                progress_bar_color = skill_data.get('progress_bar_color') # 获取 progress_bar_color

                if trigger_condition == "unconditional":
                    if skill_name and duration_seconds:
                        skill_timer = SkillTimer(skill_name, duration_seconds, self.overlay_window, progress_bar_text, progress_bar_color) # 传递 progress_bar_color 参数
                        skill_timer.start_timer()
                        print(f"触发技能倒计时: {skill_name}, 持续时间: {duration_seconds}秒, 提示文字: {progress_bar_text}, 颜色: {progress_bar_color}") # 控制台输出颜色信息
        else:
            print(f"未找到 Boss '{selected_boss_name}' 的技能数据")


    def toggle_edit_mode(self, state):
        self.is_edit_mode_enabled = (state == Qt.Checked)
        self.overlay_window.set_edit_mode(self.is_edit_mode_enabled)
        print(f"编辑模式切换为: {'启用' if self.is_edit_mode_enabled else '禁用'}")
        if not self.is_edit_mode_enabled: #  当编辑模式关闭时，保存窗口位置
            self.save_window_position() # 保存窗口位置


    def save_window_position(self):
        """
        保存 TimerOverlayWindow 的位置到配置文件。
        """
        position = self.overlay_window.get_window_position()
        try:
            with open(self.WINDOW_CONFIG_FILE, 'w') as f:
                json.dump({'x': position.x(), 'y': position.y()}, f) # 保存 x 和 y 坐标
            print(f"窗口位置已保存到: {self.WINDOW_CONFIG_FILE}")
        except Exception as e:
            print(f"保存窗口位置失败: {e}")

    def load_window_position(self):
        """
        从配置文件加载 TimerOverlayWindow 的位置。
        """
        try:
            if os.path.exists(self.WINDOW_CONFIG_FILE): # 检查配置文件是否存在
                with open(self.WINDOW_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    x = config.get('x')
                    y = config.get('y')
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)): # 验证坐标值类型
                        self.overlay_window.move(QPoint(int(x), int(y))) # 移动窗口到加载的位置
                        print(f"窗口位置已从 {self.WINDOW_CONFIG_FILE} 加载")
                    else:
                        print("配置文件中窗口位置数据无效，使用默认位置")
            else:
                print(f"窗口配置文件未找到: {self.WINDOW_CONFIG_FILE}, 使用默认位置")
        except Exception as e:
            print(f"加载窗口位置失败: {e}, 使用默认位置. 错误信息: {e}")
