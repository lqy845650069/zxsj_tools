import os

def get_resource_path(relative_path):
    """
    获取资源文件的路径 (简化版本，假设资源文件位于程序执行目录的相对路径)。

    在不打包的情况下，或者当资源文件与可执行程序位于相对位置时使用。
    此简化版本直接返回传入的相对路径，并基于程序执行目录解析。

    Args:
        relative_path (str): 资源文件相对于程序执行目录的相对路径。
                                例如: "resources/data/bosses.json" 或 "resources/images/skill_icon_1.png"

    Returns:
        str: 资源文件的绝对路径 (基于程序执行目录)。
    """
    base_path = os.path.abspath(".")  #  程序执行目录的绝对路径
    return os.path.join(base_path, relative_path)