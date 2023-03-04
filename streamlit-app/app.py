# %%
import pandas as pd
import plotly.express as px
import streamlit as st

def is_outlier(df, col, q1_col, q3_col, iqr_col):
    
    if df[col] > df[q3_col] + df[iqr_col] * 1.5 or df[col] < df[q1_col] - df[iqr_col] * 1.5:
        return True
    else:
        return False
    
def clean_data(df):

    df = df[["Name", "Color", "Rarity", "ATA", "GD WR", "IWD"]]
    df = df.dropna()    
    
    df["GD WR"] = df["GD WR"].apply(lambda x: float(x[:-1]))
    df["IWD"] = df["IWD"].apply(lambda x: float(x[:-2]))


    df["rounded_pick_order"] = df["ATA"].apply(lambda x: round(x, 0))

    q1 = df.groupby("rounded_pick_order")[["GD WR", "IWD"]].quantile(0.25)
    q3 = df.groupby("rounded_pick_order")[["GD WR", "IWD"]].quantile(0.75)

    quartile = pd.merge(q1, q3, left_on="rounded_pick_order", right_on="rounded_pick_order", suffixes=('_q1', '_q3'))

    df = pd.merge(df, quartile, left_on='rounded_pick_order', right_on='rounded_pick_order')


    df["IWD_iqr"] = df["IWD_q3"] - df["IWD_q1"]
    df["GD WR_iqr"] = df["GD WR_q3"] - df["GD WR_q1"]

    df["IWD_outlier"] = df.apply(is_outlier, args=("IWD", "IWD_q1","IWD_q3", "IWD_iqr",), axis=1)
    df["GD_WR_outlier"] = df.apply(is_outlier, args=("GD WR", "GD WR_q1", "GD WR_q3", "GD WR_iqr"), axis=1)


    return df

def plot_win_rate_over_ata(df, color):

    color_dict = {'Red':"R", 'Blue':"U", 'Black':"B", 'Green':"G", 'White':"W"}
    color = [color_dict[n] for n in color]

    sub_df = df[df["Color"].isin(color)]

    fig = px.scatter(sub_df, 
                     y="GD WR", 
                     x="ATA", 
                     color="GD_WR_outlier", 
                     title="Win rate by average turn picked",
                     labels={
                        "GD WR":"Average win rate when in hand or drawn",
                        "ATA":"Average turn picked",
                        "GD_WR_outlier": "Outliers"
                     },
                     color_discrete_sequence={False: 'rgb(55, 126, 184)', True: 'rgb(204, 80, 62)'},
    
                     hover_name="Name", 
                     hover_data=[
                            "rounded_pick_order", 
                            "ATA", "GD WR_q1",
                            "GD WR_q3"
                            ]
                            )
    
    fig.update_traces(marker_size=7)
    fig.update_layout(height=600, width=800)
    
    return fig


df = pd.read_csv("./data/ONE_card_rating.csv")

df = clean_data(df)


color = st.multiselect(
    'Color',
    ['Red', 'Blue', 'Black', 'Green', 'White'],
    default=['Red', 'Blue', 'Black', 'Green', 'White'],
    
)
fig = plot_win_rate_over_ata(df, color)
st.plotly_chart(fig, use_container_width=False)

# %%
