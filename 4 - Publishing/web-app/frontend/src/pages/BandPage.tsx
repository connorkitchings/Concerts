import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Box,
  Tabs,
  Tab,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { getBand, getNextShow, getPredictions } from '../services/api';
import { Band, NextShow, PredictionResponse } from '../types';
import PredictionTable from '../components/PredictionTable';
import PredictionChart from '../components/PredictionChart';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// TabPanel component for displaying tab content
const TabPanel: React.FC<TabPanelProps> = (props) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

/**
 * Page component for displaying band-specific prediction data.
 */
const BandPage: React.FC = () => {
  const { bandId } = useParams<{ bandId: string }>();
  const navigate = useNavigate();
  const [band, setBand] = useState<Band | null>(null);
  const [nextShow, setNextShow] = useState<NextShow | null>(null);
  const [notebookPredictions, setNotebookPredictions] = useState<PredictionResponse | null>(null);
  const [ckPlusPredictions, setCkPlusPredictions] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);

  useEffect(() => {
    const loadBandData = async (): Promise<void> => {
      if (!bandId) return;
      
      try {
        setLoading(true);
        setError(null);

        // Load band information
        const bandData = await getBand(bandId);
        setBand(bandData);

        // Load next show information
        try {
          const showData = await getNextShow(bandId);
          setNextShow(showData);
        } catch (err) {
          console.warn('Failed to load next show data:', err);
          // Don't set error state for this - it's not critical
        }

        // Load prediction data
        const [notebookData, ckPlusData] = await Promise.all([
          getPredictions(bandId, 'notebook'),
          getPredictions(bandId, 'ckplus')
        ]);

        setNotebookPredictions(notebookData);
        setCkPlusPredictions(ckPlusData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load band data');
      } finally {
        setLoading(false);
      }
    };

    loadBandData();
  }, [bandId]);

  // Handle tab change
  const handleTabChange = (_: React.SyntheticEvent, newValue: number): void => {
    setTabValue(newValue);
  };

  // Navigate back to home page
  const handleBackClick = (): void => {
    navigate('/');
  };

  // Render the next show information if available
  const renderNextShow = (): JSX.Element | null => {
    if (!nextShow) return null;

    let showText = '';
    if (nextShow.date) {
      showText += nextShow.date;
      if (nextShow.venue) {
        showText += ` at ${nextShow.venue}`;
        if (nextShow.city && nextShow.state) {
          showText += ` in ${nextShow.city}, ${nextShow.state}`;
        }
      }
    }

    if (!showText) return null;

    return (
      <Card sx={{ mb: 3, backgroundColor: 'rgba(25, 118, 210, 0.1)' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Next Show
          </Typography>
          <Typography variant="body1">
            {showText}
          </Typography>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={handleBackClick}
        sx={{ mb: 2 }}
      >
        Back to Bands
      </Button>

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      ) : band ? (
        <Box>
          <Typography variant="h3" component="h1" gutterBottom>
            {band.name}
          </Typography>

          {renderNextShow()}

          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="prediction tabs"
            >
              <Tab label={band.displayName} />
              <Tab label="CK+ Predictions" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              {notebookPredictions?.predictions.length ? (
                <>
                  <Grid item xs={12}>
                    <PredictionChart 
                      predictions={notebookPredictions.predictions} 
                      title={`Top Songs from ${band.displayName}`} 
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <PredictionTable 
                      title={band.displayName}
                      predictions={notebookPredictions.predictions}
                      lastUpdated={notebookPredictions.meta.last_updated}
                    />
                  </Grid>
                </>
              ) : (
                <Grid item xs={12}>
                  <Alert severity="info">No prediction data available</Alert>
                </Grid>
              )}
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              {ckPlusPredictions?.predictions.length ? (
                <>
                  <Grid item xs={12}>
                    <PredictionChart 
                      predictions={ckPlusPredictions.predictions} 
                      title="Top CK+ Predictions" 
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <PredictionTable 
                      title="CK+ Predictions"
                      predictions={ckPlusPredictions.predictions}
                      lastUpdated={ckPlusPredictions.meta.last_updated}
                    />
                  </Grid>
                </>
              ) : (
                <Grid item xs={12}>
                  <Alert severity="info">No CK+ prediction data available</Alert>
                </Grid>
              )}
            </Grid>
          </TabPanel>
        </Box>
      ) : (
        <Alert severity="warning">Band not found</Alert>
      )}
    </Box>
  );
};

export default BandPage;
