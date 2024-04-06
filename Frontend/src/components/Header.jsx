import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Box, TextField, IconButton, useTheme, useMediaQuery, Autocomplete } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';
import { debounce } from 'lodash'; // Make sure to install lodash for the debounce function

const Header = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const navigate = useNavigate();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    // Debounce the fetchSuggestions function to avoid too many calls
    const fetchSuggestions = debounce(async (query) => {
        if (query.length >= 3) {
            const response = await fetch(`https://ticker-2e1ica8b9.now.sh/keyword/${query}`);
            const data = await response.json();
            setSuggestions(data);
        } else {
            setSuggestions([]);
        }
    }, 300); // Adjust debounce time as needed

    useEffect(() => {
        fetchSuggestions(searchQuery);
    }, [searchQuery]);

    const handleSearch = (e, value) => {
        e.preventDefault(); // Prevent the default form submit action
        const query = value?.symbol || searchQuery; // Use the selected suggestion's symbol if available
        navigate(`/${query}`); // Navigate to the search route
    };

    return (
        <AppBar position="static" color="primary" elevation={1} sx={{ borderRadius: 8, margin: theme.spacing(2), justifyContent: 'center' }}>
            <Toolbar sx={{ justifyContent: 'center', padding: theme.spacing(0, 2) }}>
                {/* Use Autocomplete component to enable suggestions */}
                <Autocomplete
                    freeSolo
                    disableClearable
                    options={suggestions}
                    sx={{ position: 'relative', display: 'inline-flex', width: isMobile ? '100%' : '50%', maxWidth: 600 }}
                    getOptionLabel={(option) => option.name || ''}
                    onInputChange={(event, newInputValue) => {
                        setSearchQuery(newInputValue);
                    }}
                    inputValue={searchQuery}
                    onChange={handleSearch} // Handle selection
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            fullWidth
                            variant="outlined"
                            placeholder="Search stock ticker (e.g., AAPL)"
                            size="small"
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
                                ...params.InputProps,
                                endAdornment: (
                                    <>
                                        {params.InputProps.endAdornment}
                                        <IconButton type="submit" aria-label="search" sx={{ borderRadius: '50%' }}>
                                            <SearchIcon />
                                        </IconButton>
                                    </>
                                ),
                            }}
                        />
                    )}
                />
            </Toolbar>
        </AppBar>
    );
};

export default Header;
