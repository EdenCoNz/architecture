# Assets Directory

Static assets used throughout the application.

## Directory Structure

- **images/**: Image files (PNG, JPG, SVG, WebP, AVIF)
- **icons/**: Icon files and custom icon sets
- **fonts/**: Custom web fonts (WOFF2, WOFF, TTF)

## Asset Optimization Guidelines

### Images

- Use modern formats: WebP for photos, SVG for graphics
- Provide multiple resolutions for responsive images
- Compress images before committing (TinyPNG, Squoosh)
- Use lazy loading for below-the-fold images
- Max file size: 200KB per image

### Icons

- Prefer SVG for scalability and performance
- Use Material UI icons from `@mui/icons-material` when possible
- For custom icons, use SVGO for optimization
- Consider icon sprites for multiple small icons

### Fonts

- Use WOFF2 format (best compression)
- Subset fonts to include only needed characters
- Use `font-display: swap` for better performance
- Limit to 2-3 font families maximum

## Usage Examples

```typescript
// Images
import logoImage from '@/assets/images/logo.png';

// Icons (prefer Material UI)
import { Home } from '@mui/icons-material';

// Custom SVG
import customIcon from '@/assets/icons/custom.svg?react';
```

## Performance Best Practices

1. **Lazy Load**: Use React.lazy() for heavy assets
2. **Code Split**: Import assets only where needed
3. **CDN**: Consider CDN for large static assets
4. **Caching**: Assets are cache-busted via Vite's build hash
5. **Preload**: Preload critical assets in index.html
