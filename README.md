# ComfyUI-AutoData-for-lora

**中文名称：** [自动数据] (其实应该叫自动数据集) 

我手里有两个不知来源的lora，以及一个加起来就能得到奇妙画风的tagger，那我能不能把他们全部加起来，变成一个lora呢？————于是就有了这个工作流。

这是一个自定义节点集合（只有三个节点，6.1又加了些节点 是关于词典操作的节点），本仓库的核心功能是提供一个**通过 Excel 表格驱动的 For 循环工作流**，用于批量生成图片作为 Lora 训练集，并自动生成对应的原生 Tagger 的txt文本文件用于打标。（后者功能有分类，且可以禁用，单纯roll图也没有问题）除此之外，你可以用固定的提示词来批量测试lora。
对了，它最大的一个功能就是断点。允许接上先前暂停执行的部分（因为是用excel存储的数据）。

新增加功能（工作流）。把图像分类，读取元数据分出带有工作流的节点，带有基本tagger的节点，没有元数据的节点，把图像移动到目标位置，并建立硬链接（或者符号链接）。你需要输入原文件位置，目标文件位置,如果没有这个文件夹的话它会自己创建一个。（它很安全，没有对图像进行任何危险操作）不过规则集可能不准，遇到不准的情况记得发到Issues。

未来计划：

上传到ComfyUI Manager 未完成

从QQ图片（或者其它地方来的图片）中批量提取元数据并存储到词典。（将采样器，调度器，正负面提示词，随机数？,图片本身记录到excel） 未完成（明天）。

完成了对图像分类（硬连接和符号连接）的工作流，下一步是对分类图像的进行数据提取操作。(转换为png 存储元数据* 元数据使用*)

从图片得到词典（按顺序不重复写入到txt）完成

从词典得到excel(按顺序读取txt行) 完成 

## 快速开始(AutoData-for-lora工作流)（不知道该做什么的话，脑子不够用的话，太长不看的话）:

![更新_00001_](https://github.com/user-attachments/assets/dc2b5e3e-c2f7-477d-83f8-20b68ebae665)
踩踩你的
*(ningen mame:1.1), (ninjin nouka:1.1), (quasarcake:1.1), (ciloranko:1.15),konya_karasue,z3zz4,
*1girl, no shoes, nahida (genshin impact), feet, pantyhose, white pantyhose, green eyes, solo, pointy ears, white hair, soles, side ponytail, long hair, toes, open mouth, looking at viewer, foot focus, hair ornament, dress, symbol-shaped pupils, sitting, legs, bangs, cross-shaped pupils, blush, hair between eyes, bare shoulders, multicolored hair, sleeveless, foreshortening, white dress, see-through, thighs, sleeveless dress, sweat, panties under pantyhose, underwear, gradient hair, :o, thighband pantyhose, green hair, blurry, wet, fang, full body, ass, knees up, leaf hair ornament

0.安装节点（不会安装的在往下滑一点点，你应该能看懂怎么安装）

1.将上方的图片拖入comfyui，就是图片代表的工作流（exceldate）可能有些旧（新的在目录workflows下，我非常建议使用最新的工作流）

2.将excel 创建好

3.填入excel表格的文件位置

4.resources文件夹中的词典放在\custom_nodes\comfyui-easy-use\wildcards中。

5.点击执行

**运行的时候务必确保excel没有被打开，不然写入不了excel**

---

<details>
<summary> ## 安装 </summary><br/>

1. **打开 ComfyUI 目录：** 导航到你的 ComfyUI 安装目录。

2. **进入 `custom_nodes` 文件夹。进入cmd。

3. **克隆或下载本仓库：**

   * **方法一：使用 Git (推荐)**
     打开命令行或终端，进入 `custom_nodes` 文件夹，然后执行以下命令克隆本仓库：

     ```bash
     git clone [https://github.com/Camellia895/ComfyUI-AutoData-for-lora.git](https://github.com/Camellia895/ComfyUI-AutoData-for-lora.git)
     ```

   * **方法二：手动下载**
     点击 GitHub 页面上的 "Code" 按钮，然后选择 "Download ZIP"。解压下载的 ZIP 文件，将其中的文件夹（例如 `ComfyUI-AutoData-for-lora-main`）重命名为 `ComfyUI-AutoData-for-lora`，并将其移动到 `custom_nodes` 文件夹中。

4. **重启 ComfyUI：** 关闭并重新启动 ComfyUI，新的节点应该出现在你的节点列表中。
   
</details>

---

## 节点介绍

* **按序号自动加载标记图像:** 根据多种条件（修改时间、文件名、文件后缀、包含/排除标识）按顺序输出特定文件路径，适用于需要按顺序处理文件（如名称顺序）或自动筛选 Lora 训练素材的场景。
* **自动清理1x1png :** 自动扫描并删除指定文件夹中所有尺寸为 1x1 像素的 PNG 图片。这些图片是工作流不可避免而产生的占位符，通过清理可保持数据目录整洁。默认模式为试运行也就是dry_run,如果试运行成功在把试运行关掉。具体可以看控制台状况。（这个节点可以单独拖动到文件夹中作为批处理脚本使用。）
* **4转一空信号传递:** 为 ComfyUI 中的 For 循环提供简洁的引导机制，减少连线复杂性，使得基于 Excel 数据或列表的批量生成工作流更易于构建。（不论输入什么都会输出字符串格式的0，没有米奇妙妙功能）
* **一转4空信号传递:**同上
* **文件迁移并创建链接**：在目标位置创建图像的硬连接，省下100%的空间。
* **元数据规则检测器 V2**：检测元数据输出检测值
* （额外的，但不是节点）当中有个自动读取节点的![image](https://github.com/user-attachments/assets/aa8dda99-74c5-4bd4-936d-4c0f32ee3623)文件，**不用注册也能读取节点**。利好节点开发。
* （额外的，但不是节点）词典我放在resources文件夹中，请把词典移动到easy——use节点的的wildcards下。比如我的，就放在G:\ComfyUI_windows_portable\ComfyUI\custom_nodes\comfyui-easy-use\wildcards下。



## 节点详情

### 1. 按序号自动加载标记图像

这个节点旨在从指定目录中按特定规则选择文件，并每次输出一个文件，适用于需要按顺序处理文件（如图像序列）的场景。在 Lora 数据生成工作流中，可用于按顺序读取或处理生成的图片。

以图中的例子来讲解。我需要读取文件夹中带有记号的图片名（图中显示部分的工作流是用于用图像名从excel中得到txt）

![image](https://github.com/user-attachments/assets/6495c265-030b-43d2-963e-4d1178c959fa)


图中，我用 **按序号自动加载标记图像** 输入了文件位置（folder_path），和搜索标识符（search_marker 它可以不填）输出了符合特征的文件数量（int）。然后提供给for循环作为循环读取的数量。通过索引然后提供给同同样的节点，这时输出文件名和图像（还有其他输出可用于指示状态。不是需要的），同排除的标识符可以选择是否移除。

你可以配合我的另一个库里的软件食用https://github.com/Camellia895/Auto-Date-Marking-tools。它用于给图像名添加标识符。

(索引可能是翻译问题，但它的输出是int 初始输出为0，循环一次就加1)

---

### 2. 自动清理1x1png (`clean_1x1_png`)

自动扫描并删除指定文件夹中所有尺寸为 1x1 像素的 PNG 图片。这些图片是工作流不可避免（目前找到的最优解）而产生的占位符，通过清理可保持数据目录整洁。默认模式为试运行也就是dry_run,如果试运行成功在把试运行关掉。具体可以看控制台状况。或者通过输出看到。（这个节点可以单独拖动到文件夹中作为批处理脚本使用。）

![image](https://github.com/user-attachments/assets/c04be277-eb7c-4a4f-90df-88137d771c5f)


---

### 3. 4转一空信号传递: 

旨在为 ComfyUI 中的 For 循环提供简洁的引导机制，减少连线复杂性，使得基于 Excel 数据或列表的批量生成工作流更易于构建。（不论输入什么都会输出字符串格式的0，没有米奇妙妙功能）

如图，应该不需要解释，只是一个让for循环不那么乱的工具，

* ![image](https://github.com/user-attachments/assets/3a4229cf-fe4d-4884-bdb0-4485139b3181)

---

## 讲解部分 
## 为数据集服务的工作流 (AutoData-for-lora Workflow) 当然也可以用于单纯的roll图 
本仓库的核心价值在于提供一个**为数据集服务的 ComfyUI 工作流**，该工作流演示了如何结合 Excel 表格数据和上述节点，自动化生成 Lora 训练图片并自动生成对应的原生 Tagger 文本文件（不需要的话可以关掉）。（下方有个功能是通过图片读取tagger，需要的话可以打开）
输入excel位置。我只是将文本框一分为三了，你可以用一个文本框替代，这没有问题。**对了，记得在目标位置创建一个excel文件**
![image](https://github.com/user-attachments/assets/7c3fd999-2155-4c91-b63e-810e2ad1cae5)
这是你的控制台，可以控制需要读取（或写入）的excel位置，一个tagger需要生成几张图片。
写错了也没关系，重复运行也没关系，这不会导致重复图片产生（也不会花费gpu去重复生成图片），只会输出1x1的png图片，而刚刚的**自动清理1x1png**则是清理这些占位文件的。
![image](https://github.com/user-attachments/assets/3f610217-ac54-4089-9bfb-22a64346be08)
tagger来自词典或者excel，如果excel中有了的话，就用excel的，没有的话就会自动用词典填一个。
![image](https://github.com/user-attachments/assets/dcbbbe3b-06f2-4226-bd10-6d16a02cbb9e)
保存图像和写入表格标记
![image](https://github.com/user-attachments/assets/99eabd9b-d530-4b1d-9964-85f1b31bf339)
下方是简易的工作流的部分，你可以看到，我只给它输入了tagger，然后输出了图片。 你可以把你工作流整合进来，输入tagger，输出特定名称的图片。
![image](https://github.com/user-attachments/assets/009f4adc-7041-4f09-ac62-f204c59e6822)
用图像从excel中获得tagger。你可以配合我的另一个库里的软件食用https://github.com/Camellia895/Auto-Date-Marking-tools，用于给图像名添加标识符。
![image](https://github.com/user-attachments/assets/c7c2067c-7051-45d4-91e6-302431e20cf7)
然后你会的得到一个类似这样的excel表格（我做了中断，如果你点击继续运行，它就会从缺失位置继续生成图片）
![image](https://github.com/user-attachments/assets/d5ae9a1e-84d3-4b03-b9bf-0f43f01654d7)

## 新
让tagger写入到词典中，不重复，并去掉重复的逗号，去掉非法的换行符号。你可以右键点击播放声音节点，在菜单中选择执行节点。这样就就能只执行框中的节点了。
![image](https://github.com/user-attachments/assets/22625a95-8c5f-45db-8183-5014f0082225)
按顺序读取词典行，然后把词典写入的excel中。你可以右键点击播放声音节点，在菜单中选择执行节点。这样就就能只执行框中的节点了。
![image](https://github.com/user-attachments/assets/034d85e4-846d-4dfc-9939-b1fcb7d7d1e1)
两者直接以切换节点连接。选择2的时候不执行上方的节点。
![image](https://github.com/user-attachments/assets/31a15adc-ae56-4870-89b6-ea920a916f65)
##新
图像分练工作流，读取图像，并获取元数据，使用元数据检测节点判断是什么图像。
并迁移在目标位置创建连接。（符号连接和硬连接）具体可以看我在工作流中的注释。
![image](https://github.com/user-attachments/assets/ac94c1f5-ae99-4db5-b2d2-d8334077fbcd)
你会得到（因为是硬连接，所以文件夹显示的文件大小不准，请查看磁盘的大小变化，512张1024*1024图片实际上只大了4.3个Mb）
![image](https://github.com/user-attachments/assets/be1ce814-8800-4c02-8101-3b167bff8185)





---

## 鸣谢  感谢gemini 孜孜不倦的教学。我几乎烧掉了她大约四分之一的寿命了。


## 📝 本项目采用 [MIT License](https://opensource.org/licenses/MIT) 许可证。

---
## 我发现了一个很严重的问题，那就是“我不会真的写代码( ☉д⊙)”，大多代码是我来排错，ai来写的。但问题务必提出来，我会和ai一起解决它的。
