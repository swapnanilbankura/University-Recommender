import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import pairwise_distances
from scipy.cluster.hierarchy import linkage
from sklearn.cluster import AgglomerativeClustering
import warnings
import pickle

warnings.filterwarnings("ignore")


# Function to perform K-means clustering
def Kmeans(standardized_df, pca_df):
    kmeans = KMeans(n_clusters=5, random_state=42)
    standardized_df['cluster'] = kmeans.fit_predict(pca_df[['PC1', 'PC2']])
    standardized_df.dropna(inplace=True)
    with open('kmeans_model.pkl', 'wb') as f:
        pickle.dump(kmeans,f)

# Function to perform DBSCAN clustering
def Dbscan(standardized_df, df):
    X = standardized_df[['PC1','PC2','State_encoded','UGfees_scaled','Stream_Agriculture','Stream_Arts','Stream_Commerce','Stream_Engineering','Stream_Hotel-management','Stream_Law','Stream_Management','Stream_Medical','Stream_Pharmacy','Stream_Science']]
    y = standardized_df['cluster']
    k_best = SelectKBest(score_func=f_classif, k=4)
    X_selected = k_best.fit_transform(X, y)

    dbscan = DBSCAN(eps=1.0, min_samples=5)
    labels = dbscan.fit_predict(X_selected)

    labels_df = pd.DataFrame(labels, columns=['Labels'])
    df = pd.concat([labels_df, df], axis=1)
    standardized_df = pd.concat([labels_df, standardized_df], axis=1)
    df.dropna(inplace=True)
    with open('dbscan_model.pkl', 'wb') as f:
        pickle.dump(dbscan,f)

    #print("Unique labels found by DBSCAN:", set(labels))
    #print(complete_df)

# Function to perform hierarchical clustering
def Hierarch(pca_df):
    dissimilarity_matrix = pairwise_distances(pca_df, metric='euclidean')
    Z = linkage(dissimilarity_matrix, method='complete')

    hc = AgglomerativeClustering(n_clusters=3, metric='precomputed', linkage='complete')
    y_hc = hc.fit_predict(dissimilarity_matrix)

    hcluster_df = pd.DataFrame(y_hc, columns=['Hierarch clusters'])
    pca_df = pd.concat([hcluster_df, pca_df], axis=1)
    with open('hc_model.pkl', 'wb') as f:
        pickle.dump(hc,f)
    #print(pca_df)

# Function to recommend universities
def RecommendUni(Stream, State, UGfees_scaled):

    file = pd.read_csv("C:/Users/Admin/Dropbox/PC/Downloads/College_data (1).csv")
    file = file[['College_Name', 'State', 'Stream', 'UG_fee']]
    df = pd.DataFrame(file)
    df.dropna(inplace=True)
    df['UG_fee'] = df['UG_fee'].str.strip().replace({'\$': '', ',': '', '--': ''}, regex=True)
    df['UG_fee'] = pd.to_numeric(df['UG_fee'], errors='coerce')
    df.dropna(subset=['UG_fee'], inplace=True)

    # Initialize scalers and encoders
    scaler = StandardScaler()
    min_max_scaler = MinMaxScaler()
    label_encoder = LabelEncoder()
    onehot_encoder = OneHotEncoder(sparse_output=False)

    # Encode and scale features
    courses_encoded = onehot_encoder.fit_transform(df[['Stream']])
    df['State_encoded'] = label_encoder.fit_transform(df['State'])
    df['UGfees_scaled'] = min_max_scaler.fit_transform(df[['UG_fee']])

    # Create DataFrame for encoded features
    feature_names = onehot_encoder.get_feature_names_out(['Stream'])
    courses_encoded_df = pd.DataFrame(courses_encoded, columns=feature_names)

    # Combine all features into a single DataFrame
    combined_features = pd.concat([df[['State_encoded', 'UGfees_scaled']], courses_encoded_df], axis=1)
    combined_features.columns = combined_features.columns.astype(str)

    # Standardize the features
    standardized_features = scaler.fit_transform(combined_features)

    # Convert the standardized features back to a DataFrame
    standardized_df = pd.DataFrame(standardized_features, columns=['State_encoded', 'UGfees_scaled'] + list(feature_names))
    standardized_df.dropna(inplace=True)

    # Perform PCA
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(standardized_df)

    # Convert PCA features to a DataFrame
    pca_df = pd.DataFrame(pca_features, columns=['PC1', 'PC2'])
    standardized_df = pd.concat([pca_df, standardized_df], axis=1)

    Kmeans(standardized_df, pca_df)
    df = pd.concat([df[['College_Name', 'Stream', 'State']], standardized_df], axis=1)
    pca_df = pd.concat([standardized_df[['cluster']],pca_df], axis=1)
    df.dropna(inplace=True)   
       
    Dbscan(standardized_df, df)

    Hierarch(pca_df)

    UG_min, UG_max = UGfees_scaled
    df_filtered = df[(df['UGfees_scaled'] >= UG_min) & (df['UGfees_scaled'] <= UG_max)]
    df_filtered = df_filtered[df_filtered['State'].str.contains(State, case=False, na=False)]
    df_filtered = df_filtered[df_filtered['Stream'].str.contains(Stream, case=False, na=False)]
    
    return df_filtered

# Example user input
Stream = input("Enter choice of Stream: ")
UGfees_scaled = (0, 1)  # Normalized price range
State = input("Enter State: ")


recommended_universities = RecommendUni(Stream, State, UGfees_scaled)
print(recommended_universities)


