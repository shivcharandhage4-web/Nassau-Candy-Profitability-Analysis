import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title='Nassau Candy Profitability', page_icon='🍫', layout='wide')
@st.cache_data
def load_data():
    df=pd.read_csv('cleaned_dataset.csv')
    df['Order Date']=pd.to_datetime(df['Order Date']); df['Ship Date']=pd.to_datetime(df['Ship Date'])
    df['Gross Margin %']=df['Gross Profit']/df['Sales']*100
    df['Profit per Unit']=df['Gross Profit']/df['Units']
    df['Factory']=df['Product Name'].map({'Wonka Bar - Nutty Crunch Surprise':"Lot's O' Nuts",'Wonka Bar - Fudge Mallows':"Lot's O' Nuts",'Wonka Bar -Scrumdiddlyumptious':"Lot's O' Nuts",'Wonka Bar - Milk Chocolate':"Wicked Choccy's",'Wonka Bar - Triple Dazzle Caramel':"Wicked Choccy's",'Laffy Taffy':'Sugar Shack','SweeTARTS':'Sugar Shack','Nerds':'Sugar Shack','Fun Dip':'Sugar Shack','Fizzy Lifting Drinks':'Sugar Shack','Everlasting Gobstopper':'Secret Factory','Hair Toffee':'The Other Factory','Lickable Wallpaper':'Secret Factory','Wonka Gum':'Secret Factory','Kazookles':'The Other Factory'})
    return df

df=load_data(); st.title('🍫 Nassau Candy — Product Profitability & Margin Performance')
st.caption('Interactive analytics dashboard | Product, division, cost, Pareto and factory diagnostics')
with st.sidebar:
    st.header('Filters')
    d1,d2=st.date_input('Order date range',[df['Order Date'].min().date(),df['Order Date'].max().date()])
    divisions=st.multiselect('Division',sorted(df.Division.unique()),default=sorted(df.Division.unique()))
    threshold=st.slider('Margin threshold (%)',0,100,40)
    search=st.text_input('Product search')
f=df[(df['Order Date'].dt.date>=d1)&(df['Order Date'].dt.date<=d2)&df.Division.isin(divisions)].copy()
if search: f=f[f['Product Name'].str.contains(search,case=False,na=False)]
S=f.Sales.sum(); P=f['Gross Profit'].sum(); C=f.Cost.sum(); U=f.Units.sum(); M=P/S*100 if S else 0
k1,k2,k3,k4=st.columns(4); k1.metric('Sales',f'${S:,.2f}'); k2.metric('Gross Profit',f'${P:,.2f}'); k3.metric('Gross Margin',f'{M:.1f}%'); k4.metric('Units',f'{U:,.0f}')
st.divider()
prod=f.groupby(['Product ID','Product Name','Division'],as_index=False).agg(Sales=('Sales','sum'),Cost=('Cost','sum'),Gross_Profit=('Gross Profit','sum'),Units=('Units','sum'))
prod['Margin %']=prod.Gross_Profit/prod.Sales*100; prod['Profit/Unit']=prod.Gross_Profit/prod.Units; prod['Revenue Contribution %']=prod.Sales/S*100 if S else 0; prod['Profit Contribution %']=prod.Gross_Profit/P*100 if P else 0; prod['Risk']=np.where(prod['Margin %']<threshold,'Review','Healthy')

a,b=st.columns(2)
with a:
 st.subheader('Product Profitability Leaderboard'); q=prod.sort_values('Gross_Profit',ascending=False); st.plotly_chart(px.bar(q,x='Gross_Profit',y='Product Name',orientation='h',title='Gross Profit by Product'),use_container_width=True)
with b:
 st.subheader('Margin Risk'); r=prod.sort_values('Margin %'); st.plotly_chart(px.bar(r,x='Margin %',y='Product Name',orientation='h',title='Gross Margin % by Product'),use_container_width=True)
st.subheader('Product Detail'); st.dataframe(prod.sort_values('Gross_Profit',ascending=False).style.format({'Sales':'${:,.2f}','Cost':'${:,.2f}','Gross_Profit':'${:,.2f}','Margin %':'{:.1f}%','Profit/Unit':'${:.2f}','Revenue Contribution %':'{:.1f}%','Profit Contribution %':'{:.1f}%'}),use_container_width=True)

div=f.groupby('Division',as_index=False).agg(Sales=('Sales','sum'),Cost=('Cost','sum'),Gross_Profit=('Gross Profit','sum'),Units=('Units','sum')); div['Margin %']=div.Gross_Profit/div.Sales*100
c,d=st.columns(2)
with c: st.plotly_chart(px.bar(div,x='Division',y=['Sales','Gross_Profit'],barmode='group',title='Division Revenue vs Profit'),use_container_width=True)
with d: st.plotly_chart(px.box(f,x='Division',y='Gross Margin %',title='Order Margin Distribution by Division'),use_container_width=True)

st.subheader('Cost vs Margin Diagnostics'); st.plotly_chart(px.scatter(f,x='Sales',y='Gross Profit',size='Units',color='Division',hover_name='Product Name',title='Sales vs Gross Profit'),use_container_width=True)

st.subheader('Profit Pareto'); pareto=prod.sort_values('Gross_Profit',ascending=False).copy(); pareto['Cumulative Profit %']=pareto.Gross_Profit.cumsum()/P*100 if P else 0; fig=px.bar(pareto,x='Product Name',y='Gross_Profit',title='Profit Concentration'); fig.add_scatter(x=pareto['Product Name'],y=pareto['Cumulative Profit %'],name='Cumulative %',yaxis='y2'); fig.update_layout(yaxis2=dict(overlaying='y',side='right',range=[0,105],title='Cumulative Profit %')); st.plotly_chart(fig,use_container_width=True)

st.subheader('Regional / State Diagnostics'); reg=f.groupby('Region',as_index=False).agg(Sales=('Sales','sum'),Gross_Profit=('Gross Profit','sum')); reg['Margin %']=reg.Gross_Profit/reg.Sales*100; st.dataframe(reg.style.format({'Sales':'${:,.2f}','Gross_Profit':'${:,.2f}','Margin %':'{:.1f}%'}),use_container_width=True)
fac=f.groupby('Factory',as_index=False).agg(Sales=('Sales','sum'),Gross_Profit=('Gross Profit','sum'),Units=('Units','sum')); fac['Margin %']=fac.Gross_Profit/fac.Sales*100; st.subheader('Factory Performance'); st.dataframe(fac.sort_values('Gross_Profit',ascending=False).style.format({'Sales':'${:,.2f}','Gross_Profit':'${:,.2f}','Margin %':'{:.1f}%'}),use_container_width=True)
st.info('Interpretation rule: use Gross Profit Contribution to identify financial impact and Gross Margin % to identify efficiency. Products below the selected margin threshold should be reviewed for pricing, sourcing cost, promotion strategy or discontinuation.')
