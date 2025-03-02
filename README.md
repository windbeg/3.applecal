# cal_analysis
## 介绍
这是一个使用trae.ai编写用于分析cal数据的代码。

## 功能
- 统计苹果日历分类时间统计，然后用图表显示
1. 导出最近7天的日历分析；最近6周的数据分析；最近6个月数据分析

## 说明

## 目前只使用macos

## 继续修改思路
为了减少提取数据的运行时间，每次运行程序需要保存本次运行程序的时间到参数文件config.json,程序仅使用从最后一天到目前天数的日历数据更新，以减少运行时间，具体方案：
1. 生成一个参数文件config.json，用于保存最近一次运行程序的日期last_run_date；
2. 每次运行程序，需要取得config.json的最近日期last_run_date，赋值给first_date，然后用当前日期更新last_run_date；如果没有config.json文件，first_date赋值当前日期的第前360天，保存参数文件config.json,保存当前日期为last_run_date；
3. 读取日历数据，获取first_date日期到当前日期的日历数据，并添加到calendar_export.csv中；同时对celendar_export.csv中可能存在重复的日历数据进行删除

## git的保存文件
1. 