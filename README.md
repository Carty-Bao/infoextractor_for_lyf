# README

## info_extractor.py
**功能简介**

从段落文本中提取以下信息：
从背景介绍一栏提取
1、学历（大专、本硕博）
2、是否有985/211学习经历或工作经历（毕业于985/211、或在985/211）匹配985/211列表
3、是否有工商管理学习经历（MBA/EMBA/管理学专业出身（一般包含管理二字））
4、是否有管理实践经验（曾担任其他公司管理人员）

**special requirements**

将管理层信息中的 姓名列，职位列，背景介绍列提取到新的表格中，并另存为csv文件
使用delete_nb函数将独董删除

**script**
```shell
python info_extractor.py
```

**reference**

百度智能云api：https://ai.baidu.com