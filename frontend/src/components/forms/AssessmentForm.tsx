/**
 * AssessmentForm Component
 *
 * Multi-field form for collecting user onboarding assessment information.
 * Includes sport selection, age, experience level, training days, injury history, and equipment.
 *
 * Story 11.7: Complete Assessment Form
 */

import { useState, type FormEvent, type ChangeEvent } from 'react';
import {
  Box,
  Button,
  Card,
  CardActionArea,
  TextField,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  FormHelperText,
  Alert,
  CircularProgress,
  Stack,
  Grid,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  SportsFootball as SportsFootballIcon,
  SportsCricket as SportsCricketIcon,
  ErrorOutline as ErrorOutlineIcon,
} from '@mui/icons-material';

export interface AssessmentFormData {
  sport: string | null;
  age: number | null;
  experienceLevel: string | null;
  trainingDays: string | null;
  injuries: string | null;
  equipment: string[];
}

interface AssessmentFormProps {
  onSubmit: (data: AssessmentFormData) => Promise<{ success: boolean }>;
}

interface FormErrors {
  sport?: string;
  age?: string;
  experienceLevel?: string;
  trainingDays?: string;
  equipment?: string;
}

export function AssessmentForm({ onSubmit }: AssessmentFormProps) {
  const [formData, setFormData] = useState<AssessmentFormData>({
    sport: null,
    age: null,
    experienceLevel: null,
    trainingDays: null,
    injuries: null,
    equipment: [],
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Validate individual fields
  const validateAge = (value: number | null): string | undefined => {
    if (value === null || value === 0) {
      return 'Age is required';
    }
    if (value < 13) {
      return 'You must be at least 13 years old to use this service';
    }
    if (value > 100) {
      return 'Please enter a valid age';
    }
    return undefined;
  };

  // Check if form is complete and valid
  const isFormValid = (): boolean => {
    const ageError = validateAge(formData.age);
    return (
      formData.sport !== null &&
      formData.age !== null &&
      !ageError &&
      formData.experienceLevel !== null &&
      formData.trainingDays !== null &&
      formData.injuries !== null &&
      formData.equipment.length > 0
    );
  };

  // Handle sport selection
  const handleSportSelect = (sport: string) => {
    setFormData((prev) => ({ ...prev, sport }));
    setErrors((prev) => ({ ...prev, sport: undefined }));
  };

  // Handle age change
  const handleAgeChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value === '' ? null : parseInt(e.target.value, 10);
    setFormData((prev) => ({ ...prev, age: value }));

    if (value !== null) {
      const error = validateAge(value);
      setErrors((prev) => ({ ...prev, age: error }));
    }
  };

  // Handle age blur
  const handleAgeBlur = () => {
    const error = validateAge(formData.age);
    setErrors((prev) => ({ ...prev, age: error }));
  };

  // Handle experience level change
  const handleExperienceLevelChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, experienceLevel: e.target.value }));
    setErrors((prev) => ({ ...prev, experienceLevel: undefined }));
  };

  // Handle training days selection
  const handleTrainingDaysSelect = (days: string) => {
    setFormData((prev) => ({ ...prev, trainingDays: days }));
    setErrors((prev) => ({ ...prev, trainingDays: undefined }));
  };

  // Handle injury selection
  const handleInjuryChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, injuries: e.target.value }));
  };

  // Handle equipment selection
  const handleEquipmentToggle = (equipment: string) => {
    setFormData((prev) => {
      const currentEquipment = prev.equipment;
      const newEquipment = currentEquipment.includes(equipment)
        ? currentEquipment.filter((item) => item !== equipment)
        : [...currentEquipment, equipment];
      return { ...prev, equipment: newEquipment };
    });
    setErrors((prev) => ({ ...prev, equipment: undefined }));
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitError(null);

    if (!isFormValid()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Convert form data to expected format
      const submissionData: AssessmentFormData = {
        sport: formData.sport?.toLowerCase() ?? null,
        age: formData.age,
        experienceLevel: formData.experienceLevel,
        trainingDays: formData.trainingDays,
        injuries: formData.injuries === 'no' ? null : formData.injuries,
        equipment: formData.equipment,
      };

      await onSubmit(submissionData);
      setSubmitSuccess(true);
    } catch (_error) {
      setSubmitError('Unable to save your assessment. Please try again');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      aria-label="Assessment form"
      noValidate
      sx={{ maxWidth: 800, mx: 'auto', py: 4 }}
    >
      {/* Success Message */}
      {submitSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Your assessment is being processed
        </Alert>
      )}

      {/* Error Message */}
      {submitError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {submitError}
        </Alert>
      )}

      {/* Sport Selection - Story 11.1 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom align="center">
          Select Your Sport
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
          Choose your primary sport to receive personalized training programs
        </Typography>

        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Card
              elevation={formData.sport === 'football' ? 3 : 1}
              sx={{
                border: formData.sport === 'football' ? '2px solid' : '2px solid transparent',
                borderColor: formData.sport === 'football' ? 'primary.main' : 'transparent',
                transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
              }}
            >
              <CardActionArea
                onClick={() => handleSportSelect('football')}
                aria-label="Select Football"
                sx={{
                  minHeight: 160,
                  p: 3,
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Box sx={{ mb: 2 }}>
                  <SportsFootballIcon
                    sx={{
                      fontSize: 48,
                      color: formData.sport === 'football' ? 'primary.main' : 'text.secondary',
                      transition: 'color 225ms',
                    }}
                  />
                </Box>
                <Typography
                  variant="h6"
                  align="center"
                  sx={{
                    color: formData.sport === 'football' ? 'primary.main' : 'text.primary',
                    transition: 'color 225ms',
                  }}
                >
                  Football
                </Typography>
                {formData.sport === 'football' && (
                  <CheckCircleIcon
                    sx={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                      color: 'primary.main',
                      fontSize: 24,
                    }}
                  />
                )}
              </CardActionArea>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <Card
              elevation={formData.sport === 'cricket' ? 3 : 1}
              sx={{
                border: formData.sport === 'cricket' ? '2px solid' : '2px solid transparent',
                borderColor: formData.sport === 'cricket' ? 'primary.main' : 'transparent',
                transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
              }}
            >
              <CardActionArea
                onClick={() => handleSportSelect('cricket')}
                aria-label="Select Cricket"
                sx={{
                  minHeight: 160,
                  p: 3,
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Box sx={{ mb: 2 }}>
                  <SportsCricketIcon
                    sx={{
                      fontSize: 48,
                      color: formData.sport === 'cricket' ? 'primary.main' : 'text.secondary',
                      transition: 'color 225ms',
                    }}
                  />
                </Box>
                <Typography
                  variant="h6"
                  align="center"
                  sx={{
                    color: formData.sport === 'cricket' ? 'primary.main' : 'text.primary',
                    transition: 'color 225ms',
                  }}
                >
                  Cricket
                </Typography>
                {formData.sport === 'cricket' && (
                  <CheckCircleIcon
                    sx={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                      color: 'primary.main',
                      fontSize: 24,
                    }}
                  />
                )}
              </CardActionArea>
            </Card>
          </Grid>
        </Grid>

        {errors.sport && (
          <Alert severity="error" sx={{ mt: 3 }}>
            {errors.sport}
          </Alert>
        )}
      </Box>

      {/* Age Input - Story 11.2 */}
      <Box sx={{ mb: 4 }}>
        <TextField
          id="age"
          name="age"
          label="Age"
          type="number"
          fullWidth
          required
          inputProps={{
            min: 13,
            max: 100,
            inputMode: 'numeric',
            'aria-describedby': 'age-helper-text',
          }}
          value={formData.age ?? ''}
          onChange={handleAgeChange}
          onBlur={handleAgeBlur}
          error={!!errors.age}
          helperText={errors.age || 'Enter your age (13-100 years)'}
          FormHelperTextProps={{
            id: 'age-helper-text',
          }}
        />
      </Box>

      {/* Experience Level - Story 11.3 */}
      <Box sx={{ mb: 4 }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="h5" gutterBottom>
              What&apos;s your training experience level?
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Select the level that best matches your current fitness and training background
            </Typography>
          </Box>

          <FormControl error={!!errors.experienceLevel} component="fieldset" fullWidth>
            <RadioGroup
              value={formData.experienceLevel ?? ''}
              onChange={handleExperienceLevelChange}
              name="experience-level"
            >
              <FormControlLabel
                value="beginner"
                control={<Radio />}
                label={
                  <Box sx={{ ml: 1 }}>
                    <Typography variant="body1" fontWeight={500}>
                      Beginner
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      New to structured training, or returning after extended break (6+ months).
                      Focus on building foundation and learning proper form.
                    </Typography>
                  </Box>
                }
                sx={{
                  border: formData.experienceLevel === 'beginner' ? '1px solid' : 'none',
                  borderColor: 'primary.main',
                  backgroundColor:
                    formData.experienceLevel === 'beginner' ? 'action.selected' : 'transparent',
                  borderRadius: 1,
                  p: 2,
                  mb: 2,
                  m: 0,
                  alignItems: 'flex-start',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              />

              <FormControlLabel
                value="intermediate"
                control={<Radio />}
                label={
                  <Box sx={{ ml: 1 }}>
                    <Typography variant="body1" fontWeight={500}>
                      Intermediate
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Consistent training for 6+ months. Comfortable with basic exercises and ready
                      to increase intensity and complexity.
                    </Typography>
                  </Box>
                }
                sx={{
                  border: formData.experienceLevel === 'intermediate' ? '1px solid' : 'none',
                  borderColor: 'primary.main',
                  backgroundColor:
                    formData.experienceLevel === 'intermediate' ? 'action.selected' : 'transparent',
                  borderRadius: 1,
                  p: 2,
                  mb: 2,
                  m: 0,
                  alignItems: 'flex-start',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              />

              <FormControlLabel
                value="advanced"
                control={<Radio />}
                label={
                  <Box sx={{ ml: 1 }}>
                    <Typography variant="body1" fontWeight={500}>
                      Advanced
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Training consistently for 1+ year with structured programs. Comfortable with
                      high-intensity workouts and complex movements.
                    </Typography>
                  </Box>
                }
                sx={{
                  border: formData.experienceLevel === 'advanced' ? '1px solid' : 'none',
                  borderColor: 'primary.main',
                  backgroundColor:
                    formData.experienceLevel === 'advanced' ? 'action.selected' : 'transparent',
                  borderRadius: 1,
                  p: 2,
                  mb: 2,
                  m: 0,
                  alignItems: 'flex-start',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              />
            </RadioGroup>

            {errors.experienceLevel && (
              <FormHelperText>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <ErrorOutlineIcon fontSize="small" />
                  {errors.experienceLevel}
                </Box>
              </FormHelperText>
            )}
          </FormControl>
        </Stack>
      </Box>

      {/* Training Days - Story 11.4 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          How many days per week can you train?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Select your weekly training availability
        </Typography>

        <Grid container spacing={2}>
          {['2-3', '4-5', '6-7'].map((days) => (
            <Grid key={days} size={{ xs: 12, sm: 4 }}>
              <Card
                elevation={formData.trainingDays === days ? 3 : 1}
                sx={{
                  border: formData.trainingDays === days ? '2px solid' : '2px solid transparent',
                  borderColor: formData.trainingDays === days ? 'primary.main' : 'transparent',
                  transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
                }}
              >
                <CardActionArea
                  onClick={() => handleTrainingDaysSelect(days)}
                  aria-label={`${days} days per week`}
                  sx={{
                    minHeight: 100,
                    p: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography
                    variant="h6"
                    align="center"
                    sx={{
                      color: formData.trainingDays === days ? 'primary.main' : 'text.primary',
                      transition: 'color 225ms',
                    }}
                  >
                    {days} days
                  </Typography>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Injury History - Story 11.5 */}
      <Box sx={{ mb: 4 }}>
        <Stack spacing={2}>
          <Box>
            <Typography variant="h5" gutterBottom>
              Do you have any current or recent injuries?
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This helps us customize your program for safety
            </Typography>
          </Box>

          <FormControl component="fieldset">
            <RadioGroup
              value={formData.injuries ?? ''}
              onChange={handleInjuryChange}
              name="injuries"
            >
              <FormControlLabel value="no" control={<Radio />} label="No injuries" sx={{ mb: 1 }} />
              <FormControlLabel
                value="yes"
                control={<Radio />}
                label="I have injury history"
                sx={{ mb: 1 }}
              />
            </RadioGroup>
          </FormControl>
        </Stack>
      </Box>

      {/* Equipment - Story 11.6 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          What equipment do you have access to?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Select all that apply
        </Typography>

        <Grid container spacing={2}>
          {[
            { value: 'none', label: 'No equipment' },
            { value: 'basic', label: 'Basic equipment' },
            { value: 'full-gym', label: 'Full gym' },
          ].map((equipment) => (
            <Grid key={equipment.value} size={{ xs: 12, sm: 4 }}>
              <Card
                elevation={formData.equipment.includes(equipment.value) ? 3 : 1}
                sx={{
                  border: formData.equipment.includes(equipment.value)
                    ? '2px solid'
                    : '2px solid transparent',
                  borderColor: formData.equipment.includes(equipment.value)
                    ? 'primary.main'
                    : 'transparent',
                  transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
                }}
              >
                <CardActionArea
                  onClick={() => handleEquipmentToggle(equipment.value)}
                  aria-label={equipment.label}
                  sx={{
                    minHeight: 80,
                    p: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography
                    variant="body1"
                    align="center"
                    sx={{
                      color: formData.equipment.includes(equipment.value)
                        ? 'primary.main'
                        : 'text.primary',
                      transition: 'color 225ms',
                    }}
                  >
                    {equipment.label}
                  </Typography>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Submit Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={!isFormValid() || isSubmitting}
          sx={{ minWidth: 200 }}
        >
          {isSubmitting ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Submitting...
            </>
          ) : (
            'Submit Assessment'
          )}
        </Button>
      </Box>
    </Box>
  );
}
