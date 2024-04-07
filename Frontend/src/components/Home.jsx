import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import { Container, Box, Typography, Grid, Divider, Chip, Avatar } from '@mui/material';
import Header from './Header';
import SentimentSpeedometer from './SentimentSpeedometer';

const Home = () => {
    const { id } = useParams();
    const [data, setData] = useState(null);

    const fetchData = async () => {
        const response = await fetch(`/api/info?ticker=${id}`);
        const data = await response.json();
        setData(data);
    };

    useEffect(() => {
        fetchData();
    }, [id]);


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
                        <Box sx={{ borderBottom: 1, borderColor: 'divider', pb: 2, mb: 2 }}>
                            <Typography variant="h4" component="h1" fontWeight="700">
                                {data.name}
                            </Typography>
                            <Typography variant="h5" component="h2" fontWeight="100">
                                NASDAQ: {data.name}
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
                                <SentimentSpeedometer rating={500} />
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

                        <Box sx={{ my: 4 }}>
                            <Typography variant="h6" component="h2" fontWeight="300" sx={{ borderBottom: 1, borderColor: 'divider', pb: 1, mb: 2 }}>
                                Latest News
                            </Typography>
                            <Grid container spacing={2}>
                                {data.news.filter(newsItem => newsItem.source && newsItem.link).map((newsItem, index) => (
                                    <Grid container spacing={2} key={index}>
                                        {/* Sentiment Analysis Section */}
                                        <Grid item xs={12} md={3}>
                                            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', mb: 2 }}>
                                                Sentiment Analysis
                                            </Typography>
                                            {/* You can add the sentiment analysis content here */}
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
