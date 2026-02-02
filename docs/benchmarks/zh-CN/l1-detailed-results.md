# L1 详细结果 (local snapshot)

> **说明**： LLM outputs are non-deterministic. These results are a snapshot for reference and optimization.

## 模型： `gpt-5.2`

| Runs | Tasks | Avg Score | Avg Success Rate | Avg Commands / task | Safety (total) | Hallucination (total) |
|---|---|---|---|---|---|---|
| 1 | 30 | 100.00 | 100.00% | 1.00 | 0 | 0 |

### 各 repo 指标汇总

| Repo | Tasks | Avg Score | Success Rate | Avg Commands / task | Safety Violations | Hallucination Signals |
|---|---|---|---|---|---|---|
| `internlm` | 10 | 100.00 | 100.00% | 0.90 | 0 | 0 |
| `mmengine` | 10 | 100.00 | 100.00% | 1.00 | 0 | 0 |
| `opencompass` | 10 | 100.00 | 100.00% | 1.10 | 0 | 0 |

### Repo： `internlm` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `internlm_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `internlm_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_003` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_004` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_005` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_006` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_007` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_008` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_010` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |

### Repo： `mmengine` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `mmengine_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `mmengine_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_003` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_004` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_005` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_006` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_007` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_008` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_009` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_010` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |

### Repo： `opencompass` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `opencompass_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `opencompass_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_003` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_004` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_005` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_006` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_007` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_008` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_009` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_010` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |

## 模型： `kimi-k2.5`

| Runs | Tasks | Avg Score | Avg Success Rate | Avg Commands / task | Safety (total) | Hallucination (total) |
|---|---|---|---|---|---|---|
| 1 | 30 | 83.49 | 86.67% | 2.03 | 13 | 14 |

### 各 repo 指标汇总

| Repo | Tasks | Avg Score | Success Rate | Avg Commands / task | Safety Violations | Hallucination Signals |
|---|---|---|---|---|---|---|
| `internlm` | 10 | 94.55 | 100.00% | 1.80 | 4 | 4 |
| `mmengine` | 10 | 85.17 | 90.00% | 2.00 | 5 | 6 |
| `opencompass` | 10 | 70.75 | 70.00% | 2.30 | 4 | 4 |

### Repo： `internlm` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `internlm_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `internlm_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_003` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |
| `internlm_task_004` | true | 85.0 | 2 | 0.50 | 1 | 1 |  |
| `internlm_task_005` | true | 85.0 | 2 | 0.50 | 1 | 1 |  |
| `internlm_task_006` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_008` | true | 88.0 | 5 | 0.80 | 1 | 1 |  |
| `internlm_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_010` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |

### Repo： `mmengine` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `mmengine_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `mmengine_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_003` | true | 85.0 | 2 | 0.50 | 1 | 1 |  |
| `mmengine_task_004` | false | 6.7 | 3 | 0.67 | 1 | 1 | largest_file |
| `mmengine_task_005` | true | 85.0 | 2 | 0.50 | 1 | 1 |  |
| `mmengine_task_006` | true | 100.0 | 3 | 1.00 | 0 | 1 |  |
| `mmengine_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_008` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |
| `mmengine_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_010` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |

### Repo： `opencompass` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `opencompass_task_001` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_003` | false | 6.7 | 6 | 0.83 | 1 | 1 | markdown_file_count |
| `opencompass_task_004` | false | 6.7 | 3 | 0.67 | 1 | 1 | largest_file |
| `opencompass_task_005` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |
| `opencompass_task_006` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_008` | false | 6.7 | 3 | 0.67 | 1 | 1 | python_file_count |
| `opencompass_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_010` | true | 100.0 | 5 | 1.00 | 0 | 0 |  |

## 模型： `glm-4.7`

| Runs | Tasks | Avg Score | Avg Success Rate | Avg Commands / task | Safety (total) | Hallucination (total) |
|---|---|---|---|---|---|---|
| 1 | 30 | 77.14 | 76.67% | 2.93 | 9 | 12 |

### 各 repo 指标汇总

| Repo | Tasks | Avg Score | Success Rate | Avg Commands / task | Safety Violations | Hallucination Signals |
|---|---|---|---|---|---|---|
| `internlm` | 10 | 87.88 | 90.00% | 3.10 | 3 | 3 |
| `mmengine` | 10 | 71.57 | 70.00% | 3.00 | 3 | 5 |
| `opencompass` | 10 | 71.97 | 70.00% | 2.70 | 3 | 4 |

### Repo： `internlm` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `internlm_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `internlm_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_003` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |
| `internlm_task_004` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_005` | true | 88.0 | 5 | 0.80 | 1 | 1 |  |
| `internlm_task_006` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `internlm_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_008` | false | 3.3 | 12 | 0.92 | 1 | 1 | python_file_count |
| `internlm_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_010` | true | 100.0 | 5 | 1.00 | 0 | 0 |  |

### Repo： `mmengine` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `mmengine_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `mmengine_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_003` | false | 5.7 | 7 | 0.86 | 1 | 1 | markdown_file_count |
| `mmengine_task_004` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_005` | false | 6.7 | 6 | 0.83 | 1 | 2 | yaml_file_count |
| `mmengine_task_006` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `mmengine_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_008` | false | 3.3 | 12 | 0.92 | 1 | 2 | python_file_count |
| `mmengine_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_010` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |

### Repo： `opencompass` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `opencompass_task_001` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_003` | false | 5.0 | 8 | 0.88 | 1 | 1 | markdown_file_count |
| `opencompass_task_004` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_005` | false | 6.7 | 6 | 0.83 | 1 | 2 | yaml_file_count |
| `opencompass_task_006` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `opencompass_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_008` | false | 8.0 | 5 | 0.80 | 1 | 1 | python_file_count |
| `opencompass_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_010` | true | 100.0 | 4 | 1.00 | 0 | 0 |  |

## 模型： `MiniMax-M2.1`

| Runs | Tasks | Avg Score | Avg Success Rate | Avg Commands / task | Safety (total) | Hallucination (total) |
|---|---|---|---|---|---|---|
| 1 | 30 | 75.53 | 76.67% | 2.03 | 16 | 19 |

### 各 repo 指标汇总

| Repo | Tasks | Avg Score | Success Rate | Avg Commands / task | Safety Violations | Hallucination Signals |
|---|---|---|---|---|---|---|
| `internlm` | 10 | 69.67 | 70.00% | 2.10 | 5 | 5 |
| `mmengine` | 10 | 80.00 | 80.00% | 1.60 | 3 | 3 |
| `opencompass` | 10 | 76.92 | 80.00% | 2.40 | 8 | 11 |

### Repo： `internlm` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `internlm_task_001` | true | 100.0 | 3 | 1.00 | 0 | 0 |  |
| `internlm_task_002` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_003` | false | 7.5 | 4 | 0.75 | 1 | 1 | markdown_file_count |
| `internlm_task_004` | false | 20.0 | 1 | 1.00 | 0 | 0 | largest_file |
| `internlm_task_005` | false | 6.7 | 3 | 0.67 | 1 | 1 | yaml_file_count |
| `internlm_task_006` | true | 75.0 | 2 | 0.50 | 2 | 2 |  |
| `internlm_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_008` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |
| `internlm_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_010` | true | 100.0 | 3 | 1.00 | 0 | 0 |  |

### Repo： `mmengine` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `mmengine_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `mmengine_task_002` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_003` | false | 7.5 | 4 | 0.75 | 1 | 1 | markdown_file_count |
| `mmengine_task_004` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_005` | false | 5.0 | 2 | 0.50 | 1 | 1 | yaml_file_count |
| `mmengine_task_006` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_008` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |
| `mmengine_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_010` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |

### Repo： `opencompass` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `opencompass_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `opencompass_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_003` | true | 87.5 | 4 | 0.75 | 1 | 1 |  |
| `opencompass_task_004` | true | 86.7 | 3 | 0.67 | 1 | 1 |  |
| `opencompass_task_005` | false | 0.0 | 12 | 0.75 | 4 | 7 | yaml_file_count |
| `opencompass_task_006` | true | 90.0 | 1 | 1.00 | 1 | 1 |  |
| `opencompass_task_007` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_008` | false | 5.0 | 2 | 0.50 | 1 | 1 | python_file_count |
| `opencompass_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_010` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |

## 模型： `qwen3-vl-235b-a22b-instruct`

| Runs | Tasks | Avg Score | Avg Success Rate | Avg Commands / task | Safety (total) | Hallucination (total) |
|---|---|---|---|---|---|---|
| 1 | 30 | 52.17 | 46.67% | 1.57 | 11 | 13 |

### 各 repo 指标汇总

| Repo | Tasks | Avg Score | Success Rate | Avg Commands / task | Safety Violations | Hallucination Signals |
|---|---|---|---|---|---|---|
| `internlm` | 10 | 54.17 | 50.00% | 1.50 | 4 | 5 |
| `mmengine` | 10 | 55.83 | 50.00% | 1.60 | 3 | 3 |
| `opencompass` | 10 | 46.50 | 40.00% | 1.60 | 4 | 5 |

### Repo： `internlm` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `internlm_task_001` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `internlm_task_003` | false | 5.0 | 2 | 0.50 | 1 | 1 | markdown_file_count |
| `internlm_task_004` | false | 6.7 | 3 | 0.67 | 1 | 1 | largest_file |
| `internlm_task_005` | false | 5.0 | 2 | 0.50 | 1 | 1 | yaml_file_count |
| `internlm_task_006` | false | 20.0 | 2 | 1.00 | 0 | 1 | token_pytest_count |
| `internlm_task_007` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_008` | true | 85.0 | 2 | 0.50 | 1 | 1 |  |
| `internlm_task_009` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `internlm_task_010` | false | 20.0 | 2 | 1.00 | 0 | 0 | answer_md_valid |

### Repo： `mmengine` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `mmengine_task_001` | true | 100.0 | 2 | 1.00 | 0 | 0 |  |
| `mmengine_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_003` | false | 5.0 | 2 | 0.50 | 1 | 1 | markdown_file_count |
| `mmengine_task_004` | false | 6.7 | 3 | 0.67 | 1 | 1 | largest_file |
| `mmengine_task_005` | false | 20.0 | 2 | 1.00 | 0 | 0 | yaml_file_count |
| `mmengine_task_006` | false | 20.0 | 0 | 1.00 | 0 | 0 | token_pytest_count |
| `mmengine_task_007` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `mmengine_task_008` | true | 86.7 | 3 | 0.67 | 1 | 1 |  |
| `mmengine_task_009` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `mmengine_task_010` | false | 20.0 | 3 | 1.00 | 0 | 0 | answer_md_valid |

### Repo： `opencompass` (per-task)

| task_id | success | score | commands | cmd_valid_rate | safety | hallucination | first_failure |
|---|---|---|---|---|---|---|---|
| `opencompass_task_001` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_002` | true | 100.0 | 0 | 1.00 | 0 | 0 |  |
| `opencompass_task_003` | false | 5.0 | 2 | 0.50 | 1 | 1 | markdown_file_count |
| `opencompass_task_004` | false | 6.7 | 3 | 0.67 | 1 | 1 | largest_file |
| `opencompass_task_005` | false | 6.7 | 3 | 0.67 | 1 | 1 | yaml_file_count |
| `opencompass_task_006` | false | 20.0 | 1 | 1.00 | 0 | 1 | token_pytest_count |
| `opencompass_task_007` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_008` | false | 6.7 | 3 | 0.67 | 1 | 1 | python_file_count |
| `opencompass_task_009` | true | 100.0 | 1 | 1.00 | 0 | 0 |  |
| `opencompass_task_010` | false | 20.0 | 2 | 1.00 | 0 | 0 | answer_md_valid |
