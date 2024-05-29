import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio
import networkx as nx
import missingno as msno
from mlxtend.frequent_patterns import apriori, association_rules 


product = pd.read_csv("/Users/navin/Downloads/take_home_challenge/product.csv")
purchase_header = pd.read_csv("/Users/navin/Downloads/take_home_challenge/purchase_header.csv")
purchase_lines = pd.read_csv("/Users/navin/Downloads/take_home_challenge/purchase_lines.csv")

st.title('Take Home Challenge')
st.markdown('EDA of the three provided .csv files.')

st.markdown("## Getting an idea of what the data looks like")
st.dataframe(product.head())
st.dataframe(purchase_header.head())
st.dataframe(purchase_lines.head())

merged = pd.merge(purchase_lines, purchase_header)
product_purchase = pd.merge(merged, product, on = 'PRODUCT_ID')

st.markdown("### Head of merged dataframe")
st.dataframe(product_purchase.head())

st.markdown("### Invalid Data Types")
st.markdown("Seeing if there are numeric points that are impossible (negative height, etc.) and replacing them with NA")
st.markdown("#### Sorted by height")
st.dataframe(product_purchase.sort_values("HEIGHT_INCHES").head())
st.markdown("#### Sorted by width")
st.dataframe(product_purchase.sort_values("WIDTH_INCHES").head())
st.markdown("#### Sorted by depth")
st.dataframe(product_purchase.sort_values("DEPTH_INCHES").head())
st.markdown("#### Sorted by weight")
st.dataframe(product_purchase.sort_values("WEIGHT_GRAMS").head())
product_purchase.loc[(product_purchase['HEIGHT_INCHES'] <= 0) | 
                     (product_purchase['WIDTH_INCHES'] <= 0) | 
                     (product_purchase['DEPTH_INCHES'] <= 0) | 
                     (product_purchase['WEIGHT_GRAMS'] <= 0), 
                     ['HEIGHT_INCHES', 'WIDTH_INCHES', 'DEPTH_INCHES', 'WEIGHT_GRAMS']] = np.nan
st.dataframe(product_purchase.sort_values("HEIGHT_INCHES").head())

st.markdown("## Missing Data Matrix")
msno.matrix(product_purchase)
plt.title("Missing Data Matrix")
st.pyplot(plt)
st.markdown("I will be imputing the missing data later in this report, but I wanted to see some of the interactions between columns before doing so.")

st.markdown("## Data Frame Contents")
st.write(f"There are {len(product_purchase['PURCHASE_ID'].unique())} unique orders.")
st.write(f"There are {len(product_purchase['PRODUCT_ID'].unique())} unique products.")

st.markdown("## Distribution of number of items per order")
order_counts = product_purchase.groupby('PURCHASE_ID')['QUANTITY'].count()
plt.figure(figsize=(10, 6))
sns.histplot(order_counts, bins=range(order_counts.min(), 95, 2), kde=False)
plt.xlabel("Total Number of Items in an Order")
plt.ylabel("Number of Occurrences")
st.pyplot(plt)
st.markdown("Most of the orders in the dataset contain between 5 and 25 items.")

st.markdown("## Distribution of items per product")
product_counts = product_purchase.groupby('PRODUCT_ID')['QUANTITY'].count()
plt.figure(figsize=(10, 6))
sns.histplot(product_counts, bins=range(0, 100, 2), kde=False)
plt.xlabel("Number of Items of Each Product in an Order")
st.pyplot(plt)
st.markdown("Most orders do not exceed 10 of a specific product.")

st.markdown("## Distribution of number of items from each department")
department_counts = product_purchase.groupby('DEPARTMENT_NAME')['QUANTITY'].sum()
department_counts = department_counts.sort_values()
plt.figure()
department_counts.plot(kind="barh")
plt.ylabel("Department Name")
plt.xlabel("Total Number of Items Purchased")
st.pyplot(plt)
st.markdown("Produce is by far the most popular department when it comes to most items ordered.")

st.markdown("### Investigating Produce a Little Further")
st.write(f"Number of produce items purchased: {round(product_purchase[product_purchase['DEPARTMENT_NAME'] == 'Produce']['QUANTITY'].sum(), 2)}")
st.markdown("That's interesting, not every item purchased is an integer. Let's see a few examples.")
st.dataframe(product_purchase[(product_purchase["DEPARTMENT_NAME"] == "Produce") & (product_purchase['QUANTITY'] % 1 != 0)].head())
st.markdown("It seems like a lot of produce purchases are in halves or quarters, so this could indicate weight rather than count.")

st.markdown("Produce might be the most popular when it comes to most items ordered, but which department appears in the most orders?")
st.markdown("### Distribution of most popular departments per order")
order_counts = product_purchase.groupby('DEPARTMENT_NAME').size()
order_counts = order_counts.sort_values()
plt.figure()
order_counts.plot(kind="barh")
plt.ylabel("Department Name")
plt.xlabel("Total Number of Orders that Include Each Department")
st.pyplot(plt)
st.markdown("Produce is still the most commonly ordered department, but it is not overwhelming like it was by item.")
st.markdown("This makes sense because most produce items are not bought individually like items from other departments (e.g. multiple apples vs. a stick of deodorant)")

st.markdown("## Distribution of Each Numeric Column")
fig, axs = plt.subplots(2, 2, figsize=(15,12))
sns.histplot(data=product_purchase, x="HEIGHT_INCHES", bins=range(0, 30), kde=False, ax=axs[0, 0])
axs[0,0].grid(True)
sns.histplot(data=product_purchase, x="WIDTH_INCHES", bins=range(0, 30), kde=False, ax=axs[0,1])
axs[0,1].grid(True)
sns.histplot(data=product_purchase, x="DEPTH_INCHES", bins=range(0, 30), kde=False, ax=axs[1,0])
axs[1,0].grid(True)
sns.histplot(data=product_purchase, x="WEIGHT_GRAMS", bins=500, kde=False, ax=axs[1,1])
axs[1,1].set_xlim(0,5000)
axs[1,1].grid(True)
fig.tight_layout()
st.pyplot(fig)
st.markdown("As expected, height, width, depth and weight are right-skewed, as there are typically fewer products with more extreme dimensions.")

st.markdown("#### How Height, Weight, and Depth Affect Weight")
fig, axs = plt.subplots(1, 3, figsize=(15, 12))
sns.regplot(data = product_purchase, x = "HEIGHT_INCHES", y = "WEIGHT_GRAMS", ax = axs[0])
axs[0].set_xlabel(r"Height (in)")
axs[0].set_ylabel("Weight (g)")
axs[0].set_xlim(0, 30) 
axs[0].set_ylim(0, 20000)
axs[0].grid(True)
sns.regplot(data = product_purchase, x = "WIDTH_INCHES", y = "WEIGHT_GRAMS", ax = axs[1])
axs[1].set_xlabel(r"Width (in)")
axs[1].set_ylabel("Weight (g)")
axs[1].set_xlim(0,30)
axs[1].set_ylim(0, 20000)
axs[1].grid(True)
sns.regplot(data = product_purchase, x = "DEPTH_INCHES", y = "WEIGHT_GRAMS", ax = axs[2])
axs[2].set_xlabel(r"Depth (in)")
axs[2].set_ylabel("Weight (g)")
axs[2].set_xlim(0, 30)
axs[2].set_ylim(0, 20000)
axs[2].grid(True)
fig.tight_layout()
st.pyplot(fig)
st.markdown("There seems to be some subtle linear trend between height and width to volume, but surprisingly depth has the most strong linear trend.")

st.markdown("## Side-by-side Boxplots of Departments vs. Weight")
plt.figure(figsize = (12,6))
plt.xlim(0, 10000) # ignoring outliers, getting a closer look at the boxes
sns.boxplot(data = product_purchase, x = "WEIGHT_GRAMS", y = "DEPARTMENT_NAME")
plt.xticks(rotation=90)
plt.ylabel("Department Name")
plt.xlabel("Weight (grams)")
st.pyplot(plt)
st.markdown("The heaviest departments are beverage and alcohol, which makes sense because many of those products come in boxes and packs of multiple cans/bottles.")
st.markdown("This data contains a ton of outliers, and there was one dairy item that weighed over 120,000 grams, which I'd assume was a bulk order of something like milk jugs.")
st.markdown("The lightest departments were personal care and babies, which is understandable because of items like deodorant, toothpaste or diapers.")

st.markdown("## Distributions of Date and Times")
st.markdown("For this section I sliced the string of the `PURCHASE_DATE_TIME` column to get just date and just time.")
# date column
product_purchase['PURCHASE_DATE_TIME'] = pd.to_datetime(product_purchase['PURCHASE_DATE_TIME'])
product_purchase["PURCHASE_DATE"] = product_purchase["PURCHASE_DATE_TIME"].dt.date
product_purchase["PURCHASE_TIME"] = product_purchase["PURCHASE_DATE_TIME"].dt.time

# plot
fig, ax = plt.subplots(figsize=(10,6))
date_counts = product_purchase["PURCHASE_DATE"].value_counts().sort_index()
date_counts.plot(kind="bar")
ax.set_xlabel("Date")
ax.set_ylabel("Number of Purhcases")
st.pyplot(fig)
st.markdown("This data contains dates from 3/25/2020 to 4/12/2020, but most of the data takes place in April, with April 6th and 7th being the two most popular dates.")

# day of the week column
product_purchase["DAY_OF_WEEK"] = product_purchase["PURCHASE_DATE_TIME"].dt.dayofweek
day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
product_purchase["DAY_OF_WEEK"] = product_purchase["DAY_OF_WEEK"].map(day_names)
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
product_purchase["DAY_OF_WEEK"] = pd.Categorical(product_purchase["DAY_OF_WEEK"], categories=ordered_days, ordered=True)

# plot
fig, ax = plt.subplots(figsize=(10,6))
date_counts = product_purchase["DAY_OF_WEEK"].value_counts().sort_index()
date_counts.plot(kind="bar")
ax.set_xlabel("Day of the Week")
ax.set_ylabel("Number of Purchases")
st.pyplot(fig)
st.markdown("Unfortunately all days of the week seem relatively uniform, let's dig into the top 10 most popular departments to see if there are any trends between department and day of the week.")

st.markdown("### Finding the top 10 most common departments")
most_popular = department_counts.sort_values(ascending=False).head(10)
top_10_depts = most_popular.index.tolist()
most_pop_depts = product_purchase[product_purchase["DEPARTMENT_NAME"].isin(top_10_depts)]
st.markdown("Top 10 most popular departments:")
st.write(top_10_depts)
# plot
st.markdown("### Days of the Week Distribution of Top 10 Departments")
plt.figure(figsize=(16,10))
g = sns.FacetGrid(most_pop_depts, col="DEPARTMENT_NAME", col_wrap=2, height=10, aspect=1.5)
g.map(sns.countplot, "DAY_OF_WEEK")
st.pyplot(g)
st.markdown("Surprisingly, there is not a specific trend with some departments being purchased on certain days of the week, all these distributions closely resemble the total distribution.")

st.markdown("### Most Popular Times of Day")
fig, ax = plt.subplots(figsize=(10,6))
hour_counts = product_purchase["PURCHASE_TIME"].astype(str).str[:2].astype(int).value_counts().sort_index()
hour_counts.plot(kind="bar")
ax.set_xlabel("Time (hour)")
st.pyplot(fig)
st.markdown("The middle of the day (10am - 2pm) seems to be the most popular for purchases.")

st.markdown("### Most Popular Times of Day by Top 10 Departments")
most_pop_depts['HOUR'] = most_pop_depts['PURCHASE_TIME'].astype(str).str[:2].astype(int)
g = sns.FacetGrid(most_pop_depts, col="DEPARTMENT_NAME", col_wrap=2, height=10, aspect=1.5)
g.map(plt.hist, "HOUR", bins=24, range=(0, 24))
st.pyplot(g)
st.markdown("Again, there seems to be no correlation between department and time of day of purchase, and each of these subplots seems to resemble the total distribution.")

st.markdown("## Creating a Volume Column")
product_purchase["VOLUME_INCHES"] = product_purchase["HEIGHT_INCHES"] * product_purchase["WIDTH_INCHES"] * product_purchase["DEPTH_INCHES"]
fig, ax = plt.subplots(figsize=(10,6))
sns.histplot(data=product_purchase, x="VOLUME_INCHES", bins=range(0,2000,50), kde=False)
st.pyplot(fig)
st.markdown("Volume is very heavily right-skewed, with the majority of the data between 0 and 250 in$^3$")

st.markdown("### Volume by Department")
plt.figure(figsize = (12,6))
sns.boxplot(data = product_purchase, x = "VOLUME_INCHES", y = "DEPARTMENT_NAME")
plt.xlim(0, 1750) # ignoring outliers, getting a closer look at the boxes
plt.xticks(rotation=90)
plt.ylabel("Department Name")
plt.xlabel(r"Item Volume (in$^3$)")
st.pyplot(plt)
st.markdown("Alcohol by far the department with the most voluminous items.")
st.markdown("Many alcoholic beverages come in 12-packs or large bottles, so this makes sense.")

st.markdown("## Dimensions (height, width, depth, weight) vs. Volume Scatterplots")
fig, axs = plt.subplots(2, 2, figsize=(15, 12))
sns.regplot(data = product_purchase, x = "HEIGHT_INCHES", y = "VOLUME_INCHES", ax = axs[0, 0])
axs[0, 0].set_xlabel(r"Height (in)")
axs[0, 0].set_ylabel(r"Volume (in$^3$)")
axs[0, 0].set_xlim(0, 40) 
axs[0, 0].set_ylim(0, 5000)
axs[0, 0].grid(True)
sns.regplot(data = product_purchase, x = "WIDTH_INCHES", y = "VOLUME_INCHES", ax = axs[0,1])
axs[0, 1].set_xlabel(r"Width (in)")
axs[0, 1].set_ylabel(r"Volume (in$^3$)")
axs[0, 1].set_xlim(0,25)
axs[0, 1].set_ylim(0, 5000)
axs[0, 1].grid(True)
sns.regplot(data = product_purchase, x = "DEPTH_INCHES", y = "VOLUME_INCHES", ax = axs[1,0])
axs[1, 0].set_xlabel(r"Depth (in)")
axs[1, 0].set_ylabel(r"Volume (in$^3$)")
axs[1, 0].set_xlim(0, 25)
axs[1, 0].set_ylim(0, 5000)
axs[1, 0].grid(True)
sns.regplot(data = product_purchase, x = "WEIGHT_GRAMS", y = "VOLUME_INCHES", ax = axs[1,1])
axs[1, 1].set_xlabel(r"Weight (g)")
axs[1, 1].set_ylabel(r"Volume (in$^3$)")
axs[1, 1].set_xlim(0, 6000) 
axs[1, 1].set_ylim(0, 5000)
axs[1, 1].grid(True)
fig.tight_layout()
st.pyplot(fig)
st.markdown("There seems to be a strong positive linear trend between height, width and depth width volume as expected because of the volume formula, but not as much with weight.")

st.markdown("## Creating a Density Column")
st.markdown("To do this, I need to create a `VOLUME_CM` column from `VOLUME_INCHES` for the correct units.")
product_purchase["VOLUME_CM"] = product_purchase["VOLUME_INCHES"] * 16.387
product_purchase["DENSITY"] = product_purchase["WEIGHT_GRAMS"] / product_purchase["VOLUME_CM"]
fig, ax = plt.subplots(figsize=(10,6))
sns.histplot(data=product_purchase, x="DENSITY", bins=100, kde=False)
ax.set_xlim(0,10)
st.pyplot(fig)
st.markdown("Majority of density values fall between 0 and 1 g/cm$^3$.")

fig, axs = plt.subplots(3, 2, figsize=(15, 12))

st.markdown("### Density vs. Other Dimensionality Values")
fig, axs = plt.subplots(3, 2, figsize=(15, 12))
sns.regplot(data = product_purchase, x = "HEIGHT_INCHES", y = "DENSITY", ax = axs[0, 0])
axs[0, 0].set_xlabel(r"Height (in)")
axs[0, 0].set_ylabel("Density")
axs[0, 0].set_xlim(0, 40) 
axs[0, 0].set_ylim(0, 30)
axs[0, 0].grid(True)
sns.regplot(data = product_purchase, x = "WIDTH_INCHES", y = "DENSITY", ax = axs[0,1])
axs[0, 1].set_xlabel(r"Width (in)")
axs[0, 1].set_ylabel("Density")
axs[0, 1].set_xlim(0,25)
axs[0, 1].set_ylim(0, 50)
axs[0, 1].grid(True)
sns.regplot(data = product_purchase, x = "DEPTH_INCHES", y = "DENSITY", ax = axs[1,0])
axs[1, 0].set_xlabel(r"Depth (in)")
axs[1, 0].set_ylabel("Density")
axs[1, 0].set_xlim(0, 25)
axs[1, 0].set_ylim(0, 50)
axs[1, 0].grid(True)
sns.regplot(data = product_purchase, x = "VOLUME_INCHES", y = "DENSITY", ax = axs[1,1])
axs[1, 1].set_xlabel(r"Volume (in$^3$)")
axs[1, 1].set_ylabel("Density)")
axs[1, 1].set_xlim(0, 4000) 
axs[1, 1].set_ylim(0, 50)
axs[1, 1].grid(True)
sns.regplot(data = product_purchase, x = "WEIGHT_GRAMS", y = "DENSITY", ax = axs[2,0])
axs[2, 0].set_xlabel("Weight (g)")
axs[2, 0].set_ylabel("Density)")
axs[2, 0].set_xlim(0, 6000) 
axs[2, 0].set_ylim(0, 50)
axs[2, 0].grid(True)
fig.tight_layout()
st.pyplot(fig)
st.markdown("The `regplot()` function in Python usually only plots a regression line when there is a present trend. In this case this does not seem to be the case with any dimensions and density.")

st.markdown("## Imputing Missing Values")
st.markdown("It was clear from the first missing data matrix that this dataset has a ton of missing data, specifically in the height, width, depth and weight columns.")
st.markdown("I will be filling those missing values with the department-wise mean of that specific column.")

department_dims = product_purchase[["DEPARTMENT_NAME", "HEIGHT_INCHES", "WIDTH_INCHES", "DEPTH_INCHES", "WEIGHT_GRAMS"]]
department_medians = department_dims.groupby("DEPARTMENT_NAME").transform("median")
imputed = product_purchase.copy()
imputed["HEIGHT_INCHES"] = imputed["HEIGHT_INCHES"].fillna(department_medians["HEIGHT_INCHES"])
imputed["WIDTH_INCHES"] = imputed["WIDTH_INCHES"].fillna(department_medians["WIDTH_INCHES"])
imputed["DEPTH_INCHES"] = imputed["DEPTH_INCHES"].fillna(department_medians["DEPTH_INCHES"])
imputed["WEIGHT_GRAMS"] = imputed["WEIGHT_GRAMS"].fillna(department_medians["WEIGHT_GRAMS"])
# imputed volume column
imputed["VOLUME_INCHES"] = imputed["HEIGHT_INCHES"] * imputed["WIDTH_INCHES"] * imputed["DEPTH_INCHES"]
# imputed density column
imputed["VOLUME_CM"] = imputed["VOLUME_INCHES"] * 16.387
imputed["DENSITY"] = imputed["WEIGHT_GRAMS"] / imputed["VOLUME_CM"]

msno.matrix(imputed)
plt.title("Imputed Missing Data Matrix")
st.pyplot(plt)
st.markdown("Now there are only 767 missing values in the entire dataset.")
st.markdown("After some investigation, these values were caused by 3 departments not having any dimension data for their products.")
st.markdown("These departments were Books, Cards, & Magazines, Floral, and Popular.")

st.markdown("## Redoing Scatter Plots to Identify Trends")
st.markdown("Now that data has been imputed, I will redo some of these scatter plots with regression lines to identify how imputation has impacted the trends.")
st.markdown("### Imputed Height, Width, Depth vs. Volume")
fig, axs = plt.subplots(1, 3, figsize=(15, 12))
sns.regplot(data = imputed, x = "HEIGHT_INCHES", y = "WEIGHT_GRAMS", ax = axs[0])
axs[0].set_xlabel(r"Height (in)")
axs[0].set_ylabel("Weight (g)")
axs[0].set_xlim(0, 30) 
axs[0].set_ylim(0, 20000)
axs[0].grid(True)
sns.regplot(data = imputed, x = "WIDTH_INCHES", y = "WEIGHT_GRAMS", ax = axs[1])
axs[1].set_xlabel(r"Width (in)")
axs[1].set_ylabel("Weight (g)")
axs[1].set_xlim(0,30)
axs[1].set_ylim(0, 20000)
axs[1].grid(True)
sns.regplot(data = imputed, x = "DEPTH_INCHES", y = "WEIGHT_GRAMS", ax = axs[2])
axs[2].set_xlabel(r"Depth (in)")
axs[2].set_ylabel("Weight (g)")
axs[2].set_xlim(0, 30)
axs[2].set_ylim(0, 20000)
axs[2].grid(True)
fig.tight_layout()
st.pyplot(fig) 
st.markdown("After imputation, there does not seem to be any changes to the linear trends, which is a good sign if we were to run models.")

st.markdown("### Imputed Dimensions vs. Volume")
fig, axs = plt.subplots(2, 2, figsize=(15, 12))
sns.regplot(data = imputed, x = "HEIGHT_INCHES", y = "VOLUME_INCHES", ax = axs[0, 0])
axs[0, 0].set_xlabel("Height (in)")
axs[0, 0].set_ylabel(r"Volume (in$^3$)")
axs[0, 0].set_xlim(0, 40) 
axs[0, 0].set_ylim(0, 6000)
axs[0, 0].grid(True)
sns.regplot(data = imputed, x = "WIDTH_INCHES", y = "VOLUME_INCHES", ax = axs[0,1])
axs[0, 1].set_xlabel(r"Width (in)")
axs[0, 1].set_ylabel(r"Volume (in$^3$)")
axs[0, 1].set_xlim(0,25)
axs[0, 1].set_ylim(0, 6000)
axs[0, 1].grid(True)
sns.regplot(data = imputed, x = "DEPTH_INCHES", y = "VOLUME_INCHES", ax = axs[1,0])
axs[1, 0].set_xlabel(r"Depth (in)")
axs[1, 0].set_ylabel(r"Volume (in$^3$)")
axs[1, 0].set_xlim(0, 25)
axs[1, 0].set_ylim(0, 6000)
axs[1, 0].grid(True)
sns.regplot(data = imputed, x = "WEIGHT_GRAMS", y = "VOLUME_INCHES", ax = axs[1,1])
axs[1, 1].set_xlabel("Weight (g)")
axs[1, 1].set_ylabel(r"Volume (in$^3$)")
axs[1, 1].set_xlim(0, 5000) 
axs[1, 1].set_ylim(0, 6000)
axs[1, 1].grid(True)
fig.tight_layout()
st.pyplot(fig)

st.markdown("### Imputed Dimensions vs. Density")

sns.regplot(data = imputed, x = "HEIGHT_INCHES", y = "DENSITY", ax = axs[0,0])
fig, axs = plt.subplots(3, 2, figsize=(15, 12))
sns.regplot(data = imputed, x = "HEIGHT_INCHES", y = "DENSITY", ax = axs[0,0])
axs[0, 0].set_xlabel(r"Height (in)")
axs[0, 0].set_ylabel("Density")
axs[0, 0].set_xlim(0, 40) 
axs[0, 0].set_ylim(0, 30)
axs[0, 0].grid(True)
sns.regplot(data = imputed, x = "WIDTH_INCHES", y = "DENSITY", ax = axs[0,1])
axs[0, 1].set_xlabel(r"Width (in)")
axs[0, 1].set_ylabel("Density")
axs[0, 1].set_xlim(0,25)
axs[0, 1].set_ylim(0, 50)
axs[0, 1].grid(True)
sns.regplot(data = imputed, x = "WIDTH_INCHES", y = "DENSITY", ax = axs[1,0])
axs[1, 0].set_xlabel(r"Width (in)")
axs[1, 0].set_ylabel("Density")
axs[1, 0].set_xlim(0, 25)
axs[1, 0].set_ylim(0, 50)
axs[1, 0].grid(True)
sns.regplot(data = imputed, x = "VOLUME_INCHES", y = "DENSITY", ax = axs[1,1])
axs[1, 1].set_xlabel(r"Volume (in$^3$)")
axs[1, 1].set_ylabel("Density)")
axs[1, 1].set_xlim(0, 4000) 
axs[1, 1].set_ylim(0, 50)
axs[1, 1].grid(True)
sns.regplot(data = imputed, x = "WEIGHT_GRAMS", y = "DENSITY", ax = axs[2,0])
axs[2, 0].set_xlabel("Weight (g)")
axs[2, 0].set_ylabel("Density)")
axs[2, 0].set_xlim(0, 6000) 
axs[2, 0].set_ylim(0, 50)
axs[2, 0].grid(True)
fig.tight_layout()
st.pyplot(fig)
st.markdown("It does not look like the imputation changed anything about the trends between our numerical columns.")
st.markdown("This is a great sign for model-building, as the filling of missing data did not affect the dataset very much, and if anything just decreased the proportion of outliers.")

st.markdown("## Side-by-side boxplots of imputed data")
st.markdown("### Department vs. Weight")
plt.figure(figsize = (12,6))
plt.xlim(0, 10000) # ignoring outliers, getting a closer look at the boxes
sns.boxplot(data = imputed, x = "WEIGHT_GRAMS", y = "DEPARTMENT_NAME")
plt.xticks(rotation=90)
plt.ylabel("Department Name")
plt.xlabel("Weight (grams)")
st.pyplot(plt)
st.markdown("### Department vs. Volume")
plt.figure(figsize = (12,6))
sns.boxplot(data = imputed, x = "VOLUME_INCHES", y = "DEPARTMENT_NAME")
plt.xlim(0, 1750) # ignoring outliers, getting a closer look at the boxes
plt.xticks(rotation=90)
plt.ylabel("Department Name")
plt.xlabel(r"Item Volume (in$^3$)")
st.pyplot(plt)
st.markdown("It is very clear that despite imputing our data, there are still tons of outliers, which would make running models difficult. Let's try a log transform of our numerical columns to see what difference we can make.")

st.markdown("## Log Transform for Outliers")
st.markdown("We have clearly seen that the distributions of each of the numeric variables are not very close to any known distribution and are very skewed in many cases. How would a log transformation to some of those columns affect some relationships?")

st.markdown("## Transformed vs. Non-Transformed Numeric Columns")
product_purchase["LOG_HEIGHT"] = np.log(product_purchase["HEIGHT_INCHES"])
product_purchase["LOG_WIDTH"] = np.log(product_purchase["WIDTH_INCHES"])
product_purchase["LOG_DEPTH"] = np.log(product_purchase["DEPTH_INCHES"])
product_purchase["LOG_WEIGHT"] = np.log(product_purchase["WEIGHT_GRAMS"])
st.dataframe(product_purchase[['LOG_HEIGHT', 'LOG_WIDTH', 'LOG_DEPTH', 'LOG_WEIGHT']].describe())
fig, axs = plt.subplots(2, 2, figsize=(15,12))
sns.histplot(data=product_purchase, x="LOG_HEIGHT", kde=False, bins=50, ax=axs[0,0], color='red', alpha=0.5, label='Log Height')
sns.histplot(data=product_purchase, x="HEIGHT_INCHES", kde=False, bins=range(0, 20), ax=axs[0, 0], color='blue', alpha=0.5, label='Height')
axs[0,0].set_xlim(0,20)
axs[0,0].set_xlabel("Height (in)")
axs[0,0].legend()
axs[0,0].grid(True)
sns.histplot(data=product_purchase, x="LOG_WIDTH", kde=False, bins=50, ax=axs[0,1], color='red', alpha=0.5, label='Log Width')
sns.histplot(data=product_purchase, x="WIDTH_INCHES", kde=False, bins=range(0, 20), ax=axs[0,1], color='blue', alpha=0.5, label='Width')
axs[0,1].set_xlim(0,20)
axs[0,1].set_xlabel("Width (in)")
axs[0,1].legend()
axs[0,1].grid(True)
sns.histplot(data=product_purchase, x="LOG_DEPTH", kde=False, bins=50, ax=axs[1,0], color="red", alpha=0.5, label="Log Depth")
sns.histplot(data=product_purchase, x="DEPTH_INCHES", kde=False, bins=range(0, 20), ax=axs[1,0], color='blue', alpha=0.5, label='Depth')
axs[1,0].set_xlabel("Depth (in)")
axs[1,0].legend()
axs[1,0].grid(True)
sns.histplot(data=product_purchase, x="LOG_WEIGHT", kde=False, bins=100, ax=axs[1,1], color="red", alpha=0.5, label="Log Weight")
sns.histplot(data=product_purchase, x="WEIGHT_GRAMS", bins=2000, kde=False, ax=axs[1,1], color="blue", alpha=0.5, label="Weight")
axs[1,1].set_xlim(0,1000)
axs[1,1].set_xlabel("Weight (g)")
axs[1,1].legend()
axs[1,1].grid(True)
fig.tight_layout()
st.pyplot(fig)
st.markdown("From the plots it is clear that we have shrank down the data in all dimensions, especially weight. The data is significantly more normalized and less skewed, and there are far fewer outliers.")

st.markdown("## Relationships between log height, width, and depth to weight")
fig, axs = plt.subplots(1, 3, figsize=(15, 12))
sns.regplot(data = product_purchase, x = "LOG_HEIGHT", y = "LOG_WEIGHT", ax = axs[0])
axs[0].set_xlabel(r"Log Height (in)")
axs[0].set_ylabel("Log Weight (g)")
axs[0].grid(True)
sns.regplot(data = product_purchase, x = "LOG_WIDTH", y = "LOG_WEIGHT", ax = axs[1])
axs[1].set_xlabel(r"Log Width (in)")
axs[1].set_ylabel("Log Weight (g)")
axs[1].grid(True)
sns.regplot(data = product_purchase, x = "LOG_DEPTH", y = "LOG_WEIGHT", ax = axs[2])
axs[2].set_xlabel(r"Log Width (in)")
axs[2].set_ylabel("Log Weight (g)")
axs[2].grid(True)
fig.tight_layout()
st.pyplot(fig)

st.markdown("## Side-by-Side Boxplot of Log Weight by Department")
plt.figure(figsize = (12,6))
sns.boxplot(data = product_purchase, x = "LOG_WEIGHT", y = "DEPARTMENT_NAME")
plt.ylabel("Department Name")
plt.xlabel("Log Weight (grams)")
st.pyplot(plt)
st.markdown("log transform helps a ton with bringing in outliers, we no longer have points greater than 13.")

st.markdown("## Log-Volume vs. Volume")
product_purchase["LOG_VOLUME"] = np.log(product_purchase["VOLUME_INCHES"])
fig, axs = plt.subplots(1, 2, figsize=(15, 12))
sns.histplot(data=product_purchase, x="LOG_VOLUME", bins=50, kde=False, color="red", alpha=0.5, label="Log Volume", ax=axs[0])
sns.histplot(data=product_purchase, x="VOLUME_INCHES", bins=range(0,2000,50), kde=False, color="blue", alpha=0.5, label="Volue", ax=axs[1])
axs[0].set_xlabel("Log Volume")
axs[1].set_xlabel("Volume")
axs[0].legend()
axs[1].legend()
st.pyplot(fig)
st.markdown("From this plot it is very clear that we have shrunk down our volume and nearly removed any skew.")

st.markdown("### Log Volume by Department")
plt.figure(figsize = (12,6))
sns.boxplot(data = product_purchase, x = "LOG_VOLUME", y = "DEPARTMENT_NAME")
plt.xlim(0,10)
plt.ylabel("Department Name")
plt.xlabel(r"Log Item Volume (in$^3$)")
st.pyplot(plt)
st.markdown("Box plot looks much cleaner, compared to all of the outliers from earlier. all of the data is centered from 0 to 12.")

st.markdown("## Log-Density vs. Density")
product_purchase["LOG_DENSITY"] = np.log(product_purchase["DENSITY"])
fig, axs = plt.subplots(1, 2, figsize=(15, 12))
sns.histplot(data=product_purchase, x="LOG_DENSITY", bins=50, kde=False, color="red", ax=axs[0], alpha=.5, label="Log Density")
sns.histplot(data=product_purchase, x="DENSITY", bins=100, kde=False, color="blue", ax=axs[1], alpha=0.5, label="Density")
axs[0].set_xlabel("Log Density")
axs[1].set_xlabel("Density")
axs[0].set_xlim(-5, 4)
axs[1].set_xlim(0,10)
axs[0].legend()
axs[1].legend()
st.pyplot(fig)
st.markdown("Taking the log of volume and density significantly helps with the skewness of the data, and much more closely resembles something more similar to a normal.")

st.markdown("## Imputing Log Values")
st.markdown("Now that we have seen that log values have much better shape and can be used more easily, let's impute those log values and do the rest of the analysis on those.")
log_dep_dims = product_purchase[["DEPARTMENT_NAME", "LOG_HEIGHT", "LOG_WIDTH", "LOG_DEPTH", "LOG_WEIGHT", "LOG_VOLUME", "LOG_DENSITY"]]
log_dep_medians = log_dep_dims.groupby("DEPARTMENT_NAME").transform("median")
# imputing with the median of each department
log_imputed = product_purchase.copy()
log_imputed["LOG_HEIGHT"] = log_imputed["LOG_HEIGHT"].fillna(log_dep_medians["LOG_HEIGHT"])
log_imputed["LOG_WIDTH"] = log_imputed["LOG_WIDTH"].fillna(log_dep_medians["LOG_WIDTH"])
log_imputed["LOG_DEPTH"] = log_imputed["LOG_DEPTH"].fillna(log_dep_medians["LOG_DEPTH"])
log_imputed["LOG_WEIGHT"] = log_imputed["LOG_WEIGHT"].fillna(log_dep_medians["LOG_WEIGHT"])
log_imputed["LOG_VOLUME"] = log_imputed["LOG_VOLUME"].fillna(log_dep_medians["LOG_VOLUME"])
log_imputed["LOG_DENSITY"] = log_imputed["LOG_DENSITY"].fillna(log_dep_medians["LOG_DENSITY"])
log_imputed = log_imputed[["PURCHASE_ID", "PRODUCT_ID", "QUANTITY", "PURCHASE_DATE_TIME", "DEPARTMENT_NAME", 
                           "PURCHASE_DATE", "PURCHASE_TIME", "DAY_OF_WEEK", "LOG_HEIGHT", "LOG_WIDTH", "LOG_DEPTH",
                           "LOG_WEIGHT", "LOG_VOLUME", "LOG_DENSITY"]]

st.markdown("## Missing Data Matrix of Imputed Log Values")
msno.matrix(log_imputed)
plt.title("Imputed Log Missing Data Matrix")
st.pyplot(plt)

st.markdown("## Correlation Matrix of Numerical Columns")
st.markdown("seeing how numeric columns are correlated with each other, and where we can possibly avoid multicollinearity down the road")
numeric = log_imputed[["QUANTITY", "LOG_HEIGHT", "LOG_WIDTH", "LOG_DEPTH", "LOG_WEIGHT", "LOG_VOLUME"]]
correlation_matrix = numeric.corr()
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
custom_palette = sns.diverging_palette(220, 20, as_cmap=True, s=90, l=50)
custom_palette.set_bad('white')
plt.figure(figsize=(10,8))
sns.heatmap(correlation_matrix, annot = True, cmap = custom_palette, fmt = ".2f", 
            linewidths = 0.5, mask=mask, annot_kws={"size": 12})
st.pyplot(plt)
st.markdown("There really only seems to be correlation to `LOG_VOLUME`, which makes sense because it is calculated from `LOG_HEIGHT`, `LOG_WIDTH` and `LOG_DEPTH`.")

st.markdown("# Market Basket Analysis: Apriori Algorithm")
st.markdown("Seeing how certain departments are associated with each other based on order data. I'm not sure if the data provided here is customer data or what grocery stores buy from suppliers, but if it were customer data then there could be some helpful information about the layout of stores so robots do not have to travel as far to pick up highly associated items.")
# grouping by order to find what departments they order most from
basket = log_imputed.groupby(['PURCHASE_ID', 'DEPARTMENT_NAME'])["QUANTITY"].sum().unstack().reset_index().fillna(0).set_index('PURCHASE_ID')
# encoding the basket
def hot_encode(x): 
    if(x<= 0): 
        return True
    if (x > 0): 
        return False  
basket_encoded = basket.map(hot_encode)
basket = basket_encoded
# applying the model
frq_items = apriori(basket, min_support=.6, use_colnames=True)
rules = association_rules(frq_items, metric='lift', min_threshold=1)
# filtering to find one-to-one relationships between departments
one_to_one = rules[(rules['antecedents'].apply(lambda x: len(x) == 1)) & 
                         (rules['consequents'].apply(lambda x: len(x) == 1))]
matching_pairs = []
for consequent in one_to_one["consequents"].unique():
    consequent_df = one_to_one[one_to_one["consequents"] == consequent]
    antecedents = consequent_df["antecedents"].unique()
    for antecedent in antecedents:
        antecedent_df = one_to_one[one_to_one["antecedents"] == antecedent]
        for index, row in antecedent_df.iterrows():
            if row['consequents'] == consequent:
                matching_pairs.append((consequent, antecedent))
matching_consequents = set(pair[0] for pair in matching_pairs)
matching_antecedents = set(pair[1] for pair in matching_pairs)
two_way = one_to_one[
    (one_to_one['consequents'].isin(matching_consequents)) & 
    (one_to_one['antecedents'].isin(matching_antecedents))
]
two_way = two_way.sort_values(['confidence', 'lift'], ascending=[False, False])
high_conf = two_way[two_way["confidence"] >= .95]
st.dataframe(high_conf.head())
st.markdown("The confidence value in this table represents the probability that one department is present if another one is present. For example, the top value of the table is household and books, cards and magazines, and the confidence value  is 0.999707. This means that 99.97% of the orders that contain household values also contain a books, cards and magazines item.")
st.markdown("If this is customer data, then we can take this data to help change the layout of a store, placing the household department next to books, cards and magazines. Therefore the robots will not have to travel as far and we can save energy. ")

st.markdown("## Directed Graph of Highly Associated Departments")
G = nx.DiGraph()

for _, row in high_conf.iterrows():
    antecedent = list(row['antecedents'])[0]
    consequent = list(row['consequents'])[0]
    confidence = round(row['confidence'], 2)
    
    G.add_edge(antecedent, consequent, weight=confidence)

pos = nx.shell_layout(G)
plt.figure(figsize=(12, 8))
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

plt.title('Directed Graph of Association Rules (Confidence Greater than 0.95)')
st.pyplot(plt)

st.markdown("Here are the most highly associated departments (confidence >= .95), meaning that orders with one department are highly more likely to contain orders from another department. These are all two-way relationships, but I was having some issues making sure that all the arrows were in two directions.")