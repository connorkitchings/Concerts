import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Typography,
  Chip
} from '@mui/material';
import { SongPrediction } from '../types';

interface PredictionTableProps {
  title: string;
  predictions: SongPrediction[];
  lastUpdated?: string;
}

/**
 * Component for displaying prediction data in a table format.
 * 
 * @param {PredictionTableProps} props - The component props
 * @returns {JSX.Element} The rendered component
 */
const PredictionTable: React.FC<PredictionTableProps> = ({ 
  title, 
  predictions, 
  lastUpdated 
}) => {
  if (!predictions || predictions.length === 0) {
    return (
      <Typography variant="body1" color="text.secondary">
        No prediction data available
      </Typography>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="h6">{title}</Typography>
        {lastUpdated && (
          <Chip
            label={`Updated: ${lastUpdated}`}
            color="primary"
            variant="outlined"
            size="small"
          />
        )}
      </Box>
      
      <TableContainer component={Paper}>
        <Table aria-label="prediction table" size="small">
          <TableHead>
            <TableRow>
              <TableCell>Song</TableCell>
              <TableCell align="right">Times Played Last Year</TableCell>
              <TableCell align="right">Last Played</TableCell>
              <TableCell align="right">Current Gap</TableCell>
              <TableCell align="right">Average Gap</TableCell>
              <TableCell align="right">Median Gap</TableCell>
              {predictions[0]?.probability !== undefined && (
                <TableCell align="right">Probability</TableCell>
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {predictions.map((prediction) => (
              <TableRow 
                key={prediction.name}
                hover
                sx={{
                  '&:last-child td, &:last-child th': { border: 0 },
                  ...(prediction.probability && prediction.probability > 0.5 ? {
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                  } : {})
                }}
              >
                <TableCell component="th" scope="row">
                  {prediction.name}
                </TableCell>
                <TableCell align="right">{prediction.times_played_last_year}</TableCell>
                <TableCell align="right">{prediction.last_time_played}</TableCell>
                <TableCell align="right">{prediction.current_gap}</TableCell>
                <TableCell align="right">{prediction.average_gap?.toFixed(1)}</TableCell>
                <TableCell align="right">{prediction.median_gap}</TableCell>
                {prediction.probability !== undefined && (
                  <TableCell align="right">
                    <Chip
                      label={`${(prediction.probability * 100).toFixed(1)}%`}
                      color={prediction.probability > 0.5 ? "success" : 
                             prediction.probability > 0.25 ? "primary" : 
                             "default"}
                      size="small"
                    />
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PredictionTable;
