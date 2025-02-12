# University Recommender

The **University Recommender System** is a web-based application that helps students find suitable universities based on their preferred **Stream**, **State**, and **Tuition Fees**. The project consists of a **React frontend** for user interaction and a **Flask backend** powered by machine learning models to recommend universities.

## 🔹 Features

✅ **User-Friendly Interface** – Enter your preferred stream and state to receive recommendations.  
✅ **Machine Learning-Powered Recommendations** – Uses **K-Means, DBSCAN, and Hierarchical Clustering** for intelligent suggestions.  
✅ **Dynamic Data Processing** – Cleans, encodes, and scales university data for accurate recommendations.  
✅ **Flask API** – Handles search queries and returns relevant universities.  

## 🔹 Tech Stack

- **Frontend:** React, Axios, CSS  
- **Backend:** Flask, Pandas, NumPy, Scikit-learn  
- **Database:** CSV-based dataset (can be extended to a database)  
- **Modeling:** PCA, K-Means, DBSCAN, Agglomerative Clustering  

## 🔹 How It Works

1. The user enters their **preferred stream** and **state** in the search form.  
2. The frontend sends the request to the Flask API at `http://localhost:5000/recommend`.  
3. The backend loads university data, processes it, and applies **ML clustering algorithms**.  
4. The recommended universities are sent back and displayed in a **table format** on the website. 
