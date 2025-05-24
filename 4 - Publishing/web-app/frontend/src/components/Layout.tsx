import React from 'react';
import { Outlet } from 'react-router-dom';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Box, 
  useTheme 
} from '@mui/material';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import Footer from './Footer';

/**
 * Main layout component that wraps all pages.
 * Includes the header and footer.
 */
const Layout: React.FC = () => {
  const theme = useTheme();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static">
        <Toolbar>
          <MusicNoteIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Jam Band Predictions
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main content */}
      <Container 
        component="main" 
        maxWidth="lg" 
        sx={{ 
          mt: 4, 
          mb: 4, 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column' 
        }}
      >
        <Outlet />
      </Container>

      {/* Footer */}
      <Footer />
    </Box>
  );
};

export default Layout;
