#!/usr/bin/env python3
"""
Claude Code wrapper that handles workspace context and file management
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class WorkspaceClaudeHandler:
    def __init__(self):
        self.workspace_root = Path("/workspace")
        self.project_dir = self.workspace_root / "project"
        self.planning_dir = self.workspace_root / "planning"
        self.chat_dir = self.workspace_root / "chat-history"
        
    def get_workspace_context(self):
        """Build context from all workspace files"""
        context = {
            "workspace_structure": self.get_file_tree(),
            "project_files": self.get_project_files(),
            "planning_docs": self.get_planning_docs(),
            "recent_chat": self.get_recent_chat_history()
        }
        return context
    
    def get_file_tree(self):
        """Get complete workspace file structure"""
        result = subprocess.run(
            ["tree", "-I", "node_modules|.git", str(self.workspace_root)],
            capture_output=True, text=True
        )
        return result.stdout if result.returncode == 0 else "No file tree available"
    
    def get_project_files(self):
        """Get current project file contents (key files only)"""
        key_files = ["package.json", "src/App.tsx", "src/index.tsx", "README.md"]
        files = {}
        
        for file_path in key_files:
            full_path = self.project_dir / file_path
            if full_path.exists():
                try:
                    files[file_path] = full_path.read_text()
                except:
                    files[file_path] = "[Binary or unreadable file]"
        
        return files
    
    def get_planning_docs(self):
        """Get planning documents"""
        docs = {}
        if self.planning_dir.exists():
            for doc_file in self.planning_dir.glob("*.md"):
                try:
                    docs[doc_file.name] = doc_file.read_text()
                except:
                    docs[doc_file.name] = "[Unreadable file]"
        return docs
    
    def get_recent_chat_history(self):
        """Get recent chat history for context"""
        if not self.chat_dir.exists():
            return "No chat history yet"
        
        # Get most recent chat file
        chat_files = sorted(self.chat_dir.glob("session-*.md"))
        if chat_files:
            try:
                return chat_files[-1].read_text()
            except:
                return "Could not read recent chat"
        return "No chat sessions yet"
    
    def save_chat_message(self, role, content):
        """Save chat message to current session"""
        self.chat_dir.mkdir(exist_ok=True)
        
        # Find or create current session file
        today = datetime.now().strftime("%Y-%m-%d")
        session_file = self.chat_dir / f"session-{today}.md"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"\n## {role.upper()} ({timestamp})\n\n{content}\n"
        
        with open(session_file, "a") as f:
            f.write(message)
    
    def create_project_scaffold(self, project_name="React App", description=""):
        """Create a complete file tree scaffold with placeholder files and documentation"""
        print(f"🏗️  Creating project scaffold for: {project_name}")
        
        # Create directory structure
        directories = [
            self.project_dir / "src",
            self.project_dir / "src/components",
            self.project_dir / "src/components/common",
            self.project_dir / "src/components/layout",
            self.project_dir / "src/components/features",
            self.project_dir / "src/hooks",
            self.project_dir / "src/utils",
            self.project_dir / "src/types",
            self.project_dir / "src/styles",
            self.project_dir / "src/services",
            self.project_dir / "src/contexts",
            self.project_dir / "public",
        ]
        
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create main documentation files
        self._create_architecture_doc(project_name, description)
        self._create_components_doc()
        self._create_styling_doc()
        self._create_state_doc()
        
        # Create component files with documentation
        self._create_component_files()
        
        # Create utility and service files
        self._create_utility_files()
        
        # Create context files
        self._create_context_files()
        
        # Create type definitions
        self._create_type_files()
        
        # Create style files
        self._create_style_files()
        
        # Create component README
        self._create_component_readme()
        
        print("✅ Project scaffold created successfully!")
        return True
    
    def _create_architecture_doc(self, project_name, description):
        """Create ARCHITECTURE.md with overall project structure"""
        content = f"""# {project_name} Architecture

## Overview
{description or 'A modern React application built with TypeScript and best practices.'}

## Project Structure

```
project/
├── src/
│   ├── components/          # React components
│   │   ├── common/         # Reusable UI components
│   │   ├── layout/         # Layout components (Header, Footer, etc.)
│   │   └── features/       # Feature-specific components
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   ├── types/              # TypeScript type definitions
│   ├── styles/             # Global styles and themes
│   ├── services/           # API and external service integrations
│   ├── contexts/           # React Context providers
│   ├── App.tsx            # Main application component
│   └── index.tsx          # Application entry point
├── public/                 # Static assets
├── package.json           # Project dependencies
└── README.md             # Project documentation
```

## Component Architecture

### Component Hierarchy
- **App** (Root component)
  - **Layout** (Main layout wrapper)
    - **Header** (Navigation and branding)
    - **Main** (Content area)
    - **Footer** (Site information)

### Common Components
- **Button**: Reusable button with variants
- **Input**: Form input component
- **Card**: Content container
- **Modal**: Overlay dialog
- **Loading**: Loading indicator

### Feature Components
Feature-specific components are organized by domain and contain:
- UI components
- Business logic
- Local state management
- API integrations

## Data Flow

1. **Global State**: Managed via React Context (see STATE.md)
2. **Local State**: Component-specific state using useState/useReducer
3. **Side Effects**: Handled with useEffect and custom hooks
4. **API Calls**: Centralized in services layer

## Styling Strategy

- **CSS Modules**: For component-specific styles
- **Global Styles**: Theme variables and resets
- **Responsive Design**: Mobile-first approach
- See STYLING.md for detailed styling guidelines

## Best Practices

1. **Component Design**
   - Single Responsibility Principle
   - Props interface documentation
   - Default props where appropriate
   - Memoization for performance

2. **Code Organization**
   - Co-locate related files
   - Clear naming conventions
   - Consistent file structure

3. **Performance**
   - Lazy loading for routes
   - Code splitting
   - Optimized re-renders

4. **Testing**
   - Unit tests for utilities
   - Component testing
   - Integration tests
"""
        
        (self.project_dir / "ARCHITECTURE.md").write_text(content)
    
    def _create_components_doc(self):
        """Create COMPONENTS.md with component hierarchy and relationships"""
        content = """# Component Documentation

## Component Hierarchy

```
App
├── Layout
│   ├── Header
│   │   ├── Navigation
│   │   └── Logo
│   ├── Main
│   │   └── [Page Components]
│   └── Footer
│       ├── Links
│       └── Copyright
└── Providers
    ├── ThemeProvider
    └── AppStateProvider
```

## Common Components

### Button
- **Location**: `src/components/common/Button.tsx`
- **Purpose**: Reusable button component with multiple variants
- **Props**:
  - `variant`: 'primary' | 'secondary' | 'danger'
  - `size`: 'sm' | 'md' | 'lg'
  - `disabled`: boolean
  - `onClick`: () => void
  - `children`: React.ReactNode
- **Used in**: Forms, Modals, CTAs throughout the app

### Input
- **Location**: `src/components/common/Input.tsx`
- **Purpose**: Form input component with validation support
- **Props**:
  - `type`: string
  - `placeholder`: string
  - `value`: string
  - `onChange`: (value: string) => void
  - `error`: string | undefined
- **Used in**: Forms, Search bars

### Card
- **Location**: `src/components/common/Card.tsx`
- **Purpose**: Content container with consistent styling
- **Props**:
  - `title`: string | undefined
  - `children`: React.ReactNode
  - `className`: string | undefined
- **Used in**: Content sections, Feature displays

### Modal
- **Location**: `src/components/common/Modal.tsx`
- **Purpose**: Overlay dialog for focused interactions
- **Props**:
  - `isOpen`: boolean
  - `onClose`: () => void
  - `title`: string
  - `children`: React.ReactNode
- **Used in**: Confirmations, Forms, Detail views

### Loading
- **Location**: `src/components/common/Loading.tsx`
- **Purpose**: Loading state indicator
- **Props**:
  - `size`: 'sm' | 'md' | 'lg'
  - `color`: string | undefined
- **Used in**: Async operations, Data fetching

## Layout Components

### Header
- **Location**: `src/components/layout/Header.tsx`
- **Purpose**: Application header with navigation
- **Contains**: Logo, Navigation menu, User actions
- **State**: Current route, User authentication status

### Footer
- **Location**: `src/components/layout/Footer.tsx`
- **Purpose**: Application footer with links and info
- **Contains**: Links, Copyright, Social media

### Layout
- **Location**: `src/components/layout/Layout.tsx`
- **Purpose**: Main layout wrapper
- **Contains**: Header, Main content area, Footer
- **Provides**: Consistent page structure

## Component Guidelines

### Naming Conventions
- Components: PascalCase (e.g., `UserProfile`)
- Props interfaces: `I{ComponentName}Props`
- Files: Same as component name

### File Structure
```
ComponentName/
├── ComponentName.tsx      # Main component
├── ComponentName.module.css # Styles
├── ComponentName.test.tsx  # Tests
└── index.ts              # Exports
```

### Props Documentation
Every component should have:
1. TypeScript interface for props
2. JSDoc comments for complex props
3. Default props where applicable

### State Management
- Prefer local state for UI-only concerns
- Use context for cross-component state
- Document state dependencies
"""
        
        (self.project_dir / "COMPONENTS.md").write_text(content)
    
    def _create_styling_doc(self):
        """Create STYLING.md with global styles and theme documentation"""
        content = """# Styling Guidelines

## Global Theme

### Colors
```css
:root {
  /* Primary Colors */
  --primary-500: #3B82F6;
  --primary-600: #2563EB;
  --primary-700: #1D4ED8;
  
  /* Secondary Colors */
  --secondary-500: #8B5CF6;
  --secondary-600: #7C3AED;
  
  /* Neutral Colors */
  --gray-50: #F9FAFB;
  --gray-100: #F3F4F6;
  --gray-200: #E5E7EB;
  --gray-300: #D1D5DB;
  --gray-400: #9CA3AF;
  --gray-500: #6B7280;
  --gray-600: #4B5563;
  --gray-700: #374151;
  --gray-800: #1F2937;
  --gray-900: #111827;
  
  /* Semantic Colors */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
}
```

### Typography
```css
:root {
  /* Font Families */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Courier New', monospace;
  
  /* Font Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Spacing
```css
:root {
  /* Spacing Scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  --space-24: 6rem;
}
```

### Breakpoints
```css
/* Mobile First Approach */
/* Default: Mobile (< 640px) */
/* Tablet: >= 640px */
/* Desktop: >= 1024px */
/* Wide: >= 1280px */

@media (min-width: 640px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
@media (min-width: 1280px) { /* Wide */ }
```

## Component Styling

### CSS Modules
Each component uses CSS Modules for scoped styling:

```css
/* Button.module.css */
.button {
  /* Base styles */
  padding: var(--space-2) var(--space-4);
  font-weight: var(--font-medium);
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.primary {
  background-color: var(--primary-500);
  color: white;
}

.primary:hover {
  background-color: var(--primary-600);
}
```

### Global Styles
```css
/* src/styles/globals.css */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-sans);
  color: var(--gray-900);
  background-color: var(--gray-50);
  line-height: var(--leading-normal);
}

/* Utility Classes */
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

## Styling Best Practices

### 1. Use CSS Variables
- Define all colors, spacing, and typography in CSS variables
- Reference variables instead of hard-coded values
- Enables easy theming and consistency

### 2. Mobile-First Design
- Start with mobile styles
- Add complexity for larger screens
- Use min-width media queries

### 3. Component Isolation
- Use CSS Modules for component styles
- Avoid global class names
- Keep specificity low

### 4. Performance
- Minimize CSS bundle size
- Use CSS containment where appropriate
- Avoid expensive selectors

### 5. Accessibility
- Ensure sufficient color contrast
- Include focus styles
- Use semantic HTML

### 6. Animation Guidelines
```css
/* Prefer transform and opacity for animations */
.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```
"""
        
        (self.project_dir / "STYLING.md").write_text(content)
    
    def _create_state_doc(self):
        """Create STATE.md with data flow and state management documentation"""
        content = """# State Management

## Overview
This application uses a combination of local component state and React Context for global state management.

## State Architecture

### Global State (Context)
```
AppStateContext
├── user (authentication and profile)
├── theme (light/dark mode)
├── notifications (system messages)
└── preferences (user settings)
```

### Local State
- Form inputs
- UI toggles (modals, dropdowns)
- Component-specific data

## Context Providers

### AppStateContext
**Location**: `src/contexts/AppStateContext.tsx`

```typescript
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
  preferences: UserPreferences;
}

interface AppStateContextValue {
  state: AppState;
  actions: {
    setUser: (user: User | null) => void;
    toggleTheme: () => void;
    addNotification: (notification: Notification) => void;
    removeNotification: (id: string) => void;
    updatePreferences: (preferences: Partial<UserPreferences>) => void;
  };
}
```

**Usage**:
```typescript
const { state, actions } = useAppState();

// Access state
const currentUser = state.user;

// Update state
actions.setUser(newUser);
```

### ThemeContext
**Location**: `src/contexts/ThemeContext.tsx`

Manages application theme and provides theme utilities:
- Theme toggle functionality
- System preference detection
- Theme persistence in localStorage

## State Management Patterns

### 1. Form State
```typescript
// Use local state for form inputs
const [formData, setFormData] = useState({
  name: '',
  email: '',
});

// Update handler
const handleChange = (field: string, value: string) => {
  setFormData(prev => ({ ...prev, [field]: value }));
};
```

### 2. Async State
```typescript
// Loading states for async operations
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState<Data | null>(null);

// Fetch pattern
const fetchData = async () => {
  setLoading(true);
  setError(null);
  try {
    const result = await api.getData();
    setData(result);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

### 3. Derived State
```typescript
// Compute values from existing state
const isAuthenticated = useMemo(() => !!state.user, [state.user]);
const fullName = useMemo(
  () => `${state.user?.firstName} ${state.user?.lastName}`,
  [state.user]
);
```

## Custom Hooks

### useLocalStorage
Persists state to localStorage:
```typescript
const [value, setValue] = useLocalStorage('key', defaultValue);
```

### useDebounce
Debounces a value:
```typescript
const debouncedSearchTerm = useDebounce(searchTerm, 500);
```

### useAsync
Manages async operations:
```typescript
const { data, error, loading, execute } = useAsync(asyncFunction);
```

## State Best Practices

### 1. State Colocation
- Keep state as close to where it's used as possible
- Lift state up only when necessary
- Use context for truly global state

### 2. State Updates
- Always use immutable updates
- Batch related state updates
- Use functional updates for dependent state

### 3. Performance
- Memoize expensive computations
- Split contexts to avoid unnecessary re-renders
- Use React.memo for pure components

### 4. Type Safety
- Define interfaces for all state shapes
- Use discriminated unions for complex state
- Leverage TypeScript's type inference

### 5. Testing
- Test state transitions
- Mock context providers in tests
- Verify side effects

## Data Flow Examples

### User Authentication Flow
1. User submits login form (local state)
2. API call to authenticate
3. On success, update global user state
4. Navigate to dashboard
5. All components access user via context

### Theme Toggle Flow
1. User clicks theme toggle
2. ThemeContext updates theme state
3. Theme persisted to localStorage
4. CSS variables updated
5. All components re-render with new theme

### Form Submission Flow
1. User fills form (local state)
2. Validate on change (derived state)
3. Submit triggers API call
4. Show loading state
5. On success, update global state
6. On error, show error message
"""
        
        (self.project_dir / "STATE.md").write_text(content)
    
    def _create_component_files(self):
        """Create placeholder component files with documentation"""
        components = [
            # Common components
            {
                "path": "src/components/common/Button.tsx",
                "content": """// Button.tsx
// Purpose: Reusable button component used throughout the app
// Props: variant (primary|secondary|danger), size (sm|md|lg), disabled, onClick
// Used in: Header, Forms, Modals, CTAs
// Global styling: See STYLING.md for button theme variables

import React from 'react';
import styles from './Button.module.css';

interface IButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export const Button: React.FC<IButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children,
  className = '',
  type = 'button'
}) => {
  // TODO: Implement button component
  return (
    <button
      type={type}
      className={`${styles.button} ${styles[variant]} ${styles[size]} ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
"""
            },
            {
                "path": "src/components/common/Input.tsx",
                "content": """// Input.tsx
// Purpose: Form input component with validation support
// Props: type, placeholder, value, onChange, error, label, required
// Used in: Forms throughout the application
// Global styling: See STYLING.md for form input styles

import React from 'react';
import styles from './Input.module.css';

interface IInputProps {
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  label?: string;
  required?: boolean;
  name?: string;
  id?: string;
}

export const Input: React.FC<IInputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  label,
  required = false,
  name,
  id
}) => {
  // TODO: Implement input component with validation
  return (
    <div className={styles.inputWrapper}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label} {required && <span className={styles.required}>*</span>}
        </label>
      )}
      <input
        type={type}
        id={id}
        name={name}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`${styles.input} ${error ? styles.error : ''}`}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
      />
      {error && (
        <span id={`${id}-error`} className={styles.errorMessage}>
          {error}
        </span>
      )}
    </div>
  );
};
"""
            },
            {
                "path": "src/components/common/Card.tsx",
                "content": """// Card.tsx
// Purpose: Content container with consistent styling and shadows
// Props: title, children, className, onClick
// Used in: Content sections, Feature displays, Lists
// Global styling: See STYLING.md for card elevation and spacing

import React from 'react';
import styles from './Card.module.css';

interface ICardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  variant?: 'default' | 'bordered' | 'elevated';
}

export const Card: React.FC<ICardProps> = ({
  title,
  children,
  className = '',
  onClick,
  variant = 'default'
}) => {
  // TODO: Implement card component
  const isClickable = !!onClick;
  
  return (
    <div
      className={`${styles.card} ${styles[variant]} ${isClickable ? styles.clickable : ''} ${className}`}
      onClick={onClick}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
    >
      {title && <h3 className={styles.title}>{title}</h3>}
      <div className={styles.content}>{children}</div>
    </div>
  );
};
"""
            },
            {
                "path": "src/components/common/Modal.tsx",
                "content": """// Modal.tsx
// Purpose: Overlay dialog for focused user interactions
// Props: isOpen, onClose, title, children, size
// Used in: Confirmations, Forms, Detail views, Alerts
// Global styling: See STYLING.md for overlay and modal styles

import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import styles from './Modal.module.css';

interface IModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export const Modal: React.FC<IModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md'
}) => {
  // TODO: Implement modal with portal, focus trap, and escape key handling
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);
  
  if (!isOpen) return null;
  
  return createPortal(
    <div className={styles.overlay} onClick={onClose}>
      <div
        className={`${styles.modal} ${styles[size]}`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className={styles.header}>
          <h2 id="modal-title" className={styles.title}>{title}</h2>
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close modal"
          >
            ×
          </button>
        </div>
        <div className={styles.content}>{children}</div>
      </div>
    </div>,
    document.body
  );
};
"""
            },
            {
                "path": "src/components/common/Loading.tsx",
                "content": """// Loading.tsx
// Purpose: Loading state indicator for async operations
// Props: size (sm|md|lg), color, text
// Used in: Data fetching, Form submissions, Route transitions
// Global styling: See STYLING.md for animation styles

import React from 'react';
import styles from './Loading.module.css';

interface ILoadingProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  text?: string;
}

export const Loading: React.FC<ILoadingProps> = ({
  size = 'md',
  color,
  text = 'Loading...'
}) => {
  // TODO: Implement loading spinner
  return (
    <div className={styles.container}>
      <div
        className={`${styles.spinner} ${styles[size]}`}
        style={{ borderTopColor: color }}
        role="status"
        aria-live="polite"
      >
        <span className="sr-only">{text}</span>
      </div>
      {text && <p className={styles.text}>{text}</p>}
    </div>
  );
};
"""
            },
            # Layout components
            {
                "path": "src/components/layout/Layout.tsx",
                "content": """// Layout.tsx
// Purpose: Main layout wrapper providing consistent page structure
// Props: children
// Used in: App root to wrap all pages
// Contains: Header, Main content area, Footer
// Global styling: See STYLING.md for layout grid and spacing

import React from 'react';
import { Header } from './Header';
import { Footer } from './Footer';
import styles from './Layout.module.css';

interface ILayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<ILayoutProps> = ({ children }) => {
  // TODO: Implement layout with skip navigation, main landmark
  return (
    <div className={styles.layout}>
      <a href="#main-content" className={styles.skipLink}>
        Skip to main content
      </a>
      <Header />
      <main id="main-content" className={styles.main}>
        {children}
      </main>
      <Footer />
    </div>
  );
};
"""
            },
            {
                "path": "src/components/layout/Header.tsx",
                "content": """// Header.tsx
// Purpose: Application header with navigation and branding
// Contains: Logo, Navigation menu, User actions
// State: Current route (from router), User auth status (from context)
// Global styling: See STYLING.md for header theme

import React from 'react';
import { useAppState } from '../../contexts/AppStateContext';
import styles from './Header.module.css';

export const Header: React.FC = () => {
  const { state, actions } = useAppState();
  
  // TODO: Implement responsive navigation, mobile menu
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          {/* Logo component */}
        </div>
        <nav className={styles.nav} aria-label="Main navigation">
          {/* Navigation items */}
        </nav>
        <div className={styles.actions}>
          {/* User actions, theme toggle */}
        </div>
      </div>
    </header>
  );
};
"""
            },
            {
                "path": "src/components/layout/Footer.tsx",
                "content": """// Footer.tsx
// Purpose: Application footer with links and company information
// Contains: Links, Copyright, Social media icons
// Global styling: See STYLING.md for footer styles

import React from 'react';
import styles from './Footer.module.css';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  // TODO: Implement footer with links, social media
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.links}>
          {/* Footer links */}
        </div>
        <div className={styles.social}>
          {/* Social media links */}
        </div>
        <div className={styles.copyright}>
          © {currentYear} Your Company. All rights reserved.
        </div>
      </div>
    </footer>
  );
};
"""
            }
        ]
        
        # Create component files
        for component in components:
            file_path = self.project_dir / component["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(component["content"])
            
            # Create corresponding CSS module file
            css_path = file_path.with_suffix('.module.css')
            css_path.write_text(f"""/* {file_path.stem}.module.css */
/* Component-specific styles for {file_path.stem} */
/* See STYLING.md for global theme variables */

.container {{
  /* Component container styles */
}}
""")
    
    def _create_utility_files(self):
        """Create utility function files"""
        utils = [
            {
                "path": "src/utils/helpers.ts",
                "content": """// helpers.ts
// Purpose: General utility functions used throughout the app
// Used in: Components, services, and other utilities

/**
 * Format a date to a readable string
 */
export const formatDate = (date: Date): string => {
  // TODO: Implement date formatting
  return date.toLocaleDateString();
};

/**
 * Debounce a function call
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Generate a unique ID
 */
export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Capitalize first letter of a string
 */
export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};
"""
            },
            {
                "path": "src/utils/validators.ts",
                "content": """// validators.ts
// Purpose: Form validation functions
// Used in: Form components, Input validation

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate required field
 */
export const isRequired = (value: any): boolean => {
  return value !== null && value !== undefined && value !== '';
};

/**
 * Validate minimum length
 */
export const minLength = (min: number) => (value: string): boolean => {
  return value.length >= min;
};

/**
 * Validate maximum length
 */
export const maxLength = (max: number) => (value: string): boolean => {
  return value.length <= max;
};

/**
 * Compose multiple validators
 */
export const composeValidators = (...validators: Array<(value: any) => boolean | string>) => 
  (value: any): string | undefined => {
    for (const validator of validators) {
      const result = validator(value);
      if (typeof result === 'string') return result;
      if (!result) return 'Invalid value';
    }
    return undefined;
  };
"""
            }
        ]
        
        for util in utils:
            file_path = self.project_dir / util["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(util["content"])
    
    def _create_context_files(self):
        """Create React Context files"""
        contexts = [
            {
                "path": "src/contexts/AppStateContext.tsx",
                "content": """// AppStateContext.tsx
// Purpose: Global application state management
// Provides: User state, notifications, preferences
// Used in: Throughout the app for global state access
// See STATE.md for state management patterns

import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { User, Notification, UserPreferences } from '../types';

interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
  preferences: UserPreferences;
}

type AppStateAction = 
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'TOGGLE_THEME' }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'UPDATE_PREFERENCES'; payload: Partial<UserPreferences> };

const initialState: AppState = {
  user: null,
  theme: 'light',
  notifications: [],
  preferences: {
    language: 'en',
    timezone: 'UTC',
  }
};

const appStateReducer = (state: AppState, action: AppStateAction): AppState => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'TOGGLE_THEME':
      return { ...state, theme: state.theme === 'light' ? 'dark' : 'light' };
    case 'ADD_NOTIFICATION':
      return { ...state, notifications: [...state.notifications, action.payload] };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    case 'UPDATE_PREFERENCES':
      return {
        ...state,
        preferences: { ...state.preferences, ...action.payload }
      };
    default:
      return state;
  }
};

interface AppStateContextValue {
  state: AppState;
  actions: {
    setUser: (user: User | null) => void;
    toggleTheme: () => void;
    addNotification: (notification: Notification) => void;
    removeNotification: (id: string) => void;
    updatePreferences: (preferences: Partial<UserPreferences>) => void;
  };
}

const AppStateContext = createContext<AppStateContextValue | undefined>(undefined);

export const AppStateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appStateReducer, initialState);
  
  const actions = {
    setUser: (user: User | null) => dispatch({ type: 'SET_USER', payload: user }),
    toggleTheme: () => dispatch({ type: 'TOGGLE_THEME' }),
    addNotification: (notification: Notification) => 
      dispatch({ type: 'ADD_NOTIFICATION', payload: notification }),
    removeNotification: (id: string) => 
      dispatch({ type: 'REMOVE_NOTIFICATION', payload: id }),
    updatePreferences: (preferences: Partial<UserPreferences>) =>
      dispatch({ type: 'UPDATE_PREFERENCES', payload: preferences }),
  };
  
  return (
    <AppStateContext.Provider value={{ state, actions }}>
      {children}
    </AppStateContext.Provider>
  );
};

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within AppStateProvider');
  }
  return context;
};
"""
            }
        ]
        
        for context in contexts:
            file_path = self.project_dir / context["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(context["content"])
    
    def _create_type_files(self):
        """Create TypeScript type definition files"""
        types = [
            {
                "path": "src/types/index.ts",
                "content": """// index.ts
// Purpose: Central type definitions used throughout the application
// Used in: Components, contexts, services

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatar?: string;
  role: 'admin' | 'user';
  createdAt: Date;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  timestamp: Date;
  read: boolean;
}

export interface UserPreferences {
  language: string;
  timezone: string;
  notifications?: {
    email: boolean;
    push: boolean;
  };
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
"""
            }
        ]
        
        for type_file in types:
            file_path = self.project_dir / type_file["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(type_file["content"])
    
    def _create_style_files(self):
        """Create global style files"""
        styles = [
            {
                "path": "src/styles/globals.css",
                "content": """/* globals.css */
/* Global styles and CSS reset */
/* See STYLING.md for theme variables and guidelines */

:root {
  /* Colors */
  --primary-500: #3B82F6;
  --primary-600: #2563EB;
  --gray-50: #F9FAFB;
  --gray-900: #111827;
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  /* Spacing */
  --space-4: 1rem;
  --space-8: 2rem;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-sans);
  color: var(--gray-900);
  background-color: var(--gray-50);
  line-height: 1.5;
}

/* Accessibility */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Focus styles */
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
"""
            }
        ]
        
        for style in styles:
            file_path = self.project_dir / style["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(style["content"])
    
    def _create_component_readme(self):
        """Create README for components directory"""
        content = """# Components Directory

This directory contains all React components organized by type and feature.

## Structure

```
components/
├── common/          # Reusable UI components
├── layout/          # Layout components
└── features/        # Feature-specific components
```

## Component Guidelines

### Creating a New Component

1. **File Structure**
   ```
   ComponentName/
   ├── ComponentName.tsx
   ├── ComponentName.module.css
   ├── ComponentName.test.tsx
   └── index.ts
   ```

2. **Component Template**
   ```typescript
   // ComponentName.tsx
   // Purpose: [Describe what this component does]
   // Props: [List main props]
   // Used in: [Where this component is used]
   // Global styling: [Reference to STYLING.md if applicable]
   
   import React from 'react';
   import styles from './ComponentName.module.css';
   
   interface IComponentNameProps {
     // Define props here
   }
   
   export const ComponentName: React.FC<IComponentNameProps> = (props) => {
     // Component implementation
   };
   ```

3. **Documentation**
   - Add inline comments for complex logic
   - Document all props in the interface
   - Update COMPONENTS.md when adding new components

## Best Practices

1. **Single Responsibility**: Each component should do one thing well
2. **Props Documentation**: Use TypeScript interfaces with JSDoc comments
3. **Accessibility**: Include ARIA labels, roles, and keyboard navigation
4. **Performance**: Use React.memo for pure components, useMemo for expensive computations
5. **Testing**: Write tests for all interactive components

## Common Components

See individual component files for detailed documentation:
- `Button` - Versatile button with multiple variants
- `Input` - Form input with validation
- `Card` - Content container
- `Modal` - Overlay dialog
- `Loading` - Loading states

## Adding to the Component Library

When creating a new reusable component:
1. Place it in the `common/` directory
2. Document it thoroughly
3. Add it to COMPONENTS.md
4. Create usage examples
5. Write comprehensive tests
"""
        
        readme_path = self.project_dir / "src/components/README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(content)
    
    def _create_service_files(self):
        """Create service layer files for API integration"""
        services = [
            {
                "path": "src/services/api.ts",
                "content": """// api.ts
// Purpose: Central API client for all backend communications
// Used in: Components and hooks that need to fetch data
// Configuration: Base URL and auth headers

import { ApiResponse } from '../types';

class ApiClient {
  private baseURL: string;
  private headers: HeadersInit;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || '/api';
    this.headers = {
      'Content-Type': 'application/json',
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          ...this.headers,
          ...options.headers,
        },
      });

      const data = await response.json();

      return {
        data,
        status: response.status,
        error: response.ok ? undefined : data.message || 'Request failed',
      };
    } catch (error) {
      return {
        data: null as any,
        status: 500,
        error: error instanceof Error ? error.message : 'Network error',
      };
    }
  }

  // GET request
  get<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  post<T>(endpoint: string, data: any) {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // PUT request
  put<T>(endpoint: string, data: any) {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // Set auth token
  setAuthToken(token: string) {
    this.headers = {
      ...this.headers,
      Authorization: `Bearer ${token}`,
    };
  }

  // Clear auth token
  clearAuthToken() {
    const { Authorization, ...headers } = this.headers as any;
    this.headers = headers;
  }
}

export const api = new ApiClient();
"""
            }
        ]
        
        for service in services:
            file_path = self.project_dir / service["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(service["content"])
    
    def _create_hook_files(self):
        """Create custom React hooks"""
        hooks = [
            {
                "path": "src/hooks/useLocalStorage.ts",
                "content": """// useLocalStorage.ts
// Purpose: Persist state to localStorage with TypeScript support
// Used in: Components that need persistent state across sessions
// Example: Theme preferences, user settings

import { useState, useEffect } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // Get from local storage then parse stored json or return initialValue
  const readValue = (): T => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  };

  const [storedValue, setStoredValue] = useState<T>(readValue);

  // Return a wrapped version of useState's setter function that persists the new value to localStorage
  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      
      // Save to local state
      setStoredValue(valueToStore);
      
      // Save to local storage
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  useEffect(() => {
    setStoredValue(readValue());
  }, []);

  return [storedValue, setValue];
}
"""
            },
            {
                "path": "src/hooks/useDebounce.ts",
                "content": """// useDebounce.ts
// Purpose: Debounce rapidly changing values
// Used in: Search inputs, form validation, API calls
// Example: Search suggestions, real-time validation

import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Update debounced value after delay
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Cancel the timeout if value changes (also on delay change or unmount)
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
"""
            },
            {
                "path": "src/hooks/index.ts",
                "content": """// index.ts
// Purpose: Export all custom hooks from a single location
// This makes imports cleaner throughout the application

export { useLocalStorage } from './useLocalStorage';
export { useDebounce } from './useDebounce';
"""
            }
        ]
        
        for hook in hooks:
            file_path = self.project_dir / hook["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(hook["content"])
    
    def execute_claude_code(self, user_message):
        """Execute Claude Code with full workspace context"""
        
        # Check if this is a new project that needs scaffolding
        if self._is_new_project() and self._should_create_scaffold(user_message):
            project_info = self._extract_project_info(user_message)
            self.create_project_scaffold(project_info['name'], project_info['description'])
        
        # Save user message to chat history
        self.save_chat_message("user", user_message)
        
        # Build context-aware prompt
        context = self.get_workspace_context()
        
        enhanced_prompt = f"""
WORKSPACE CONTEXT:
{json.dumps(context, indent=2)}

USER MESSAGE:
{user_message}

You are operating in a complete development workspace with access to:
- /workspace/project/ - The React app being built
- /workspace/planning/ - Requirements and planning documents  
- /workspace/reference/ - User-uploaded examples and assets
- /workspace/chat-history/ - Previous conversation history

Please help the user build their React application. You can:
1. Create/modify files in any workspace directory
2. Update planning documents as requirements evolve
3. Reference previous conversations and decisions
4. Use uploaded reference materials for guidance

IMPORTANT: The project has been scaffolded with:
- Complete file structure (see ARCHITECTURE.md)
- All components as placeholder files with documentation comments
- Global documentation files (COMPONENTS.md, STYLING.md, STATE.md)
- Each component includes comments about its purpose, props, usage, and styling references

Use this scaffolding to understand the entire application structure and make global changes effectively.

Focus on iterative development - ask clarifying questions and build incrementally.
"""

        try:
            # Execute Claude Code with enhanced context
            result = subprocess.run(
                ["claude-code", enhanced_prompt],
                capture_output=True,
                text=True,
                cwd=str(self.workspace_root),
                timeout=120  # 2 minute timeout
            )
            
            response = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
            
            # Save Claude's response to chat history
            self.save_chat_message("assistant", response)
            
            return {
                "success": True,
                "response": response,
                "context_used": True,
                "workspace_updated": True
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "response": "Request timed out. Please try with a simpler request.",
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Error executing Claude Code: {str(e)}",
                "error": str(e)
            }
    
    def _is_new_project(self):
        """Check if this is a new project that needs scaffolding"""
        # Check if key scaffold files exist
        architecture_exists = (self.project_dir / "ARCHITECTURE.md").exists()
        components_exists = (self.project_dir / "COMPONENTS.md").exists()
        src_exists = (self.project_dir / "src").exists()
        
        return not (architecture_exists and components_exists and src_exists)
    
    def _should_create_scaffold(self, user_message):
        """Determine if the user message indicates starting a new project"""
        keywords = ['build', 'create', 'make', 'start', 'new', 'app', 'application', 'project']
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def _extract_project_info(self, user_message):
        """Extract project name and description from user message"""
        # Simple extraction - could be enhanced with better NLP
        words = user_message.split()
        
        # Try to find project name patterns
        project_name = "React App"
        description = user_message
        
        # Look for patterns like "todo app", "blog site", etc.
        for i, word in enumerate(words):
            if word.lower() in ['app', 'application', 'site', 'platform', 'tool']:
                if i > 0:
                    project_name = f"{words[i-1].title()} {word.title()}"
                    break
        
        return {
            'name': project_name,
            'description': description
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python claude-handler.py 'Your message to Claude'")
        sys.exit(1)
    
    handler = WorkspaceClaudeHandler()
    result = handler.execute_claude_code(" ".join(sys.argv[1:]))
    
    print(json.dumps(result, indent=2))