import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da página (o tema claro será controlado via .streamlit/config.toml)
st.set_page_config(
    page_title="Dashboard Colheita de Milho",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded"
)

ACCENT_GREEN = "#2FE576"
ACCENT_DARK = "#148848"
ALERT_RED = "#E63946"
BAR_PRIMARY = "#1D4E89"
BAR_ORANGE = "#FFB703"
SIDEBAR_BG = "#4F5A66"
CONTENT_BG = "#F3F5FA"
SECTION_BG = "#FFFFFF"
CARD_BORDER = "#E1E4EC"
LOSS_SCALE = ["#2FE576", "#FFB703", "#E63946"]

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-color: {CONTENT_BG};
    }}
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG};
        color: #f7f9fb;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem;
    }}
    [data-testid="stSidebar"] .st-expander {{
        border: none;
        background: rgba(0,0,0,0.05);
        border-radius: 12px;
        margin-bottom: 0.6rem;
    }}
    [data-testid="stSidebar"] .st-expanderHeader {{
        background: rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        color: #f7f9fb;
        font-weight: 600;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }}
    [data-testid="stSidebar"] .st-expanderHeader:hover {{
        background: rgba(255, 255, 255, 0.12);
    }}
    [data-testid="stSidebar"] .st-expanderHeader[aria-expanded="true"] {{
        background: rgba(255, 255, 255, 0.18);
        border-color: rgba(255, 255, 255, 0.25);
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .st-expanderContent {{
        padding-top: 0.2rem;
    }}
    [data-testid="stSidebar"] * {{
        color: #f7f9fb !important;
    }}
    [data-testid="stSidebar"] h2 {{
        color: #f7f9fb;
        letter-spacing: 0.5px;
    }}
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {{
        background-color: rgba(255, 255, 255, 0.14);
        border-radius: 8px;
    }}
    [data-testid="stSidebar"] .stDateInput input {{
        background-color: rgba(255, 255, 255, 0.95);
        color: #1f2530 !important;
        border-radius: 10px;
    }}
    [data-testid="stSidebar"] .stRadio > div {{
        background: transparent;
        border-radius: 8px;
        padding: 0.4rem 0.2rem;
    }}
    [data-testid="stSidebar"] .stRadio > div > label {{
        background: transparent;
    }}
    div[data-testid="metric-container"] {{
        background: #FFFFFF;
        border: 1px solid {CARD_BORDER};
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 10px 25px rgba(23, 40, 73, 0.08);
    }}
    .kpi-card {{
        display: flex;
        gap: 1rem;
        background: #FFFFFF;
        border: 1px solid {CARD_BORDER};
        border-radius: 22px;
        padding: 1rem 1.2rem;
        box-shadow: 0 15px 30px rgba(23, 40, 73, 0.08);
        min-height: 120px;
    }}
    .kpi-card__icon {{
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background: {CONTENT_BG};
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.6rem;
    }}
    .kpi-card__body {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        flex: 1;
    }}
    .kpi-card__label {{
        font-size: 0.95rem;
        color: #516070;
        margin-bottom: 0.2rem;
    }}
    .kpi-card__value {{
        font-size: 1.6rem;
        font-weight: 700;
        color: #101828;
    }}
    .stButton button, .stDownloadButton button {{
        background: {ACCENT_GREEN};
        color: #1f2530;
        border: none;
        border-radius: 999px;
        font-weight: 600;
        padding: 0.6rem 1.4rem;
    }}
    .section-card {{
        background: {SECTION_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(33, 50, 79, 0.08);
    }}
    .section-card h2 {{
        color: #1f2530;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.35rem;
        margin-bottom: 1.5rem;
    }}
    .section-header {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1.2rem;
    }}
    .section-header__icon {{
        width: 48px;
        height: 48px;
        border-radius: 16px;
        background: {CONTENT_BG};
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.5rem;
    }}
    .section-header__text {{
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2530;
    }}
    div[data-testid="stPlotlyChart"] {{
        background: #FFFFFF;
        border: 1px solid {CARD_BORDER};
        border-radius: 22px;
        padding: 0.8rem;
        box-shadow: 0 12px 32px rgba(23, 40, 73, 0.08);
    }}
    div[data-testid="stPlotlyChart"] > div {{
        border-radius: 16px;
    }}
    hr.soft-divider {{
        border: none;
        border-top: 1px solid {CARD_BORDER};
        margin: 2rem 0 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def safe_mean(series: pd.Series) -> float:
    """Retorna a média tratando NaN e séries vazias."""
    if series.empty:
        return 0.0
    return float(np.nan_to_num(series.mean(), nan=0.0))


theme_primary = st.get_option("theme.primaryColor") or ACCENT_GREEN


def format_brl_number(value: float, decimals: int = 2) -> str:
    """Formata números usando padrão brasileiro (ponto milhar, vírgula decimal)."""
    format_pattern = f"{{:,.{decimals}f}}" if decimals > 0 else "{:,.0f}"
    formatted = format_pattern.format(value)
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def section_header(icon: str, title: str):
    st.markdown(
        f"""
        <div class='section-header'>
            <div class='section-header__icon'>{icon}</div>
            <div class='section-header__text'>{title}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def apply_chart_theme(fig, margin=None):
    margin = margin or dict(l=50, r=30, t=80, b=50)
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=margin,
        font=dict(color="#1f2530"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E9EDF5", zerolinecolor="#E9EDF5")
    fig.update_yaxes(showgrid=True, gridcolor="#E9EDF5", zerolinecolor="#E9EDF5")
    return fig


def render_kpi_card(icon: str, label: str, value: str):
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-card__icon'>{icon}</div>
            <div class='kpi-card__body'>
                <div class='kpi-card__label'>{label}</div>
                <div class='kpi-card__value'>{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel('Colheita do Milho.xlsx')
    df['Data_Plantio'] = pd.to_datetime(df['Data_Plantio'])
    df['Data_Colheita'] = pd.to_datetime(df['Data_Colheita'])
    df['ROI_%'] = (df['Margem_Operacional_R$'] / df['Custo_Total_R$']) * 100
    return df

df = load_data()
referencias = {
    "prod_estimada": safe_mean(df['Produtividade_Estimada_t_ha']),
    "perdas": safe_mean(df['Perdas_Colheita_%']),
    "roi": safe_mean(df['ROI_%'])
}

# Header
st.title("🌽 Dashboard - Colheita de Milho")
st.markdown("<hr class='soft-divider'>", unsafe_allow_html=True)

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

with st.sidebar.expander("🧑‍🌾 Fazendas", expanded=True):
    fazendas_selecionadas = st.multiselect(
        "Selecione as Fazendas",
        options=sorted(df['Fazenda'].unique()),
        default=sorted(df['Fazenda'].unique())
    )

with st.sidebar.expander("🌽 Híbridos", expanded=False):
    modo_hibrido = st.radio("Modo de seleção", ["Todos", "Selecionar"], index=0, horizontal=True, key="hibrido_radio")
    if modo_hibrido == "Todos":
        hibridos_selecionados = df['Hibrido'].unique().tolist()
    else:
        hibridos_selecionados = st.multiselect(
            "Escolha os Híbridos",
            options=sorted(df['Hibrido'].unique()),
            default=sorted(df['Hibrido'].unique()),
            key="hibrido_multiselect"
        )

with st.sidebar.expander("💧 Sistemas de Irrigação", expanded=False):
    modo_irrigacao = st.radio("Filtro", ["Todos", "Selecionar"], index=0, horizontal=True, key="irrigacao_radio")
    if modo_irrigacao == "Todos":
        irrigacao_selecionada = df['Sistema_Irrigacao'].unique().tolist()
    else:
        irrigacao_selecionada = st.multiselect(
            "Escolha os Sistemas",
            options=sorted(df['Sistema_Irrigacao'].unique()),
            default=sorted(df['Sistema_Irrigacao'].unique()),
            key="irrigacao_multiselect"
        )

st.sidebar.markdown("### 📅 Período de Colheita")
periodo_padrao = (
    df['Data_Colheita'].min().date(),
    df['Data_Colheita'].max().date()
)
periodo_colheita = st.sidebar.date_input(
    "Selecione o intervalo",
    value=periodo_padrao,
    min_value=periodo_padrao[0],
    max_value=periodo_padrao[1],
    format="DD/MM/YYYY"
)
if isinstance(periodo_colheita, tuple):
    data_inicio, data_fim = periodo_colheita
else:
    data_inicio = data_fim = periodo_colheita

# Aplicar filtros
df_filtrado = df[
    (df['Fazenda'].isin(fazendas_selecionadas)) &
    (df['Hibrido'].isin(hibridos_selecionados)) &
    (df['Sistema_Irrigacao'].isin(irrigacao_selecionada)) &
    (df['Data_Colheita'] >= pd.to_datetime(data_inicio)) &
    (df['Data_Colheita'] <= pd.to_datetime(data_fim))
]

# Verificar se há dados filtrados
if len(df_filtrado) == 0:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Ajuste os filtros.")
    st.stop()

# KPIs principais
section_header("📊", "Indicadores Principais")

area_total = df_filtrado['Area_Colhida_ha'].sum()
producao_total = df_filtrado['Ton_Real'].sum()
prod_media = safe_mean(df_filtrado['Produtividade_Real_t_ha'])
prod_estimada_media = safe_mean(df_filtrado['Produtividade_Estimada_t_ha'])
perdas_media = safe_mean(df_filtrado['Perdas_Colheita_%'])
roi_medio = safe_mean(df_filtrado['ROI_%'])

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    render_kpi_card("🌾", "Área Total (ha)", format_brl_number(area_total, 1))

with col2:
    render_kpi_card("📦", "Produção Real (t)", format_brl_number(producao_total, 1))

with col3:
    render_kpi_card(
        "⚖️",
        "Produtividade Média (t/ha)",
        format_brl_number(prod_media, 2)
    )

with col4:
    render_kpi_card(
        "🛡️",
        "Perdas Médias (%)",
        f"{format_brl_number(perdas_media, 2)}%"
    )

with col5:
    render_kpi_card(
        "💹",
        "ROI Médio (%)",
        f"{format_brl_number(roi_medio, 1)}%"
    )

section_header("🎯", "Indicadores vs Metas")

meta_produtividade = prod_estimada_media if prod_estimada_media > 0 else referencias['prod_estimada']
meta_produtividade = max(meta_produtividade, 0.1)
prod_range_max = max(meta_produtividade, prod_media) * 1.25

col_ind1, col_ind2 = st.columns(2)

with col_ind1:
    fig_prod = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=prod_media,
        title={'text': "Produtividade Real x Meta"},
        number={'suffix': " t/ha", 'valueformat': ".2f"},
        delta={
            'reference': meta_produtividade,
            'valueformat': ".2f",
            'relative': False,
            'increasing': {'color': ACCENT_DARK},
            'decreasing': {'color': ALERT_RED}
        },
        gauge={
            'axis': {'range': [0, max(prod_range_max, 1)]},
            'bar': {'color': ACCENT_GREEN},
            'bgcolor': '#E7F7ED',
            'steps': [
                {'range': [0, meta_produtividade * 0.8], 'color': '#FDE2E1'},
                {'range': [meta_produtividade * 0.8, meta_produtividade], 'color': '#FFF5DA'},
                {'range': [meta_produtividade, max(prod_range_max, meta_produtividade)], 'color': '#D8F8E0'}
            ],
            'threshold': {'line': {'color': ACCENT_DARK, 'width': 4}, 'value': meta_produtividade}
        }
    ))
    fig_prod.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=80, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF"
    )
    st.plotly_chart(fig_prod, use_container_width=True)

with col_ind2:
    perdas_referencia = referencias['perdas']
    perdas_range_max = max(perdas_media, perdas_referencia) * 1.6
    perdas_range_max = max(perdas_range_max, 5)
    fig_perdas = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=perdas_media,
        title={'text': "Perdas na Colheita"},
        number={'suffix': "%", 'valueformat': ".2f"},
        delta={
            'reference': perdas_referencia,
            'valueformat': ".2f",
            'relative': False,
            'increasing': {'color': ALERT_RED},
            'decreasing': {'color': ACCENT_DARK}
        },
        gauge={
            'axis': {'range': [0, perdas_range_max]},
            'bar': {'color': ALERT_RED},
            'bgcolor': '#FDECEA',
            'steps': [
                {'range': [0, perdas_referencia * 0.5], 'color': '#D8F8E0'},
                {'range': [perdas_referencia * 0.5, perdas_referencia], 'color': '#FFF5DA'},
                {'range': [perdas_referencia, perdas_range_max], 'color': '#FDE2E1'}
            ],
            'threshold': {'line': {'color': ALERT_RED, 'width': 4}, 'value': perdas_referencia}
        }
    ))
    fig_perdas.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=80, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF"
    )
    st.plotly_chart(fig_perdas, use_container_width=True)

# KPIs Financeiros
section_header("💰", "Indicadores Financeiros")

col1, col2, col3 = st.columns(3)

with col1:
    custo_total = df_filtrado['Custo_Total_R$'].sum()
    render_kpi_card("💸", "Custo Total", f"R$ {format_brl_number(custo_total/1000, 0)}k")

with col2:
    receita_total = df_filtrado['Receita_Bruta_R$'].sum()
    render_kpi_card("📈", "Receita Bruta", f"R$ {format_brl_number(receita_total/1000, 0)}k")

with col3:
    margem_total = df_filtrado['Margem_Operacional_R$'].sum()
    render_kpi_card("🏦", "Margem Operacional", f"R$ {format_brl_number(margem_total/1000, 0)}k")

# Gráficos - Linha 1 e 2
section_header("📈", "Análises Comparativas")

col1, col2 = st.columns(2)

with col1:
    prod_fazenda = df_filtrado.groupby('Fazenda').agg({
        'Produtividade_Real_t_ha': 'mean',
        'Produtividade_Estimada_t_ha': 'mean'
    }).reset_index().sort_values('Produtividade_Real_t_ha', ascending=False)
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        name='Estimada',
        x=prod_fazenda['Fazenda'],
        y=prod_fazenda['Produtividade_Estimada_t_ha'],
        marker_color=BAR_PRIMARY,
        text=prod_fazenda['Produtividade_Estimada_t_ha'].round(2),
        textposition='outside'
    ))
    fig1.add_trace(go.Bar(
        name='Real',
        x=prod_fazenda['Fazenda'],
        y=prod_fazenda['Produtividade_Real_t_ha'],
        marker_color=ACCENT_GREEN,
        text=prod_fazenda['Produtividade_Real_t_ha'].round(2),
        textposition='outside'
    ))
    fig1.update_layout(
        title='Produtividade: Estimada vs Real por Fazenda',
        xaxis_title='Fazenda',
        yaxis_title='Produtividade (t/ha)',
        barmode='group',
        legend_title='Tipo'
    )
    fig1 = apply_chart_theme(fig1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    margem_fazenda = df_filtrado.groupby('Fazenda')['Margem_Operacional_R$'].sum().reset_index()
    margem_fazenda['Margem_Mil'] = margem_fazenda['Margem_Operacional_R$'] / 1000
    margem_fazenda = margem_fazenda.sort_values('Margem_Mil', ascending=False)
    
    fig2 = px.bar(
        margem_fazenda,
        x='Fazenda',
        y='Margem_Mil',
        title='Margem Operacional por Fazenda',
        labels={'Margem_Mil': 'Margem (R$ mil)', 'Fazenda': 'Fazenda'},
        text='Margem_Mil',
        color='Margem_Mil',
        color_continuous_scale=['#D9EDE0', ACCENT_GREEN]
    )
    fig2.update_traces(texttemplate='R$ %{text:.0f}k', textposition='outside')
    fig2.update_layout(showlegend=False)
    fig2 = apply_chart_theme(fig2)
    st.plotly_chart(fig2, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    perdas_hibrido = df_filtrado.groupby('Hibrido')['Perdas_Colheita_%'].mean().sort_values().reset_index()
    fig3 = px.bar(
        perdas_hibrido,
        y='Hibrido',
        x='Perdas_Colheita_%',
        orientation='h',
        title='Perdas na Colheita por Híbrido',
        labels={'Perdas_Colheita_%': 'Perdas (%)', 'Hibrido': 'Híbrido'},
        text='Perdas_Colheita_%',
        color='Perdas_Colheita_%',
        color_continuous_scale=LOSS_SCALE
    )
    fig3.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig3.update_layout(showlegend=False)
    fig3 = apply_chart_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    prod_irrigacao = df_filtrado.groupby('Sistema_Irrigacao')['Produtividade_Real_t_ha'].mean().sort_values(ascending=False).reset_index()
    fig4 = px.bar(
        prod_irrigacao,
        x='Sistema_Irrigacao',
        y='Produtividade_Real_t_ha',
        title='Produtividade por Sistema de Irrigação',
        labels={'Produtividade_Real_t_ha': 'Produtividade (t/ha)', 'Sistema_Irrigacao': 'Sistema'},
        text='Produtividade_Real_t_ha',
        color='Produtividade_Real_t_ha',
        color_continuous_scale=[BAR_PRIMARY, ACCENT_GREEN]
    )
    fig4.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig4.update_layout(showlegend=False)
    fig4 = apply_chart_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

section_header("📉", "Distribuições & ROI")

col1, col2 = st.columns(2)

with col1:
    fig5 = px.histogram(
        df_filtrado,
        x='Produtividade_Real_t_ha',
        nbins=20,
        title='Distribuição da Produtividade Real',
        labels={'Produtividade_Real_t_ha': 'Produtividade (t/ha)', 'count': 'Frequência'},
        color_discrete_sequence=[BAR_PRIMARY]
    )
    
    media = df_filtrado['Produtividade_Real_t_ha'].mean()
    fig5.add_vline(x=media, line_dash="dash", line_color=theme_primary, 
                   annotation_text=f"Média: {media:.2f}", annotation_position="top")
    
    fig5 = apply_chart_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    roi_fazenda = df_filtrado.groupby('Fazenda').agg({
        'Margem_Operacional_R$': 'sum',
        'Custo_Total_R$': 'sum'
    }).reset_index()
    roi_fazenda['ROI_%'] = (roi_fazenda['Margem_Operacional_R$'] / roi_fazenda['Custo_Total_R$']) * 100
    
    fig6 = px.bar(
        roi_fazenda,
        x='Fazenda',
        y='ROI_%',
        title='ROI por Fazenda',
        labels={'ROI_%': 'ROI (%)', 'Fazenda': 'Fazenda'},
        text='ROI_%',
        color='ROI_%',
        color_continuous_scale=[BAR_PRIMARY, ACCENT_GREEN]
    )
    fig6.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig6.update_layout(showlegend=False)
    fig6 = apply_chart_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

section_header("📋", "Dados Detalhados")

df_display = df_filtrado[[
    'Fazenda', 'Bloco', 'Talhao', 'Hibrido', 'Sistema_Irrigacao',
    'Area_Colhida_ha', 'Produtividade_Real_t_ha', 'Ton_Real',
    'Perdas_Colheita_%', 'Margem_Operacional_R$', 'ROI_%'
]].copy()

df_display.columns = [
    'Fazenda', 'Bloco', 'Talhão', 'Híbrido', 'Sistema Irrigação',
    'Área (ha)', 'Produtividade (t/ha)', 'Produção (t)',
    'Perdas (%)', 'Margem (R$)', 'ROI (%)'
]

df_display['Área (ha)'] = df_display['Área (ha)'].round(2)
df_display['Produtividade (t/ha)'] = df_display['Produtividade (t/ha)'].round(2)
df_display['Produção (t)'] = df_display['Produção (t)'].round(2)
df_display['Perdas (%)'] = df_display['Perdas (%)'].round(2)
df_display['Margem (R$)'] = df_display['Margem (R$)'].round(2)
df_display['ROI (%)'] = df_display['ROI (%)'].round(2)

st.dataframe(df_display, use_container_width=True, height=400)

st.download_button(
    label="📥 Download dos Dados Filtrados (CSV)",
    data=df_display.to_csv(index=False).encode('utf-8'),
    file_name='dados_colheita_filtrados.csv',
    mime='text/csv'
)
st.markdown(
    """
    <div style='text-align: center;'>
        <p>Dashboard desenvolvido para análise de colheita de milho 🌽</p>
    </div>
    """,
    unsafe_allow_html=True
)
