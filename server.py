from flask import Flask, request,jsonify,json, make_response
from flask_cors import CORS
from waitress import serve
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

with open('kmeans_model.pkl', 'rb') as f:
    kmeans_model = pickle.load(f)
with open('dbscan_model.pkl', 'rb') as f:
    dbscan_model = pickle.load(f)
with open('hc_model.pkl', 'rb') as f:
    hc_model = pickle.load(f)


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
    df = pd.concat([df[['College_Name', 'Stream', 'State']], standardized_df], axis=1)
    #pca_df = pd.concat([pca_df[['PC1', 'PC2']], standardized_df[['cluster']]], axis=1)
    df.dropna(inplace=True)

    # Filter universities based on user input
    UG_min, UG_max = UGfees_scaled
    df_filtered = df[(df['UGfees_scaled'] >= UG_min) & (df['UGfees_scaled'] <= UG_max)]
    df_filtered = df_filtered[df_filtered['State'].str.contains(State, case=False, na=False)]
    df_filtered = df_filtered[df_filtered['Stream'].str.contains(Stream, case=False, na=False)]
    
    
    pca_df['kmeans_cluster'] = kmeans_model.predict(pca_df[['PC1', 'PC2']])
    pca_df['dbscan_cluster'] = dbscan_model.fit_predict(pca_df[['PC1', 'PC2']])

    dissimilarity_matrix = pairwise_distances(pca_df, metric='euclidean')
    pca_df['hc_cluster'] = hc_model.fit_predict(dissimilarity_matrix)
    
    df = pd.concat([pca_df[['kmeans_cluster','dbscan_cluster','hc_cluster']],df], axis=1)
    df_filtered = df_filtered.merge(pca_df[['PC1', 'PC2', 'kmeans_cluster', 'dbscan_cluster', 'hc_cluster']], left_index=True, right_index=True, how='left')
    return df_filtered

@app.route("/")
def hello_world():
    return ("Hello World")

@app.route('/recommend',methods=['POST','OPTIONS'])
def api_create_order():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "POST": # The actual request following the preflight
        return recommend()
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def recommend():
    #user_criteria = [x for x in request.form.values()]
    #final = [np.array(user_criteria)]

    data = request.json
    Stream = data['Stream']
    State = data['State']
    UGfees_scaled = (0.0, 1.0) 

    recommended_universities = RecommendUni(Stream, State, UGfees_scaled)
    
    # Convert DataFrame to JSON
    response = recommended_universities.to_json(orient='columns')
    
    return jsonify(json.loads(response))
    

if __name__ == "__main__":
    serve(app, host="localhost", port=5000)