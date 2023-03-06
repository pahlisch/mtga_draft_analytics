
import pandas as pd
import plotly.express as px
import streamlit as st
import os
st.set_page_config(layout="wide")

st.header("Phyrexia All Will Be One Draft Pick Order")
st.write("The data in this app comes from 17Lands (17lands.com)")

color_dict = {"Red":"R", "Blue":"U", "Black":"B", "Green":"G", "White":"W", "Colorless":"C", "Multicolor":"M"}



script_dir = os.path.dirname(os.path.abspath(__file__))
data_filename = "../data/ONE_card_rating.csv"

data_filepath = os.path.join(script_dir, data_filename)

def is_outlier(df, col, q1_col, q3_col, iqr_col):
    
    if df[col] > df[q3_col] + df[iqr_col] * 1.5 or df[col] < df[q1_col] - df[iqr_col] * 1.5:
        return True
    else:
        return False
    
def clean_data(df):

    df = df[["Name", "Color", "Rarity", "ATA", "GD WR", "IWD"]]  
    df["Color"] = df["Color"].fillna("C")
    df["Color"] = df["Color"].apply(lambda x: x if len(x) == 1 else 'M')
    
    df = df.dropna()  
    df["GD WR"] = df["GD WR"].apply(lambda x: float(x[:-1]))
    df["IWD"] = df["IWD"].apply(lambda x: float(x[:-2]))


    df["rounded_pick_order"] = df["ATA"].apply(lambda x: round(x, 0))

    q1 = df.groupby("rounded_pick_order")[["GD WR", "IWD"]].quantile(0.25)
    q3 = df.groupby("rounded_pick_order")[["GD WR", "IWD"]].quantile(0.75)

    quartile = pd.merge(q1, q3, left_on="rounded_pick_order", right_on="rounded_pick_order", suffixes=("_q1", "_q3"))

    df = pd.merge(df, quartile, left_on="rounded_pick_order", right_on="rounded_pick_order")


    df["IWD_iqr"] = df["IWD_q3"] - df["IWD_q1"]
    df["GD WR_iqr"] = df["GD WR_q3"] - df["GD WR_q1"]

    df["IWD_outlier"] = df.apply(is_outlier, args=("IWD", "IWD_q1","IWD_q3", "IWD_iqr",), axis=1)
    df["GD_WR_outlier"] = df.apply(is_outlier, args=("GD WR", "GD WR_q1", "GD WR_q3", "GD WR_iqr"), axis=1)


    return df

def plot_win_rate_over_ata(df, color):

    color = [color_dict[n] for n in color]

    sub_df = df[df["Color"].isin(color)]

    color_map = {
    "C": "#c3c3c3",
    "B": "#303030",
    "W": "rgb(247,225,160)",
    "G": "rgb(26,115,49)",
    "M": "rgb(218,165,32)",
    "U": "rgb(33,84,154)",
    "R": "rgb(209,32,36)"
    }

    #using a dictionary as color_map is throwing an error, this is a workaround so I can pass a list as argument
    color_map = {key:value for key, value in color_map.items() if key in color}

    if display_color == "Yes":
        color = "Color"
    else:
        color = None

    fig = px.scatter(sub_df, 
                     y="GD WR", 
                     x="ATA", 
                     color=color, 
                     title="Win rate by average turn picked",
                     labels={
                        "GD WR":"Average win rate when in hand or drawn",
                        "ATA":"Average turn picked",
                        "Color":"Card Color"
                     },
                     color_discrete_sequence=list(color_map.values()),
                     hover_name="Name", 
                     hover_data=[
                            "rounded_pick_order", 
                            "ATA"
                            ]
                            )
    
    fig.update_traces(marker_size=7)
    fig.update_layout(autosize=True, height=700, width=1200)
    fig.update_layout(xaxis=dict(dtick=2))

    return fig


df = pd.read_csv(data_filepath)

df = clean_data(df)

with st.sidebar:
    color = st.multiselect(
        "Color",
        color_dict.keys(),
        default=color_dict.keys()
        
        )
    display_color = st.radio("Display card colors on graph", ["Yes", "No"])
    

fig = plot_win_rate_over_ata(df, color)
st.plotly_chart(fig, use_container_width=True)

# %%
