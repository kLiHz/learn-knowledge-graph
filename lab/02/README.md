# 实验二 知识图谱认知进阶

## 实验背景

本次实验基于实验一的 Neo4j 图数据库环境以及相关图数据库操作知识, 尝试对大数据库文件 (思知 [OwnThink][ownthink] 的 [1.4 亿条数据][ownthink-v2]) 进行导入. 通过此次实验, 可以学习有关大数据文件的处理, 大数据文件导入到图数据库的相关知识和操作等. 

[ownthink]: https://www.ownthink.com/

## 实验环境

1. Neo4j 4.4.8
2. Python 3.10

## 实验原理

### OwnThink 中文知识图谱

本次实验使用的 OwnThink 公开的中文知识图谱中的数据, 是以 `(实体, 属性, 值)`, `(实体, 关系, 实体)` 混合的形式组织, 存储在 CSV 文件中.

将 [下载][ownthink-v2] 得到的文件解压缩后, 得到 `ownthink_v2.csv`:

[ownthink-v2]: http://openkg.cn/dataset/ownthink-v2

#### 查看知识图谱数据规模

(统计文章行数): 

Bash:

```console
$ wc -l ~/ownthink_v2.csv
140919781 /home/henry/ownthink_v2.csv
```

PowerShell:

法 1: 使用带 `-ReadCount` 参数的 `Get-Content`

```powershell
PS> Get-Content "D:\temp\ownthink_v2.csv" -ReadCount 1000 | Measure-Object -Line
```

法 2: 使用 `StreamReader` 流式处理

```powershell
$testFile = "D:\temp\ownthink_v2.csv"
$count = 0
$reader = New-Object IO.StreamReader $testFile
if ($reader) {
    while(-not ($reader.EndOfStream)) { [void]$reader.ReadLine(); $count++ }
    $reader.Close()
}
Write-Output $count
```

法 3: 使用 `switch` 命令

```powershell
$count = 0 
switch -File 'D:\temp\ownthink_v2.csv' { default { ++$count } }
Write-Output $count
```

<!--
    https://stackoverflow.com/questions/12084642/powershell-get-number-of-lines-of-big-large-file 
    https://stackoverflow.com/questions/54893310/powershell-count-lines-extremely-large-file
-->



#### 查看知识图谱数据内容

Bash (文件前 10 行):

```console
$ head ownthink_v2.csv
实体,属性,值
胶饴,描述,别名: 饴糖、畅糖、畅、软糖。
词条,描述,词条（拼音：cí tiáo）也叫词目，是辞书学用语，指收列的词语及其释文。
词条,标签,文化
红色食品,描述,红色食品是指食品为红色、橙红色或棕红色的食品。
红色食品,中文名,红色食品
红色食品,是否含防腐剂,否
红色食品,主要食用功效,预防感冒，缓解疲劳
红色食品,适宜人群,全部人群
红色食品,用途,增强表皮细胞再生和防止皮肤衰老
```

PowerShell (文件后 10 行):

```powershell
PS> Get-Content "D:\temp\ownthink_v2.csv" -Last 10 
贵州聚盛恒源贸易有限公司,歧义关系,贵州聚盛恒源贸易有限公司
贵州聚盛恒源贸易有限公司,歧义权重,1
北都崩解情景,歧义关系,北都崩解情景
北都崩解情景,歧义权重,1
蒋臣奏行钞法,歧义关系,蒋臣奏行钞法
蒋臣奏行钞法,歧义权重,1
宋应亨不屈,歧义关系,宋应亨不屈
宋应亨不屈,歧义权重,1
进出蛮荒五十年,歧义关系,进出蛮荒五十年
进出蛮荒五十年,歧义权重,1
```

也可以不解压文件, 在 Python 中使用 [`zipfile`][zipfile] 模块直接打开文件.

[zipfile]: https://docs.python.org/3/library/zipfile.html

```python
import zipfile
zippedFileName = 'C:/Users/Henry/Downloads/ownthink_v2.zip'
pwd = 'https://www.ownthink.com/'
with zipfile.ZipFile(zippedFileName) as archive:
    with archive.open('ownthink_v2.csv', pwd=bytes(pwd, encoding='utf-8')) as f:
        lineCount = 0
        for line in f:
            lineCount += 1
        print(lineCount)
```

### 从 CSV 批量导入 Neo4j

参照 [Neo4j `import` 工具操作指南][neo4j-import-manual], 有两种方式可以从 CSV 载入数据到 Neo4j 中: 命令行工具 `neo4j-admin import` 或者 Cypher 语句 `LOAD CSV`. 

使用 `neo4j-admin import` 可以从 CSV 中导入大规模数据到某一 *从未使用过的* 数据库中, 且在每个数据库上 **只能执行一次**; 该命令默认导入到 `neo4j` 这一数据库, 也可以用 `--database=<database>` 选项指定要导入的数据库.

[neo4j-import-manual]: https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/ "Import - Operations Manual (neo4j.com)"

而使用 `LOAD CSV` 可以导入中等大小的 CSV 文件到任一已经存在的数据库中, 可以被执行多次, 也不要求待导入的数据库非空.

由于 `neo4j-admin` 中的 `import` 命令所导入的是未在使用中的空数据库, 其导入数据的速度往往更快. 详情可参考 [Neo4j Admin import][neo4j-admin-import-manual].

[neo4j-admin-import-manual]: https://neo4j.com/docs/operations-manual/current/tutorial/neo4j-admin-import/ "Neo4j Admin import - Operations Manual"

待导入的 CSV 文件需要有以下要求:

- 字段之间默认以逗号分割开, 也可以指定其他的分隔符;
- 所有文件需要使用相同的分隔符;
- 节点和关系都可以使用多个数据源;
- 一个数据源可以由多个文件提供;
- 用于指明数据字段信息的独立标头文件 (header), 需要作为每个数据源的第一个文件中被指出;
- 标头 (header) 中没有对应信息的字段将被忽略;
- 使用 UTF-8 编码;
- 默认情况下, 导入工具将截去字串前后的空白, 如需保留, 则应将数据用引号包裹起来.

导入时不会为数据库建立索引和限制, 需要在之后手动添加.

每个数据源的 CSV 文件的头文件 (header file) 指明了数据字段 (field) 该如何被解释. 头文件和数据文件需要使用相同分隔符.

头文件以 `<name>:<field_type>` 的形式记录字段的信息. `<name>` 可以用于节点的 ID 字段和各属性字段, 其他情况下 `<name>` 将被忽略.

对于节点, CSV 文件中的每个项都应该有唯一标识该项的 `ID`, 对应的标签 (`LABLE`) 和属性则是可选的.

唯一 ID 将在创建关系时用以查找到正确的节点. 可以通过给唯一 ID 字段设置一个属性名来将其保留下来, 属性名在 `<name>:ID` 中的 `<name>` 被定义, 比如 `songID:ID`. 如果未指定这样的属性名, 则 ID 将无法在之后用于检索. 指定了属性名后, 该属性的类型只能通过 `--id-type` 命令行选项进行全局配置, 而不能通过 `<field_type>` 指定. 如果不为节点指定 ID, 则节点将无法在导入过程中被任何属性关联起来.

导入过长将会从 `LABEL` 字段读取多个标签, 多个标签默认使用 `;` 间隔开来, 或者用 `--array-delimeter` 指定使用的间隔符.

参考格式:

|`:ID`|`name`| `:LABEL` |
|:---|:---|:-------------|
|`<实体 ID>`| `<实体 'name' 属性值>` | `<实体标签>`     |

参考示例:

|`movieID:ID`|`title`|`year:int`| `:LABEL` |
|:---|:---|:---|:-------------|
| tt0133093 | "The Matrix"             | 1999 | Movie        |
| tt0234215 | "The Matrix Reloaded"    | 2003 | Movie;Sequel |
| tt0242653 | "The Matrix Revolutions" | 2003 | Movie;Sequel |

描述实体关系的 CSV 文件中的每一项, 应指明起始节点 ID 和终到节点 ID, 节点的类型 `:TYPE` 也必须指定:

| `:START_ID`  |`:END_ID`| `:TYPE` |
|:-------------|:---|:------------|
| `<起始节点的 ID>` | `<终到节点的 ID>` | `<关系的类型>`   |

### 设计格式转换方式

截取部分 OwnThink 数据库中实体相对应的内容:

```none
艺术[文化名词],中文名,艺术
艺术[文化名词],外文名,Art
艺术[文化名词],概念,指比现实有典型性的社会意识形态
艺术[文化名词],拼音,yi shu
艺术[文化名词],著名艺术家,赵佶、刘松年、赵孟頫、齐白石等
艺术[文化名词],标签,语言术语
艺术[文化名词],标签,美术
艺术[文化名词],标签,文学
艺术[文化名词],标签,文化
```

```none
天津三绝,描述,天津三绝又称天津风味食品三绝，是指“狗不理包子”、“十八街麻花”、“耳朵眼炸糕”天津三种传统美食。
天津三绝,中文名,天津三绝
天津三绝,外文名,Tianjin ruin
天津三绝,全称,天津风味食品三绝
天津三绝,所属地区,中国天津
天津三绝,属性,中华美食
天津三绝,社会影响,驰名中外
天津三绝,标签,生活
```

OwnThink 数据库的标头为 `实体,属性,值`, 但是为了将节点关联起来, 应该将实体一些属性对应的 `值` 创建为 `实体` 并为其分配 ID, 并以 `(节点)-[关系]-(节点)` 的方式存储.

观察数据库中的内容可以看到, 每行的第一列为知识库中收录的实体, 如有歧义, 则会在实体名后以 `[]` 的形式标出. 因此, 在构建知识图谱的过程中, 将为其创造唯一的实体.

知识库中每个实体对应的 `(实体, 关系, 值)` 三元组中, "关系" 对应位置往往有 "释义" "描述" 几项, 通过观察, 认为, 当 `关系` 为这几项时, 不应创造出对应的实体, 而作为实体的属性进行存储; 除此以外, 比如当 `关系` 为 "标签" "名称" "分类" 等时, 则将创造对应的实体, 并将相同名称视为同一实体.


### 编程处理大文件

由于文件过大, 将大文件整个载入内存不现实. 一种方法就是将文件视作流来处理, 比如 Python 中文件对象的 `readline()` 方法就能逐行读取文件. 也可以分块加载文件, 本质上和将文件视作流的方法类似.

## 实验过程

### 下载 OwnThink 知识库

见前文所述.

### 转换文件为 Neo4j 支持导入的格式

按照前文所说, 将 OwnThink 的文件转为存放实体和关系的 CSV. 主要流程如下:

- 从文件读入三元组: 使用 `csv.DictReader`
- 拆分成节点文件和关系文件: 一个 "实体" 节点往往对应多个三元组, 在连续的几行中出现, 读入完成即写出, 使用名称作为唯一 ID. 在内存中根据 "值" 建立一个字典 (关联容器), 为其保存一个唯一 ID, 写出关系时对 "值" 节点使用这个唯一的 ID. 每读入一个三元组都会判断: 如果是作为 "实体" 节点属性的值, 则不创建节点, 暂时存储在内存中, 等待输出; 否则直接输出.

在实际过程中, 遇到其中一行中含有 `\x00` NULL 空字节 (`_csv.Error: line contains NUL`) [^ownthink-gh-issue], 影响了 `csv.DictReader` 的读取:

```python-repl
>>> with open('D:/temp/ownthink_v2/ownthink_v2.csv', 'r') as f:
...   i = 1
...   while i < 9929228:
...     l = f.readline()
...     if i > 9929225:
...       l
...     i += 1
...
'杂剧石棺,"出土\x00时间",1978年\n'
'杂剧石棺,现存地,河南博物院\n'
```

由于文件中含有空字节的地方较少, 因此在处理的代码中加入了异常处理. 如若问题较多, 则考虑对文件进行预处理.

通常对于 `csv.Reader` 是直接使用 `for` 循环进行迭代, 但是因为异常可能发生在每次迭代, 因而不能对整个循环体进行异常处理. 
故采用 `while True` 和 `__next()__` 组合的方式:

```python
def foo(val: int) -> str:
    if val in [1, 3, 5]:
        raise ValueError()
    else:
        return f'{val}'


gen = map(foo, [1, 2, 3, 4, 5])
cnt = 0

while True:
    try:
        s = gen.__next__()
    except ValueError:
        # If encounters exceptions
        print(f'Oops! Exception at No. {cnt + 1}.')
        continue
    except StopIteration:
        # If iteration reaches the end:
        break
    finally:
        # Count in the 'finally' block:
        cnt += 1

    # Do something with s
    print('Got: ', s)

print(f'Processed {cnt - 1} objects.')
```

此外, 由于最初没有考虑周到, 导致实体和 "值" 的 ID 有冲突的现象: 比如为 "值" 节点分配的 ID "9" 和名为 "9" 的实体 (其 ID 也为 '9'). 这里采用了 Neo4j 提供的 ID 命名空间 (ID Spaces) 的方法解决冲突的问题.

之后导入时仍有错误, 通过检查 Neo4j 安装目录下的 `import.report` 得知, 文件中还包含像这样的空项, 也应该在编写代码时注意处理:

调试过程:

```none
more import.report
...
藏族 (nId)-[null]->8467 (eId) is missing data
蕉心格 (nId)-[null]->8467 (eId) is missing data
内附格 (nId)-[null]->8467 (eId) is missing data
内附格 (nId)-[null]->8467 (eId) is missing data
摘领格 (nId)-[null]->8467 (eId) is missing data
...
```

定位并确认 `entitySet.csv` 中对应 ID 的内容:

```python-repl
>>> with open('./import/entitySet.csv') as f:
...   cnt = 0
...   for line in f:
...     cnt += 1
...     if 8495 < cnt < 8505:
...       line
...
'8463,圣安德肋,Entity\n'
'8464,基督教三大流派之一,Entity\n'
'8465,腾讯QQ,Entity\n'
'8466,腾讯,Entity\n'
'8467,,Entity\n'
'8468,简体中文、繁体中文、英语、日语、韩语、法语、德语等多国语言,Entity\n'
'8469,腾讯网,Entity\n'
'8470,http://im.qq.com/,Entity\n'
'8471,信息,Entity\n'
```

在原始文件中确认:

```console
$ grep -e '^藏族,' /mnt/d/temp/ownthink_v2/ownthink_v2.csv
藏族,描述,藏族（藏文：བོད་པ་ ）是中国的56个民族之一，是青藏高原的原住民。
藏族,中文名,藏族
藏族,外文名,Tibetan/Tibet Autonomous Region
藏族,人口,750万（全世界）
藏族,人口分布,中国，尼泊尔，印度，不丹，欧洲
藏族,语言,藏语
藏族,文字,藏文
藏族,信仰宗教,藏传佛教、苯教等
藏族,历法,藏历
藏族,形成时间,吐蕃王朝时代 皓中王朝时代
藏族,,
藏族,标签,民族
藏族,标签,文化
```

可见, 在实验过程中会遇到很多问题. 建议一边编写代码, 一边生成少量的数据进行试导入, 可以发现很多问题.

考虑到大文件处理时间过长, 代码加入了一个简略的断点保存的功能 (不过可能用处不大, 实际上花费时间并不多). 实现功能的原理是捕捉 SIGINT 信号, 并通过异常处理完成存档.

由于 Neo4j 还支持直接导入压缩文件, 为了减小空间占用, 可以直接写出压缩后的 CSV 文件.
不过经过实际测试, 不管以压缩形式进行读取还是写出, 都会造成明显的效率下降.

### 导入 Neo4j 数据库

将生成的文件放入 Neo4j 安装目录的 `import` 目录下. 本实验中生成的文件为:

- `entities-20220612-105728.csv`
- `entitySet.csv`
- `relations-20220612-105728.csv`

在 Shell 中切换到 Neo4j 安装目录:

如果有必要, 还需要通过 `JAVA_HOME` 环境变量指定使用的 Java 版本.

```powershell
PS> ./bin/neo4j-admin import --database="ownthink" `
    --nodes=Entity="import/entities-20220612-105728.csv" `
    --nodes=Entity="import/entitySet.csv" `
    --relationships=Attrib="import/relations-20220612-105728.csv" `
    --multiline-fields=true `
    --skip-duplicate-nodes=true `
    --skip-bad-relationships=true `
    --ignore-empty-strings=true `
    --force
```

注意待导入的数据库必须尚未存在. 如果要强制导入可以添加 `--force` 选项. 导入过程仅仅是将数据变得可用, 导入之后还需要用户手动创建对应的数据库, 才能访问导入的数据.

> 一些技巧: Neo4j 支持多个文件组成的数据源, 也就是一个 `--nodes` 选项对应的数据源, 甚至支持正则匹配文件名, 也可以指定独立的标头文件. 掌握这些技巧可能会很有用.

还有一些可能会用到的选项:

```powershell
PS> ./bin/neo4j-admin import --database="ownthink" `
    --nodes=Entity="import/entities.csv" `
    --nodes=Entity="import/entitySet.csv" `
    --relationships=Attrib="import/relations-header.csv,import/relations.csv" `
    --multiline-fields=true `
    --skip-duplicate-nodes=true `
    --skip-bad-relationships=true `
    --ignore-empty-strings=true `
    --skip-bad-entries-logging `
    --ignore-extra-columns `
    --bad-tolerance=200000000 `
    --force
```

不过, Neo4j 社区版 (Community) 仅支持单个数据库, 如要创建数据库会提示 "Unsupported administration command: CREATE DATABASE". 因此, 需要一些技巧 [^neo4j-hack]:

1. 打开 Neo4j 安装目录下的 `NEO4J_HOME\conf\neo4j.conf` 文件;
2. 取消 `dbms.default_database=neo4j` 的注释;
3. 将 `neo4j` 改为新数据库要使用的名称 (长度在 3 ~ 63 个字符之间), 比如 `dbms.default_database=mydatabase`;
4. 保存文件;
5. 重启 Neo4j 服务器以及 Web UI;
6. 之后再打开 Neo4j 的页面, 默认的 "neo4j" 数据库和新创建的数据库都会出现, 但是不能切换; 如需切换, 需要重复第 3 步.

### 查看导入结果

由于尚未建立索引, 查询速度会很慢.

## 实验心得

可见, 在实验过程中会遇到很多问题. 这次的数据量很大, 如果等全部生成完再调试不容易发现问题 (不容易分辩是由于何种原因导致的错误, 并且由于数据量大, 每次试错的时间成本也会很高). 建议一边编写代码, 一边先生成少量的数据进行试导入.

## 参考资料

[^ownthink-gh-issue]: 另请参见 [_csv.Error: line contains NULL byte - Issue #28 - ownthink/KnowledgeGraphData](https://github.com/ownthink/KnowledgeGraphData/issues/28)

[^neo4j-hack]: 参考 [Error occurs when creating a new database under Neo4j 4.0 - Stack Overflow](https://stackoverflow.com/questions/60429947/error-occurs-when-creating-a-new-database-under-neo4j-4-0).
