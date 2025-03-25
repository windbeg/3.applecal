# 修改过程
## 20250302
为了减少提取数据的运行时间，每次运行程序需要保存本次运行程序的时间到参数文件config.json,程序仅使用从最后一天到目前天数的日历数据更新，以减少运行时间，具体方案：
1. 生成一个参数文件config.json，用于保存最近一次运行程序的日期last_run_date；
2. 每次运行程序，需要取得config.json的最近日期last_run_date，赋值给first_date，然后用当前日期更新last_run_date；如果没有config.json文件，first_date赋值当前日期的第前360天，保存参数文件config.json,保存当前日期为last_run_date；
3. 读取日历数据，获取first_date日期到当前日期的日历数据，并添加到calendar_export.csv中；同时对celendar_export.csv中可能存在重复的日历数据进行删除


## 20250307
把config.json文件改名为data.json，calendar_analysis.py继续调用data.json文件。
建立一个config.json文件，用于存储日历参数，保存如下的键值对：

# 保存日历的分类， 键是苹果日历中日历的名称，值是用于日历分析的日历分类
# 键和值可以根据需要进行修改
1. 个人：个人
2. 日历：放松
3. 工作：工作
4. 读书：读书
然后在程序中使用如下的代码读取config.json文件：
1. calendar_analysis.py中使用如下的代码读取config.json文件：



## 20250324
1. 修改index.html文件，直接使用config.json的日历键值对。

# requirements.txt文件介绍

GitHub 项目中的 requirements.txt 文件是 Python 项目中常用的依赖管理文件，它列出了项目所需的所有 Python 包及其版本。

## 作用
1. 记录项目依赖：明确列出项目需要的所有第三方库
2. 版本控制：指定每个依赖包的具体版本，确保开发环境一致性
3. 简化环境配置：新开发者可以快速搭建相同的开发环境
4. 部署辅助：在服务器上部署时，可以快速安装所有依赖
## 使用方法
### 创建 requirements.txt
你可以手动创建，或使用以下命令自动生成：

```bash
pip freeze > /Users/mac/trae/3.applecal/requirements.txt
 ```
```

### 安装依赖
使用以下命令安装文件中列出的所有依赖：

```bash
pip install -r /Users/mac/trae/3.applecal/requirements.txt
 ```
```

### 示例文件
对于你的项目，一个简单的 requirements.txt 可能如下：

```plaintext
python-dateutil>=2.8.2
 ```

这表示项目依赖 python-dateutil 库，版本需要 2.8.2 或更高。

如果你想为你的项目创建一个完整的 requirements.txt，可以先确认你使用了哪些第三方库，然后列出它们。从你的代码来看，至少需要 python-dateutil