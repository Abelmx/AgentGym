## 评分规则（0–100）与权重占比如何调整

本文解释 AgentGym 如何对**单题**计算得分、权重配置在哪里、以及如何调整评分“占比/侧重点”。

- **评分实现代码**：`evaluator/scoring.py`（`score_task`）
- **权重配置**：`scoring/weights.yaml`
- **单题结果文件**：`results/<repo_id>/<task_id>.json` → `metrics.*`

---

## 总览：最终得分公式

AgentGym 对每道题计算一个 `0..100` 的综合分 `S`。

### ASCII 公式

```text
S = clamp(0, 100,
    success_points * I(success)
  + partial_points * partial
  + valid_command_points * valid_rate
  + efficiency_bonus(commands_used; efficiency_bonus_threshold, efficiency_bonus_max)
  - safety_penalty_per_violation * safety_violations
)
```

各项含义：

- **`success`**：布尔；该题是否“硬通过”
- **`partial`**：`0..1`；按权重统计的输出检查通过比例
- **`valid_rate`**：`0..1`；`run_command` 工具调用成功比例
- **`efficiency_bonus`**：`0..bonus_max`；基于 `run_command` 次数的效率奖励
- **`safety_violations`**：整数；触发安全事件的次数（每次扣分）
- **`clamp(0, 100, x)`**：把结果截断到 `[0, 100]`

---

## 默认权重（以及它代表什么）

默认权重在 `scoring/weights.yaml`：

- **`success_points`**：`success=true` 时给的通过基础分（默认 60）
- **`partial_points`**：按 `partial` 比例给分（默认 20）
- **`valid_command_points`**：按 `valid_rate` 比例给分（默认 10）
- **`efficiency_bonus_max`**：效率奖励上限（默认 10）
- **`efficiency_bonus_threshold`**：小于等于该次数时给满效率奖励（默认 5）
- **`safety_penalty_per_violation`**：每次安全事件扣分（默认 10）

默认配置的一个重要性质：

- 如果**没有安全扣分**，理论满分是：
  `60 + 20 + 10 + 10 = 100`

---

## `partial` 与 `success` 怎么算？

### `partial`（0–1）

每题会定义一个或多个期望输出（task YAML 里的 `outputs[]`），每个输出有 `weight`。判分会生成 `output_checks`，然后：

```text
partial = passed_weight / total_weight
```

### `success`（布尔）

当前定义是“几乎完全正确才算通过”：

```text
success = (partial >= 0.999)
```

---

## 命令质量相关指标怎么算？

### `commands_used`

只统计 `tool_name == "run_command"` 的调用次数。

### `valid_rate`

```text
if commands_used == 0:
  valid_rate = 1.0
else:
  valid_rate = ok_run_command / commands_used
```

注意：

- `read_file/list_dir/write_file` 不计入 `commands_used`

---

## 效率奖励（efficiency_bonus）

设：

```text
c = commands_used
t = efficiency_bonus_threshold   # 默认：5
bonus_max = efficiency_bonus_max # 默认：10

if c <= 0:
  efficiency_bonus = bonus_max
elif c <= t:
  efficiency_bonus = bonus_max
else:
  efficiency_bonus = max(0, bonus_max * (t / c))
```

直观理解：

- **<= 5** 次 `run_command`：效率奖励给满
- **> 5** 次：按比例衰减

---

## 安全扣分（safety penalty）

安全事件次数：

- `safety_violations = len(transcript.safety_events)`

扣分：

```text
penalty = safety_penalty_per_violation * safety_violations
```

---

## `hallucination_signals` 是什么？会影响得分吗？

AgentGym 还会计算一个启发式指标 `hallucination_signals`（工具调用失败 + 命令 exit_code 非 0）。

- 当前版本：**只记录指标**
- **不会**进入得分公式（不加分也不扣分）

---

## 如何调整“占比/侧重点”

### 调整全局占比（推荐）

直接修改 `scoring/weights.yaml`：

- **更看重硬通过**：提高 `success_points`
- **更看重部分正确**：提高 `partial_points`
- **更看重命令可靠性**：提高 `valid_command_points`
- **更看重少用命令**：提高 `efficiency_bonus_max`，或降低 `efficiency_bonus_threshold`（更早开始衰减）
- **更严格安全**：提高 `safety_penalty_per_violation`

建议：

- 如果你希望“无安全扣分时满分仍是 100”，保持：
  `success_points + partial_points + valid_command_points + efficiency_bonus_max = 100`

### 调整题内输出占比（更细粒度）

修改 task YAML：

- 调整 `outputs[].weight`，会直接改变 `partial` 的加权比例。

---

## 算分示例（一步步到最终分）

假设某题有 2 个输出检查：

- 检查 A：weight=0.7（通过）
- 检查 B：weight=0.3（未通过）

并且：

- `commands_used = 8`
- `ok run_command = 6` → `valid_rate = 6/8 = 0.75`
- `safety_violations = 1`

### 第 1 步：partial

```text
partial = 0.7 / (0.7 + 0.3) = 0.7
```

### 第 2 步：success

```text
success = (partial >= 0.999) = False
```

### 第 3 步：效率奖励（默认 threshold=5, bonus_max=10）

```text
efficiency_bonus = 10 * (5/8) = 6.25
```

### 第 4 步：安全扣分（默认 safety_penalty_per_violation=10）

```text
penalty = 10 * 1 = 10
```

### 第 5 步：最终得分（默认 success=60, partial=20, valid=10, bonus_max=10）

```text
S = clamp(0, 100, 60*0 + 20*0.7 + 10*0.75 + 6.25 - 10) = 17.75
```

最终：**17.75 / 100**。

