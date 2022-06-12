# 实验二 知识图谱认知进阶

## 实验背景

本次实验基于实验一的 Neo4j 图数据库环境以及相关图数据库操作知识, 尝试对大数据库文件 (思知 [OwnThink][ownthink] 的 [1.4 亿条数据][ownthink-v2]) 进行导入. 通过此次实验, 可以学习有关大数据文件的处理, 大数据文件导入到图数据库的相关知识和操作等. 

[ownthink]: https://www.ownthink.com/

## 实验环境

1. Neo4j 4.4.3
2. Python

## 实验原理

### OwnThink 中文知识图谱

本次实验使用的 OwnThink 公开的中文知识图谱中的数据, 是以 `(实体, 属性, 值)`, `(实体, 关系, 实体)` 混合的形式组织, 存储在 CSV 文件中.

将 [下载][ownthink-v2] 得到的文件解压缩后, 得到 `ownthink_v2.csv`:

[ownthink-v2]: http://openkg.cn/dataset/ownthink-v2


查看知识图谱数据规模: 

Bash:

```bash
$ wc -l ~/ownthink_v2.csv
140919781 /home/henry/ownthink_v2.csv
```

PowerShell:

```powershell
PS> Get-Content "D:\temp\ownthink_v2.csv" -ReadCount 1000 | Measure-Object -Line
```

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

```powershell
$count = 0 
switch -File 'D:\temp\ownthink_v2.csv' { default { ++$count } }
Write-Output $count
```

<!--
    https://stackoverflow.com/questions/12084642/powershell-get-number-of-lines-of-big-large-file 
    https://stackoverflow.com/questions/54893310/powershell-count-lines-extremely-large-file
-->



查看知识图谱数据内容:

Bash (文件前 10 行):

```bash
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

### 从 CSV 批量导入 Neo4j

参照 [Neo4j `import` 工具操作指南][neo4j-import-manual], 有两种方式可以从 CSV 载入数据到 Neo4j 中: 命令行工具 `neo4j-admin import` 或者 Cypher 语句 `LOAD CSV`. 

使用 `neo4j-admin import` 可以从 CSV 中导入大规模数据到某一 *从未使用过的* 数据库中, 且在每个数据库上 **只能执行一次**; 该命令默认导入到 `neo4j` 这一数据库, 也可以用 `--database=<database>` 选项指定要导入的数据库.

[neo4j-import-manual]: https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/ "Import - Operations Manual (neo4j.com)"

而使用 `LOAD CSV` 可以导入中等大小的 CSV 文件到任一已经存在的数据库中, 可以被执行多次, 也不要求待导入的数据库非空.

由于 `neo4j-admin` 中的 `import` 命令所导入的是未在使用中的空数据库, 其导入数据的速度往往更快.

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

|**`:ID`**|`name`|**`:LABEL`**|
|:-|:-|:-|
|`<实体 ID>`| `<实体 'name' 属性值>` | `<实体标签>` |

参考示例:

|**`movieID:ID`**|`title`|`year:int`|**`:LABEL`**|
|:-|:-|:-|:-|
| tt0133093 | "The Matrix"             | 1999 | Movie        |
| tt0234215 | "The Matrix Reloaded"    | 2003 | Movie;Sequel |
| tt0242653 | "The Matrix Revolutions" | 2003 | Movie;Sequel |

描述实体关系的 CSV 文件中的每一项, 应指明起始节点 ID 和终到节点 ID:

|**`:START_ID`**|**`:END_ID`**|**`:TYPE`**|
|:-:|:-:|:-:|
|`<起始节点的 ID>`| `<终到节点的 ID>` | `<关系的类型>` |

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


