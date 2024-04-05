import React from 'react';
import ReactSpeedometer from 'react-d3-speedometer';

const SentimentSpeedometer = ({ rating }) => {
    const sentimentLabels = ['Str. Negative', 'Negative', 'Neutral', 'Positive', 'Str. Positive'];

    // Normalize the rating to a scale of 1-5
    const normalizeRating = (rating) => {
        // Each segment represents a range of 200 (1000/5)
        return Math.ceil(rating / 200);
    };

    // Get sentiment label based on normalized rating
    const getSentimentLabel = (rating) => {
        const normalizedRating = normalizeRating(rating);
        // Adjust for array indexing starting at 0
        const index = Math.min(Math.max(normalizedRating, 1), 5) - 1;
        return sentimentLabels[index];
    };

    return (
        <div style={{ textAlign: 'center' }}>
            <ReactSpeedometer
                value={rating} // Use the normalized rating for the value
                width={500}
                segments={5}
                customSegmentLabels={sentimentLabels.map((label, index) => ({
                    text: label,
                    position: 'OUTSIDE',
                    color: '#333',
                }))}
                needleColor={'#000000'}
                needleTransitionDuration={4000}
                needleTransition="easeElastic"
                currentValueText={`Sentiment Rating: ${getSentimentLabel(rating)}`}
            />
        </div>
    );
};

export default SentimentSpeedometer;
