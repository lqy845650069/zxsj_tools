# src/core/data_manager.py
import json
import os
from src.utils.resource import get_resource_path

class DataManager:
    def __init__(self):
        self.boss_data = []
        self.boss_skill_data_map = {} #  使用字典存储 Boss 技能数据，key: boss_name, value: skills_list
        self.data_folder = os.path.join("resources", "data")
        self.boss_data_file = os.path.join(self.data_folder, "bosses.json")

    def load_boss_data(self):
        """
        从 JSON 文件加载 Boss 数据和技能数据。
        """
        try:
            with open(get_resource_path(self.boss_data_file), 'r', encoding='utf-8') as f:
                self.boss_data = json.load(f)
            print(f"成功加载 Boss 数据，共 {len(self.boss_data)} 个 Boss.")
            self._process_skill_data() #  加载 Boss 数据后，处理技能数据
        except FileNotFoundError:
            print(f"警告: Boss 数据文件未找到: {self.boss_data_file}")
            self.boss_data = []
        except json.JSONDecodeError:
            print(f"错误: Boss 数据文件 JSON 格式解析失败: {self.boss_data_file}")
            self.boss_data = []
        except Exception as e:
            print(f"加载 Boss 数据时发生未知错误: {e}")
            self.boss_data = []

    def _process_skill_data(self):
        """
        处理 Boss 数据，提取技能数据并存储到 boss_skill_data_map 中。
        """
        self.boss_skill_data_map = {} #  清空之前的技能数据
        for boss in self.boss_data:
            boss_name = boss.get('name')
            skills = boss.get('skills', []) # 获取技能列表，如果不存在则默认为空列表
            if boss_name:
                self.boss_skill_data_map[boss_name] = skills

    def get_all_bosses(self):
        """
        返回所有 Boss 数据列表 (只包含基本信息，不包含技能)。
        """
        return self.boss_data

    def get_boss_names(self):
        """
        返回所有 Boss 名称的列表。
        """
        return [boss.get('name') for boss in self.boss_data if boss.get('name')]

    def get_boss_skill_data(self, boss_name):
        """
        根据 Boss 名称获取技能数据。
        """
        return self.boss_skill_data_map.get(boss_name, []) #  如果找不到 Boss 的技能数据，返回空列表
    
    def get_skill_data_by_name(self, boss_name, skill_name):
        """
        根据 Boss 名称和技能名称查找并返回技能数据字典。
        """
        skill_data_list = self.get_boss_skill_data(boss_name)
        if skill_data_list:
            for skill_data in skill_data_list:
                if skill_data.get('name') == skill_name:
                    return skill_data # 找到匹配的技能数据，返回字典
        return None # 如果 Boss 或技能未找到，返回 None