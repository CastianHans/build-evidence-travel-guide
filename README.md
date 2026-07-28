# 循证旅行计划与 PDF

面向中国用户出境游的 AI Agent Skill。它会把官方资料、小红书的正向与避雷体验、Reddit 等国外社区以及目的地本地语言平台的资料，整理成可以直接照着执行的旅行计划和 PDF 手册。

本项目不是景点清单生成器。它会从酒店地址出发，核算逐段交通、真实停留时间、排队、吃饭、休息、天气备选、价格和支付方式，并在成稿前审计证据覆盖。

## 主要特点

- 默认使用简体中文沟通和交付。
- 小红书是中国游客体验的核心来源，同时参考 Reddit、目的地本地平台、地图评价和攻略网站。
- 每个重要景点、餐厅、交通方案和商品都分别检索正向体验与避雷信息。
- 拦截重复链接、错对象帖子、标题党、疑似推广、缺少正文摘录和证据平台过于单一的问题。
- 价格默认同时记录目的地当地价格、折合人民币价格和中国常见渠道对比价。
- 支付章节默认检查支付宝、微信支付、银联、Visa、Mastercard、现金需求、境外手续费和支付失败备选。
- 从确切酒店地址构建每天的完整路线，不会只给出“上午去 A、下午去 B”。
- 单独核算交通卡、机场交通、打车、退税、行李、境外上网和购物保修。
- 最终 PDF 会先做文本检查，再逐页渲染检查排版。

## 安装

需要 Python 3.10 或更高版本。PDF 渲染还需要 Poppler；PDF 制作与检查可使用 ReportLab、pypdf 和 Pillow。

```text
npx skills add CastianHans/build-evidence-travel-guide@build-evidence-travel-guide
```

手动安装时，将 `build-evidence-travel-guide/` 文件夹复制到 Codex 或其他兼容 Agent 的 Skills 目录。

## 使用示例

```text
$build-evidence-travel-guide
请为我的韩国家庭旅行制作一份简体中文的循证旅行计划和 PDF。
先收集必要资料，再同时检索小红书、Reddit、韩国本地平台和官方来源。
每个重要项目都要做正向种草和反向避雷验证。
```

Skill 会先询问：

- 目的地、日期和出入境交通；
- 同行人员的实际步行、地形和天气耐受能力；
- 每晚酒店或拟住宿区域；
- 必去、可选和明确不想去的项目；
- 预算、节奏、饮食、行李、支付和购物需求；
- 已购机票、门票、交通卡、电话卡和保险；
- 允许只读检索的平台及浏览器条件。

不要提供密码、浏览器 Cookie、完整护照号码、银行卡号、验证码或 API Key。

## 可选调研工具

- [Agent-Reach](https://github.com/Panniantong/Agent-Reach)：平台路由和可用性检查；
- [OpenCLI](https://github.com/jackwener/opencli)：通过用户自行登录的浏览器只读查看平台内容；
- Poppler、ReportLab、pypdf、Pillow：生成和检查 PDF。

只读检查本机依赖：

```text
python build-evidence-travel-guide/scripts/doctor.py
```

软件安装成功不等于平台已经可读。需要登录时，由用户在自己的浏览器中手动登录；Skill 不自动登录、不提取 Cookie，也不点赞、收藏、评论或发帖。

## 证据审计

初始化研究目录：

```text
python build-evidence-travel-guide/scripts/init_project.py path/to/project
```

填写：

- `research/candidates.csv`
- `research/evidence.csv`

执行审计：

```text
python build-evidence-travel-guide/scripts/audit_evidence.py path/to/project
```

返回码：

- `0`：所有受控候选项通过；
- `2`：仍有关键或重要候选项证据不足；
- `3`：数据结构或证据完整性错误。

只有唯一、直接相关、非推广且完成对象身份核验的证据才能计数。

## PDF 检查

```text
python build-evidence-travel-guide/scripts/validate_pdf.py guide.pdf \
  --require "天气" --require "出发前准备"

python build-evidence-travel-guide/scripts/render_pdf.py \
  guide.pdf path/to/empty-render-directory
```

文本检查不能替代视觉检查。需要查看联系表，并抽查完整分辨率页面。

## 自动化测试

```text
python -m unittest discover \
  -s build-evidence-travel-guide/tests -v
```

测试覆盖正常多平台证据、重复 URL、重复证据编号、孤立证据、候选对象错配、推广内容、身份核验和降低证据门槛时的书面理由。

## 许可证

MIT。第三方工具、帖子、地图和图片仍受各自许可证、著作权和平台条款约束。
