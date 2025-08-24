# A-RAG-System-for-Exploring-the-Biosynthesis-and-Biological-Activities-of-THIQs
这是我的毕业设计：四氢异喹啉生物碱化学空间的探索及基于RAG的知识检索平台。包括四氢异喹啉生物碱化学空间的探索及基于RAG的知识检索平台的搭建。目的是构建一个四氢异喹啉生物碱的专属数据集和用于相关文献的检索生成和生源及活性挖掘的专家模型。

# 目录

## 一、文献检索
1. PubMed数据库

检索词：关键词：tetrahydroisoquinoline (THIQ)；benzylisoquinoline (BIAs)；phenethylisoquinoline (PEIAs)；ipecac (IAs)；Amaryllidaceae (AmAs) alkaloids；1-benzylisoquinolines（1-BIAs）；bisbenzylisoquinolines（bisBIAs）；morphinans；aporphines；protoberberines (BBRs）；phthalideisoquinolines (PQs）；benzophenanthridines (BZPs）；protopines；pavines


2. WOS数据库
3. Scopus数据库
4. 数据清洗

## 二、文献筛选
1. 数据准备
2. 批量推理

## 三、信息提取
1. 结构提取
2. 生源信息提取
3. 活性信息提取

## 四、化学信息分析

## 五、RAG检索系统
1. 知识库构建
   - 文献摘要→片段列表→Embedding模型→向量→向量数据库
2. 回答系统
   - 用户问题→Embedding模型→向量数据库→召回→重排→大模型
