# 实验三 实体抽取关键技术 - 中文分词

实体抽取是完成知识图谱必不可少的核心部分，其涉及到的关键技术为中文分词。

计划通过本次实验掌握目前最流行的 8 种中文分词方法，并学会利用这 8 种方法开展相关的
分词实验和实体抽取实验，同时利用准确率, 召回率, F1, 算法运行时间等评价指标对 8 种
算法进行精度和时间等指标的对比，并得出相关结论，为后期相关实体抽取进行技术准备。

## 实验原理

### 中文分词的概念

中文分词是中文文本处理的一个基础步骤，也是中文人机自然语言交互的基础模块。不同于英文的是，中文句子中没有词的界限，因此在进行中文自然语言处理时，通常需要先进行分词，分词效果将直接影响词性、句法树等模块的效果。在人机自然语言交互中，成熟的中文分词算法能够达到更好的自然语言处理效果，帮助计算机理解复杂的中文语言。

根据实现原理和特点，中文分词主要分为基于词典的分词算法和基于统计的机器学习算法.

**基于词典的分词算法** 也称字符串匹配分词算法, 本质上就是字符串匹配。将待匹配的字符串基于一定的算法策略，和一个足够大的词典进行字符串匹配，如果匹配命中，则说明匹配成功，识别了该词。根据不同的匹配策略，又分为正向最大匹配法，逆向最大匹配法，双向匹配分词，全切分路径选择等。

最大匹配法（Maximum Matching）主要分为三种：

- 正向最大匹配算法（Forward MM, FMM）：从左到右对语句进行匹配，匹配的词越长越好。这种方式切分会有歧义问题出现。
- 逆向最大匹配算法（Backward MM, BMM）：从右到左对语句进行匹配，同样也是匹配的词越长越好。这种方式同样也会有歧义问题。
- 双向最大匹配算法（Bi-directional MM）：则同时采用正向最大匹配和逆向最大匹配，选择二者分词结果中词数较少者。但这种方式同样会产生歧义问题。由此可见，词数少也不一定划分就正确。

全切分路径选择，将所有可能的切分结果全部列出来，从中选择最佳的切分路径。分为两种选择方法：

- n 最短路径方法。将所有的切分结果组成有向无环图，切词结果作为节点，词和词之间的边赋予权重，找到权重和最小的路径即为最终结果。比如可以通过词频作为权重，找到一条总词频最大的路径即可认为是最佳路径。
- n 元语法模型。同样采用 n 最短路径，只不过路径构成时会考虑词的上下文关系。一元表示考虑词的前后一个词，二元则表示考虑词的前后两个词。然后根据语料库的统计结果，找到概率最大的路径。

基于词典的分词算法是应用最广泛, 分词速度最快的。很长一段时间内研究者都在对基于字符串匹配方法进行优化，比如最大长度设定, 字符串存储和查找方式, 以及对于词表的组织结构，比如采用 Trie 索引树, 哈希索引等。

**基于统计的机器学习算法** 中, 常用的是算法是 HMM, CRF, SVM, 深度学习等算法，比如 stanford、Hanlp 分词工具是基于 CRF 算法。以 CRF 为例，基本思路是对汉字进行标注训练，不仅考虑了词语出现的频率，还考虑上下文，具备较好的学习能力，因此其对歧义词和未登录词的识别都具有良好的效果。

Nianwen Xue 在其论文 *Combining Classifiers for Chinese Word Segmentation* 中首次提出对每个字符进行标注，通过机器学习算法训练分类器进行分词，在论文 *Chinese word segmentation as character tagging* 中较为详细地阐述了基于字标注的分词法。

常见的分词器都是使用 **机器学习算法和词典相结合**，一方面能够提高分词准确率，另一方面能够改善领域适应性。

随着深度学习的兴起，也出现了基于神经网络的分词器，例如有人员尝试使用双向 LSTM + CRF 实现分词器，其本质上是序列标注，所以有通用性，命名实体识别等都可以使用该模型，据报道其分词器字符准确率可高达97.5%。算法框架的思路与论文 *Neural Architectures for Named Entity Recognition* 类似，利用该框架可以实现中文分词.

目前中文分词难点主要有三个：

1. 分词标准：以人物名为例, 在哈工大的标准中, 姓和名是分开的，但在 Hanlp 中是合在一起的。一般而言, 需要根据不同的需求制定不同的分词标准。
2. 歧义：对同一个待切分字符串存在多个分词结果. 歧义又分为组合型歧义, 交集型歧义和真歧义三种类型。
3. 新词：也称未被词典收录的词，该问题的解决依赖于人们对分词技术和汉语语言结构的进一步认识.

### 分词工具

#### 结巴分词 jieba

- 基于前缀词典实现高效的词图扫描，生成句子中汉字所有可能成词情况所构成的有向无环图 (DAG)；
- 采用了动态规划查找最大概率路径, 找出基于词频的最大切分组合；
- 对于未登录词，采用了基于汉字成词能力的 HMM 模型，使用了 Viterbi 算法。支持三种分词模式:


[结巴分词 jieba](https://github.com/fxsjy/jieba) 工具支持三种分词模式:

1. 精确分词，试图将句子最精确的切开，适合文本分析
2. 全模式，把句子中所有的可以成词的词语都扫描出来, 速度非常快，但是不能解决歧义
3. 搜索引擎模式，在精确模式基础上，对长词进行再次切分，提高recall，适合于搜索引擎。

```
py -m pip install jieba
```

#### HanLP

[HanLP](https://github.com/hankcs/HanLP/) 是面向生产环境的多语种自然语言处理工具包，基于 PyTorch 和 TensorFlow 2.x 双引擎，目标是普及落地最前沿的NLP技术。HanLP具备功能完善、精度准确、性能高效、语料时新、架构清晰、可自定义的特点。

一系列模型与算法组成的 NLP 工具包，由大快搜索主导并完全开源，目标是普及自然语言处理在生产环境中的应用。HanLP具备功能完善、性能高效、架构清晰、语料时新、可自定义的特点。

```
py -m pip install hanlp
```

[HanLP 分词功能使用教程](https://hanlp.hankcs.com/docs/api/hanlp/pretrained/tok.html).

#### SnowNLP

[SnowNLP](https://github.com/isnowfy/snownlp) 是一个可以方便的处理中文文本内容的 Python 类库，是作者受到了 [TextBlob](https://github.com/sloria/TextBlob) 的启发而写的. 和 TextBlob 不同的是，这里没有用 [NLTK](https://www.nltk.org/), 所有的算法都是自己实现的，并且自带了一些训练好的字典。

```
py -m pip install snownlp
```

#### FoolNLTK

[FoolNLTK](https://github.com/rockyzhengwu/FoolNLTK) 的介绍:

- 可能不是最快的开源中文分词，但很可能是最准的开源中文分词
- 基于 [BiLSTM 模型](http://www.aclweb.org/anthology/N16-1030) 训练而成
- 包含分词，词性标注，实体识别,　都有比较高的准确率
- 用户自定义词典
- 可训练自己的模型
- 批量处理

```
py -m pip install foolnltk
```

#### HIT LTP

LPT (Language Technology Platform) 提供了一系列中文自然语言处理工具，用户可以使用这些工具对于中文文本进行分词、词性标注、句法分析等等工作。其最新版本为 [LTP 4](https://github.com/HIT-SCIR/ltp).

安装和使用方法参考: [docs/quickstart.rst - HIT-SCIR/ltp - GitHub](https://github.com/HIT-SCIR/ltp/blob/master/docs/quickstart.rst)

```
py -m -pip install ltp
```

```python
from ltp import LTP
ltp = LTP()  # 默认加载 Small 模型
segment, _ = ltp.seg(["他叫汤姆去拿外衣。"])
# [['他', '叫', '汤姆', '去', '拿', '外衣', '。']]
```

#### Jiagu

[Jiagu](https://github.com/ownthink/Jiagu) 基于 BiLSTM 模型，使用大规模语料训练而成, 提供有中文分词, 词性标注, 命名实体识别, 知识图谱关系抽取, 关键词提取, 文本摘要, 新词发现, 情感分析, 文本聚类等常用自然语言处理功能。

```
py -m pip install jiagu
```

#### THULAC

[THULAC](https://github.com/thunlp/THULAC) (THU Lexical Analyzer for Chinese) 由清华大学自然语言处理与社会人文计算实验室研制推出的一套中文词法分析工具包，具有中文分词和词性标注功能。T

```python
py -m pip install thulac
```


#### NLPIR-ICTCLAS 汉语分词系统

[NLPIR-ICTCLAS 汉语分词系统](http://ictclas.nlpir.org/) 主要功能包括中文分词; 英文分词; 词性标注; 命名实体识别; 新词识别; 关键词提取; 支持用户专业词典与微博分析。NLPIR系统支持多种编码、多种操作系统、多种开发语言与平台。

#### 其他

[Ansj 中文分词](https://github.com/NLPchina/ansj_seg): 一个基于 n-Gram + CRF + HMM 的中文分词的 Java 实现。目前实现了中文分词, 中文姓名识别, 用户自定义词典, 关键字提取, 自动摘要, 关键字标记等功能。

[斯坦福分词器](https://nlp.stanford.edu/software/segmenter.shtml): 作为众多斯坦福自然语言处理中的一个包，目前最新版本3.7.0， 由 Java 实现的 CRF 算法。可以直接使用训练好的模型，也提供训练模型接口。

[KCWS 中文分词器](https://github.com/koth/kcws): 一个基于深度学习的字嵌入 + Bi-LSTM + CRF 分词器.

[ZPar](https://github.com/frcchang/zpar/releases) 分词器: 新加坡科技设计大学开发的中文分词器，包括分词, 词性标注和 Parser，支持多语言.


### 实验数据

实验的测试集包括：msr、pku、other三个数据，具体内容见test_msr.txt、test_pku.txt、test_other.txt三个文本文档。

msr.txt、pku.txt、other.txt为标准分词参考答案，学生需要结合自己的分词结果和已有的参考答案进行对比，分别计算的相应算法在各个数据集上的准确率、召回率、F1值、运行时间等指标。





### 准确率、精确率、召回率及 F 值

机器学习中的分类评估包含有以下这么几个概念。

**准确率** (Accuracy) ，即正确分类的数量占总的数量的比值，是一个用来衡量分类器预测结果与真实结果差异的一个指标，越接近于 1 说明分类结果越准确。

二分类的结果有以下几种可能性：

- True Positive (TP): 表示将正样本预测为正样本，即预测正确;
- False Positive (FP): 表示将负样本预测为正样本，即预测错误;
- False Negative (FN): 表示将正样本预测为负样本，即预测错误;
- True Negative (TN): 表示将负样本预测为负样本，即预测正确.



**精确率** (Precision) 计算的是预测对的正样本在整个预测为正样本中的比重，而 **召回率** (Recall) 计算的是预测对的正样本在整个真实正样本中的比重。因此，一般来说，召回率越高，意味着模型找寻正样本的能力越强。

准确率、精确率、召回率的计算公式如下：

$$
\begin{align}
\text{Accuracy} = & \frac{TP+TN}{TP+FP+FN+TN} \\
\text{Precision} = & \frac{TP}{TP+FP} \\
\text{Recall} = & \frac{TP}{TP+FN} \\
\end{align}
$$
值得注意的是，在实际任务中，并不明确哪一类是正样本或哪一类是负样本，所以对于每个类别，都可以计算其各项指标。

实际评估一个系统时，应同时考虑 P 和 R，但同时要比较两个数值，很难做到一目了然。所以常采用综合两个值进行评价的办法，综合指标 **F 值** 就是其中一种。计算公式如下:

$$
\text{F-score} = (1+\beta^2)\frac{P \times R}{\beta^2 \times P + R}
$$

其中，$\beta$ 决定对 *P* 侧重还是对 *R* 侧重，通常设定为 1、2 或 $\frac 1 2$. $\beta$ 取值为 1，即对二者一样重视，这时的 F-score 称为 $F_1$ 值。

机器学习中二分类的评估标准，无法直接应用于分词。

在对汉语分词性能进行评估时，采用了常用的３个评测指标：准确率（P）、召回率（R）、综合指标 F 值（F）。准确率表示在切分的全部词语中，正确的所占的比值。召回率指在所有切分词语中（包括切分的和不应该忽略的），正确切分的词语所占的比值。准确率描述系统切分的词语中，正确的占多少。召回率表示应该得到的词语中，系统正确切分出了多少。计算公式如下：

$$
P = \frac{\text{准确切分的词语数}}{\text{切分出的所有词语数}}
$$

$$
R = \frac{\text{准确切分的词语数}}{\text{应该切分的词语数}}
$$

若一字符串的分词结果为一系列单词，设每个单词按照其在文中的起止位置可记作区间 $[i,j] (0\leq i \leq j \leq n)$, 那么标准答案对应的所有区间就可以构成一集合 A，作为正类，其他的区间则作为负类; 同理，根据分词结果，可以得到集合 B。


$$
TP \cup FN = A
$$

$$
TP \cup FP = B
$$

$$
A \cap B = TP
$$

则对于分词结果，P、R 的计算公式：

$$
\text{Precision} = \frac{\vert A\cap B\vert}{\vert B \vert}
$$

$$
\text{Recall} = \frac{\vert A\cap B\vert}{\vert A \vert}
$$

## 实验过程

对实验数据进行中文分词

学生参照各个分词算法的相关示例, 编写本次实验的 Python 代码, 对 `test_msr.txt`, `test_pku.txt`, `test_other.txt` 三个文本文档的内容进行分词, 并分别计算各个算法在三个数据集上的准确率, 召回率, F1值, 运行时间等评价指标.

实验过程和实验结果需要截图. 学生还需要利用表格对各个算法的实验结果进行对比展示并且做出相关分析.

各个算法的准确率, 召回率, F1值, 运行时间等评价指标部分可以参照下表 1. 

> 下表 1 为 8 种分词算法在 msr 数据集上的分词结果, 算法在其他 2 个数据集上的结果请同学们自己添加。

表1  8 种分词算法在 msr 数据集上的分词结果        

| 分词方法 | 准确率 | 召回率 | F1 | 运行时间 (秒) |
| :---- | :---: | :---: | :---: | :---: |
| jieba |       |       |       |       |
| pyhanlp |  | | | |
| snownlp |  | | | |
| foolnltk |  | | | |
| jiagu |  | | | |
| pyltp |  | | | |
| thulac |  | | | |
| pynlpir |  | | | |

 

参考资源

1. 常用分词工具使用教程

https://github.com/ownthink/evaluation/blob/master/Tutorial.md

2. 中文分词性能对比

https://github.com/ownthink/evaluation


## 参考资料

[中文分词算法简介 - Jiaying Lu 卢嘉颖 的个人博客](https://lujiaying.github.io/posts/2018/01/Chinese-word-segmentation/) 以及 [知乎上的备份](https://zhuanlan.zhihu.com/p/33261835)

[中文分词常见方法 - mandagod 的博客 - CSDN 博客](https://blog.csdn.net/mandagod/article/details/97108355)
