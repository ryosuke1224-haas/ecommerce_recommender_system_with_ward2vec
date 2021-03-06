# -*- coding: utf-8 -*-
"""Ecommerce Recommender System with Word2Vec.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HiQz7t-5RXlehJtTWjSvuU2HuVQul2oc

# Ecommerce Recommender System with Word2Vec
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import gensim
from gensim import corpora, models, similarities
# %matplotlib inline
import warnings;
warnings.filterwarnings('ignore')

df = pd.read_excel('https://drive.google.com/uc?export=download&id=1icqOqpQ9fcBIbN2E_dWDJzXaF1Js2laf')

#Define ntile function
def ntile(a,n):
  q = a.quantile(np.linspace(1/n,1,n))
  output = []
  for i in a:
    if np.isnan(i):
      k = np.nan
    else:
      k = 0
      for j in q:
        if i<=j:
          break
        k += 1
        
    output.append(k)

  return np.array(output)

"""# Preprocessing & Exploration"""

df.head()

# some data exploration
# top 10 product
print(df['Description'].value_counts()[:10])
print('---------')
# top 10 country
print(df['Country'].value_counts()[:10])

#average price by country
df[['UnitPrice','Country']].groupby('Country').mean().sort_values(by=['UnitPrice'])

#average Quantity by country
df[['Quantity','Country']].groupby('Country').mean().sort_values(by=['Quantity'])

df.info()

#Appears to be some nulls in CustomerID and Description
df.isna().sum()

#Drop these rows from the dataset
df = df.dropna()

#Number of unique customers
df['CustomerID'].nunique()

df['Description'].nunique()

df.columns

df['Quantity'].describe()

df['UnitPrice'].describe()

sns.distplot(df['Quantity'])

sns.distplot(df['UnitPrice'])

plt.figure(figsize=(20,6))
sns.boxplot(x='Country',y='Quantity',data=df)

plt.figure(figsize=(20,6))
sns.boxplot(x='Country',y='UnitPrice',data=df)

df[['Country','InvoiceNo']].groupby('Country').count().plot(kind='bar')

df[['Country','Quantity']].groupby('Country').sum().plot(kind='bar')

df[['Country','UnitPrice']].groupby('Country').mean().plot(kind='bar')

df[['Description','Quantity']].groupby('Description').sum().sort_values(by='Quantity',ascending=False)

df[['Description','InvoiceNo']].groupby('Description').count().sort_values(by='InvoiceNo',ascending=False)

df[['Description','UnitPrice']].groupby('Description').mean().sort_values(by='UnitPrice',ascending=False)

"""# Product Recommender"""

#Break unique customers into a train and validation set
customers_train, customers_test = train_test_split(df['CustomerID'].unique(),test_size=0.1,random_state=42)

#Create train and test datasets
df_train = df[df['CustomerID'].isin(customers_train)]
df_test = df[df['CustomerID'].isin(customers_test)]

print(len(customers_train))
print(len(customers_test))

#For each customer, create sequence of purchases - training set
purchase_list_train = []

for customer in customers_train:
  purch_list = df_train[df_train['CustomerID']==customer]['Description'].tolist()
  purchase_list_train.append(purch_list)

#Quick validation: check the first customer in customers_train
customers_train[0]

#Validate the number of instances in the training set for customer 17007
len(df_train[df_train['CustomerID']==17007.0])

#Validate the number of purchases in the purchases list for customer 17007: matches above
len(purchase_list_train[0])

purchase_list_train[0]

#For each customer, create sequence of purchases - test set
purchase_list_test = []

for customer in customers_test:
  purch_list = df_test[df_test['CustomerID']==customer]['Description'].tolist()
  purchase_list_test.append(purch_list)

#Train a word2vec model
#Starting with a vector size of 10
product_model = gensim.models.Word2Vec(purchase_list_train,min_count=1,size=100,window=10,seed=7)

#Define a function to give the n-most similar products based a single description
#The use case here is to recommend products to the consumer based on their most recent purchase
def n_most_similar(Description,n):
  return product_model.most_similar(positive=Description)[:n]

#Find 5 most similar products to first customer in training set's most recent purchase
n_most_similar(purchase_list_train[0][-1],5)

#Define a function to give the n-most similar products based on ALL products a consumer has purchased
#The use case here is to recommend products to the consumer based on ALL purchases that they have made
def n_most_similar_list(purchase_list,n):
    product_vec = []
    for i in purchase_list:
      vec = product_model[i]
      product_vec.append(vec)
      mean_vec = np.mean(product_vec, axis=0)

    return product_model.similar_by_vector(mean_vec,n)

#Find 5 most similar products to first customer in training set's entire purchasing history
n_most_similar_list(purchase_list_train[0],5)

#Let's examine our two functions to see how they're working

#List of purchases for second customer in our training set
list_of_purchases = purchase_list_train[1]

print('Description of products purchased by this customer:\n', list_of_purchases,'\n')

print('Five top recommended products based on most recent purchase:\n', n_most_similar(list_of_purchases[-1],5),'\n')

print('Five top recommended products based on all purchases:\n', n_most_similar_list(list_of_purchases,5),'\n')

#Test similarity of different products
product_model.similarity('WHITE HANGING HEART T-LIGHT HOLDER','WHITE METAL LANTERN')

#Analogy product finder - potential for a consumer facing product discovery app
product_model.most_similar(positive=['PINK PARTY SUNGLASSES'],negative=["SILK PURSE BABUSHKA PINK"])[:5]

#Dimensionality reduction for visualization
vector_list = product_model[df_train['Description'].unique().tolist()]

#Reduce the vector list to 2 dimensions for visualization
from sklearn.manifold import TSNE
data_embed=TSNE(n_components=2, perplexity=50, verbose=2, method='barnes_hut').fit_transform(vector_list)

#put the reduced vectors into a dataframe
reduced_df = pd.DataFrame(data_embed,columns=['x','y'])
vocab = pd.DataFrame(list(product_model.wv.vocab))
df_forviz = pd.concat([reduced_df,vocab],axis=1)

len(vocab)

df_train['Description'].nunique()

df_forviz

#Adding features to the dataframe to color the visualization; here is avg unit price for each product
product_price_bins = df_train[['Description','UnitPrice']].groupby('Description').mean().reset_index()
product_price_bins['Price_Ntile'] = ntile(product_price_bins['UnitPrice'],5)
product_price_bins

len(df_train[df_train['Description']==' 4 PURPLE FLOCK DINNER CANDLES'])

#Adding features to the dataframe to color the visualization; here total order count for each product
product_order_bins = df_train[['Description','InvoiceNo']].groupby('Description').count().reset_index()
product_order_bins['Orders_Ntile'] = ntile(product_order_bins['InvoiceNo'],5)
product_order_bins

#Adding features to the dataframe to color the visualization; here is total quantity ordered for each product
total_quantity = df_train[['Description','Quantity']].groupby('Description').sum().reset_index()
total_quantity['Quantity_Ntile'] = ntile(total_quantity['Quantity'],5)
total_quantity

df_forviz_temp = df_forviz.merge(product_price_bins,left_on=0,right_on='Description')
df_forviz_temp

df_forviz_temp2 = df_forviz_temp.merge(product_order_bins,left_on='Description',right_on='Description')
df_forviz_temp2

df_forviz_final = df_forviz_temp2.merge(total_quantity,left_on='Description',right_on='Description')
df_forviz_final

df_forviz_final.to_csv('mytext.tsv',sep='\t',index=False)

from google.colab.output import eval_js
from IPython.display import Javascript
!git clone https://github.com/CAHLR/d3-scatterplot.git

def show_port(port, data_file, width=600, height=800):
  display(Javascript("""
  (async ()=>{
    fm = document.createElement('iframe')
    fm.src = await google.colab.kernel.proxyPort(%d) + '/index.html?dataset=%s'
    fm.width = '90%%'
    fm.height = '%d'
    fm.frameBorder = 0
    document.body.append(fm)
  })();
  """ % (port, data_file, height)))

port = 8000
data_file = 'mytext.tsv'
height = 1500

get_ipython().system_raw('cd d3-scatterplot && python3 -m http.server %d &' % port) 
show_port(port, data_file, height)

"""#Product Recommender Validation"""

def aggregate_vectors(products):
    product_vec = []
    for i in products:
        try:
            product_vec.append(product_model[i])
        except KeyError:
            continue
        
    return np.mean(product_vec, axis=0)

purchase_list_test_2=[]
for i in purchase_list_test:
  if len(i)>1:
    purchase_list_test_2.append(i)

purchased_item_without_last=[]
last_purchase_item=[]
for i in range(len(purchase_list_test_2)):
  last_purchase=purchase_list_test_2[i][-1]
  last_purchase_item.append(last_purchase)  
  without_last=purchase_list_test_2[i][:-1]
  purchased_item_without_last.append(without_last)

last_purchase=pd.DataFrame(last_purchase_item)
last_purchase.columns=['last_purchase']

average_item=[]
for i in purchased_item_without_last:
  average=aggregate_vectors(i)
  average_item.append(average)

pred = pd.DataFrame()
n=100
for i in range(len(purchase_list_test_2)):
  a=pd.DataFrame(product_model.similar_by_vector(average_item[i],n))
  a=a.drop(1, axis=1).T
  pred=pd.concat([pred, a],axis=0)
pred=pred.reset_index().drop('index', axis=1)
pred=pd.concat([pred,last_purchase],axis=1)

a=pd.DataFrame()
for i in range(n):
  a['correct_'+str(i)]=(pred[i]==pred['last_purchase']).astype(int)

a['correct']=a.sum(axis=1)

pred['correct']=a['correct']

accuracy_rate = pred['correct'].sum()/len(pred)
accuracy_rate

"""# Customer Recommender"""

#copy dataframe to be used for customer recommender
df2 = pd.DataFrame(df)

#Convert CustomerID to string
df['CustomerID'] = df['CustomerID'].astype(str)

#Break unique products into a train and validation set
products_train, products_test = train_test_split(df2['StockCode'].unique(),test_size=0.1,random_state=42)

#Create train and test datasets
df2_train = df2[df2['StockCode'].isin(products_train)]
df2_test = df2[df2['StockCode'].isin(products_test)]

print(len(products_train))
print(len(products_test))

#For each product, create sequence of purchases (customers who purchased that product) - training set
customer_list_train = []

for product in products_train:
  cust_list = df2_train[df2_train['StockCode'] == product]['CustomerID'].tolist()
  customer_list_train.append(cust_list)

#Validate first StockCode
print('First StockCode:', products_train[0])

#Number of instances of stock code 23006 in the training set
print('Number of instances of 23006:', len(df2_train[df2_train['StockCode']==23006]))

#Validate same number in customer list - checks out
print('Number of instances of 23006 in customer list:', len(customer_list_train[0]))

#For each product, create sequence of purchases (customers who purchased that product) - test set
customer_list_test = []

for product in products_test:
  cust_list = df2_test[df2_test['StockCode']==product]['CustomerID'].tolist()
  customer_list_test.append(cust_list)

df2.head(60)

#Train a word2vec model
#Starting with a vector size of 10
customer_model = gensim.models.Word2Vec(customer_list_train, min_count=1, size=100, window=100,seed=7)

#Find 5 most similar customers
customer_model.most_similar(positive='17850.0')[:5]

#Seeing this customer's history
df2[df2.CustomerID == '17850.0']['Description'][:10].tolist()

#Seeing this customer's most similar customer's history
most_similar_customer = customer_model.most_similar(positive='17850.0')[:1][0][0]
df2[df2.CustomerID == most_similar_customer]['Description'][:10].tolist()

#Dimensionality reduction
vector_list = customer_model[df2_train['CustomerID'].unique().tolist()]

#function to output list of customers likely to buy a product
def potential_customers(stock_code):
  past_cust = df2_train[df2_train['StockCode']==stock_code]['CustomerID'].tolist()[:10]
  potential_customers = customer_model.most_similar(positive=past_cust)[:10]
  return potential_customers

#Example product
product_id = '84406B'

#Description of the product code we are using
print('Description of produce we are looking at:\n', df2[df2.StockCode == product_id]['Description'][:1].tolist()[0], '\n')

#Testing the function by sending in the product code
potential_cust = potential_customers(product_id)
print('Customers likely to want to buy this product:\n', potential_cust[:5], '\n')

#Purchase history of the most likely next customer
print('Purchase history of', potential_cust[0][0], ':')
print(df2[df2.CustomerID == potential_cust[0][0]]['Description'][:10].tolist())

#Purchase history of the second most likely next customer
print('Purchase history of', potential_cust[1][0], ':')
print(df2[df2.CustomerID == potential_cust[1][0]]['Description'][:10].tolist(), '\n')

from sklearn.manifold import TSNE
data_embed = TSNE(n_components=2, perplexity=50, verbose=2, method='barnes_hut').fit_transform(vector_list)

data_embed

vector_list

df2_train.head()

df2_train[['CustomerID','Quantity']].groupby('CustomerID').sum().reset_index()['Quantity']

reduced_df = pd.DataFrame(data_embed,columns=['x','y'])
vocab = pd.DataFrame(list(customer_model.wv.vocab))
df2_forviz = pd.concat([reduced_df,vocab],axis=1)
df2_forviz['country'] = df2_train[['CustomerID','Country']].groupby('CustomerID').first().reset_index()['Country']
df2_forviz['quantity'] = df2_train[['CustomerID','Quantity']].groupby('CustomerID').sum().reset_index()['Quantity']

df2_train['total_spend'] = df2_train.Quantity * df2_train.UnitPrice
df2_forviz['total_spend'] = df2_train[['CustomerID','total_spend']].groupby('CustomerID').sum().reset_index()['total_spend']
df2_forviz = df2_forviz.rename(columns={0: 'CustomerId'})

df2_forviz.head()

df2_forviz.to_csv('mytext2.tsv',sep='\t',index=False)

def show_port(port, data_file, width=600, height=800):
  display(Javascript("""
  (async ()=>{
    fm = document.createElement('iframe')
    fm.src = await google.colab.kernel.proxyPort(%d) + '/index.html?dataset=%s'
    fm.width = '90%%'
    fm.height = '%d'
    fm.frameBorder = 0
    document.body.append(fm)
  })();
  """ % (port, data_file, height)))

port = 8000
data_file = 'mytext2.tsv'
height = 1600

get_ipython().system_raw('cd d3-scatterplot && python3 -m http.server %d &' % port) 
show_port(port, data_file, height)

"""#Customer Recommender Validation"""

def aggregate_vectors_cust(customers):
    customer_vec = []
    for i in customers:
        try:
            customer_vec.append(customer_model[i])
        except KeyError:
            continue
        
    return np.mean(customer_vec, axis=0)

customer_list_test_2=[]
for i in customer_list_test:
  if len(i)>1:
    customer_list_test_2.append(i)

purchased_cust_without_last=[]
last_purchase_cust=[]
for i in range(len(customer_list_test_2)):
  last_purchase=customer_list_test_2[i][-1]
  last_purchase_cust.append(last_purchase)  
  without_last=customer_list_test_2[i][:-1]
  purchased_cust_without_last.append(without_last)

last_purchase=pd.DataFrame(last_purchase_cust)
last_purchase.columns=['last_purchase']

average_cust=[]
for i in purchased_cust_without_last:
  average=aggregate_vectors_cust(i)
  average_cust.append(average)

pred = pd.DataFrame()
n=100
for i in range(len(customer_list_test_2)):
  a=pd.DataFrame(customer_model.similar_by_vector(average_cust[i],n))
  a=a.drop(1, axis=1).T
  pred=pd.concat([pred, a],axis=0)
pred=pred.reset_index().drop('index', axis=1)
pred=pd.concat([pred,last_purchase],axis=1)

pred

a=pd.DataFrame()
for i in range(n):
  a['correct_'+str(i)]=(pred[i]==pred['last_purchase']).astype(int)

a['correct']=a.sum(axis=1)

pred['correct']=a['correct']

accuracy_rate = pred['correct'].sum()/len(pred)
accuracy_rate