import pandas as pd
import streamlit as st
from plotly import express as px
import re


st.title("資料視覺化")
st.write('''
            # 說明：
            1. 目的：視覺化盤點量與電腦庫存量間的差異
            2. 選擇欄位-盤點量：12/30 盤點量
            3. 選擇欄位-盤點量與電腦庫存差：盤點量扣除電腦庫存差
            4. 輸出二種**圖表**供分析
            5. 表格： 結果呈現
         - 長條圖：實際量與電腦量比較
         - 矩形樹狀圖： 實際量與電腦量差的比較
            ''')
file_path = "./static/data_2026.xlsx"
data = pd.read_excel(file_path)
st.divider()
col = ['藥品代碼', '藥名', r'12/30預期量', r'12/30電腦量', '備註']
df = data[col]
# conditions
limit = st.radio("盤點量：", ["盤點量非0", "盤點量為0"], index=0, horizontal=True)
type = st.radio("劑型：", ["口服", "針劑", "其他"], index=0, horizontal=True)
note = st.radio("盤點量與電腦庫存差：", ["錯誤", "無資料", "OK"], index=0, horizontal=True)

if limit == "盤點量非0":
    result = df.query(f"`{'12/30預期量'}` != 0")
else:
    result = df.query(f"`{'12/30預期量'}` == 0")

result['type'] = result['藥品代碼'].str[-1]
if type == "口服":
    resultX = result.query("type == 'O'")
elif type == "針劑":
    resultX = result.query("type == 'I'")
else:
    resultX = result.query("type != 'I' and type != 'O'")

if note == "無資料":
    resultZ = resultX.query("備註 == @note")
elif note == "錯誤":
    resultZ = resultX.query("備註 == @note")
else:
    resultZ = resultX.query("備註 == 'OK'")
# st.write(resultZ.head(10))
resultZ.rename(columns={'12/30預期量':'12/30量'}, inplace=True)
resultZ.drop(columns=['type'], inplace=True)
st.markdown(f"### 分析總筆數： 共 **{resultZ.shape[0]}** 筆")

st.divider()
st.title("表格：")
st.subheader("依藥品代碼排序")
st.write(resultZ)

st.divider()
st.title("圖表：")
fig_type = st.radio("選擇圖表： ", [r'長條圖(依12/30盤點量)', '矩形樹狀圖'], index=0, horizontal=True)
fig_data = resultZ[['藥名', r'12/30量', r'12/30電腦量', '備註']]
fig_data = fig_data.sort_values(by='12/30量', ascending=False)
if note != '無資料':
    if fig_data.empty:
        st.markdown("### 無資料")
    else:
        if fig_type == '長條圖(依12/30盤點量)':
            fig = px.bar(fig_data, x='藥名', y=[r'12/30量', r'12/30電腦量'])
            fig.update_layout(
                    xaxis_tickangle=-45
                )   
            fig.update_layout(yaxis_title="數量")
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig_data['diff'] = fig_data[r'12/30量'] - fig_data[r'12/30電腦量']
            if 0 not in fig_data['diff'].unique():
                fig_map = px.treemap(fig_data, path=['藥名'], values=fig_data['diff'],
                                    color='12/30量', color_continuous_scale='Blues')
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.markdown("### 無資料")
else:
    st.title(note)
st.divider()
st.markdown(f'<h2 style="color:#0000CD;">調撥整理</h>', unsafe_allow_html=True)
allocate = pd.read_excel('./static/allocate.xlsx', engine="openpyxl")
allocate['formula'] = allocate['藥品代碼'].str[-1]
formula = st.radio("劑型： ", ["口服", "針劑", "其他"], index=0, horizontal=True)
if formula == "口服":
    allocate_type = allocate.query("formula == 'O'")
elif formula == "針劑":
    allocate_type = allocate.query("formula == 'I'")
else:
    allocate_type = allocate.query("formula != 'I' and formula != 'O'")
allocate_type_over = allocate_type.query('調撥總計 > 0')
sel = allocate_type_over['備註'].unique()
alloc_note = st.multiselect("可能因素： ", sel, default=sel[1])
values = st.slider("調撥總次數範圍： ", 0, 50, (7, 7))

allocate_type_ = allocate_type_over.query(f'調撥總計 >= {int(values[0])} & 調撥總計 <= {int(values[1])}')
fig_alloc = allocate_type_[allocate_type_['備註'].isin(alloc_note)]
data_alloc = fig_alloc[['藥品名稱', '1月', '2月', '3月', '4月', 
                        '5月', '6月', '7月', '8月', '9月',
                        '10月', '11月', '12月','備註']]
alloc_melt = data_alloc.melt(id_vars=['藥品名稱', '備註'], 
                          var_name='月份', 
                          value_name='次數')

alloc_scatter_3d = px.scatter_3d(
    alloc_melt, 
    x='藥品名稱', 
    y='月份', 
    z='次數', 
    color='次數',           # 顏色隨次數變化
    hover_data=['備註'],    # 懸停顯示備註
    opacity=0.7,           # 調整透明度增加重疊時的可視度
    height=700             # 調整圖表高度
)

# 2. 優化佈局 (避免 X 軸標籤擁擠)
alloc_scatter_3d.update_layout(scene=dict(
    xaxis_title='藥品名稱',
    yaxis_title='月份',
    zaxis_title='次數'
))
st.plotly_chart(alloc_scatter_3d, use_container_width=True)