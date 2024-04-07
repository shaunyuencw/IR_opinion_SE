import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, TextField, IconButton, Button, useTheme, useMediaQuery, Autocomplete, MenuItem, Select, FormControl, InputLabel, Box, Collapse, Typography } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowDropUpIcon from '@mui/icons-material/ArrowDropUp';
import { useNavigate } from 'react-router-dom';
import { debounce } from 'lodash';

const Header = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [exactPhrase, setExactPhrase] = useState('');
    const [includeWords, setIncludeWords] = useState('');
    const [excludeWords, setExcludeWords] = useState('');
    const [exchangeType, setExchangeType] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const navigate = useNavigate();
    const theme = useTheme();

    const fetchSuggestions = debounce(async () => {
        if (searchQuery.length >= 3) {
            const queryParts = [];
            if (searchQuery) queryParts.push(`search_term=${searchQuery}`);
            if (exactPhrase) queryParts.push(`exact_phrase=${exactPhrase}`);
            if (includeWords) queryParts.push(`include_words=${includeWords}`);
            if (excludeWords) queryParts.push(`exclude_words=${excludeWords}`);
            if (exchangeType) queryParts.push(`exchange_type=${exchangeType}`);
            const queryString = queryParts.join('&');

            const response = await fetch(`/api/query?${queryString}`);
            const data = await response.json();
            setSuggestions(data);
        } else {
            setSuggestions([]);
        }
    }, 300);

    useEffect(() => {
        fetchSuggestions();
    }, [searchQuery, exactPhrase, includeWords, excludeWords, exchangeType]);

    const handleSearch = (event, value) => {
        event.preventDefault();
        if (value && value.symbol) {
            navigate(`/${value.symbol}`);
        } else {
            navigate(`/${searchQuery}`);
        }
    };

    return (
        <AppBar position="static" elevation={1} sx={{ margin: theme.spacing(0), padding: '20px', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', borderRadius: 8, background: '#93c5fd' }}>
            <Toolbar sx={{ width: '100%', justifyContent: 'space-between', padding: theme.spacing(0) }}>
                <IconButton onClick={(e) => handleSearch(e, { symbol: searchQuery })} aria-label="search" color="inherit">
                    <SearchIcon fontSize="large" />
                </IconButton>
                <Autocomplete
                    freeSolo
                    disableClearable
                    color="inherit"
                    options={suggestions}
                    sx={{ width: '90%' }}
                    getOptionLabel={(option) => `${option.name} (${option.symbol})`}
                    onInputChange={(event, newInputValue) => {
                        setSearchQuery(newInputValue);
                    }}
                    inputValue={searchQuery}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            fullWidth
                            variant="outlined"
                            placeholder="Search stock ticker (e.g., AAPL, Apple)"
                            size="medium"
                        />
                    )}
                />
                <IconButton onClick={() => setShowAdvanced(!showAdvanced)} aria-label="expand">
                    {showAdvanced ? <ArrowDropUpIcon fontSize="large" /> : <ArrowDropDownIcon fontSize="large" />}
                </IconButton>
            </Toolbar>
            <Collapse in={showAdvanced} sx={{ width: '100%' }}>
                <Typography variant="h6" sx={{ my: 2, color: '#020617' }}>Narrow your search result</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}>
                    <TextField
                        label="Exact Phrase"
                        variant="outlined"
                        size="medium"
                        fullWidth
                        value={exactPhrase}
                        onChange={(e) => setExactPhrase(e.target.value)}
                    />
                    <TextField
                        label="Include Words"
                        variant="outlined"
                        size="medium"
                        fullWidth
                        value={includeWords}
                        onChange={(e) => setIncludeWords(e.target.value)}
                    />
                    <TextField
                        label="Exclude Words"
                        variant="outlined"
                        size="medium"
                        fullWidth
                        value={excludeWords}
                        onChange={(e) => setExcludeWords(e.target.value)}
                    />
                    <FormControl fullWidth size="medium">
                        <InputLabel>Exchange Type</InputLabel>
                        <Select
                            value={exchangeType}
                            label="Exchange Type"
                            onChange={(e) => setExchangeType(e.target.value)}
                        >
                            <MenuItem value="">Any</MenuItem>
                            <MenuItem value="NYSE">NYSE</MenuItem>
                            <MenuItem value="NASDAQ">NASDAQ</MenuItem>
                        </Select>
                    </FormControl>

                </Box>
            </Collapse>
        </AppBar>
    );
};

export default Header;
