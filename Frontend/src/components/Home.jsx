import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import { Container, Box, Typography, Grid, Divider } from '@mui/material';
import Header from './Header';
import SentimentSpeedometer from './SentimentSpeedometer';

const Home = () => {
    const { id } = useParams();
    const [data, setData] = useState(null);

    useEffect(() => {
        // Fetch stock data from the backend when component mounts or id changes
        fetch(`/api/${id}`)
            .then(res => res.json())
            .then(data => {
                setData(data)
                console.log(data);
            })
            .catch((error) => {
                console.error("Failed to fetch data:", error);
            });
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
                                <Grid item xs={12} md={6}>
                                    <Typography variant="h6" fontWeight="700">
                                        Tesla to open new factory in Texas
                                    </Typography>
                                    <Typography>
                                        Tesla Inc. will open a new factory in Austin, Texas, to produce its Cybertruck, Semi, Model 3, and Model Y vehicles. The company has already started construction on the site, which will be the largest Tesla factory in the world.
                                    </Typography>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Typography variant="h6" fontWeight="700">
                                        Tesla to open new factory in Texas
                                    </Typography>
                                    <Typography>
                                        Tesla Inc. will open a new factory in Austin, Texas, to produce its Cybertruck, Semi, Model 3, and Model Y vehicles. The company has already started construction on the site, which will be the largest Tesla factory in the world.
                                    </Typography>
                                </Grid>
                            </Grid>
                        </Box>
                    </Box>
                )}
            </Container>
        </>
    );
};

export default Home;
