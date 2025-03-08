# src/utils/trigger_check_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import queue, os
from src.utils.image_utils import detect_image_on_screen # 假设 detect_image_on_screen 函数在 image_utils.py 中

class TriggerCheckThread(QThread):
    """
    通用的触发条件检查工作线程。
    负责在后台线程执行各种触发条件检查任务，并将结果通过信号发送回主线程。
    使用队列接收触发检查任务。
    """
    trigger_check_finished = pyqtSignal(str, bool)  # 定义信号，参数1: 技能名称 (str)，参数2: 触发结果 (bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_queue = queue.Queue(20) # 创建任务队列
        self.is_running = True

    def run(self):
        """
        线程运行函数，不断从任务队列中获取任务并执行。
        """
        while self.is_running:
            task = self.task_queue.get() # 从队列中取出任务，如果队列为空，线程会等待直到有任务

            if not self.is_running:
                print("在 get() 后检测到线程停止信号，准备退出线程循环")
                break # 立即退出 while 循环

            if task:
                skill_data = task #  任务就是技能数据 (字典)
                skill_name = skill_data.get('name')
                trigger_condition = skill_data.get('trigger_condition')
                param = skill_data.get('param')
                recognition_result = False # 默认识别结果为 False

                try:
                    print(f"触发检查线程开始处理技能: {skill_name}, 触发条件: {trigger_condition}")
                    if trigger_condition == "unconditional":
                        recognition_result = True # 无条件触发，直接设置为 True
                        print(f"技能 '{skill_name}' (无条件触发) 检查完成，结果: {recognition_result}")

                    elif trigger_condition == "condition_image":
                        if param:
                            image_path = os.path.join('resources', 'images', param) 
                            print(f"技能 '{skill_name}' (图像识别触发) 开始图像识别，目标图片: {image_path}")
                            recognition_result = detect_image_on_screen(image_path) # 执行图像识别
                            print(f"技能 '{skill_name}' (图像识别触发) 图像识别完成，结果: {recognition_result}, 图片: {image_path}")
                        else:
                            print(f"警告: 技能 '{skill_name}' (图像识别触发) 配置不完整，缺少图片路径")


                    if self.is_running: # 检查线程是否仍然运行
                        self.trigger_check_finished.emit(skill_name, recognition_result) # 发射信号，传递技能名称和触发结果

                except Exception as e:
                    print(f"触发检查线程处理技能 '{skill_name}' 时发生错误: {e}")
                    if self.is_running:
                        self.trigger_check_finished.emit(skill_name, False) # 发生错误时，也发送触发失败的信号
                finally:
                    print(f"触发检查线程完成技能 '{skill_name}' 的处理")
            else:
                if not self.is_running: # 队列为空时，再次检查 self.is_running，如果为 False，则退出循环 <--- 关键检查
                    print("队列为空时检测到线程停止信号，准备退出线程循环")
                    break # 退出 while 循环
                self.msleep(50) #  队列为空时，休眠一段时间，避免 CPU 占用过高

        print("触发检查线程已退出")


    def enqueue_task(self, task_data):
        """
        将触发检查任务放入队列。
        """
        self.task_queue.put(task_data)


    def stop_worker(self):
        """
        停止工作线程。
        """
        print(f"收到停止线程请求，当前队列大小：{self.task_queue.qsize()}")
        self.is_running = False
        self.quit()
        if not self.wait(5000): # 等待线程结束，最多 5 秒
            print(f"警告: 线程 '{self.__class__.__name__}' 无法在超时时间内结束，可能需要强制终止")
            self.terminate() #  在极端情况下可以考虑 terminate()，但不推荐，可能导致资源泄漏或数据损坏
        else:
            print(f"线程 '{self.__class__.__name__}' 已正常结束")