# WCAG 2.1 AA Accessibility Implementation
## Campus Resource Hub

**Version:** 1.0  
**Date:** November 9, 2025  
**Compliance Level:** WCAG 2.1 Level AA

---

## Overview

This document details the accessibility features implemented in Campus Resource Hub to ensure WCAG 2.1 Level AA compliance. Our goal is to create an inclusive platform accessible to all users, regardless of ability.

---

## 1. Perceivable

### 1.1 Text Alternatives
**Success Criterion 1.1.1 (Level A)**

✅ **Implementation:**
- All images include descriptive `alt` attributes
- Decorative images use `role="img"` with `aria-label` or are marked as `aria-hidden="true"`
- Icon-only buttons include `aria-label` for context
- Form inputs have associated `<label>` elements

```html
<img src="resource.jpg" alt="Image of Computer Lab 3" />
<button aria-label="Close alert"><span aria-hidden="true">×</span></button>
```

### 1.2 Time-based Media
**Success Criterion 1.2.1-1.2.5 (Level A/AA)**

✅ **Implementation:**
- Currently no video or audio content
- Future media will include captions and transcripts

### 1.3 Adaptable
**Success Criterion 1.3.1-1.3.3 (Level A/AA)**

✅ **Implementation:**
- Semantic HTML5 structure (`<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>`)
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA landmarks for page regions
- Data tables use `<th scope="col">` for headers
- Form labels explicitly associated with inputs

```html
<header role="banner">
  <nav role="navigation" aria-label="Main navigation">
    <!-- Navigation content -->
  </nav>
</header>
<main id="main-content" role="main">
  <!-- Page content -->
</main>
```

### 1.4 Distinguishable
**Success Criterion 1.4.1-1.4.13 (Level A/AA/AAA)**

✅ **Implementation:**

**Color Contrast (1.4.3)**
- Text: 4.5:1 minimum contrast ratio
- Large text: 3:1 minimum contrast ratio
- UI components: 3:1 minimum contrast ratio
- Colors tested with WebAIM Contrast Checker

**Text Resizing (1.4.4)**
- Text can be resized up to 200% without loss of functionality
- Responsive units (rem, em) used throughout

**Images of Text (1.4.5)**
- Logo is the only image of text (exemption for branding)
- All other text is rendered as actual text

**Reflow (1.4.10)**
- Content reflows to 320px width without horizontal scrolling
- Mobile-first responsive design with Bootstrap 5

**Non-text Contrast (1.4.11)**
- UI components have 3:1 contrast ratio
- Focus indicators clearly visible

**Text Spacing (1.4.12)**
- Content adapts to user-defined text spacing
- No content is cut off with increased spacing

---

## 2. Operable

### 2.1 Keyboard Accessible
**Success Criterion 2.1.1-2.1.4 (Level A/AA)**

✅ **Implementation:**

**Keyboard Navigation (2.1.1)**
- All functionality available via keyboard
- Tab order follows logical reading sequence
- No keyboard traps

**No Keyboard Trap (2.1.2)**
- Users can navigate away from all components
- Modal dialogs include escape key functionality

**Keyboard Shortcuts (2.1.4)**
- No single-key shortcuts that could interfere
- Future shortcuts will be remappable

```css
/* Enhanced focus indicators */
*:focus {
    outline: 3px solid #0d6efd;
    outline-offset: 2px;
}
```

### 2.2 Enough Time
**Success Criterion 2.2.1-2.2.2 (Level A)**

✅ **Implementation:**
- Session timeout set to 30 minutes with warning
- No time limits on booking or form completion
- Users can extend sessions

### 2.3 Seizures and Physical Reactions
**Success Criterion 2.3.1 (Level A)**

✅ **Implementation:**
- No flashing content
- Animations are subtle and can be disabled
- Respects `prefers-reduced-motion` preference

```css
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

### 2.4 Navigable
**Success Criterion 2.4.1-2.4.7 (Level A/AA)**

✅ **Implementation:**

**Bypass Blocks (2.4.1)**
- Skip navigation link at top of every page
- Jumps directly to main content
- Visible on focus

```html
<a href="#main-content" class="skip-link visually-hidden-focusable">
    Skip to main content
</a>
```

**Page Titled (2.4.2)**
- Every page has descriptive `<title>` element
- Format: "Page Name - Campus Resource Hub"

**Focus Order (2.4.3)**
- Logical tab order throughout
- No unexpected focus jumps

**Link Purpose (2.4.4)**
- Link text clearly describes destination
- Context provided via `aria-label` when needed

```html
<a href="/resources/123" aria-label="View details for Computer Lab 3">
    View Details
</a>
```

**Multiple Ways (2.4.5)**
- Search functionality
- Category navigation
- Breadcrumb navigation

**Headings and Labels (2.4.6)**
- Descriptive headings for all sections
- Form labels clearly describe purpose

**Focus Visible (2.4.7)**
- Enhanced focus indicators on all interactive elements
- 3px solid blue outline with 2px offset

### 2.5 Input Modalities
**Success Criterion 2.5.1-2.5.4 (Level A/AA)**

✅ **Implementation:**

**Pointer Gestures (2.5.1)**
- All pointer interactions have keyboard alternatives
- No complex gestures required

**Pointer Cancellation (2.5.2)**
- Click actions execute on mouse up, not down
- Users can cancel accidental clicks

**Label in Name (2.5.3)**
- Visible labels match accessible names
- Speech input users can activate controls by speaking label

**Target Size (2.5.5 - AAA, implemented)**
- All interactive elements minimum 44x44px
- Adequate spacing between targets

```css
.btn, .form-control, .form-select {
    min-height: 44px;
}
```

---

## 3. Understandable

### 3.1 Readable
**Success Criterion 3.1.1-3.1.2 (Level A/AA)**

✅ **Implementation:**
- Page language declared: `<html lang="en">`
- Content written in clear, plain language
- No jargon without explanation

### 3.2 Predictable
**Success Criterion 3.2.1-3.2.4 (Level A/AA)**

✅ **Implementation:**

**On Focus (3.2.1)**
- Focus does not trigger unexpected context changes
- No automatic form submissions on focus

**On Input (3.2.2)**
- Input fields don't auto-submit
- Users explicitly submit forms via button

**Consistent Navigation (3.2.3)**
- Navigation menu identical across all pages
- Same order and structure throughout

**Consistent Identification (3.2.4)**
- Icons and buttons function identically across pages
- Login button always in same location

### 3.3 Input Assistance
**Success Criterion 3.3.1-3.3.4 (Level A/AA)**

✅ **Implementation:**

**Error Identification (3.3.1)**
- Form errors clearly identified
- Error messages describe problem

**Labels or Instructions (3.3.2)**
- All form fields have labels
- Required fields marked with asterisk and "required" in label
- Helper text provided where needed

```html
<label for="email">
    Email Address <span class="text-danger" aria-label="required">*</span>
</label>
<input type="email" id="email" required aria-required="true" 
       aria-describedby="email-help">
<small id="email-help">Use your institutional email</small>
```

**Error Suggestion (3.3.3)**
- Validation errors include suggestions
- "Please enter a valid email address"

**Error Prevention (3.3.4)**
- Confirmation required for critical actions
- "Are you sure you want to delete this resource?"

---

## 4. Robust

### 4.1 Compatible
**Success Criterion 4.1.1-4.1.3 (Level A/AA)**

✅ **Implementation:**

**Parsing (4.1.1)**
- Valid HTML5 markup
- No duplicate IDs
- Proper nesting of elements

**Name, Role, Value (4.1.2)**
- ARIA roles used appropriately
- Custom components have proper ARIA attributes
- Dynamic content updates announced to screen readers

**Status Messages (4.1.3)**
- ARIA live regions for flash messages
- `role="alert"` for critical messages
- `aria-live="polite"` for non-critical updates

```html
<div aria-live="polite" aria-atomic="true">
    <div class="alert alert-success" role="alert">
        Booking created successfully!
    </div>
</div>
```

---

## Testing Strategy

### Automated Testing
- **Tool**: axe-selenium-python 2.1.6
- **Frequency**: Every build via CI/CD
- **Coverage**: All pages and user flows

### Manual Testing

**Keyboard Navigation**
- Tab through entire application
- Verify all functionality accessible
- Check focus indicators visible

**Screen Reader Testing**
- **Tools**: NVDA (Windows), JAWS (Windows), VoiceOver (macOS)
- **Tests**: 
  - Page structure navigation
  - Form completion
  - Error handling
  - Dynamic content updates

**Visual Testing**
- Color contrast validation with WebAIM
- Text resizing to 200%
- Zoom testing to 400%
- Responsive design at various breakpoints

### Browser Compatibility
- Chrome/Edge (Chromium)
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Known Issues & Future Improvements

### Current Limitations
- File upload progress not announced to screen readers (planned for v1.1)
- Calendar booking interface requires enhanced ARIA (planned for v1.1)
- PDF documents need accessible alternatives

### Planned Enhancements
- ARIA live announcements for search results
- Enhanced keyboard shortcuts with customization
- High contrast mode improvements
- Additional language support for international students

---

## Compliance Statement

Campus Resource Hub aims to conform to WCAG 2.1 Level AA. We are committed to ensuring digital accessibility for all users and continuously work to improve the user experience.

### Feedback
Users experiencing accessibility barriers can contact: accessibility@campusresourcehub.edu

### Last Updated
November 9, 2025

### Next Audit
December 2025
