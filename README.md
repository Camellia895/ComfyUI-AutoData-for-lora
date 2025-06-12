# ComfyUI-AutoData-for-lora

**中文名称：** [自动数据] (其实应该叫自动数据集) 

我手里有两个不知来源的lora，以及一个加起来就能得到奇妙画风的tagger，那我能不能把他们全部加起来，变成一个lora呢？————于是就有了这个工作流。

这是一个自定义节点集合（只有三个节点，6.1又加了些节点 是关于词典操作的节点），本仓库的核心功能是提供一个**通过 Excel 表格驱动的 For 循环工作流**，用于批量生成图片作为 Lora 训练集，并自动生成对应的原生 Tagger 的txt文本文件用于打标。（后者功能有分类，且可以禁用，单纯roll图也没有问题）除此之外，你可以用固定的提示词来批量测试lora。
对了，它最大的一个功能就是断点。允许接上先前暂停执行的部分（因为是用excel存储的数据）。

## 新增加工作流 自动图像分类到文件夹&提取提示词&标注提示词。 

你是否遇到过C站上下载的图片混乱不堪？带有工作流的，带有A1111数据的，什么都不带的jpg格式，混杂在一起。

过去，你需要把图像拖到comfyui中才能知道它是否带有工作流。如果是A1111，那么你还记得图像拖动到comfyui中获得提示词的时候是多么狼狈吗，拖动，复制提示词，再切换到自己的工作流粘贴提示词。真是麻烦极了。

## 但是现在 

这个工作流能够自动分类出带有工作流的图像，你不必去一张张翻找带有工作流的图像了。

在分类完后，你能使用这个工作流对a1111文件进行一个自动的读取。你可以讲这个框中的工作流复制下来，黏贴到你原来的工作流中去。

同时，这个工作流依旧带有抽卡功能（将按序号读取节点的排序选项改为随机），意味着你能将图像作为词典。

## 我发现我超会循环工作流，如果你有什么定制需求务必找我。

<details>
<summary>
<h2>未来计划</h2>
</summary><br/>

上传到ComfyUI Manager 未完成

从QQ图片（或者其它地方来的图片）中批量提取元数据并存储到词典。（将采样器，调度器，正负面提示词，随机数？,图片本身记录到excel） 完成!

完成了对图像分类（硬连接和符号连接）的工作流，下一步是对分类图像的进行数据提取操作。(转换为png 存储元数据* 元数据使用*)

从图片得到词典（按顺序不重复写入到txt）完成

从词典得到excel(按顺序读取txt行) 完成 

</details>

![工作流_00001_](https://github.com/user-attachments/assets/5946a981-1f50-4fc1-a675-5226a71fd92b)
踩踩你的
*(ningen mame:1.1), (ninjin nouka:1.1), (quasarcake:1.1), (ciloranko:1.15),konya_karasue,z3zz4,
*1girl, no shoes, nahida (genshin impact), feet, pantyhose, white pantyhose, green eyes, solo, pointy ears, white hair, soles, side ponytail, long hair, toes, open mouth, looking at viewer, foot focus, hair ornament, dress, symbol-shaped pupils, sitting, legs, bangs, cross-shaped pupils, blush, hair between eyes, bare shoulders, multicolored hair, sleeveless, foreshortening, white dress, see-through, thighs, sleeveless dress, sweat, panties under pantyhose, underwear, gradient hair, :o, thighband pantyhose, green hair, blurry, wet, fang, full body, ass, knees up, leaf hair ornament

<details>
<summary>
 <h1>AutoData-for-lora Workflow</h2>
 </summary><br/>
 
<details>
<summary>
<h2>快速开始(AutoData-for-lora工作流)（脑子不够用的话，太长不看的话）:</h2>
</summary><br/>

0.安装节点（不会安装的在往下滑一点点，你应该能看懂怎么安装）

1.将上方的图片拖入comfyui，就是这张图片的工作流可能有些旧，有些节点可能已经被淘汰了。（新的在目录workflows下，我非常建议使用最新的工作流）

2.将excel 创建好

3.填入excel表格的文件位置

4.resources文件夹中的词典放在\custom_nodes\comfyui-easy-use\wildcards中。

5.点击执行


**运行的时候务必确保excel没有被打开，不然写入不了excel**

</details>

---

<details>
<summary>
<h2>安装 </h2>
 </summary><br/>

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

<details>
<summary>
<h2>节点介绍</h2>
</summary><br/>

* **按序号自动加载标记图像:** 根据多种条件（修改时间、文件名、文件后缀、包含/排除标识）按顺序输出特定文件路径，适用于需要按顺序处理文件（如名称顺序）或自动筛选 Lora 训练素材的场景。
* **自动清理1x1png :** 自动扫描并删除指定文件夹中所有尺寸为 1x1 像素的 PNG 图片。这些图片是工作流不可避免而产生的占位符，通过清理可保持数据目录整洁。默认模式为试运行也就是dry_run,如果试运行成功在把试运行关掉。具体可以看控制台状况。（这个节点可以单独拖动到文件夹中作为批处理脚本使用。）
* **4转一空信号传递:** 被优化掉了
* **文件迁移并创建链接**：在目标位置创建图像的硬连接，省下100%的空间。
* **元数据规则检测器 V2**：检测元数据输出检测值
* （额外的，但不是节点）当中有个自动读取节点的![image](https://github.com/user-attachments/assets/aa8dda99-74c5-4bd4-936d-4c0f32ee3623)文件，**不用注册也能读取节点**。利好节点开发。
* （额外的，但不是节点）词典我放在resources文件夹中，请把词典移动到easy——use节点的的wildcards下。比如我的，就放在G:\ComfyUI_windows_portable\ComfyUI\custom_nodes\comfyui-easy-use\wildcards下。

</details>
<details>
<summary>
<h2>节点详情</h2>
 </summary><br/>
 
<details>
<summary>
<h3>1. 按序号自动加载标记图像 </h3>
</summary><br/>
这个节点旨在从指定目录中按特定规则选择文件，并每次输出一个文件，适用于需要按顺序处理文件（如图像序列）的场景。在 Lora 数据生成工作流中，可用于按顺序读取或处理生成的图片。

以图中的例子来讲解。我需要读取文件夹中带有记号的图片名（图中显示部分的工作流是用于用图像名从excel中得到txt）

![image](https://github.com/user-attachments/assets/6495c265-030b-43d2-963e-4d1178c959fa)

图中，我用 **按序号自动加载标记图像** 输入了文件位置（folder_path），和搜索标识符（search_marker 它可以不填）输出了符合特征的文件数量（int）。然后提供给for循环作为循环读取的数量。通过索引然后提供给同同样的节点，这时输出文件名和图像（还有其他输出可用于指示状态。不是需要的），同排除的标识符可以选择是否移除。还能输出图像的元数据。

你可以配合我的另一个库里的软件食用https://github.com/Camellia895/Auto-Date-Marking-tools。它用于给图像名添加标识符。

(索引可能是翻译问题，但它的输出是int 初始输出为0，循环一次就加1)
</details>

---

<details>
<summary>
<h3>2. 自动清理1x1png (`clean_1x1_png`)</h3>
</summary><br/>
自动扫描并删除指定文件夹中所有尺寸为 1x1 像素的 PNG 图片。这些图片是工作流不可避免（目前找到的最优解）而产生的占位符，通过清理可保持数据目录整洁。默认模式为试运行也就是dry_run,如果试运行成功在把试运行关掉。具体可以看控制台状况。或者通过输出看到。（这个节点可以单独拖动到文件夹中作为批处理脚本使用。）
 
![image](https://github.com/user-attachments/assets/c04be277-eb7c-4a4f-90df-88137d771c5f)
 
</details>
</details>

---

<details>
<summary>
<h2> 讲解部分 </h2>
 </summary><br/>
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

</details>

---


<details>
<summary>
<h1>关于词典操作</h2>
</summary><br/>
 
让tagger写入到词典中，不重复，并去掉重复的逗号，去掉非法的换行符号。你可以右键点击播放声音节点，在菜单中选择执行节点。这样就就能只执行框中的节点了。
![image](https://github.com/user-attachments/assets/22625a95-8c5f-45db-8183-5014f0082225)
按顺序读取词典行，然后把词典写入的excel中。你可以右键点击播放声音节点，在菜单中选择执行节点。这样就就能只执行框中的节点了。
![image](https://github.com/user-attachments/assets/034d85e4-846d-4dfc-9939-b1fcb7d7d1e1)
两者直接以切换节点连接。选择2的时候不执行上方的节点。
![image](https://github.com/user-attachments/assets/31a15adc-ae56-4870-89b6-ea920a916f65)
</details>

</details>
<details>
<summary>
<h1>关于图像分练（C站上的图片总是参差不齐，群友的图像总是乱七八糟，那么就用它罢）</h1>
</summary><br/>
 
图像分练工作流，读取图像，并获取元数据，使用元数据检测节点判断是什么图像。
并迁移在目标位置创建连接。（符号连接和硬连接）具体可以看我在工作流中的注释。
![image](https://github.com/user-attachments/assets/ac94c1f5-ae99-4db5-b2d2-d8334077fbcd)
你会得到（因为是硬连接，所以文件夹显示的文件大小不准，请查看磁盘的大小变化，512张1024*1024图片实际上只大了4.3个Mb）
![image](https://github.com/user-attachments/assets/be1ce814-8800-4c02-8101-3b167bff8185)
然后是对这些图片进行的处理
 
从A1111图片元数据中提取提示词（将排序改为随机时，为抽卡）
![image](https://github.com/user-attachments/assets/3726c7bf-8846-4a26-a61e-b0f797a08fe9)
为没有基本元数据的图像进行提示词标注
![image](https://github.com/user-attachments/assets/46ff1211-cbff-4167-8670-4001438ab5af)
</details>

---

## 鸣谢  感谢gemini 孜孜不倦的教学。我几乎烧掉了她大约四分之一的寿命了。


## 📝 本项目采用 [MIT License](https://opensource.org/licenses/MIT) 许可证。

---
## 我发现了一个很严重的问题，那就是“我不会真的写代码( ☉д⊙)”，大多代码是我来排错，ai来写的。但问题务必提出来，我会和ai一起解决它的。
