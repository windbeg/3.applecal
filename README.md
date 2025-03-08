# cal_analysis
## 介绍
这是一个使用trae.ai编写用于分析cal数据的代码。

## 功能
- 统计苹果日历分类时间统计，然后用图表显示
1. 导出最近7天的日历分析；最近6周的数据分析；最近6个月数据分析

## 说明
1. 目前只使用macos
2. config.json文件用于保存日历参数，保存如下的键值对：
    - 保存日历的分类， 键是苹果日历中日历的名称，值是用于日历分析的日历分类
    - 键和值可以根据需要进行修改
    - 个人：个人
    - 日历：放松
    - 工作：工作
    - 读书：读书
3. 如果数据出现错误，请删除date.json、calendar_export.csv、calendar_analysis.csv文件，然后重新运行程序。

4. 最后的界面如下
https://windbeg-1333132289.cos.ap-shanghai.myqcloud.com/pic/20250308203005-539.png