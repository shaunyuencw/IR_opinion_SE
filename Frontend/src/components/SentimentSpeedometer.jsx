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
        const normalizedRating = normalizeRating(getSentimentRating(rating));
        // Adjust for array indexing starting at 0
        const index = Math.min(Math.max(normalizedRating, 1), 5) - 1;
        return sentimentLabels[index];
    };

    // Convert the overall normalized sentimental score from [-1, 1] to [0, 1000]
    const getSentimentRating = (score) => {
        return ((score + 1)/2 * 1000);
    }

    return (
        <div style={{ textAlign: 'center' }}>
            <ReactSpeedometer
                value={getSentimentRating(rating)} // Use the normalized rating for the value
                valueTextFontSize='22px'
                valueTextFontWeight='bold'
                paddingVertical={17}
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
                currentValueText={`Overall Rating: ${getSentimentLabel(rating)} (${Math.round(rating * 100) / 100})`}
            />
        </div>
    );
};

export default SentimentSpeedometer;
