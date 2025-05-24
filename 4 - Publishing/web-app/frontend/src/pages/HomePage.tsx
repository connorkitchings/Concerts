import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia, 
  CardActionArea,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getBands } from '../services/api';
import { Band } from '../types';

/**
 * Home page component that displays all available bands.
 */
const HomePage: React.FC = () => {
  const [bands, setBands] = useState<Band[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Load bands on component mount
  useEffect(() => {
    const loadBands = async () => {
      try {
        setLoading(true);
        const data = await getBands();
        setBands(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load bands');
      } finally {
        setLoading(false);
      }
    };

    loadBands();
  }, []);

  // Navigate to band page when a band card is clicked
  const handleBandClick = (bandId: string) => {
    navigate(`/bands/${bandId}`);
  };

  // Map band IDs to image paths (in a real app, these would be proper image URLs)
  const bandImages: Record<string, string> = {
    wsp: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuTOhzrA7rC3NwXnxhm5iXQobcF9Rrh7HnHmEkV4s&s',
    goose: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQhGw0HE6QFgcBCqLXcWQIJeXe6D7Jnp59Ox0Qrk-E&s',
    phish: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTzh7-4bsDd8lYxRz_RDaWH7SdZJ_Z_AwHEEw&s',
    um: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2TlUmY_FQBgBn7BndvWI_rYFpYOKNUCMrwx8cQSY&s'
  };

  return (
    <Box>
      <Typography variant="h2" component="h1" align="center" gutterBottom>
        Jam Band Song Predictions
      </Typography>
      
      <Typography variant="h5" align="center" color="textSecondary" paragraph>
        Explore song predictions for your favorite jam bands based on historical data and advanced analytics.
      </Typography>
      
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      ) : (
        <Grid container spacing={4} sx={{ mt: 2 }}>
          {bands.map((band) => (
            <Grid item key={band.id} xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.3s',
                  '&:hover': {
                    transform: 'scale(1.03)',
                  }
                }}
              >
                <CardActionArea onClick={() => handleBandClick(band.id)}>
                  <CardMedia
                    component="img"
                    height="200"
                    image={bandImages[band.id] || 'https://via.placeholder.com/300x200'}
                    alt={band.name}
                  />
                  <CardContent>
                    <Typography gutterBottom variant="h5" component="h2">
                      {band.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {band.displayName}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default HomePage;
