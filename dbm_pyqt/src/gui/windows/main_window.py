# src/gui/windows/main_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QCheckBox, QComboBox
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
import json  # 导入 json 模块
import os    # 导入 os 模块

from src.core.data_manager import DataManager
from src.gui.windows.timer_overlay_window import TimerOverlayWindow, SkillTimer
from src.utils.trigger_check_thread import TriggerCheckThread

class DBMWindow(QWidget):
    # 配置文件路径
    WINDOW_CONFIG_FILE = os.path.join("resources", "data", "window_config.json")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBM 应用程序")
        self.setGeometry(300, 300, 800, 600)

        self.trigger_check_thread = None # 初始化触发检查线程为 None

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
        self.start_timer_button.clicked.connect(self.start_first_timer)
        timer_control_layout.addWidget(self.start_timer_button)
        main_layout.addLayout(timer_control_layout)
        # ---- 布局调整结束 ----

        self.populate_boss_list()

        self.overlay_window = TimerOverlayWindow()

        self.load_window_position() # 加载窗口位置
        self.overlay_window.show()
        self.is_edit_mode_enabled = False
        self.start_trigger_check_thread() #  启动触发检查线程  <--- 启动线程


    def closeEvent(self, event):
        self.save_window_position() # 保存窗口位置
        self.stop_trigger_check_thread() #  停止触发检查线程  <--- 停止线程
        self.overlay_window.close()
        event.accept()

    def start_trigger_check_thread(self):
        """
        启动通用的触发检查工作线程。
        """
        if self.trigger_check_thread is None: #  只在线程未创建时创建
            self.trigger_check_thread = TriggerCheckThread(self) # 创建触发检查线程实例
            self.trigger_check_thread.trigger_check_finished.connect(self.handle_trigger_check_result) # 连接信号和槽函数  <--- 连接信号
            self.trigger_check_thread.start() # 启动线程
            print("触发检查线程已启动")
        elif not self.trigger_check_thread.isRunning(): # 如果线程已创建但未运行，则重新启动
            self.trigger_check_thread.start()
            print("触发检查线程已重新启动")
        else:
            print("触发检查线程已在运行中，无需启动")

    def stop_trigger_check_thread(self):
        """
        停止触发检查工作线程。
        """
        if self.trigger_check_thread and self.trigger_check_thread.isRunning():
            self.trigger_check_thread.stop_worker()
            self.trigger_check_thread.trigger_check_finished.disconnect(self.handle_trigger_check_result) # 断开信号连接
            self.trigger_check_thread = None #  设置为 None，方便下次重新创建
            print("触发检查线程已停止")
        else:
            print("触发检查线程未运行或未创建，无需停止")

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

    def start_first_timer(self):
        """
        触发选定 Boss 的技能倒计时 (临时实现：触发所有技能的无条件倒计时)。
        """
        selected_boss_name = self.boss_selection_combobox.currentText() # 获取选定的 Boss 名称
        if selected_boss_name == "请选择 Boss":
            print("请先选择 Boss")
            return

        skill_data_list = self.data_manager.get_boss_skill_data(selected_boss_name) # 获取选定 Boss 的技能数据
        if skill_data_list:
            skill_data = skill_data_list[0]
            if skill_data:
                self.try_start_new_timer(skill_data)
        else:
            print(f"未找到 Boss '{selected_boss_name}' 的技能数据")

    def try_start_new_timer(self, skill_data):
        trigger_condition = skill_data.get('trigger_condition')

        if trigger_condition in ["unconditional", "condition_image"]: #  只处理 unconditional 和 condition_image 触发条件
            print(f"将技能 '{skill_data.get('name')}' 的触发检查任务放入队列")
            self.trigger_check_thread.enqueue_task(skill_data) # 将技能数据作为任务放入队列 <---  放入任务队列
        else:
            print(f"未知触发条件类型: {trigger_condition}，技能 '{skill_data.get('name')}' 无法触发")


    @pyqtSlot(str, bool) #  槽函数，接收技能名称和触发结果
    def handle_trigger_check_result(self, skill_name, result):
        """
        处理触发检查线程返回的触发结果。  运行在 GUI 线程中。
        """
        print(f"接收到技能 '{skill_name}' 的触发检查结果: {result}")
        if result: # 触发条件满足
            skill_data_list = self.data_manager.get_boss_skill_data(self.boss_selection_combobox.currentText()) #  重新获取 Boss 技能数据
            if skill_data_list:
                for skill_data in skill_data_list:
                    if skill_data.get('name') == skill_name: #  找到对应的技能数据
                        skill_name = skill_data.get('name')
                        duration_seconds = skill_data.get('countdown_duration')
                        progress_bar_text = skill_data.get('progress_bar_text', "")
                        progress_bar_color = skill_data.get('progress_bar_color')
                        show_progress = skill_data.get('show', True)

                        skill_timer = SkillTimer(skill_name, duration_seconds, self.overlay_window, self, progress_bar_text, progress_bar_color, show_progress)
                        skill_timer.start_timer()
                        print(f"触发条件满足，启动技能倒计时 (工作线程触发): {skill_name}, 持续时间: {duration_seconds}秒, 提示: {progress_bar_text}, 颜色: {progress_bar_color}, 显示进度条: {show_progress}")
                        break # 找到技能后跳出循环
        else:
            print(f"技能 '{skill_name}' 的触发条件不满足，未触发倒计时")


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
