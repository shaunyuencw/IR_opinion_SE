import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { CircularProgress, Container, Box, Typography, Grid, Chip, Avatar, FormControl, InputLabel, Select, MenuItem, Stack } from '@mui/material';
import Header from './Header';
import SentimentSpeedometer from './SentimentSpeedometer';

const Home = () => {
    const { id } = useParams();
    const [data, setData] = useState(null);
    const [sentimentFilter, setSentimentFilter] = useState('');

    const fetchData = async () => {
        const response = await fetch(`/api/info?ticker=${id}`);
        const data = await response.json();
        setData(data);
    };

    useEffect(() => {
        fetchData();
    }, [id]);

    // Determine the color of the chip based on the sentiment
    const getColor = (sentiment) => {
        switch (sentiment.toLowerCase()) {
            case 'positive':
                return 'success';
            case 'negative':
                return 'error';
            case 'neutral':
                return 'warning';
            default:
                return 'default';
        }
    };

    // Function to count articles by sentiment
    const countArticlesBySentiment = () => data ? data.news.reduce((acc, curr) => {
        const sentiment = curr.sentiment.sentiment.toLowerCase();
        acc[sentiment] = (acc[sentiment] || 0) + 1;
        return acc;
    }, {positive: 0, neutral: 0, negative: 0}) : {positive: 0, neutral: 0, negative: 0};

    const sentimentCounts = data ? countArticlesBySentiment() : {positive: 0, neutral: 0, negative: 0};

    return (
        <>
            <Container>
                {data === null ? (
                    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                        <CircularProgress size={150} />
                    </Box>
                ) : (
                    <Box sx={{ my: 4 }}>
                        <Header />
                        <Box sx={{ borderBottom: 1, borderColor: 'divider', pb: 2, mb: 2, pt: 8 }}>
                            <Typography variant="h4" component="h1" fontWeight="700">
                                {data.name}
                            </Typography>
                        </Box>

                        <Grid container spacing={2} sx={{ borderBottom: 1, borderColor: 'divider', pb: 2 }}>
                            <Grid item xs={12} sm={6} md={3}>
                                <Typography variant='h6'>Sector</Typography>
                                <Typography>{data.info.sector}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6} md={3}>
                                <Typography variant='h6'>Country</Typography>
                                <Typography>{data.info.country}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6} md={3}>
                                <Typography variant='h6'>Employee</Typography>
                                <Typography>{data.info.employees}</Typography>
                            </Grid>
                            <Grid item xs={12} sm={6} md={3}>
                                <Typography variant='h6'>Website</Typography>
                                <Typography>{data.info.website}</Typography>
                            </Grid>
                        </Grid>

                        <Box sx={{ my: 4 }}>
                            <Typography variant="h6" component="h2" fontWeight="300" sx={{ borderBottom: 1, borderColor: 'divider', pb: 1, mb: 2 }}>
                                Sentiment Analysis
                            </Typography>
                            <Typography textAlign="justify">
                                <SentimentSpeedometer rating={data.sentimental_score} />
                            </Typography>
                        </Box>

                        <Box sx={{ my: 4 }}>
                            <Typography variant="h6" component="h2" fontWeight="300" sx={{ borderBottom: 1, borderColor: 'divider', pb: 1, mb: 2 }}>
                                Summary
                            </Typography>
                            <Typography textAlign="justify">
                                {data.info.summary}
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Stack direction="row" spacing={1}>
                                <Chip label={`Total Articles: ${data.news.length}`} />
                                <Chip label={`Positive: ${sentimentCounts.positive}`} color="success" />
                                <Chip label={`Neutral: ${sentimentCounts.neutral}`} color="warning" />
                                <Chip label={`Negative: ${sentimentCounts.negative}`} color="error" />
                            </Stack>
                            <FormControl variant="outlined" sx={{ minWidth: 180 }}>
                                <InputLabel>Sentiment Filter</InputLabel>
                                <Select
                                    value={sentimentFilter}
                                    onChange={(e) => setSentimentFilter(e.target.value)}
                                    label="Sentiment Filter"
                                >
                                    <MenuItem value="">All</MenuItem>
                                    <MenuItem value="positive">Positive</MenuItem>
                                    <MenuItem value="neutral">Neutral</MenuItem>
                                    <MenuItem value="negative">Negative</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>

                        <Box sx={{ my: 4 }}>
                            <Typography variant="h6" component="h2" fontWeight="300" sx={{ borderBottom: 1, borderColor: 'divider', pb: 1, mb: 2 }}>
                                Latest News
                            </Typography>
                            <Grid container spacing={2}>
                                {data.news.filter(newsItem => sentimentFilter === '' || newsItem.sentiment.sentiment.toLowerCase() === sentimentFilter).map((newsItem, index) => (
                                    <Grid container spacing={2} mt={2} key={index}>
                                        {/* Sentiment Analysis Section */}
                                        <Grid item xs={12} md={3}>
                                            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', p: 2 }}>
                                                <Chip
                                                    label={`${newsItem.sentiment.sentiment} | Confidence: ${Math.round(newsItem.sentiment.confidence * 100)}%`}
                                                    color={getColor(newsItem.sentiment.sentiment)}
                                                    size="large"
                                                />
                                            </Typography>
                                            <Typography variant="body2" component="div" sx={{ mb: 1 }}>

                                            </Typography>
                                        </Grid>

                                        {/* News Content Section */}
                                        <Grid item xs={12} md={9}>
                                            <Box display="flex" flexDirection="column">
                                                <Box display="flex" alignItems="center" marginBottom={1}>
                                                    {newsItem.source && newsItem.source.icon ? (
                                                        <Avatar src={newsItem.source.icon} alt={newsItem.source.name} sx={{ width: 48, height: 48, marginRight: 2 }} />
                                                    ) : (
                                                        <Avatar sx={{ width: 48, height: 48, marginRight: 2 }} />
                                                    )}
                                                    <Typography variant="h6" fontWeight="700" component="a" href={newsItem.link} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: 'inherit' }}>
                                                        {newsItem.title}
                                                    </Typography>
                                                </Box>
                                                <Typography variant="body2" color="textSecondary">
                                                    {newsItem.source ? newsItem.source.name : 'Unknown Source'} by {newsItem.source && newsItem.source.authors ? newsItem.source.authors.join(", ") : 'Anonymous'}
                                                </Typography>
                                                {newsItem.thumbnail && (
                                                    <Box component="img" src={newsItem.thumbnail} alt="News thumbnail" sx={{ width: '100%', mt: 2, borderRadius: 2 }} onError={(e) => { e.target.style.display = 'none'; }} />
                                                )}
                                                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                                                    {newsItem.date}
                                                </Typography>
                                            </Box>
                                        </Grid>
                                    </Grid>
                                ))}

                            </Grid>
                        </Box>

                    </Box>
                )}
            </Container>
        </>
    );
};

export default Home;
