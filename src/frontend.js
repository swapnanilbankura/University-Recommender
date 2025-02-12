import React from 'react';
import { useState} from 'react';
import axios from 'axios';
import './frontend.css';

const RecommendForm = ()=>{

    const [formData, setFormData] = useState({
        Stream: '',
        State: '',
    });
    const [recommendations, setRecommendations] = useState(null);
    
    const handleChange = (e)=>{
        const { name, value} = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleSearchSubmit = async(e)=>{
        e.preventDefault();
        try{
            const response = await axios.post('http://localhost:5000/recommend', formData, {
                headers:{
                    'Content-Type': 'application/json'
                },
            });
            setRecommendations(response.data);
             console.log(recommendations);

        }catch(error){
            console.error('Error sending data:', error);
        }   
    };

    return(
        <div class='master'>
            <h1>University Recommendation System</h1>
            <form onSubmit={handleSearchSubmit}>
                <div>
                    <label> Stream :</label>
                    <input type="text" name="Stream" value={formData.Stream} onChange={handleChange} required />
                </div>
                <div>
                    <label>State :</label>
                    <input type="text" name="State" value={formData.State} onChange={handleChange} required />
                </div>
                <button type="submit" id='btn'>Get Recommendations</button>
            </form>
            <div>
                {recommendations && (
                    <div>
                        <h2>Here are some options-</h2>
                        <table border="1">
                            <thead>
                                <tr>
                                    <th>College Name</th>
                                    <th>State</th>
                                    <th>Stream</th>
                                    <th>UG Fees Scaled</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.keys(recommendations.College_Name).map((key) => (
                                    <tr key={key}>
                                        <td>{recommendations.College_Name[key]}</td>
                                        <td>{recommendations.State[key]}</td>
                                        <td>{recommendations.Stream[key]}</td>
                                        <td>{recommendations.UGfees_scaled[key]}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );

};

export default RecommendForm;