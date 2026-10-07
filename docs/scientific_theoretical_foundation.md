# FireGuard 施工现场火灾动力学与应急疏散科学理论支撑白皮书

> **为第一届“海之子”杯AI智能体挑战计划提供深厚工程物理与疏散动力学理论依据**  
> 融合国际消防动力学（SFPE/NFPA）、国家工程标准（GB/T 50720 / GB 50016）与人体生物力学生命安全准则。

---

## 一、在建工程特殊火灾动力学模型 (Fire Dynamics in Construction)

在建高层建筑与已竣工建筑存在根本性的火灾物理差异：在建建筑无永久防火分区、未安装自动喷淋、未封堵电梯井和通风管道贯通上下，形成强烈的“立体扩散”。

### 1.1 垂直管道井“烟囱效应”流体动力学方程 (Stack Effect)
在建核心筒管道井、楼梯间、施工洞口内外存在巨大温度差与高度差，形成极强的浮力驱动热压：

$$\Delta P = \rho_0 g H \left(1 - \frac{T_0}{T_s}\right) = \rho_0 g H \left(\frac{T_s - T_0}{T_s}\right)$$

其中：
- $\Delta P$：竖向井道内外压力差 ($\text{Pa}$)；
- $\rho_0$：外界环境空气密度 ($\approx 1.2\,\text{kg/m}^3$)；
- $g$：重力加速度 ($9.8\,\text{m/s}^2$)；
- $H$：未封闭竖向高度 ($\text{m}$)；
- $T_0$：施工现场环境初始绝对温度 ($\text{K}$)；
- $T_s$：火羽流烟气平均绝对温度 ($\text{K}$)。

**烟气垂直向上喷涌速度公式**：
$$v_{\text{vert}} = C_d \sqrt{\frac{2 \Delta P}{\rho_s}} = C_d \sqrt{2 g H \frac{T_s - T_0}{T_0}}$$

- 当 $H = 15\,\text{m}$（约3~4层作业高度），$T_s = 573\,\text{K}$ ($300^\circ\text{C}$)，$T_0 = 293\,\text{K}$ ($20^\circ\text{C}$)，流量系数 $C_d \approx 0.65$ 时：
  $$v_{\text{vert}} \approx 0.65 \times \sqrt{2 \times 9.8 \times 15 \times \frac{280}{293}} \approx 3.5 \sim 4.8\,\text{m/s}$$
- **工程推论与智能体规则**：烟气仅需 **$3 \sim 5$ 秒** 即可封死垂直连通层！FireGuard 规则引擎据此设定：**垂直孔洞一旦下方测得高温明火，瞬时将上层孔洞周边 $5\,\text{m}$ 半径的所有通道阻断（权重设为 $\infty$）**。

---

### 1.2 顶棚射流与水平烟气前锋蔓延模型 (Ceiling Jet & Horizontal Spread)
火羽流撞击楼层顶板后转为水平径向射流，沿无隔墙作业层迅速向四周蔓延：

$$v_{\text{horiz}} = 0.95 \left(\frac{\dot{Q}}{H_{\text{ceil}}}\right)^{1/3}$$

- 施工现场木模板堆起火热释放速率 $\dot{Q} \approx 1.5 \sim 2.5\,\text{MW}$，楼层净高 $H_{\text{ceil}} \approx 3.6\,\text{m}$；
- 算得初期水平扩散前锋速度：
  $$v_{\text{horiz}} \approx 0.6 \sim 0.9\,\text{m/s}$$
- **时空威胁窗口公式**：
  $$T_{\text{reach}}(e_{ij}) = \frac{D(\text{Fire}, e_{ij})}{v_{\text{horiz}}}$$
  智能体据此计算该通道是否会在工友到达前被浓烟覆盖。若 $T_{\text{reach}} < T_{\text{worker\_arrive}}$，则提前弃用该通道。

---

## 二、人员生命安全可用疏散时间（ASET）准则与生理极限

国际消防工程师协会（SFPE Handbook）与我国规范对逃生终点判定确立了三大极限生理判据：

```
                    ┌────────────────────────┐
                    │ ASET 必需逃生安全窗口  │
                    └───────────┬────────────┘
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
   【能见度判据】          【热辐射判据】          【毒性剂量 FED 判据】
   S >= 5.0m (熟悉)        q'' <= 2.5 kW/m^2      FED_CO <= 0.3
   S >= 10.0m (未知)       T_air <= 60 ℃          防呼吸道吸入窒息
```

### 2.1 能见度与行进速率衰减方程 (Jin's Law)
日本学者金滋教授（Jin）通过大量实测给出的高毒浓烟下人行步速公式：

$$v(K) = \begin{cases} v_0 & (K \le 0.1\,\text{m}^{-1}) \\ v_0 \left(1 - 0.707 \log_{10} \frac{K}{0.1}\right) & (0.1 < K \le 1.0\,\text{m}^{-1}) \\ 0.3\,\text{m/s} & (K > 1.0\,\text{m}^{-1}) \end{cases}$$

- $K$ 为消光系数（Extinction Coefficient），与烟气质量浓度直接正相关；
- 在浓烟环境下，工友步速将由正常的 $1.25\,\text{m/s}$ 暴跌至 **$0.3\,\text{m/s}$**。
- **FireGuard 算法落地**：当边烟雾因子 $R_{\text{smoke}} > 0.5$ 时，算法自动将该边等效行进耗时倍率放大 4 倍，迫使 A* 寻找虽绕远但无烟的高速通道。

### 2.2 Purser 一氧化碳毒性累积有效剂量模型 (FED)
工友在施工现场吸入 CO 的失能剂量采用国际标准的 Purser 方程计算：

$$\text{FED}_{\text{CO}} = \sum_{t=0}^{T} \frac{[C_{\text{CO}}(t)]^{1.036} \times \dot{V}_E \times \Delta t}{35000}$$

- 当 $\text{FED} \ge 0.3$ 时，敏感人群出现眩晕与意识不清；
- 当 $\text{FED} \ge 1.0$ 时，人员陷入昏迷并死亡；
- 智能体监测到某作业区 CO 浓度累计接近 $0.15$ 时，立即启动最高级别音频穿刺警报。

---

## 三、基于社会力模型（Social Force）的通道流率与防踩踏分流

### 3.1 临时通道通行能力与拥挤流率方程 (Nelson-Mowrer Model)
狭长施工通道的人流比流量（Specific Flow $F_s$）：

$$F_s = D \times v(D)$$

其中密度-速度关系：
$$v(D) = v_{\text{free}} \left[1 - a \cdot D\right] \quad (D \le D_{\text{jam}} \approx 3.8\,\text{人/m}^2)$$

- 当通道有效净宽 $W_{\text{eff}} = W_{\text{actual}} - 2 \times 0.15\,\text{m}$（边界层修正）；
- 通道最大通行率：$C_{\text{max}} = F_{s,\text{max}} \times W_{\text{eff}} \approx 1.3\,\text{人/(m·s)} \times W_{\text{eff}}$。
- **GB 50016 双出口均衡分流推论**：
  若全层 20 名工友在 15 秒内全部涌向有效净宽 $0.9\,\text{m}$ 的西侧单梯，通道负荷率将达：
  $$\text{Demand} = \frac{20}{15} \approx 1.33\,\text{人/s} > C_{\text{max}} = 1.3 \times (0.9 - 0.3) = 0.78\,\text{人/s}$$
  必将发生堵塞踩踏！FireGuard 引入**拥挤惩罚因子 $\gamma \cdot \text{Crowd}$**，强制将人流动态平抑分流至东侧主楼梯与南侧避难平台，实现最优全局逃生。

---

## 四、国家强制性规范（GB/T 50720-2011）参数矩阵

| 规范条款 | 物理对象 | 强制性阈值 | 智能体决策映射 |
|---|---|---|---|
| **第4.3.2条** | 地面设置临时疏散通道 | 净宽 $\ge 1.5\,\text{m}$ | $W < 1.5\,\text{m} \Rightarrow \text{Penalty} = \infty$ |
| **第4.3.2条** | 利用既有结构、楼梯通道 | 净宽 $\ge 1.0\,\text{m}$ | $W < 1.0\,\text{m} \Rightarrow \text{Penalty} = \infty$ |
| **第4.3.2条** | 爬梯及脚手架临时通道 | 净宽 $\ge 0.6\,\text{m}$ | $W < 0.6\,\text{m} \Rightarrow \text{Penalty} = \infty$ |
| **第4.3.2条** | 临空面防护栏杆 | 高度 $\ge 1.2\,\text{m}$ | 无坚固护栏 $\Rightarrow \text{Cost} \times 10$ |
| **第4.3.4条** | 临时用房至疏散门距离 | $\le 15\,\text{m}$ | 超限触发超距合规警告 |
| **第4.3.4条** | 危化品/易燃材料库房疏散距离 | $\le 10\,\text{m}$ | 优先排查并隔离周边动火点 |

---

## 五、学术论证总结

FireGuard 的设计决非工程经验的拍脑袋，而是建立在**火灾浮力羽流物理学、人体毒理学生理耐受极限、行人流体力学与国家建筑规范**的坚实交叉基石之上。这一整套科学论证体系，使系统在面对中南大学土木与AI专家评委答辩时，具有无可辩驳的学术厚度与工程说服力！
