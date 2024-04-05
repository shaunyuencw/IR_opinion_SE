import React, { useState } from 'react';
import { AppBar, Toolbar, Box, TextField, IconButton, useTheme, useMediaQuery } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';

const Header = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const navigate = useNavigate();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    const handleSearch = (e) => {
        e.preventDefault(); // Prevent the default form submit action
        navigate(`/${searchQuery}`); // Navigate to the search route
    };

    return (
        <AppBar position="static" color="primary" elevation={1} sx={{ borderRadius: 8, margin: theme.spacing(2), justifyContent: 'center' }}>
            <Toolbar sx={{ justifyContent: 'center', padding: theme.spacing(0, 2) }}>
                {/* Centralized Search Box with Rounded Corners */}
                <Box 
                    component="form" // This Box acts as a form
                    onSubmit={handleSearch} // Handle form submission
                    sx={{ position: 'relative', display: 'inline-flex', width: isMobile ? '100%' : '50%', maxWidth: 600 }}
                >
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Search stock ticker (e.g., AAPL)"
                        size="small"
                        value={searchQuery} // Controlled component with searchQuery state
                        onChange={(e) => setSearchQuery(e.target.value)} // Update state on change
                        sx={{
                            borderRadius: 20,
                            backgroundColor: theme.palette.background.paper,
                            "& .MuiOutlinedInput-root": {
                                borderRadius: 20,
                            },
                            "& fieldset": {
                                borderWidth: `2px`,
                            },
                            "&:hover fieldset": {
                                borderColor: 'secondary.main',
                            },
                            "& .Mui-focused fieldset": {
                                borderColor: theme.palette.secondary.main,
                            },
                        }}
                        InputProps={{
                            endAdornment: (
                                <IconButton type="submit" aria-label="search" sx={{ borderRadius: '50%' }}>
                                    <SearchIcon />
                                </IconButton>
                            ),
                        }}
                    />
                </Box>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
