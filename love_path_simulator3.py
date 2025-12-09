import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
from scipy import interpolate
from scipy.signal import find_peaks
from matplotlib.lines import Line2D
from collections import defaultdict

# 设置中文字体
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# ========== 1. 事件生成词典 ==========
EVENT_TEMPLATES = {
    'growth_spurt': {
        'high_devotion': [
            "🚀 坚定地朝着目标前进，每一步都更加确信。",
            "📈 在持续的投入中，突然感受到了清晰的进步。",
            "💪 执着终于开花结果，理解有了质的飞跃。"
        ],
        'high_volatility': [
            "⚡ 一场激烈的交流后，反而让关系突破了瓶颈。",
            "🌪️ 在危机中被迫做出的选择，带来了意想不到的成长。",
            "🔥 冲突的余温中，反而看清了什么是真正重要的。"
        ],
        'high_discipline': [
            "🏗️ 日复一日的坚持，终于在这一刻看到了质变。",
            "🔄 通过有计划的努力，达到了一个重要的里程碑。",
            "🧱 稳定的积累在这一刻凝聚为深刻的理解。"
        ],
        'default': [
            "✨ 感受到了明显的进步，对爱的理解又深了一层。",
            "🌱 在这一刻，以前的困惑突然变得清晰。",
            "🎯 离本质的爱又近了一步。"
        ]
    },
    
    'peak': {
        'high': [
            "🏔️ 达到了一个理解的高峰，视野从未如此开阔。",
            "🌟 在这一刻，感觉自己真正理解了什么是爱。"
        ],
        'medium': [
            "⛰️ 在一个平静的时刻，感受到了关系的完满。",
            "💫 日常中的小确幸，累积成了大的满足感。"
        ]
    },
    
    'valley': {
        'high_discipline': [
            "🛡️ 面对挫折，依靠纪律和理性保持稳定，在痛苦中反思。",
            "⚖️ 在危机中，没有逃避，而是选择了面对和解决。"
        ],
        'high_volatility': [
            "🌀 情绪剧烈波动，一切都陷入混乱，但也打破了旧的模式。",
            "🌊 在痛苦的漩涡中挣扎，反而触底反弹。"
        ],
        'high_devotion': [
            "💔 即使在低谷中，对目标的执着也从未动摇。",
            "🕳️ 黑暗的时刻反而坚定了最初的信念。"
        ],
        'default': [
            "🌑 经历了一段艰难的时期，但也在其中学习。",
            "🪨 遇到了障碍，不得不停下来重新思考。"
        ]
    },
    
    'turning_point': {
        'positive': [
            "🔄 想法发生了根本性的转变，走上了新的道路。",
            "🧭 重新校准了方向，对爱有了不同的理解。"
        ],
        'negative': [
            "⚠️ 开始怀疑之前的道路，进入了反思期。",
            "❓ 原有的理解被动摇，需要寻找新的答案。"
        ]
    },
    
    'awakening': {
        'default': [
            "💡 顿悟时刻！所有散落的片段突然连接起来。",
            "⚡ 一道闪电划破夜空，终于明白了这一切的意义。",
            "🔗 在某一瞬间，过去的所有经历都有了新的解释。"
        ]
    }
}

# ========== 2. 结局描述词典 ==========
ENDING_TEMPLATES = {
    '圆满抵达': [
        "🎉 成功抵达了本质之爱，所有的旅程都有了意义。",
        "🌟 在终点回首，发现每一步都是必要的。",
        "✨ 终于明白了，爱不是目标，而是整个旅程本身。",
        "🏁 抵达终点，却发现终点只是一个新的起点。"
    ],
    '基本理解': [
        "📚 对爱有了较深的理解，但知道还有更多等待探索。",
        "🌄 看到了爱的轮廓，但细节仍需慢慢体会。",
        "🧭 找到了方向，但道路依然漫长。"
    ],
    '部分领悟': [
        "🌱 有所领悟，但仍有许多困惑在心头。",
        "🔍 看清了一些片段，但整体画面依然模糊。",
        "🌀 在探索中前进，时而清晰，时而迷茫。"
    ],
    '未能抵达': [
        "🌀 旅程结束了，但答案仍在迷雾中。",
        "🕳️ 付出了很多，但似乎仍在原地打转。",
        "❓ 也许爱的本质本就不是可以抵达的地方。",
        "🌫️ 在迷雾中徘徊，最终接受了有些问题没有答案。"
    ]
}

# ========== 3. 核心模型类 ==========
class LovePathSimulator:
    def __init__(self, params):
        self.params = params
        self.time_points = None
        self.path_values = None
        self.events = []
        self.path_type = params['path_type']
        
    def generate_path(self):
        if self.path_type == 'continuous':
            self._generate_continuous_path()
        else:
            self._generate_discrete_path()
        
        self.events = self._extract_events_from_path()
        
    def _generate_continuous_path(self):
        num_points = 200
        self.time_points = np.linspace(0, 1, num_points)
        
        # 基础趋势
        base = np.linspace(0, 1, num_points) ** (1 / max(0.1, self.params['convergence_speed']))
        
        # 添加波动
        volatility = self.params['volatility']
        if volatility > 0:
            # 随机波动
            np.random.seed(int(random.random() * 1000))
            random_walk = np.cumsum(np.random.randn(num_points) * 0.05)
            random_walk = random_walk - random_walk[0]
            random_walk = random_walk / (np.max(np.abs(random_walk)) + 1e-6) * volatility
            
            # 添加一些尖峰波动（模拟重大事件）
            spike_positions = np.random.choice(num_points, size=int(volatility * 5), replace=False)
            for pos in spike_positions:
                spike = np.zeros(num_points)
                spike_width = int(num_points * 0.05)
                start = max(0, pos - spike_width)
                end = min(num_points, pos + spike_width)
                spike[start:end] = np.random.normal(0, volatility * 0.5, end-start)
                random_walk += spike
            
            combined = base + random_walk * 0.5
        else:
            combined = base
        
        # 应用纪律性
        discipline = self.params.get('discipline', 0.5)
        if discipline > 0:
            from scipy.ndimage import gaussian_filter1d
            combined = gaussian_filter1d(combined, sigma=10 * discipline)
        
        # 确保范围，但不强制达到1
        self.path_values = np.clip(combined, 0, 0.98)
        
    def _generate_discrete_path(self):
        num_events = max(8, int(self.params.get('num_events', 15)))
        self.time_points = np.sort(np.random.rand(num_events))
        self.time_points[0] = 0
        self.time_points[-1] = 1
        
        self.path_values = np.zeros(num_events)
        self.path_values[0] = np.random.uniform(0, 0.2)
        
        # 顿悟点
        awakening_idx = int(num_events * self.params.get('awakening_threshold', 0.7))
        
        # 顿悟前的随机漫步
        for i in range(1, awakening_idx):
            change = np.random.uniform(-0.3, 0.4) * (1 - self.params['devotion']) * 0.3
            change += np.random.uniform(0, 0.15) * self.params['devotion']
            self.path_values[i] = np.clip(self.path_values[i-1] + change, 0, 0.7)
            
            if random.random() < self.params['volatility'] * 0.4:
                jump = np.random.uniform(-0.3, 0.3) * self.params['volatility']
                self.path_values[i] = np.clip(self.path_values[i] + jump, 0, 0.7)
        
        # 顿悟时刻
        if awakening_idx < num_events:
            awakening_boost = np.random.uniform(0.3, 0.5) * self.params['devotion']
            self.path_values[awakening_idx] = np.clip(
                self.path_values[awakening_idx-1] + awakening_boost, 0, 0.9
            )
            
            # 顿悟后收敛，但不保证达到1
            remaining = num_events - awakening_idx - 1
            if remaining > 0:
                # 计算最终抵达概率
                final_value_probability = (
                    self.params['devotion'] * 0.7 +          # 执着度贡献
                    min(1.0, self.params['volatility'] * 2) * 0.2 +  # 适当波动有帮助
                    (self.params.get('awakening_threshold', 0.7) < 0.8) * 0.1  # 不太晚顿悟
                )
                
                # 顿悟后有足够时间发展
                if num_events - awakening_idx > 3:
                    final_value_base = 0.7 + random.uniform(0, 0.3) * final_value_probability
                else:
                    # 顿悟太晚，发展时间不足
                    final_value_base = 0.5 + random.uniform(0, 0.3) * final_value_probability
                
                # 添加一些随机性
                final_value = min(0.98, max(0.1, final_value_base + random.uniform(-0.1, 0.1)))
                
                # 如果是极低参数，可能完全失败
                if (self.params['devotion'] < 0.2 and 
                    self.params['volatility'] < 0.2 and 
                    random.random() > 0.7):
                    final_value = random.uniform(0, 0.3)  # 彻底失败
                
                # 生成顿悟后的路径
                final_values = np.linspace(self.path_values[awakening_idx], final_value, remaining + 1)
                self.path_values[awakening_idx+1:] = final_values[1:]
        
        # 如果没有顿悟，直接计算最终值
        if awakening_idx >= num_events:
            # 计算最终抵达概率（无顿悟情况）
            final_value_probability = self.params['devotion'] * 0.5 + self.params['volatility'] * 0.1
            final_value = random.uniform(0.2, 0.6) * final_value_probability
            
            # 极低参数可能失败
            if (self.params['devotion'] < 0.2 and 
                self.params['volatility'] < 0.2 and 
                random.random() > 0.5):
                final_value = random.uniform(0, 0.2)
            
            self.path_values[-1] = final_value
        
        # 确保不超过0.98
        self.path_values[-1] = min(0.98, self.path_values[-1])
    
    def _extract_events_from_path(self):
        """从路径特征中提取关键事件"""
        if self.path_values is None or len(self.path_values) < 10:
            return []
        
        events = []
        
        # 1. 计算导数
        derivatives = np.gradient(self.path_values, self.time_points)
        
        # 2. 找增长爆发点（斜率最大的地方）
        if len(derivatives) > 0:
            max_growth_idx = np.argmax(derivatives)
            if derivatives[max_growth_idx] > 0.2:
                growth_desc = self._generate_event_description(
                    'growth_spurt', 
                    intensity=derivatives[max_growth_idx]
                )
                events.append({
                    'time': float(self.time_points[max_growth_idx]),
                    'value': float(self.path_values[max_growth_idx]),
                    'type': 'growth_spurt',
                    'intensity': float(derivatives[max_growth_idx]),
                    'description': growth_desc
                })
        
        # 3. 找峰值
        peaks, properties = find_peaks(self.path_values, height=0.3, distance=len(self.time_points)//10)
        for idx in peaks[:3]:  # 最多3个峰值
            height = self.path_values[idx]
            desc_type = 'high' if height > 0.7 else 'medium'
            peak_desc = random.choice(EVENT_TEMPLATES['peak'][desc_type])
            events.append({
                'time': float(self.time_points[idx]),
                'value': float(height),
                'type': 'peak',
                'height': float(height),
                'description': peak_desc
            })
        
        # 4. 找低谷（对连续路径特别重要）
        valleys, _ = find_peaks(-self.path_values, height=-0.5, distance=len(self.time_points)//10)
        for idx in valleys[:2]:  # 最多2个低谷
            depth = self.path_values[idx]
            valley_desc = self._generate_event_description('valley', depth=depth)
            events.append({
                'time': float(self.time_points[idx]),
                'value': float(depth),
                'type': 'valley',
                'depth': float(depth),
                'description': valley_desc
            })
        
        # 5. 对于离散路径，检测顿悟点（平衡版）
        if self.path_type == 'discrete':
            jumps = np.diff(self.path_values)
            if len(jumps) > 0:
                max_jump_idx = np.argmax(jumps)
                max_jump = jumps[max_jump_idx]
                
                # ========== 平衡的顿悟检测 ==========
                # 条件1：必须在顿悟阈值之后（但允许稍早一点）
                awakening_threshold = self.params.get('awakening_threshold', 0.7)
                min_awakening_idx = int(len(self.time_points) * max(0.5, awakening_threshold - 0.2))
                
                if max_jump_idx < min_awakening_idx:
                    # 跳跃发生在合理区间前，不算顿悟
                    pass
                else:
                    # 条件2：相对显著性或绝对显著性满足一项即可
                    avg_jump = np.mean(np.abs(jumps))
                    
                    # 动态阈值：基于参数调整
                    base_threshold = 0.2  # 稍微降低绝对阈值
                    
                    # 执着度越高，越容易顿悟
                    devotion_factor = 1.0 - (self.params['devotion'] * 0.3)  # 0.7-1.0
                    # 波动性越高，需要更大的跳跃才算是顿悟
                    volatility_factor = 1.0 + (self.params['volatility'] * 0.2)  # 1.0-1.2
                    
                    absolute_threshold = base_threshold * devotion_factor * volatility_factor
                    
                    # 相对显著性：跳跃是平均值的倍数
                    relative_significant = (avg_jump > 0.05 and 
                                          max_jump > avg_jump * 2.5)  # 降低到2.5倍
                    
                    # 绝对显著性：超过动态阈值
                    absolute_significant = max_jump > absolute_threshold
                    
                    # 两者满足其一即可，但需确保不是微小波动
                    if max_jump > 0.15 and (relative_significant or absolute_significant):
                        awakening_desc = random.choice(EVENT_TEMPLATES['awakening']['default'])
                        events.append({
                            'time': float(self.time_points[max_jump_idx + 1]),
                            'value': float(self.path_values[max_jump_idx + 1]),
                            'type': 'awakening',
                            'jump_magnitude': float(max_jump),
                            'description': awakening_desc
                        })
        
        # 6. 找转折点（二阶导数极值），但排除终点附近的平坦区域
        if len(self.path_values) > 10:
            second_derivatives = np.gradient(derivatives, self.time_points)
            
            # 排除最后20%的时间区域，因为这里可能已经到达平台期
            exclude_zone_start = int(len(self.time_points) * 0.8)
            
            # 只在前80%找转折点
            valid_indices = np.arange(len(self.time_points))[:exclude_zone_start]
            valid_curvatures = np.abs(second_derivatives[:exclude_zone_start])
            
            if len(valid_curvatures) > 5:
                turning_points, _ = find_peaks(
                    valid_curvatures,
                    height=np.std(valid_curvatures) * 1.5,
                    distance=len(self.time_points)//20
                )
                
                for idx in turning_points[:2]:  # 最多2个转折点
                    # 额外检查：不能太靠近已经很高的区域
                    if self.path_values[idx] > 0.9:
                        continue  # 跳过已经接近终点的转折
                        
                    curvature = second_derivatives[idx]
                    desc_type = 'positive' if curvature > 0 else 'negative'
                    turning_desc = random.choice(EVENT_TEMPLATES['turning_point'][desc_type])
                    events.append({
                        'time': float(self.time_points[idx]),
                        'value': float(self.path_values[idx]),
                        'type': 'turning_point',
                        'curvature': float(curvature),
                        'description': turning_desc
                    })
        
        # 7. 按时间排序并选择最重要的6个事件
        events.sort(key=lambda x: x['time'])
        
        # 优先保留重要事件类型
        event_priority = {'awakening': 4, 'growth_spurt': 3, 'valley': 2, 'peak': 1, 'turning_point': 1}
        if len(events) > 6:
            events.sort(key=lambda x: event_priority.get(x['type'], 0), reverse=True)
            events = events[:6]
            events.sort(key=lambda x: x['time'])
        
        # 8. 添加结局事件
        summary = self.get_path_summary()
        ending_desc = random.choice(ENDING_TEMPLATES.get(summary['ending_type'], ["旅程结束。"]))
        events.append({
            'time': 1.0,
            'value': float(self.path_values[-1]),
            'type': 'ending',
            'description': f"【{summary['ending_type']}】{ending_desc}",
            'final_value': float(self.path_values[-1])
        })
        
        return events
    
    def _generate_event_description(self, event_type, **kwargs):
        """根据参数生成事件描述"""
        if event_type == 'growth_spurt':
            intensity = kwargs.get('intensity', 0.5)
            if self.params['devotion'] > 0.8:
                key = 'high_devotion'
            elif self.params['volatility'] > 0.6:
                key = 'high_volatility'
            elif self.params.get('discipline', 0) > 0.7:
                key = 'high_discipline'
            else:
                key = 'default'
            
            desc = random.choice(EVENT_TEMPLATES['growth_spurt'][key])
            if intensity > 0.8:
                desc = "💥 " + desc
            elif intensity > 0.5:
                desc = "🚀 " + desc
            return desc
            
        elif event_type == 'valley':
            depth = kwargs.get('depth', 0.5)
            depth_level = "轻微挫折" if depth > 0.4 else "中度危机" if depth > 0.2 else "重大危机"
            
            if self.params.get('discipline', 0) > self.params.get('volatility', 0):
                style = 'high_discipline'
            elif self.params['volatility'] > 0.5:
                style = 'high_volatility'
            elif self.params['devotion'] > 0.7:
                style = 'high_devotion'
            else:
                style = 'default'
            
            desc = random.choice(EVENT_TEMPLATES['valley'][style])
            return f"【{depth_level}】{desc}"
        
        return "发生了一个重要事件。"
    
    def get_path_summary(self):
        if self.path_values is None:
            return {}
        
        final_value = float(self.path_values[-1])
        
        # 判断结局类型
        if final_value > 0.9:
            ending_type = "圆满抵达"
            ending_desc = "成功理解了本质之爱"
        elif final_value > 0.7:
            ending_type = "基本理解" 
            ending_desc = "对爱有了较深的理解，但尚未完全抵达"
        elif final_value > 0.4:
            ending_type = "部分领悟"
            ending_desc = "有所领悟，但仍有困惑"
        else:
            ending_type = "未能抵达"
            ending_desc = "仍在探索中，未能真正理解爱的本质"
        
        awakening_event = next((e for e in self.events if e['type'] == 'awakening'), None)
        
        return {
            'final_value': final_value,
            'ending_type': ending_type,
            'ending_desc': ending_desc,
            'avg_growth': float(np.mean(np.diff(self.path_values))),
            'volatility_measured': float(np.std(np.diff(self.path_values))),
            'awakening_point': awakening_event,
            'event_count': len([e for e in self.events if e['type'] != 'ending']),  # 不包含结局事件
            'event_types': [e['type'] for e in self.events if e['type'] != 'ending']
        }

# ========== 4. 可视化函数 ==========
def plot_path_with_emergent_events(ax, time_points, path_values, events, path_type):
    """绘制带有涌现事件的路径"""
    
    # 绘制路径
    if path_type == 'continuous':
        ax.plot(time_points, path_values, color='#2E86AB', linewidth=3, alpha=0.8, 
                label='连续之爱', zorder=5)
    else:
        ax.plot(time_points, path_values, color='#E15554', linewidth=2, 
                linestyle=':', alpha=0.6, zorder=6)
        ax.scatter(time_points, path_values, color='#E15554', s=80, 
                  alpha=0.8, zorder=7, label='离散之爱')
    
    # 事件标记样式（添加结局样式）
    event_styles = {
        'growth_spurt': {'marker': '^', 'color': '#4CAF50', 'size': 120},
        'peak': {'marker': 'o', 'color': '#FFC107', 'size': 110},
        'valley': {'marker': 'v', 'color': '#F44336', 'size': 120},
        'turning_point': {'marker': 's', 'color': '#9C27B0', 'size': 100},
        'awakening': {'marker': '*', 'color': '#FF9800', 'size': 160},
        'ending': {'marker': 'D', 'color': '#2E86AB', 'size': 140}  # 菱形表示结局
    }
    
    # 绘制事件点（排除结局事件，因为已经标了终点B）
    for i, event in enumerate(events):
        if event['type'] == 'ending':
            continue  # 跳过结局事件，因为终点B已经表示了
        
        style = event_styles.get(event['type'], {'marker': 'o', 'color': '#666', 'size': 90})
        
        ax.scatter(event['time'], event['value'],
                  marker=style['marker'],
                  color=style['color'],
                  s=style['size'],
                  edgecolors='white',
                  linewidth=2,
                  zorder=15,
                  alpha=0.9)
        
        # 智能标注避免重叠
        offset_x = 0.03 if i % 2 == 0 else -0.03
        offset_y = 0.04 if i % 3 == 0 else -0.04
        
        # 为重要事件添加简短标注
        if event['type'] in ['awakening', 'growth_spurt']:
            label = event['type'][:3].upper()
            ax.annotate(label,
                       xy=(event['time'], event['value']),
                       xytext=(event['time'] + offset_x, event['value'] + offset_y),
                       fontsize=9,
                       fontweight='bold',
                       color=style['color'],
                       arrowprops=dict(arrowstyle='->', color=style['color'], alpha=0.6))
    
    # 绘制A点和B点
    ax.scatter(0, 0, color='#4A4A4A', s=200, zorder=20, marker='s', 
              edgecolors='white', linewidth=2, label='起点 (A)')
    
    # 根据最终值确定终点颜色
    final_value = path_values[-1]
    if final_value > 0.9:
        b_color = '#4CAF50'  # 绿色：圆满抵达
    elif final_value > 0.7:
        b_color = '#FFC107'  # 黄色：基本理解
    elif final_value > 0.4:
        b_color = '#FF9800'  # 橙色：部分领悟
    else:
        b_color = '#F44336'  # 红色：未能抵达
    
    ax.scatter(1, final_value, color=b_color, s=300, zorder=20, marker='*', 
              edgecolors='white', linewidth=2, label='终点 (B)')
    
    # 设置坐标轴
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('时间进程', fontsize=12, fontweight='medium')
    ax.set_ylabel('爱的领悟', fontsize=12, fontweight='medium')
    
    # 添加终点值标注
    ax.annotate(f'{final_value:.2f}', xy=(1, final_value), xytext=(0.95, final_value + 0.05),
                fontsize=10, fontweight='bold', color=b_color,
                arrowprops=dict(arrowstyle='->', color=b_color, alpha=0.6))
    
    # 添加网格
    ax.grid(True, alpha=0.2, linestyle='--')
    
    # 创建图例
    legend_elements = []
    if path_type == 'continuous':
        legend_elements.append(Line2D([0], [0], color='#2E86AB', lw=3, label='连续之爱'))
    else:
        legend_elements.append(Line2D([0], [0], color='#E15554', lw=2, 
                                     linestyle=':', label='离散之爱'))
    
    # 添加事件图例（排除结局）
    for event_type, style in event_styles.items():
        if event_type == 'ending':
            continue
        legend_elements.append(
            Line2D([0], [0], marker=style['marker'], color='w',
                  markerfacecolor=style['color'], markersize=8,
                  label=event_type.replace('_', ' ').title())
        )
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, 
             frameon=True, framealpha=0.9)
    
    # 标题
    title = '连续之爱路径' if path_type == 'continuous' else '离散之爱路径'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

# ========== 5. Streamlit应用主函数 ==========
def main():
    st.set_page_config(
        page_title="Love in the Era of All Plagues, 或《霍乱时期的爱情》模拟器",
        page_icon="💘",
        layout="wide"
    )
    
    # 初始化session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    st.title("💘 Love in the Era of All Plagues, 或《霍乱时期的爱情》模拟器")
    st.markdown("探索从「俗世的个体(A)」到「本质的爱(B)」的无限可能路径。如果你是乌尔比诺医生/弗洛伦蒂诺·阿里萨，你会走向圆满的结局吗")
    
    # 侧边栏：参数控制
    with st.sidebar:
        st.header("🎛️ 参数设置")
        
        # 路径类型
        path_type = st.radio(
            "路径类型:",
            ["continuous", "discrete"],
            format_func=lambda x: "连续之爱(医生式)" if x == "continuous" else "离散之爱(男主式)"
        )
        
        st.subheader("核心参数")
        devotion = st.slider("执着度", 0.0, 1.0, 0.7, 0.05,
                           help="对本质之爱的追求强度")
        volatility = st.slider("人生波动", 0.0, 1.0, 0.4, 0.05,
                             help="经历的戏剧性和变化幅度")
        
        # 路径特定参数
        if path_type == 'continuous':
            convergence_speed = st.slider("收敛速度", 0.1, 3.0, 1.0, 0.1,
                                        help="抵达本质之爱的速度")
            discipline = st.slider("纪律性", 0.0, 1.0, 0.6, 0.05,
                                 help="路径的平滑与克制程度")
            params = {
                'path_type': path_type,
                'devotion': devotion,
                'volatility': volatility,
                'convergence_speed': convergence_speed,
                'discipline': discipline
            }
        else:
            num_events = st.slider("经历数量", 8, 40, 15, 1,
                                 help="离散经历的数量")
            awakening_threshold = st.slider("顿悟阈值", 0.1, 0.9, 0.7, 0.05,
                                          help="触发顿悟的时间点")
            params = {
                'path_type': path_type,
                'devotion': devotion,
                'volatility': volatility,
                'num_events': num_events,
                'awakening_threshold': awakening_threshold
            }
        
        # 生成按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ 生成新路径", type="primary", use_container_width=True):
                simulator = LovePathSimulator(params)
                simulator.generate_path()
                st.session_state.simulator = simulator
                
                # 保存历史
                summary = simulator.get_path_summary()
                st.session_state.history.append({
                    'params': params.copy(),
                    'summary': summary,
                    'timestamp': np.datetime64('now')
                })
                st.rerun()
        
        with col2:
            if st.button("🔄 重置历史", type="secondary", use_container_width=True):
                st.session_state.history = []
                st.rerun()
    
    # 主内容区
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if 'simulator' in st.session_state:
            simulator = st.session_state.simulator
            
            # 绘制图表
            fig, ax = plt.subplots(figsize=(10, 6))
            plot_path_with_emergent_events(ax, 
                                         simulator.time_points,
                                         simulator.path_values,
                                         simulator.events,
                                         simulator.path_type)
            
            st.pyplot(fig)
            plt.close(fig)
            
            # 路径统计和结局显示
            with st.expander("📊 路径统计与结局", expanded=True):
                summary = simulator.get_path_summary()
                
                # 显示结局信息
                cols = st.columns([1, 2])
                with cols[0]:
                    # 根据结局类型选择表情符号
                    if summary['ending_type'] == '圆满抵达':
                        emoji = "🎉"
                    elif summary['ending_type'] == '基本理解':
                        emoji = "📚"
                    elif summary['ending_type'] == '部分领悟':
                        emoji = "🌱"
                    else:
                        emoji = "🌀"
                    
                    st.metric(f"{emoji} 结局", 
                             summary['ending_type'], 
                             delta=f"最终值: {summary['final_value']:.2f}")
                with cols[1]:
                    st.caption(summary['ending_desc'])
                
                # 统计指标
                cols = st.columns(4)
                cols[0].metric("平均增长", f"{summary['avg_growth']:.3f}")
                cols[1].metric("波动性", f"{summary['volatility_measured']:.3f}")
                cols[2].metric("事件数", summary['event_count'])
                cols[3].metric("执着度", f"{simulator.params['devotion']:.2f}")
        else:
            st.info("👈 请在侧边栏设置参数并点击「生成新路径」")
            # 显示示例参数建议
            with st.expander("💡 参数建议", expanded=False):
                st.markdown("""
                **连续之爱（医生式）推荐参数：**
                - 执着度：0.7-0.9
                - 纪律性：0.6-0.8
                - 收敛速度：1.0-1.5
                
                **离散之爱（男主式）推荐参数：**
                - 执着度：0.5-0.7
                - 波动性：0.4-0.7
                - 顿悟阈值：0.6-0.8
                """)
    
    with col2:
        if 'simulator' in st.session_state:
            st.subheader("📖 关键事件时间线")
            
            # 分离结局事件和其他事件
            ending_event = None
            other_events = []
            for event in simulator.events:
                if event['type'] == 'ending':
                    ending_event = event
                else:
                    other_events.append(event)
            
            # 先显示过程事件
            for i, event in enumerate(other_events):
                # 事件颜色
                event_colors = {
                    'growth_spurt': '#4CAF50',
                    'peak': '#FFC107',
                    'valley': '#F44336',
                    'turning_point': '#9C27B0',
                    'awakening': '#FF9800'
                }
                
                with st.container():
                    # 事件头
                    event_header = f"**{i+1}. {event['type'].replace('_', ' ').title()}**"
                    if 'intensity' in event:
                        event_header += f" (强度: {event['intensity']:.2f})"
                    elif 'depth' in event:
                        event_header += f" (深度: {event['depth']:.2f})"
                    elif 'jump_magnitude' in event:
                        event_header += f" (跳跃: {event['jump_magnitude']:.2f})"
                    
                    st.markdown(f"<h4 style='color:{event_colors.get(event['type'], '#666')}'>{event_header}</h4>", 
                               unsafe_allow_html=True)
                    
                    # 事件内容
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(event['description'])
                    with col_b:
                        st.caption(f"时间: {event['time']:.2f}")
                        st.caption(f"值: {event['value']:.2f}")
                    
                    st.divider()
            
            # 最后显示结局事件
            if ending_event:
                with st.container():
                    # 根据最终值确定颜色
                    final_value = ending_event['final_value']
                    if final_value > 0.9:
                        color = '#4CAF50'
                        emoji = "🎉"
                    elif final_value > 0.7:
                        color = '#FFC107'
                        emoji = "📚"
                    elif final_value > 0.4:
                        color = '#FF9800'
                        emoji = "🌱"
                    else:
                        color = '#F44336'
                        emoji = "🌀"
                    
                    st.markdown(f"<h4 style='color:{color}'>{emoji} 结局：{ending_event['description'].split('】')[0][1:]}</h4>", 
                               unsafe_allow_html=True)
                    
                    st.write(ending_event['description'].split('】')[1])
                    st.caption(f"时间: {ending_event['time']:.1f}")
                    st.caption(f"最终值: {final_value:.2f}")
    
    # 历史记录
    with st.expander("📜 生成历史（最近3次）", expanded=False):
        if st.session_state.history:
            for i, record in enumerate(reversed(st.session_state.history[-3:])):
                idx = len(st.session_state.history) - i
                with st.container():
                    cols = st.columns([3, 2, 1])
                    with cols[0]:
                        st.write(f"**记录 #{idx}**")
                        path_type_name = "连续" if record['params']['path_type'] == 'continuous' else "离散"
                        st.write(f"类型: {path_type_name}之爱")
                        st.write(f"结局: {record['summary']['ending_type']}")
                    with cols[1]:
                        st.write(f"执着度: {record['params']['devotion']:.2f}")
                        st.write(f"最终值: {record['summary']['final_value']:.2f}")
                    with cols[2]:
                        if st.button("加载", key=f"load_{idx}", use_container_width=True):
                            simulator = LovePathSimulator(record['params'])
                            simulator.generate_path()
                            st.session_state.simulator = simulator
                            st.rerun()
                    st.divider()
        else:
            st.write("暂无历史记录")
    
    # 模型说明
    with st.expander("ℹ️ 模型说明", expanded=False):
        st.markdown("""
        ### 🎯 事件类型说明
        
        **增长爆发 (Growth Spurt)**
        - 路径斜率最大的时刻
        - 代表理解上的快速突破
        - 强度由执着度和纪律性共同决定
        
        **峰值 (Peak)**
        - 路径的局部最大值
        - 代表阶段性的完满或深刻理解
        - 高波动性路径会有更多峰值
        
        **低谷 (Valley)**
        - 路径的局部最小值
        - 代表挫折、危机或困惑期
        - 纪律性决定低谷后的恢复速度
        
        **转折点 (Turning Point)**
        - 路径曲率变化最大的点
        - 代表思维方式或理解方向的变化
        - 排除终点附近的平坦区域
        
        **顿悟时刻 (Awakening)**
        - 仅出现在离散路径
        - 代表所有离散经验突然被连接理解
        - 由顿悟阈值参数控制发生时间
        - 需要满足多重条件（时间、相对大小、绝对阈值）
        
        **结局 (Ending)**
        - 路径的最终状态
        - 四种结局类型：圆满抵达、基本理解、部分领悟、未能抵达
        
        ### ⚙️ 参数影响
        
        - **执着度**: 提高增长爆发的可能性和强度，增加成功抵达的概率
        - **纪律性**: 平滑路径，减少低谷深度，促进稳定增长
        - **波动性**: 增加峰值和低谷数量，创造更多转折机会
        - **顿悟阈值**: 控制顿悟时刻的发生时机，太晚可能无法充分发展
        
        ### 🎨 可视化说明
        
        - **终点颜色**: 根据结局类型变化（绿→圆满，黄→基本，橙→部分，红→失败）
        - **事件标记**: 不同形状表示不同事件类型
        - **终点B的位置**: 根据最终值决定，不一定在y=1的位置
        
        ### 💡 新特性
        
        1. **动态结局系统**: 路径不一定达到1，可能有多种结局
        2. **智能顿悟检测**: 防止虚假顿悟，平衡检测条件
        3. **终点区域优化**: 避免将平台期误判为转折点
        4. **结局事件**: 路径结束时添加有意义的结局描述
        5. **历史记录**: 保存最近3次模拟参数和结果
        """)

if __name__ == "__main__":
    main()