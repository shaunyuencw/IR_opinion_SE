import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, TextField, IconButton, useTheme, useMediaQuery, Autocomplete } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';
import { debounce } from 'lodash';

const Header = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const navigate = useNavigate();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    // Debounce the fetchSuggestions function to avoid too many calls
    const fetchSuggestions = debounce(async (query) => {
        if (query.length >= 3) {
            // const response = await fetch(`https://ticker-2e1ica8b9.now.sh/keyword/${query}`);
            const response = await fetch(`/api/query?search_term=${query}`);
            const data = await response.json();
            setSuggestions(data);
        } else {
            setSuggestions([]);
        }
    }, 300); // Adjust debounce time as needed

    useEffect(() => {
        fetchSuggestions(searchQuery);
    }, [searchQuery]);

    const handleSearch = (event, value, reason) => {
        if (reason === 'selectOption' && value) {
            // When a suggestion is selected, navigate using its symbol
            navigate(`/${value.symbol}`);
        } else if (reason === 'createOption' || reason === 'blur') {
            // When the user types a custom value and presses enter or the input loses focus
            navigate(`/${searchQuery}`);
        }
    };

    return (
        <AppBar position="static" color="primary" elevation={1} sx={{ borderRadius: 8, margin: theme.spacing(2), justifyContent: 'center' }}>
            <Toolbar sx={{ justifyContent: 'center', padding: theme.spacing(0, 2) }}>
                <Autocomplete
                    freeSolo
                    disableClearable
                    options={suggestions}
                    sx={{ position: 'relative', display: 'inline-flex', width: isMobile ? '100%' : '50%', maxWidth: 600 }}
                    getOptionLabel={(option) => `${option.name} (${option.symbol})`}
                    onInputChange={(event, newInputValue) => {
                        setSearchQuery(newInputValue);
                    }}
                    inputValue={searchQuery}
                    onChange={handleSearch}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            fullWidth
                            variant="outlined"
                            placeholder="Search stock ticker (e.g., AAPL, Apple)"
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
                                        <IconButton onClick={(e) => handleSearch(e, { symbol: searchQuery }, 'createOption')} aria-label="search" sx={{ borderRadius: '50%' }}>
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
