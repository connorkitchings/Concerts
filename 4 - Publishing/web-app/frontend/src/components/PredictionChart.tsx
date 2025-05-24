import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { SongPrediction } from '../types';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface PredictionChartProps {
  predictions: SongPrediction[];
  title: string;
}

/**
 * Component that displays song predictions as a bar chart.
 * Shows the top songs with highest probability or shortest gap.
 * 
 * @param {PredictionChartProps} props - The component props
 * @returns {JSX.Element} The rendered component
 */
const PredictionChart: React.FC<PredictionChartProps> = ({ predictions, title }) => {
  if (!predictions || predictions.length === 0) {
    return null;
  }

  // Sort predictions by probability if available, otherwise by current gap
  const sortedPredictions = [...predictions]
    .sort((a, b) => {
      if (a.probability !== undefined && b.probability !== undefined) {
        return b.probability - a.probability;
      }
      if (a.current_gap !== undefined && b.current_gap !== undefined) {
        return a.current_gap - b.current_gap;
      }
      return 0;
    })
    .slice(0, 10); // Take top 10

  const labels = sortedPredictions.map(p => p.name);
  
  // Prepare chart data
  const chartData = {
    labels,
    datasets: [
      {
        label: 'Probability',
        data: sortedPredictions.map(p => 
          p.probability !== undefined 
            ? (p.probability * 100) 
            : (p.current_gap ? 100 - Math.min(p.current_gap / 2, 100) : 0)
        ),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const prediction = sortedPredictions[context.dataIndex];
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (prediction.probability !== undefined) {
              label += `${(prediction.probability * 100).toFixed(1)}%`;
            } else {
              label += `Gap: ${prediction.current_gap}`;
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Probability (%)'
        }
      }
    }
  };

  return (
    <Paper sx={{ p: 2, height: 400, mb: 3 }}>
      <Box height="100%">
        <Bar data={chartData} options={options} />
      </Box>
    </Paper>
  );
};

export default PredictionChart;
