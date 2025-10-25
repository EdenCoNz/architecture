/**
 * Onboarding Page
 *
 * Container page for the user onboarding assessment form.
 * Collects essential user information for personalized training program generation.
 *
 * Feature 11: Onboarding & Assessment
 * Story 11.7: Complete Assessment Form
 * Story 11.8: Progress Through Assessment Steps
 * Story 11.12: Redirect After Assessment Completion
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Box, Alert, CircularProgress } from '@mui/material';
import { AssessmentFormStepper } from '../../components/forms';
import type { AssessmentFormData } from '../../components/forms';
import { submitAssessment } from '../../services/api';

export function Onboarding() {
  const navigate = useNavigate();
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [transitionError, setTransitionError] = useState<string | null>(null);

  // Redirect if user has already completed onboarding
  useEffect(() => {
    const hasCompleted = localStorage.getItem('hasCompletedOnboarding');
    if (hasCompleted === 'true') {
      navigate('/', { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (data: AssessmentFormData) => {
    try {
      const response = await submitAssessment({
        sport: data.sport,
        age: data.age,
        experienceLevel: data.experienceLevel,
        trainingDays: data.trainingDays,
        injuries: data.injuries,
        equipment: data.equipment,
      });

      // Mark that the user has completed onboarding
      localStorage.setItem('hasCompletedOnboarding', 'true');

      // Show loading state for program preparation
      setIsTransitioning(true);

      // Simulate brief delay for better UX (user sees "preparing program" message)
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Navigate to home page (program view will be implemented in future story)
      navigate('/', { replace: true });

      return { success: response.success };
    } catch (error) {
      // If submission succeeded but navigation failed
      if (localStorage.getItem('hasCompletedOnboarding') === 'true') {
        setIsTransitioning(false);
        setTransitionError(
          "Your assessment is saved, but we couldn't load your program. Please try refreshing."
        );
      }
      throw error;
    }
  };

  // Show loading state while transitioning to program
  if (isTransitioning) {
    return (
      <Container maxWidth="md">
        <Box
          sx={{
            py: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '60vh',
          }}
        >
          <CircularProgress size={60} sx={{ mb: 3 }} />
          <Typography variant="h5" component="h1" align="center" gutterBottom>
            Preparing Your Program
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary">
            We&apos;re generating a personalized training plan based on your assessment...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        {/* Transition Error Message */}
        {transitionError && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {transitionError}
          </Alert>
        )}

        <Typography variant="h3" component="h1" align="center" gutterBottom>
          Welcome to Your Training Journey
        </Typography>
        <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Let&apos;s get to know you better so we can create a personalized training program
          tailored to your needs.
        </Typography>

        <AssessmentFormStepper onSubmit={handleSubmit} />
      </Box>
    </Container>
  );
}
