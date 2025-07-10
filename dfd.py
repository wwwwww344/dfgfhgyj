import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

# 设置页面配置
st.set_page_config(
    page_title="全球南方国家GDP占比分析",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 添加自定义CSS
st.markdown("""
<style>
    :root {
        --primary-color: #2E8B57;
        --background-color: #f5f5f5;
        --secondary-background-color: #e0e0e0;
        --text-color: #333333;
    }
    .main-header {
        color: var(--primary-color);
    }
    .css-18e3th9 {
        padding-top: 3rem;
        padding-bottom: 10rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .css-1d391kg {
        background-color: var(--background-color);
    }
    .css-1dp5vir {
        background-color: var(--secondary-background-color);
    }
</style>
""", unsafe_allow_html=True)

# 自定义颜色映射
color_map = LinearSegmentedColormap.from_list(
    "custom_cmap", ["#2E8B57", "#4CAF50", "#81C784", "#A5D6A7"]
)

# 标题和说明
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="color: #2E8B57; font-size: 2.5rem; animation: fadeIn 1s ease-in-out;">
        <i class="fa fa-globe"></i> 全球南方国家GDP占比动态增长趋势
    </h1>
    <p style="font-size: 1.1rem; color: #666; max-width: 800px; margin: 0 auto;">
        本看板展示了全球南方国家（发展中国家）GDP占全球总量比例的动态增长趋势。
        页面加载后将自动播放动画，展示各年份数据变化。
    </p>
</div>

<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# 从本地CSV文件读取数据
@st.cache_data
def load_data(file_path):
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检查文件是否可读
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"没有读取权限: {file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查数据是否为空
        if df.empty:
            raise ValueError("CSV文件为空")
        
        st.success(f"成功加载数据: {file_path}")
        return df
    
    except FileNotFoundError as e:
        st.error(str(e))
        return None
    except PermissionError as e:
        st.error(str(e))
        return None
    except pd.errors.ParserError as e:
        st.error(f"CSV解析错误: {str(e)}")
        return None
    except ValueError as e:
        st.error(str(e))
        return None
    except Exception as e:
        st.error(f"加载数据时出错: {str(e)}")
        return None

# 获取当前工作目录
current_dir = os.getcwd()

# 设置CSV文件路径
csv_file_path = os.path.join(current_dir, "global_south_gdp.csv")

# 加载数据
st.sidebar.markdown('## <i class="fa fa-database"></i> 数据设置', unsafe_allow_html=True)
st.sidebar.info(f"正在从以下位置读取数据:\n\n`{csv_file_path}`")

# 读取数据并检查
df = load_data(csv_file_path)

# 关键检查：确保数据成功加载
if df is None:
    st.error("无法继续执行：数据加载失败。请检查CSV文件路径和格式。")
    st.stop()

# 检查数据是否包含必要的列
required_columns = [
    "年份", 
    "全球南方国家GDP占比(%)", 
    "亚洲贡献(%)", 
    "非洲贡献(%)", 
    "拉丁美洲贡献(%)", 
    "大洋洲贡献(%)"
]

# 验证所有必要列都存在
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"CSV文件缺少必要的列: {', '.join(missing_columns)}")
    st.error("请确保CSV文件包含以下列: " + ", ".join(required_columns))
    st.stop()

# 检查必要列是否有缺失值
for col in required_columns:
    if df[col].isnull().any():
        st.warning(f"列 '{col}' 包含缺失值，可能影响分析结果")

# 添加颜色列（如果不存在）
region_colors = {
    "亚洲": "#32CD32",  # 绿色
    "非洲": "#FFA500",  # 橙色
    "拉丁美洲": "#FF6347",  # 红色
    "大洋洲": "#1E90FF"   # 蓝色
}

for region, color in region_colors.items():
    if f"{region}颜色" not in df.columns:
        df[f"{region}颜色"] = color

# 侧边栏 - 筛选和交互控件
with st.sidebar:
    st.markdown('## <i class="fa fa-sliders"></i> 筛选选项', unsafe_allow_html=True)
    
    # 区域筛选
    st.markdown('### <i class="fa fa-map-o"></i> 选择区域', unsafe_allow_html=True)
    regions = ["亚洲", "非洲", "拉丁美洲", "大洋洲"]
    selected_regions = st.multiselect(
        "显示区域",
        regions,
        default=regions,
        help="选择要在图表中显示的区域"
    )
    
    # 动画速度控制
    st.markdown('### <i class="fa fa-clock-o"></i> 动画速度', unsafe_allow_html=True)
    animation_speed = st.slider(
        "速度",
        min_value=100,
        max_value=2000,
        value=500,
        step=100,
        help="数值越小，动画速度越快"
    )
    
    # 关于部分
    st.markdown("---")
    st.markdown('## <i class="fa fa-info-circle"></i> 关于', unsafe_allow_html=True)
    st.markdown("""
    本应用展示了全球南方国家GDP占比的动态增长趋势。
    数据来源于本地CSV文件。
    
    技术栈：
    - Streamlit
    - Plotly
    - Pandas
    - NumPy
    
    最后更新：2023年
    """)

# 创建交互式动画图表
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("""
    <div class="card" style="background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 class="card-title" style="color: #2E8B57; font-size: 1.5rem; margin-bottom: 1rem;">全球南方国家GDP占比动态变化</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用graph_objects API创建动画图表
    fig = go.Figure()
    
    # 添加初始数据
    fig.add_trace(
        go.Scatter(
            x=df["年份"],
            y=df["全球南方国家GDP占比(%)"],
            mode="lines+markers",
            line=dict(color="#2E8B57", width=4, shape="spline"),
            marker=dict(size=10, color="#1F6E46", symbol="circle"),
            name="全球南方国家GDP占比(%)",
            hovertemplate="年份: %{x}<br>占比: %{y:.2f}%<extra></extra>"
        )
    )
    
    # 添加目标线
    min_value = df["全球南方国家GDP占比(%)"].min()
    max_value = df["全球南方国家GDP占比(%)"].max()
    
    fig.add_hline(
        y=min_value, line_dash="dash", 
        annotation_text=f"最低值 (~{min_value:.1f}%)",
        annotation_position="bottom right",
        line_color="#FF6347",
        annotation_font=dict(color="#FF6347")
    )
    fig.add_hline(
        y=max_value, line_dash="dash", 
        annotation_text=f"最高值 (~{max_value:.1f}%)",
        annotation_position="top right",
        line_color="#4682B4",
        annotation_font=dict(color="#4682B4")
    )
    
    # 创建动画帧
    frames = []
    for year in df["年份"].unique():
        year_data = df[df["年份"] <= year]
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=year_data["年份"],
                        y=year_data["全球南方国家GDP占比(%)"],
                        mode="lines+markers",
                        line=dict(color="#2E8B57", width=4, shape="spline"),
                        marker=dict(size=10, color="#1F6E46", symbol="circle"),
                    )
                ],
                name=str(year)
            )
        )
    
    # 更新图表布局
    fig.update_layout(
        title="全球南方国家GDP占比变化",
        xaxis_title="年份",
        yaxis_title="GDP占比(%)",
        hovermode="x unified",
        height=500,
        margin=dict(l=40, r=20, t=40, b=60),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color="#333333"),
        showlegend=False,
        # 设置动画参数
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "播放",
                "method": "animate",
                "args": [None, {
                    "frame": {"duration": animation_speed, "redraw": True},
                    "fromcurrent": True,
                    "transition": {"duration": 300, "easing": "quadratic-in-out"}
                }]
            }, {
                "label": "暂停",
                "method": "animate",
                "args": [[None], {
                    "frame": {"duration": 0, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 0}
                }]
            }],
            "direction": "left",
            "pad": {"r": 10, "t": 85},
            "x": 0.1,
            "y": 0,
            "xanchor": "right",
            "yanchor": "top"
        }],
        sliders=[{
            "active": 0,
            "steps": [{
                "args": [[f.name], {
                    "frame": {"duration": animation_speed, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300}
                }],
                "label": f.name,
                "method": "animate"
            } for f in frames],
            "x": 0.1,
            "len": 0.9,
            "xanchor": "left",
            "yanchor": "top",
            "pad": {"t": 100, "b": 10},
            "currentvalue": {
                "visible": True,
                "prefix": "年份: ",
                "xanchor": "right",
                "font": {"size": 14, "color": "#2E8B57"}
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"}
        }]
    )
    
    # 添加帧数据
    fig.frames = frames
    
    # 设置初始视图范围
    fig.update_xaxes(range=[df["年份"].min(), df["年份"].max()])
    fig.update_yaxes(range=[max(0, min_value-5), min(100, max_value+5)])
    
    # 自动播放动画
    config = {
        'displayModeBar': True,
        'scrollZoom': True,
        'responsive': True
    }
    
    # 显示图表
    try:
        st.plotly_chart(fig, use_container_width=True, config=config)
        # 使用JavaScript触发播放按钮点击事件
        st.markdown("""
        <script>
            // 等待图表加载完成
            setTimeout(() => {
                // 查找并点击播放按钮
                const playButton = document.querySelector('button[aria-label="Play"]');
                if (playButton) {
                    playButton.click();
                }
            }, 1000);
        </script>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"图表显示出错: {str(e)}")
        st.write("尝试使用静态图表替代:")
        static_fig = go.Figure()
        static_fig.add_trace(
            go.Scatter(
                x=df["年份"],
                y=df["全球南方国家GDP占比(%)"],
                mode="lines+markers",
                line=dict(color="#2E8B57", width=4, shape="spline"),
                marker=dict(size=10, color="#1F6E46", symbol="circle"),
                hovertemplate="年份: %{x}<br>占比: %{y:.2f}%<extra></extra>"
            )
        )
        static_fig.update_layout(
            title="全球南方国家GDP占比变化 (静态图)",
            xaxis_title="年份",
            yaxis_title="GDP占比(%)",
            height=500,
            margin=dict(l=40, r=20, t=40, b=60),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="sans-serif", size=12, color="#333333"),
        )
        static_fig.add_hline(
            y=min_value, line_dash="dash", 
            annotation_text=f"最低值 (~{min_value:.1f}%)",
            annotation_position="bottom right",
            line_color="#FF6347",
            annotation_font=dict(color="#FF6347")
        )
        static_fig.add_hline(
            y=max_value, line_dash="dash", 
            annotation_text=f"最高值 (~{max_value:.1f}%)",
            annotation_position="top right",
            line_color="#4682B4",
            annotation_font=dict(color="#4682B4")
        )
        st.plotly_chart(static_fig, use_container_width=True)
    
    # 数据摘要卡片
    col1_sum, col2_sum = st.columns(2)
    with col1_sum:
        st.markdown(f"""
        <div class="stat-card" style="background-color: #e8f5e9; border-radius: 8px; padding: 1rem; text-align: center;">
            <p class="stat-title" style="color: #666; font-size: 0.9rem;">起始占比 ({df["年份"].min()}年)</p>
            <p class="stat-value" style="color: #2E8B57; font-size: 1.5rem; font-weight: bold;">
                {df.iloc[0]["全球南方国家GDP占比(%)"]:.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2_sum:
        st.markdown(f"""
        <div class="stat-card" style="background-color: #e8f5e9; border-radius: 8px; padding: 1rem; text-align: center;">
            <p class="stat-title" style="color: #666; font-size: 0.9rem;">当前占比 ({df["年份"].max()}年)</p>
            <p class="stat-value" style="color: #2E8B57; font-size: 1.5rem; font-weight: bold;">
                {df.iloc[-1]["全球南方国家GDP占比(%)"]:.2f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card" style="background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 class="card-title" style="color: #2E8B57; font-size: 1.5rem; margin-bottom: 1rem;">各区域贡献动态变化</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建区域贡献动画图表
    region_columns = [f"{region}贡献(%)" for region in selected_regions]
    region_names = selected_regions
    region_colors = [df[f"{region}颜色"].iloc[0] for region in selected_regions]
    
    # 准备数据用于动画
    df_melted = pd.melt(
        df,
        id_vars=["年份"],
        value_vars=region_columns,
        var_name="区域",
        value_name="贡献(%)"
    )
    
    # 替换区域名称
    for region in regions:
        df_melted.loc[df_melted["区域"] == f"{region}贡献(%)", "区域"] = region
    
    # 创建动画条形图
    fig_regions = px.bar(
        df_melted,
        x="区域",
        y="贡献(%)",
        color="区域",
        color_discrete_sequence=region_colors,
        animation_frame="年份",
        range_y=[0, df[region_columns].max().max() * 1.1],
        template="plotly_white"
    )
    
    # 更新布局
    fig_regions.update_layout(
        xaxis_title="",
        yaxis_title="贡献比例(%)",
        hovermode="x unified",
        height=500,
        margin=dict(l=40, r=20, t=40, b=60),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color="#333333"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="rgba(255,255,255,0)"
        ),
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "播放",
                "method": "animate",
                "args": [None, {
                    "frame": {"duration": animation_speed, "redraw": True},
                    "fromcurrent": True,
                    "transition": {"duration": 300, "easing": "quadratic-in-out"}
                }]
            }, {
                "label": "暂停",
                "method": "animate",
                "args": [[None], {
                    "frame": {"duration": 0, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 0}
                }]
            }],
            "direction": "left",
            "pad": {"r": 10, "t": 85},
            "x": 0.1,
            "y": 0,
            "xanchor": "right",
            "yanchor": "top"
        }],
        sliders=[{
            "active": 0,
            "steps": [{
                "args": [[f.name], {
                    "frame": {"duration": animation_speed, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300}
                }],
                "label": f.name,
                "method": "animate"
            } for f in fig_regions.frames],
            "x": 0.1,
            "len": 0.9,
            "xanchor": "left",
            "yanchor": "top",
            "pad": {"t": 100, "b": 10},
            "currentvalue": {
                "visible": True,
                "prefix": "年份: ",
                "xanchor": "right",
                "font": {"size": 14, "color": "#2E8B57"}
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"}
        }]
    )
    
    # 显示图表
    st.plotly_chart(fig_regions, use_container_width=True)
    
    # 饼图显示当前年份各区域贡献比例
    st.markdown("""
    <div class="card" style="background-color: white; border-radius: 10px; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 class="card-title" style="color: #2E8B57; font-size: 1.5rem; margin-bottom: 1rem;">各区域贡献占比</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加年份选择器
    selected_year = st.slider(
        "选择年份查看各区域贡献占比",
        min_value=int(df["年份"].min()),
        max_value=int(df["年份"].max()),
        value=int(df["年份"].max()),
        step=1
    )
    
    # 获取所选年份的数据
    year_data = df[df["年份"] == selected_year]
    
    if not year_data.empty:
        region_contributions = [year_data[f"{region}贡献(%)"].values[0] for region in selected_regions]
        
        # 创建饼图
        fig_pie = px.pie(
            values=region_contributions,
            names=selected_regions,
            color=selected_regions,
            color_discrete_sequence=region_colors,
            title=f"{selected_year}年各区域贡献占比"
        )
        
        fig_pie.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="sans-serif", size=10, color="#333333")
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning(f"没有找到 {selected_year} 年的数据")

# 数据下载区域
st.markdown("""
<div class="download-section" style="background-color: white; border-radius: 10px; padding: 1.5rem; margin-top: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h3 style="color: #2E8B57; font-size: 1.5rem; margin-bottom: 1rem;">数据下载</h3>
    <p style="color: #666; margin-bottom: 1rem;">您可以下载当前数据用于进一步分析：</p>
    <div class="download-buttons" style="display: flex; gap: 1rem;">
""", unsafe_allow_html=True)

# 准备下载数据
csv_data = df.to_csv(index=False, encoding="utf-8-sig")
excel_data = BytesIO()
df.to_excel(excel_data, index=False, engine="openpyxl")
excel_data.seek(0)

# 下载按钮
col_download1, col_download2 = st.columns(2)
with col_download1:
    st.download_button(
        label="📥 下载数据 (CSV)",
        data=csv_data,
        file_name="全球南方国家GDP占比数据.csv",
        mime="text/csv",
        key="download-csv",
        use_container_width=True
    )

with col_download2:
    st.download_button(
        label="📥 下载数据 (Excel)",
        data=excel_data,
        file_name="全球南方国家GDP占比数据.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download-excel",
        use_container_width=True
    )

st.markdown("</div></div>", unsafe_allow_html=True)

# 数据表格预览
with st.expander("查看详细数据"):
    st.dataframe(df, use_container_width=True)

# 关键洞察
st.markdown("""
<div class="insights-section" style="background-color: white; border-radius: 10px; padding: 1.5rem; margin-top: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h3 style="color: #2E8B57; font-size: 1.5rem; margin-bottom: 1rem;">关键洞察</h3>
    <div class="insight-cards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
        <div class="insight-card" style="background-color: #e8f5e9; border-radius: 8px; padding: 1.2rem; border-left: 4px solid #2E8B57;">
            <h4 style="color: #2E8B57; font-size: 1.2rem; margin-bottom: 0.5rem;">显著增长趋势</h4>
            <p style="color: #666;">分析期间，全球南方国家GDP占比从{df.iloc[0]["全球南方国家GDP占比(%)"]:.2f}%增长至{df.iloc[-1]["全球南方国家GDP占比(%)"]:.2f}%，反映了全球经济力量格局的变化。</p>
        </div>
        <div class="insight-card" style="background-color: #e8f5e9; border-radius: 8px; padding: 1.2rem; border-left: 4px solid #2E8B57;">
            <h4 style="color: #2E8B57; font-size: 1.2rem; margin-bottom: 0.5rem;">区域贡献差异</h4>
            <p style="color: #666;">{df[region_columns].sum(axis=0).idxmax().replace('贡献(%)', '')}贡献最大，成为全球南方经济增长的主要推动力。其他区域也呈现稳步增长趋势。</p>
        </div>
        <div class="insight-card" style="background-color: #e8f5e9; border-radius: 8px; padding: 1.2rem; border-left: 4px solid #2E8B57;">
            <h4 style="color: #2E8B57; font-size: 1.2rem; margin-bottom: 0.5rem;">趋势预测</h4>
            <p style="color: #666;">按照当前趋势，全球南方国家GDP占比有望继续提升，进一步重塑全球经济格局。</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 页脚
st.markdown("""
<style>
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: #666;
        font-size: 0.9rem;
    }
</style>
<div class="footer">
    <p>数据来源于本地CSV文件 | 最后更新：2023年</p>
    <p>
        <a href="#" style="color: #2E8B57; text-decoration: none; margin: 0 0.5rem;">
            <i class="fa fa-github"></i> GitHub
        </a>
        <a href="#" style="color: #2E8B57; text-decoration: none; margin: 0 0.5rem;">
            <i class="fa fa-twitter"></i> Twitter
        </a>
        <a href="#" style="color: #2E8B57; text-decoration: none; margin: 0 0.5rem;">
            <i class="fa fa-linkedin"></i> LinkedIn
        </a>
    </p>
</div>
""", unsafe_allow_html=True)