# Plan: 实现 `just install brew` 命令

## TL;DR

> **快速摘要**: 实现 Homebrew 包管理器的自动化安装命令，支持非交互式安装和安装验证
> 
> **交付物**: 
> - `src/just/installers/brew/__init__.py` - 包初始化文件
> - `src/just/installers/brew/installer.py` - 安装逻辑实现
> 
> **预估工作量**: 简单 (约 20 分钟)
> **并行执行**: 无需 (单一任务)

---

## Context

### 原始需求
用户希望在 just-cli 中添加 `just install brew` 命令，实现在 macOS 上自动安装 Homebrew。

### 调研结果
1. **官方安装脚本**: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. **安装路径**: 
   - Apple Silicon (M1-M4): `/opt/homebrew`
   - Intel Mac: `/usr/local`
3. **前置要求**: Xcode Command Line Tools (安装脚本会自动检查)
4. **非交互式安装**: 需要设置 `CI=1` 环境变量

### 代码风格
遵循现有 installer 模式 (参考 cloudflare, nvm, docker):
- 使用 `@just.installer(check="...")` 装饰器
- 使用 `just.system.platform` 检测平台
- 使用 `just.execute_commands()` 执行命令
- 使用 `just.system.pms.brew.is_available()` 检测是否已安装

---

## Work Objectives

### 核心目标
创建 Homebrew 安装器，支持:
1. 检测是否已安装 (避免重复安装)
2. 非交互式自动安装 (设置 CI=1)
3. 安装后验证

### 具体交付物
- `src/just/installers/brew/__init__.py` - 包初始化 (空文件或配置)
- `src/just/installers/brew/installer.py` - 主安装逻辑

### 完成定义
- [ ] `just install brew` 命令可用
- [ ] 已安装时提示无需安装
- [ ] 未安装时执行安装
- [ ] 安装后验证成功

### 必须有
- 检测 brew 是否已安装
- 非交互式安装支持
- 安装后验证

### 禁止项
- 仅支持 macOS (darwin) 平台
- 不实现 Linuxbrew (超出需求)

---

## Verification Strategy

### 测试决策
- **基础设施**: 无需 (简单 CLI 命令)
- **Agent QA**: 手动验证命令行为

### QA 策略
每个任务必须包含 agent 可执行的 QA 场景。

---

## TODOs

- [ ] 1. 创建 `src/just/installers/brew/` 目录结构

  **工作内容**:
  - 创建 `src/just/installers/brew/__init__.py`
  - 创建 `src/just/installers/brew/installer.py`
  
  **禁止**:
  - 不添加不必要的文件
  
  **推荐 Agent**:
  - Category: `quick`
  - Skills: []
  
  **并行化**:
  - 可并行: 否 (单一任务)
  - 阻塞: 无
  - 依赖: 无
  
  **引用**:
  - `src/just/installers/cloudflare/installer.py` - 参考 `@just.installer` 装饰器用法
  - `src/just/installers/nvm/installer.py` - 参考跨平台处理逻辑
  
  **验收标准**:
  - [ ] 目录 `src/just/installers/brew/` 存在
  - [ ] 文件 `__init__.py` 和 `installer.py` 存在
  - [ ] `just install brew --help` 显示帮助信息
  
  **QA 场景**:
  ```
  场景: 命令帮助可用
    工具: Bash
    步骤:
      1. 运行 `just install brew --help`
    预期结果: 显示帮助信息，包含 "Install Homebrew" 描述
    失败指示: 命令未找到或无帮助信息
    证据: 终端输出
  ```
  
  **提交**: 是
  - 信息: `feat(installer): add Homebrew installer`

- [ ] 2. 实现 brew installer 逻辑

  **工作内容**:
  - 导入必要模块
  - 添加 `@just.installer(check="brew --version")` 装饰器
  - 实现 `install_brew()` 函数
  - 检测 brew 是否已安装
  - 非交互式安装命令: `CI=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  
  **禁止**:
  - 不实现 Windows/Linux 安装
  
  **推荐 Agent**:
  - Category: `quick`
  - Skills: []
  
  **并行化**:
  - 可并行: 否
  - 阻塞: Task 1
  - 依赖: Task 1
  
  **引用**:
  - `src/just/installers/cloudflare/installer.py:3` - `@just.installer(check=...)` 模式
  - `src/just/installers/nvm/installer.py:14-29` - 平台检测和命令执行模式
  
  **验收标准**:
  - [ ] 装饰器 `@just.installer(check="brew --version")` 已添加
  - [ ] 函数检查 `just.system.pms.brew.is_available()`
  - [ ] 已安装时打印信息并返回
  - [ ] 未安装时执行非交互式安装命令
  
  **QA 场景**:
  ```
  场景: 已安装时提示信息
    工具: Bash
    前提: brew 已安装在系统中
    步骤:
      1. 运行 `just install brew`
    预期结果: 显示提示信息表示已安装，不执行安装
    失败指示: 尝试重复安装
    证据: 终端输出
  ```
  
  **提交**: 是
  - 信息: `feat(installer): implement brew installer logic`

- [ ] 3. 验证安装

  **工作内容**:
  - 在未安装 brew 的系统上测试安装 (可选)
  - 验证命令正常工作
  
  **推荐 Agent**:
  - Category: `unspecified-high`
  - Skills: []
  
  **并行化**:
  - 可并行: 否
  - 阻塞: Task 2
  - 依赖: Task 2
  
  **验收标准**:
  - [ ] `--help` 显示正确信息
  - [ ] 已安装时行为正确
  
  **QA 场景**:
  ```
  场景: 帮助信息正确
    工具: Bash
    步骤:
      1. just install brew --help
    预期结果: 显示包含 "Homebrew" 的帮助信息
    证据: 终端输出
  ```
  
  **提交**: 否

---

## Success Criteria

### 验证命令
```bash
just install brew --help  # 显示帮助
just install brew         # 执行安装 (未安装时) 或提示已安装
```

### 最终检查
- [ ] `just install brew --help` 正常工作
- [ ] 已安装 brew 时提示正确
- [ ] 安装逻辑完整 (检测 + 安装 + 验证)
