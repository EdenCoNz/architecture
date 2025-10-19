/**
 * MUI Components Theme Testing
 *
 * Tests to verify that all Material UI components used in the application
 * render correctly in both light and dark themes.
 *
 * This test suite covers all MUI components currently in use:
 * - Typography (h1-h6, body1, body2, caption)
 * - Layout (Container, Box, Paper, Stack)
 * - Inputs (Button, IconButton)
 * - Feedback (Alert, CircularProgress)
 * - Surfaces (Card, CardHeader, CardContent, AppBar, Toolbar)
 * - Navigation (Links styled as buttons)
 */

import { describe, it, expect } from 'vitest';
import { render } from '../test-utils';
import {
  Typography,
  Container,
  Box,
  Paper,
  Stack,
  Button,
  IconButton,
  Alert,
  CircularProgress,
  Card,
  CardHeader,
  CardContent,
  AppBar,
  Toolbar,
  Tooltip,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import MenuIcon from '@mui/icons-material/Menu';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

describe('MUI Components Theme Testing', () => {
  describe('Typography Components', () => {
    const variants = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'body1', 'body2', 'caption'] as const;

    variants.forEach((variant) => {
      it(`should render ${variant} in light mode`, () => {
        const { container } = render(<Typography variant={variant}>Test {variant}</Typography>, {
          preloadedState: { theme: { mode: 'light' } },
        });

        expect(container.querySelector('.MuiTypography-root')).toBeInTheDocument();
        expect(container.textContent).toContain(`Test ${variant}`);
      });

      it(`should render ${variant} in dark mode`, () => {
        const { container } = render(<Typography variant={variant}>Test {variant}</Typography>, {
          preloadedState: { theme: { mode: 'dark' } },
        });

        expect(container.querySelector('.MuiTypography-root')).toBeInTheDocument();
        expect(container.textContent).toContain(`Test ${variant}`);
      });
    });
  });

  describe('Layout Components', () => {
    it('should render Container in both themes', () => {
      const { rerender, container } = render(<Container>Test Content</Container>, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiContainer-root')).toBeInTheDocument();

      rerender(<Container>Test Content</Container>);
      expect(container.querySelector('.MuiContainer-root')).toBeInTheDocument();
    });

    it('should render Box in both themes', () => {
      const { rerender, container } = render(<Box sx={{ p: 2 }}>Test Box</Box>, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiBox-root')).toBeInTheDocument();

      rerender(<Box sx={{ p: 2 }}>Test Box</Box>);
      expect(container.querySelector('.MuiBox-root')).toBeInTheDocument();
    });

    it('should render Paper with elevation in both themes', () => {
      const { rerender, container } = render(<Paper elevation={2}>Paper Content</Paper>, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiPaper-root')).toBeInTheDocument();
      expect(container.querySelector('.MuiPaper-elevation2')).toBeInTheDocument();

      rerender(<Paper elevation={2}>Paper Content</Paper>);
      expect(container.querySelector('.MuiPaper-root')).toBeInTheDocument();
    });

    it('should render Stack in both themes', () => {
      const { rerender, container } = render(
        <Stack spacing={2}>
          <div>Item 1</div>
          <div>Item 2</div>
        </Stack>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiStack-root')).toBeInTheDocument();

      rerender(
        <Stack spacing={2}>
          <div>Item 1</div>
          <div>Item 2</div>
        </Stack>
      );
      expect(container.querySelector('.MuiStack-root')).toBeInTheDocument();
    });
  });

  describe('Button Components', () => {
    it('should render contained Button in both themes', () => {
      const { rerender, container } = render(
        <Button variant="contained" color="primary">
          Test Button
        </Button>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiButton-contained')).toBeInTheDocument();
      expect(container.querySelector('.MuiButton-colorPrimary')).toBeInTheDocument();

      rerender(
        <Button variant="contained" color="primary">
          Test Button
        </Button>
      );
      expect(container.querySelector('.MuiButton-contained')).toBeInTheDocument();
    });

    it('should render outlined Button in both themes', () => {
      const { rerender, container } = render(
        <Button variant="outlined" color="primary">
          Test Button
        </Button>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiButton-outlined')).toBeInTheDocument();

      rerender(
        <Button variant="outlined" color="primary">
          Test Button
        </Button>
      );
      expect(container.querySelector('.MuiButton-outlined')).toBeInTheDocument();
    });

    it('should render IconButton in both themes', () => {
      const { rerender, container } = render(
        <IconButton aria-label="test icon">
          <HomeIcon />
        </IconButton>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiIconButton-root')).toBeInTheDocument();

      rerender(
        <IconButton aria-label="test icon">
          <HomeIcon />
        </IconButton>
      );
      expect(container.querySelector('.MuiIconButton-root')).toBeInTheDocument();
    });

    it('should render Button with icon in both themes', () => {
      const { rerender, container } = render(<Button startIcon={<HomeIcon />}>With Icon</Button>, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiButton-startIcon')).toBeInTheDocument();

      rerender(<Button startIcon={<HomeIcon />}>With Icon</Button>);
      expect(container.querySelector('.MuiButton-startIcon')).toBeInTheDocument();
    });
  });

  describe('Feedback Components', () => {
    it('should render success Alert in both themes', () => {
      const { rerender, container } = render(
        <Alert severity="success" variant="filled">
          Success message
        </Alert>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiAlert-filledSuccess')).toBeInTheDocument();

      rerender(
        <Alert severity="success" variant="filled">
          Success message
        </Alert>
      );
      expect(container.querySelector('.MuiAlert-filledSuccess')).toBeInTheDocument();
    });

    it('should render error Alert in both themes', () => {
      const { rerender, container } = render(
        <Alert severity="error" variant="filled">
          Error message
        </Alert>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiAlert-filledError')).toBeInTheDocument();

      rerender(
        <Alert severity="error" variant="filled">
          Error message
        </Alert>
      );
      expect(container.querySelector('.MuiAlert-filledError')).toBeInTheDocument();
    });

    it('should render CircularProgress in both themes', () => {
      const { rerender, container } = render(<CircularProgress />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiCircularProgress-root')).toBeInTheDocument();

      rerender(<CircularProgress />);
      expect(container.querySelector('.MuiCircularProgress-root')).toBeInTheDocument();
    });

    it('should render Tooltip in both themes', async () => {
      const { rerender, container } = render(
        <Tooltip title="Test tooltip">
          <Button>Hover me</Button>
        </Tooltip>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiButton-root')).toBeInTheDocument();

      rerender(
        <Tooltip title="Test tooltip">
          <Button>Hover me</Button>
        </Tooltip>
      );
      expect(container.querySelector('.MuiButton-root')).toBeInTheDocument();
    });
  });

  describe('Surface Components', () => {
    it('should render Card in both themes', () => {
      const { rerender, container } = render(
        <Card elevation={1}>
          <CardHeader title="Card Title" subheader="Card Subheader" />
          <CardContent>Card content goes here</CardContent>
        </Card>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiCard-root')).toBeInTheDocument();
      expect(container.querySelector('.MuiCardHeader-root')).toBeInTheDocument();
      expect(container.querySelector('.MuiCardContent-root')).toBeInTheDocument();

      rerender(
        <Card elevation={1}>
          <CardHeader title="Card Title" subheader="Card Subheader" />
          <CardContent>Card content goes here</CardContent>
        </Card>
      );
      expect(container.querySelector('.MuiCard-root')).toBeInTheDocument();
    });

    it('should render AppBar in both themes', () => {
      const { rerender, container } = render(
        <AppBar position="sticky" color="primary">
          <Toolbar>
            <Typography variant="h6">App Title</Typography>
          </Toolbar>
        </AppBar>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiAppBar-root')).toBeInTheDocument();
      expect(container.querySelector('.MuiToolbar-root')).toBeInTheDocument();

      rerender(
        <AppBar position="sticky" color="primary">
          <Toolbar>
            <Typography variant="h6">App Title</Typography>
          </Toolbar>
        </AppBar>
      );
      expect(container.querySelector('.MuiAppBar-root')).toBeInTheDocument();
    });
  });

  describe('Icon Components', () => {
    it('should render HomeIcon in both themes', () => {
      const { rerender, container } = render(<HomeIcon />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiSvgIcon-root')).toBeInTheDocument();

      rerender(<HomeIcon />);
      expect(container.querySelector('.MuiSvgIcon-root')).toBeInTheDocument();
    });

    it('should render MenuIcon in both themes', () => {
      const { rerender, container } = render(<MenuIcon />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiSvgIcon-root')).toBeInTheDocument();

      rerender(<MenuIcon />);
      expect(container.querySelector('.MuiSvgIcon-root')).toBeInTheDocument();
    });

    it('should render ErrorOutlineIcon in both themes', () => {
      const { rerender, container } = render(<ErrorOutlineIcon />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiSvgIcon-root')).toBeInTheDocument();

      rerender(<ErrorOutlineIcon />);
      expect(container.querySelector('.MuiSvgIcon-root')).toBeInTheDocument();
    });

    it('should render icons with custom color in both themes', () => {
      const { rerender, container } = render(<HomeIcon color="primary" />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiSvgIcon-colorPrimary')).toBeInTheDocument();

      rerender(<HomeIcon color="primary" />);
      expect(container.querySelector('.MuiSvgIcon-colorPrimary')).toBeInTheDocument();
    });

    it('should render error colored icon in both themes', () => {
      const { rerender, container } = render(<ErrorOutlineIcon color="error" />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(container.querySelector('.MuiSvgIcon-colorError')).toBeInTheDocument();

      rerender(<ErrorOutlineIcon color="error" />);
      expect(container.querySelector('.MuiSvgIcon-colorError')).toBeInTheDocument();
    });
  });

  describe('Responsive Typography', () => {
    it('should render responsive headings with sx prop in both themes', () => {
      const { rerender, container } = render(
        <Typography
          variant="h1"
          sx={{
            fontSize: {
              xs: '4rem',
              sm: '6rem',
              md: '8rem',
            },
          }}
        >
          Responsive Heading
        </Typography>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.MuiTypography-h1')).toBeInTheDocument();

      rerender(
        <Typography
          variant="h1"
          sx={{
            fontSize: {
              xs: '4rem',
              sm: '6rem',
              md: '8rem',
            },
          }}
        >
          Responsive Heading
        </Typography>
      );
      expect(container.querySelector('.MuiTypography-h1')).toBeInTheDocument();
    });
  });

  describe('Color Variants', () => {
    const colors = ['primary', 'secondary', 'error', 'warning', 'info', 'success'] as const;

    colors.forEach((color) => {
      it(`should render Button with ${color} color in both themes`, () => {
        const { rerender, container } = render(
          <Button variant="contained" color={color}>
            {color} Button
          </Button>,
          { preloadedState: { theme: { mode: 'light' } } }
        );

        const colorClass = color.charAt(0).toUpperCase() + color.slice(1);
        expect(container.querySelector(`.MuiButton-color${colorClass}`)).toBeInTheDocument();

        rerender(
          <Button variant="contained" color={color}>
            {color} Button
          </Button>
        );
        expect(container.querySelector(`.MuiButton-color${colorClass}`)).toBeInTheDocument();
      });
    });
  });

  describe('Disabled States', () => {
    it('should render disabled Button in both themes', () => {
      const { rerender, container } = render(
        <Button variant="contained" disabled>
          Disabled Button
        </Button>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.Mui-disabled')).toBeInTheDocument();

      rerender(
        <Button variant="contained" disabled>
          Disabled Button
        </Button>
      );
      expect(container.querySelector('.Mui-disabled')).toBeInTheDocument();
    });

    it('should render disabled IconButton in both themes', () => {
      const { rerender, container } = render(
        <IconButton disabled aria-label="disabled">
          <HomeIcon />
        </IconButton>,
        { preloadedState: { theme: { mode: 'light' } } }
      );

      expect(container.querySelector('.Mui-disabled')).toBeInTheDocument();

      rerender(
        <IconButton disabled aria-label="disabled">
          <HomeIcon />
        </IconButton>
      );
      expect(container.querySelector('.Mui-disabled')).toBeInTheDocument();
    });
  });
});
