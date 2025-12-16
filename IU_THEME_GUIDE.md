# 🎓 Indiana University Theme Guide

## Overview

Your Campus Resource Hub now features the **official Indiana University brand colors** with a professional, academic design.

---

## 🎨 Color Palette

### Primary Colors

| Color | Hex Code | Usage |
|-------|----------|-------|
| **IU Crimson** | `#990000` | Primary buttons, headers, navigation |
| **IU Crimson Dark** | `#7C0000` | Hover states, accents |
| **IU Cream** | `#EFEAE4` | Backgrounds, text on crimson |
| **IU Cream Light** | `#F7F2ED` | Page background |

### Supporting Colors

| Color | Hex Code | Usage |
|-------|----------|-------|
| **Gray** | `#666666` | Body text |
| **Gray Light** | `#CCCCCC` | Borders |
| **Gray Dark** | `#333333` | Headings |

### Status Colors

| Color | Hex Code | Usage |
|-------|----------|-------|
| **Success** | `#2D6A4F` | Success messages, confirmations |
| **Warning** | `#C17817` | Warnings, pending states |
| **Danger** | `#990000` | Errors, rejections |
| **Info** | `#2C4F82` | Information, help text |

---

## 📝 Typography

### Font Families

**Headers:**
- Primary: `Georgia, 'Times New Roman', serif`
- Professional, academic serif font
- Used for h1-h6 elements

**Body Text:**
- Primary: `'Helvetica Neue', Arial, sans-serif`
- Clean, readable sans-serif
- Used for paragraphs and UI elements

---

## 🎯 Design Elements

### Navigation Bar
- **Background**: IU Crimson gradient
- **Text**: IU Cream
- **Hover**: Lighter cream background overlay
- **Shadow**: Medium shadow for depth

### Hero Section
- **Background**: IU Crimson gradient
- **Text**: IU Cream
- **Border**: 4px cream bottom border
- **Buttons**: Cream background with crimson text

### Cards
- **Background**: White
- **Border**: None (shadow only)
- **Header**: IU Crimson with cream text
- **Hover**: Lift effect with increased shadow
- **Border Radius**: 12px for modern look

### Buttons

**Primary (Crimson):**
```css
background: #990000
color: #EFEAE4
hover: #7C0000 with lift effect
```

**Outline:**
```css
border: 2px solid #990000
color: #990000
hover: filled crimson
```

### Forms
- **Border**: 2px light gray
- **Focus**: IU Crimson with subtle shadow
- **Border Radius**: 6px

---

## 🏛️ Academic Styling

### Professional Elements

**Academic Headers:**
- Serif font (Georgia)
- IU Crimson color
- Bottom border (3px solid crimson)

**Professional Cards:**
- White background
- Left border (4px solid crimson)
- Medium shadow
- Generous padding

**Dividers:**
- 3px height
- Gradient from crimson to cream
- 2rem top/bottom margin

---

## ♿ Accessibility Features

### Included Accessibility Support

✅ **High Contrast Mode** - Enhanced colors for visibility  
✅ **Focus Indicators** - 3px crimson outline  
✅ **Screen Reader Support** - `.sr-only` class  
✅ **Keyboard Navigation** - Full support  
✅ **Color Contrast** - WCAG AA compliant  

### Focus States
```css
:focus {
    outline: 3px solid #990000;
    outline-offset: 2px;
}
```

---

## 📱 Responsive Design

### Breakpoints

**Mobile (< 768px):**
- Reduced hero text size (2rem)
- Single column layouts
- Larger touch targets

**Tablet (768px - 1024px):**
- Two-column grids
- Adjusted padding

**Desktop (> 1024px):**
- Full three-column layouts
- Maximum shadows and effects

---

## 🎨 Using the Theme

### Custom Utility Classes

```html
<!-- Text Colors -->
<p class="text-crimson">IU Crimson text</p>
<p class="text-cream">IU Cream text</p>

<!-- Backgrounds -->
<div class="bg-crimson">Crimson background</div>
<div class="bg-cream">Cream background</div>

<!-- Borders -->
<div class="border-crimson">Crimson border</div>

<!-- Academic Styling -->
<h2 class="academic-header">Professional Header</h2>
<div class="professional-card">Academic Content Card</div>
<hr class="iu-divider">
```

---

## 🎯 Component Examples

### Navigation
```html
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <!-- IU Crimson with cream text -->
</nav>
```

### Hero Section
```html
<div class="hero-section">
    <h1>Campus Resource Hub</h1>
    <p class="lead">Indiana University</p>
    <button class="btn btn-light">Get Started</button>
</div>
```

### Cards
```html
<div class="card">
    <div class="card-header">Resource Details</div>
    <div class="card-body">
        <!-- Content -->
    </div>
    <div class="card-footer">Actions</div>
</div>
```

### Buttons
```html
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-outline-primary">Secondary Action</button>
```

---

## 🖨️ Print Styles

The theme includes optimized print styles:
- Removes navigation and footer
- Converts to high-contrast
- Simplifies colors for ink efficiency

---

## 🔄 Customization

### Changing Colors

Edit `src/static/css/style.css`:

```css
:root {
    --iu-crimson: #990000;        /* Change primary color */
    --iu-cream: #EFEAE4;          /* Change secondary color */
    --iu-gray: #666666;           /* Change text color */
}
```

### Changing Fonts

```css
:root {
    --font-primary: 'Your Serif Font', serif;
    --font-secondary: 'Your Sans Font', sans-serif;
}
```

---

## 📸 Visual Reference

### Before (Generic Blue Theme)
- Primary: Generic Blue (#0056b3)
- Secondary: Gray
- Generic corporate look

### After (IU Theme)
- Primary: IU Crimson (#990000)
- Secondary: IU Cream (#EFEAE4)
- Professional academic aesthetic

---

## ✅ Brand Compliance

This theme follows **Indiana University Brand Guidelines**:

✅ Official IU Crimson color  
✅ Official IU Cream color  
✅ Professional serif typography  
✅ Academic design principles  
✅ Accessibility standards  
✅ Responsive design  

**Reference**: IU Brand Guidelines (https://brand.iu.edu)

---

## 🚀 Testing Your Theme

### Visual Check
1. Start your app: `python run.py`
2. Visit: http://localhost:5000
3. Check:
   - Navigation bar (should be crimson)
   - Buttons (crimson with cream text)
   - Cards (white with crimson headers)
   - Footer (dark gray with cream text)

### Accessibility Check
1. Use browser dev tools
2. Check contrast ratios
3. Test keyboard navigation
4. Verify focus indicators

---

## 📝 Maintenance

### Updating Colors
All colors are defined in CSS variables at the top of `style.css`. Change once, updates everywhere!

### Adding New Components
Follow the existing pattern:
1. Use CSS variables
2. Include hover states
3. Add focus indicators
4. Test responsive behavior

---

## 🎓 Perfect For

✅ University projects  
✅ Academic presentations  
✅ IU-affiliated applications  
✅ Professional demonstrations  
✅ Student portfolios  

---

## 📚 Resources

- **IU Brand Colors**: https://brand.iu.edu/color
- **CSS File**: `src/static/css/style.css`
- **Base Template**: `src/views/base.html`

---

**Your Campus Resource Hub now has authentic Indiana University styling! 🎓**

*Go Hoosiers!* 🔴⚪

