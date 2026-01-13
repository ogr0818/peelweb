import pandas as pd
import streamlit as st
from plotly import express as px
import re


def main():
    st.title("資料視覺化")
    st.write('''
             # 說明：
                1. 目的：視覺化盤點量與電腦庫存量間的差異
                2. 選擇欄位-盤點量：年終點量
                3. 選擇欄位-盤點量：盤點量扣除電腦庫存差
                4. 輸出二種**圖表**供分析
             ''')
    file_path = "./static/data_2026.xlsx"
    data = pd.read_excel(file_path)
    st.divider()
    col = ['藥品代碼', '藥名', r'12/27盤點量', r'12/30預期量', '備註']
    df = data[col]
    # conditions
    limit = st.radio("盤點量：", ["盤點量非0", "盤點量為0"], index=0, horizontal=True)
    type = st.radio("劑型：", ["口服", "針劑", "其他"], index=0, horizontal=True)
    note = st.radio("年終盤點量與電腦庫存差：", ["錯誤", "無資料", "OK"], index=0, horizontal=True)
    if limit == "盤點量非0":
        result = df.query(f"`{'12/27盤點量'}` != 0")
    else:
        result = df.query(f"`{'12/27盤點量'}` == 0")
        pass

    df['type'] = df['藥品代碼'].str[-1]
    if type == "口服":
        resultX = df.query("type == 'O'")
    elif type == "針劑":
        resultX = df.query("type == 'I'")
    else:
        resultX = df.query("type != 'I' and type != 'O'")
    
    if note == "無資料":
        resultZ = resultX.query("備註 == @note")
    elif note == "錯誤":
        resultZ = resultX.query("備註 == @note")
    else:
        resultZ = resultX.query("備註 == 'OK'")
    # st.write(resultZ.head(10))
    st.markdown(f"### 分析總筆數： {resultZ.shape[0]}")
    st.divider()
    st.title("圖表：")
    fig_type = st.radio("選擇圖表： ", ['長條圖', '矩形樹狀圖'], index=0, horizontal=True)
    fig_data = resultZ[['藥名', r'12/27盤點量', r'12/30預期量']]
    fig_data = fig_data.sort_values(by='12/27盤點量', ascending=False)
    if fig_type == '長條圖':
        fig = px.bar(fig_data, x='藥名', y=[r'12/27盤點量', r'12/30預期量'])
        fig.update_layout(
                xaxis_tickangle=-45
            )   
        fig.update_layout(yaxis_title="數量")
        st.plotly_chart(fig, use_container_width=True)
    else:
        diff = fig_data['12/27盤點量'] - fig_data['12/30預期量']
        fig_map = px.treemap(fig_data, path=['藥名'], values=diff, color='12/27盤點量')
        st.plotly_chart(fig_map, use_container_width=True)

if __name__ == "__main__":
    main()