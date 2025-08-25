# An Expert Model Based on a THIQAs Literature Knowledge Base and RAG Technology
这是我的毕业设计，聚焦于四氢异喹啉生物碱（Tetrahydroisoquinoline Alkaloids, THIQAs）领域，构建一个 THIQAs 的专属数据集和基于THIQAs文献知识库及检索增强生成（RAG）技术的专家模型。

# 目录

## 一、前言

## 二、文献检索
1. PubMed数据库
2. WOS数据库
3. Scopus数据库
4. 数据清洗

## 三、文献筛选
1. 数据准备
2. 批量推理

## 四、信息提取
1. 结构提取
2. 生源信息提取
3. 活性信息提取

## 五、化学信息分析

## 六、基于文献知识库和RAG技术的专家模型的搭建
1. 知识库构建
   - 文献摘要→片段列表→Embedding模型→向量→向量数据库
2. 回答系统
   - 用户问题→Embedding模型→向量数据库→召回→重排→大模型



**一、前言**

   四氢异喹啉类生物碱（Tetrahydroisoquinoline Alkaloids, THIQAs）在植物中广泛分布，其生物合成前体主要为酪氨酸或苯丙氨酸，并呈现出广泛的结构多样性。该类生物碱具有显著的生物活性和悠久的药用历史，其代表性药物包括镇痛药吗啡、镇咳药可待因、抗菌药黄连素、抗风湿药青藤碱，以及乙酰胆碱酯酶抑制剂加兰他敏等[1]。目前，FDA批准的含有四氢异喹啉（THIQ）骨架的临床药物包括抗帕金森药阿朴吗啡（1）、镇咳药诺斯卡品（2）、抗高血压药喹那普利（3）、驱虫药吡喹酮（4）、治疗膀胱癌药物索利那新（5）、抗癌药曲贝替丁（6）、鲁比替丁（7）、骨骼肌松弛剂筒箭毒碱（8）、多沙库铵（9）、阿曲库铵（10）和米伐库铵（11）等[3,4]。 综上可见，THIQ骨架作为一类重要的药物优势结构，已被成功应用于开发针对多种疾病（如帕金森病、癌症、高血压、感染、肌肉痉挛等）的临床有效药物，充分证明了其在药物研发和临床治疗中的潜力。
   
<img width="1101" height="958" alt="image" src="https://github.com/user-attachments/assets/8686a133-0fe5-478c-a558-913cda18aa4d" />

   
   目前主流天然产物数据库如NPASS、COCONUT 和 SuperNatural 3.0等虽各具特色，能够提供基础化学信息、生物活性及靶标等注释信息，但若研究人员希望系统获取某一类生物碱（如THIQs）的结构、生物来源、活性、作用机制及疾病靶标等多维信息，往往需在多个数据库间反复检索与整合，操作复杂且效率低下，尤其对非专业用户而言更具挑战。
   
   鉴于此，本文旨在构建一个专注于四氢异喹啉类生物碱的整合型数据集，融合 NPASS、COCONUT 与 SuperNatural 3.0 等数据库的优势资源，系统整合 THIQs 的化学信息（包括名称、结构如SMILES/InChI、分子量、分子式、理化性质如logP/TPSA/XLogP等）、生物来源信息（物种注释、分类信息）、活性信息（生物活性、药理作用、靶标、作用机制）、分类注释（基于结构特征的化学分类信息、生物合成通路）以及文献支持信息等。在此基础上，本研究将进一步以该数据集为基础，开展对THIQAs的化学空间探索与化学信息学分析，揭示其结构多样性与化学空间分布特征，为后续开展基于 THIQ 骨架的虚拟筛选、先导化合物优化、分子生成及知识图谱构建等提供坚实的数据基础。
   
   同时，为了方便检索 THIQAs 相关文献的检索和生源及活性挖掘，本项目拟搭建一个基于THIQAs文献知识库和检索增强生成（RAG）技术的专家模型，能够快速获取与 THIQAs 相关的结构、生源及活性信息，并准确响应用户提出的问题，同时所有回答均可溯源、有文献参考依据，相比于已有的大模型，它可以有效缓解幻觉问题、答案可溯源、知识库可迭代优化等特点。本研究的局限性在于，当前知识库仅基于文献摘要构建，其知识范围侧重于四氢异喹啉生物碱的结构、生源及生物活性等核心信息的检索。然而，摘要信息对生物合成途径等复杂过程的阐述深度有限。为进一步提升系统回答的深度与准确性，未来工作需要将知识库扩展至全文数据，以期对生源途径等机制进行更为细致的剖析。
   
**二、文献检索**

   我们在三个主要数据库——Web of Science、Scopus 和 PubMed 中进行了文献检索，使用 "tetrahydroisoquinoline" 及其亚类如 "benzylisoquinoline"、 "protoberberines" 等作为主要检索词检索所有类型的文章，然后收集其 DOI 和 Abstract 信息，最后整合三个数据库的文献并进行去重等数据清洗工作。

**三、文献筛选**

   文献筛选采用火山引擎的批量推理进行，通过DeepSeek-R1模型，阅读文献摘要，筛选出与四氢异喹啉生物碱相关的文献。

   1.数据准备

      import json
      ## 你的数据，自行处理成
      data = []
      ## 必须是list[dict]结构，
      huoshan_data_jsonl = [
         {
            "custom_id": f"uuid-xxxx", # 必须唯一
            "body": {
               "messages": [
                  {"role": "system", "content": "你的系统提示词"},
                  {
                     "role": "user",
                     "content": "你的文本内容",
                  },
               ],
               "temperature": 0.0,
               # 其他参数
            },
         }
         for d in data
      ]
      huoshan_data_jsonl = sum(huoshan_data_jsonl, [])

      with open("hs_data.jsonl", "w", encoding="utf-8") as f:
         for d in huoshan_data_jsonl:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
      len(huoshan_data_jsonl), huoshan_data_jsonl[0]
         
   
      
   
