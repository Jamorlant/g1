# Kaggle 数据集建议

下面这些数据集都适合当前“面向工业物联网的高效可撤销属性基访问控制”原型的实验扩展。建议优先下载为本地 `CSV` 后，通过 `--dataset-file` 接入实验脚本。

## 1. 工业监测与智能制造

### 1.1 Smart Manufacturing IoT-Cloud Monitoring Dataset

- 适用方向：工业监测、预测性维护、异常检测
- 规模特点：`100,000` 条传感器记录，`50` 台机器
- 适合作为：高体量业务明文、批量记录加密、数据集切片实验
- Kaggle 链接：
  - https://www.kaggle.com/datasets/ziya07/smart-manufacturing-iot-cloud-monitoring-dataset/data

### 1.2 Smart Manufacturing Process Data

- 适用方向：工艺过程监测、质量分析、轻量级初始实验
- 规模特点：`10,000` 行，按分钟时间戳记录
- 适合作为：中等规模对照实验
- Kaggle 链接：
  - https://www.kaggle.com/datasets/programmer3/smart-manufacturing-process-data

### 1.3 Industrial IoT Multi-Axis Vibration Dataset

- 适用方向：多变量时序、振动异常检测、设备状态监测
- 规模特点：多轴振动 + 环境 + 控制参数
- 适合作为：更贴近 IIoT 传感器场景的实验输入
- Kaggle 链接：
  - https://www.kaggle.com/datasets/sydsxdiq/industrial-iot-dataset-vibration-gas-environment/data

## 2. 预测性维护

### 2.1 Machine Predictive Maintenance Classification

- 适用方向：预测性维护、机器故障分析
- 规模特点：`10,000` 条样本，约 `531 KB` 的 CSV
- 适合作为：快速验证、附加分类实验
- Kaggle 链接：
  - https://www.kaggle.com/datasets/shivamb/machine-predictive-maintenance-classification

## 3. IIoT / IoT 安全数据

### 3.1 X-IIoTD Dataset

- 适用方向：工业物联网网络安全、访问控制、加密保护高体量日志
- 规模特点：`820,834` 条记录，`68` 个特征，单文件约 `355.31 MB`
- 适合作为：大规模明文加密、批量日志保护、高负载实验
- Kaggle 链接：
  - https://www.kaggle.com/datasets/annaamalai1752/x-iiotd-dataset

### 3.2 IoT Intrusion Detection

- 适用方向：IoT 安全日志、攻击检测数据保护
- 规模特点：`1,191,264` 条实例，`47` 个特征
- 适合作为：超大规模负载实验
- Kaggle 链接：
  - https://www.kaggle.com/datasets/subhajournal/iotintrusion

### 3.3 IoT Botnet Traffic Dataset

- 适用方向：IoT 流量保护、边缘侧日志加密
- 规模特点：超过 `700,000` 行
- 适合作为：高体量流量日志实验
- Kaggle 链接：
  - https://www.kaggle.com/datasets/dyutidasmahaptra/iot-botnet-traffic-dataset

## 4. 推荐选型

如果你想让论文实验更像“工业物联网数据共享”而不是纯网络安全，更建议按下面优先级选择：

1. `Smart Manufacturing IoT-Cloud Monitoring Dataset`
2. `Industrial IoT Multi-Axis Vibration Dataset`
3. `X-IIoTD Dataset`

如果你更想把“海量工业日志访问控制”作为论文卖点，则优先：

1. `X-IIoTD Dataset`
2. `IoT Intrusion Detection`
3. `IoT Botnet Traffic Dataset`

## 5. 接入方式

下载到本机后，直接运行：

```bash
py -3 main.py benchmark --output output/benchmarks_kaggle --dataset-file "D:\datasets\your_dataset.csv"
```

## 6. 写论文时的表述建议

可以写成：

“为提高实验说服力，本文在原型系统验证基础上，进一步选取 Kaggle 公共工业物联网/智能制造数据集作为业务明文载体，通过大规模工业传感器记录与日志数据模拟云端共享场景，并对不同策略规模、明文规模及撤销前后性能进行系统评估。”

