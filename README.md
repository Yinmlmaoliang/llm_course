# 基于ChatGLM-6B与LoRA微调技术构建学术论文写作领域的语言模型

## 项目简介
本项目基于ChatGLM-6B模型,采用LoRA（Low-Rank Adaptation）微调技术,构建了一个专注于论文写作问题问答的语言模型。
## 特性
- 基于大规模预训练模型ChatGLM-6B
- 使用LoRA技术进行领域特定微调
- 专注于学术论文写作场景
- 提供Web应用界面,便于使用
## 快速开始
### 1. 下载模型

请从以下链接下载预训练模型:
[ChatGLM-6B-学术论文写作问答 模型](https://pan.quark.cn/s/fbfe6572170c)

请从以下链接下载数据集:
[问答数据](https://pan.quark.cn/s/6a145db8bb72)

下载完成后,请将模型文件解压到项目根目录。

### 2. 环境配置
确保您的系统已安装Python 3.10+。

下载并设置 LLaMA Factory 后，环境不需要重新安装。

执行以下命令安装本项目所需依赖:
```bash
pip install -r requirements.txt
```
### 3. 运行Web应用

在项目根目录下,执行以下命令启动Web应用:

```bash
python webapp.py
```
启动成功后,请在浏览器中访问 `http://localhost:7870` 来使用Web应用。

## 致谢
- [THUDM/ChatGLM-6B](https://github.com/THUDM/ChatGLM-6B) - 基础模型
- [LLaMA Factory](https://llamafactory.readthedocs.io/zh-cn/latest/index.html) - 训练与微调平台