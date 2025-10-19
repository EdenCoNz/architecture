# User Story Template Library

## Purpose
This library provides reusable templates for common development patterns to help create consistent, atomic user stories quickly. Each template is technology-agnostic, focuses on observable behaviors, and follows atomicity best practices.

## How to Use Templates

1. **Select the appropriate template** based on the operation or pattern you need
2. **Customize the placeholders** (marked with {curly braces}) to match your specific feature
3. **Verify acceptance criteria** are specific to your use case
4. **Add the technology-agnostic disclaimer** at the end
5. **Run atomicity validation** to ensure the story scores >= 70

## Template Categories

- [Create/Add Operations](#createadd-operations)
- [Read/Display Operations](#readdisplay-operations)
- [Update/Edit Operations](#updateedit-operations)
- [Delete/Remove Operations](#deleteremove-operations)
- [Authentication & Authorization](#authentication--authorization)
- [API Endpoint](#api-endpoint)
- [Configuration](#configuration)
- [UI Component](#ui-component)
- [Service Layer](#service-layer)
- [Design](#design)

---

## Create/Add Operations

### Template: Create New Entity

**Title Format:** `Create {Entity Name}`

**Description:**
```
Enable users to create a new {entity name} by providing required information. The system validates input, stores the {entity}, and provides confirmation of successful creation.
```

**Acceptance Criteria:**
```
- Users can provide all required information for a new {entity}
- System validates input and displays clear error messages for invalid data
- Successfully created {entity} is persisted and retrievable
```

**Usage Example:**
```
### Create New Task

Enable users to create a new task by providing required information. The system validates input, stores the task, and provides confirmation of successful creation.

Acceptance Criteria:
- Users can provide all required information for a new task
- System validates input and displays clear error messages for invalid data
- Successfully created task is persisted and retrievable

Agent: backend-developer
Dependencies: none

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {entity name}: Replace with your domain object (e.g., "task", "user profile", "product listing")
- Add domain-specific validation rules to acceptance criteria
- Consider if creation requires authentication (add criteria if needed)

**Atomicity Score:** 85-95 (EXCELLENT)
- Simple CRUD operation
- Touches 1-3 files typically
- Clear, focused scope
- 3 acceptance criteria

---

### Template: Initialize New Component or Module

**Title Format:** `Initialize {Component/Module Name}`

**Description:**
```
Set up the {component/module name} with proper structure, configuration, and foundational elements required for future development.
```

**Acceptance Criteria:**
```
- {Component/module} structure created following project conventions
- Essential configuration files present and properly formatted
- {Component/module} can be successfully integrated into the application
```

**Usage Example:**
```
### Initialize Payment Processing Module

Set up the payment processing module with proper structure, configuration, and foundational elements required for future development.

Acceptance Criteria:
- Payment module structure created following project conventions
- Essential configuration files present and properly formatted
- Payment module can be successfully integrated into the application

Agent: backend-developer
Dependencies: none

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {component/module name}: Specific component or module being initialized
- Adjust criteria based on complexity (configuration needs, dependencies)
- Consider if initialization includes example/placeholder code

**Atomicity Score:** 80-90 (GOOD to EXCELLENT)
- Focused on setup only
- Typically 2-4 files
- No complex logic

---

## Read/Display Operations

### Template: Display List of Entities

**Title Format:** `Display {Entity} List`

**Description:**
```
Present users with a list of all {entities}, showing key information for each item. The list should be easy to scan and navigate.
```

**Acceptance Criteria:**
```
- All {entities} are retrieved and displayed to the user
- Each {entity} shows essential identifying information
- List is presented in a clear, organized format
```

**Usage Example:**
```
### Display Task List

Present users with a list of all tasks, showing key information for each item. The list should be easy to scan and navigate.

Acceptance Criteria:
- All tasks are retrieved and displayed to the user
- Each task shows essential identifying information
- List is presented in a clear, organized format

Agent: frontend-developer
Dependencies: 2

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {entity/entities}: Domain object being listed
- Add pagination, filtering, or sorting criteria if needed (but consider splitting if too complex)
- Specify what "essential information" means for your domain

**Atomicity Score:** 85-95 (EXCELLENT)
- Single responsibility: display list
- Typically 1-3 files (component + service)
- No complex business logic

---

### Template: Display Single Entity Details

**Title Format:** `Display {Entity} Details`

**Description:**
```
Show comprehensive information about a single {entity} when a user selects or navigates to it. All relevant fields and related data should be visible.
```

**Acceptance Criteria:**
```
- {Entity} data is retrieved based on identifier
- All relevant information about the {entity} is displayed
- User can clearly see all details in an organized layout
```

**Usage Example:**
```
### Display User Profile Details

Show comprehensive information about a single user profile when a user selects or navigates to it. All relevant fields and related data should be visible.

Acceptance Criteria:
- User profile data is retrieved based on identifier
- All relevant information about the user profile is displayed
- User can clearly see all details in an organized layout

Agent: frontend-developer
Dependencies: 3

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {entity}: Specific domain object
- Define what "relevant information" includes
- Consider read-only vs editable display (split if both needed)

**Atomicity Score:** 85-95 (EXCELLENT)
- Single view responsibility
- 1-3 files
- Straightforward retrieval

---

## Update/Edit Operations

### Template: Update Existing Entity

**Title Format:** `Update {Entity} Information`

**Description:**
```
Allow users to modify information for an existing {entity}. Changes are validated, persisted, and confirmed to the user.
```

**Acceptance Criteria:**
```
- Users can modify editable fields of an existing {entity}
- System validates changes and displays clear error messages for invalid input
- Successfully updated {entity} reflects changes immediately
```

**Usage Example:**
```
### Update Task Information

Allow users to modify information for an existing task. Changes are validated, persisted, and confirmed to the user.

Acceptance Criteria:
- Users can modify editable fields of an existing task
- System validates changes and displays clear error messages for invalid input
- Successfully updated task reflects changes immediately

Agent: backend-developer
Dependencies: 5

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {entity}: Domain object being updated
- Specify which fields are editable vs read-only if important
- Consider partial updates vs full replacement

**Atomicity Score:** 85-90 (EXCELLENT to GOOD)
- Single operation focus
- 1-4 files (endpoint, validation, persistence)
- Clear scope

---

## Delete/Remove Operations

### Template: Delete Entity

**Title Format:** `Delete {Entity}`

**Description:**
```
Enable users to remove an existing {entity} from the system. The operation includes confirmation and handles any necessary cleanup.
```

**Acceptance Criteria:**
```
- Users can initiate deletion of a specific {entity}
- System confirms deletion intent before proceeding
- Deleted {entity} is removed from system and no longer accessible
```

**Usage Example:**
```
### Delete Task

Enable users to remove an existing task from the system. The operation includes confirmation and handles any necessary cleanup.

Acceptance Criteria:
- Users can initiate deletion of a specific task
- System confirms deletion intent before proceeding
- Deleted task is removed from system and no longer accessible

Agent: backend-developer
Dependencies: 7

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {entity}: Domain object being deleted
- Consider soft delete vs hard delete (mention in criteria if soft delete)
- Consider cascading deletes or orphaned data handling

**Atomicity Score:** 85-95 (EXCELLENT)
- Single destructive operation
- 1-3 files
- Clear, focused responsibility

---

## Authentication & Authorization

### Template: User Login

**Title Format:** `Enable User Login`

**Description:**
```
Allow users to authenticate with their credentials. The system verifies credentials, establishes a session, and provides appropriate feedback for success or failure.
```

**Acceptance Criteria:**
```
- Users can provide credentials to authenticate
- System verifies credentials and establishes authenticated session on success
- Clear error messages displayed for invalid credentials
```

**Usage Example:**
```
### Enable User Login

Allow users to authenticate with their credentials. The system verifies credentials, establishes a session, and provides appropriate feedback for success or failure.

Acceptance Criteria:
- Users can provide credentials to authenticate
- System verifies credentials and establishes authenticated session on success
- Clear error messages displayed for invalid credentials

Agent: backend-developer
Dependencies: none

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- Adjust for specific authentication method (but keep technology-agnostic)
- Consider session duration requirements
- Consider multi-factor authentication (but split into separate story)

**Atomicity Score:** 75-85 (GOOD)
- Moderately complex operation
- 3-5 files (endpoint, auth service, session management)
- Could be split further for very complex auth

---

### Template: User Registration

**Title Format:** `Enable User Registration`

**Description:**
```
Allow new users to create an account by providing required information. The system validates uniqueness, creates the account, and confirms successful registration.
```

**Acceptance Criteria:**
```
- New users can provide required registration information
- System validates input and checks for existing accounts
- Successfully registered users can immediately use their account
```

**Usage Example:**
```
### Enable User Registration

Allow new users to create an account by providing required information. The system validates uniqueness, creates the account, and confirms successful registration.

Acceptance Criteria:
- New users can provide required registration information
- System validates input and checks for existing accounts
- Successfully registered users can immediately use their account

Agent: backend-developer
Dependencies: none

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- Define "required information" based on domain needs
- Consider email verification (split into separate story if needed)
- Consider password requirements

**Atomicity Score:** 75-85 (GOOD)
- Moderately complex with validation
- 3-5 files
- May need splitting if includes email verification or complex validation

---

### Template: User Logout

**Title Format:** `Enable User Logout`

**Description:**
```
Allow authenticated users to end their session securely. The system terminates the session and clears authentication state.
```

**Acceptance Criteria:**
```
- Authenticated users can initiate logout
- System terminates user session and clears authentication state
- User is redirected to appropriate page after logout
```

**Usage Example:**
```
### Enable User Logout

Allow authenticated users to end their session securely. The system terminates the session and clears authentication state.

Acceptance Criteria:
- Authenticated users can initiate logout
- System terminates user session and clears authentication state
- User is redirected to appropriate page after logout

Agent: frontend-developer
Dependencies: 8

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- Specify logout behavior (local only, clear tokens, etc.)
- Define redirect destination
- Consider "logout from all devices" feature (separate story)

**Atomicity Score:** 90-100 (EXCELLENT)
- Simple operation
- 1-3 files
- Clear, focused scope

---

### Template: Password Reset

**Title Format:** `Enable Password Reset`

**Description:**
```
Allow users who have forgotten their password to reset it securely. The system verifies user identity and enables password change.
```

**Acceptance Criteria:**
```
- Users can request a password reset for their account
- System verifies user identity through secure mechanism
- Users can set a new password after verification
```

**Usage Example:**
```
### Enable Password Reset

Allow users who have forgotten their password to reset it securely. The system verifies user identity and enables password change.

Acceptance Criteria:
- Users can request a password reset for their account
- System verifies user identity through secure mechanism
- Users can set a new password after verification

Agent: backend-developer
Dependencies: 9

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- "Secure mechanism" intentionally generic (could be email, SMS, security questions)
- Consider splitting into "Request Reset" and "Complete Reset" for better atomicity
- Consider token expiration requirements

**Atomicity Score:** 70-80 (GOOD)
- Moderately complex multi-step flow
- 4-6 files
- Consider splitting into 2 stories for better atomicity

---

## API Endpoint

### Template: Create API Endpoint

**Title Format:** `Create {Entity} API Endpoint`

**Description:**
```
Implement API endpoint that allows clients to {operation} {entity} data. The endpoint handles requests, performs the operation, and returns appropriate responses.
```

**Acceptance Criteria:**
```
- API endpoint accessible via HTTP at defined path
- Endpoint accepts properly formatted requests
- Endpoint returns appropriate responses including success and error cases
```

**Usage Example:**
```
### Create Task Retrieval API Endpoint

Implement API endpoint that allows clients to retrieve task data. The endpoint handles requests, performs the operation, and returns appropriate responses.

Acceptance Criteria:
- API endpoint accessible via HTTP at defined path
- Endpoint accepts properly formatted requests for task retrieval
- Endpoint returns appropriate responses including success and error cases

Agent: backend-developer
Dependencies: 3

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {entity}: Domain object
- {operation}: retrieve, create, update, delete, etc.
- Specify request/response format requirements if critical (but remain technology-agnostic)
- Consider authentication requirements

**Atomicity Score:** 85-95 (EXCELLENT)
- Single endpoint
- 1-3 files (route, controller, validation)
- Clear responsibility

---

## Configuration

### Template: Configure Environment Settings

**Title Format:** `Configure {Component} Environment Settings`

**Description:**
```
Set up environment configuration for {component} to support different deployment contexts. Configuration should be externalized and easy to modify without code changes.
```

**Acceptance Criteria:**
```
- {Component} reads configuration from environment settings
- Configuration supports multiple environments (development, production, etc.)
- Configuration changes don't require code modifications
```

**Usage Example:**
```
### Configure Database Environment Settings

Set up environment configuration for database to support different deployment contexts. Configuration should be externalized and easy to modify without code changes.

Acceptance Criteria:
- Database reads configuration from environment settings
- Configuration supports multiple environments (development, production, etc.)
- Configuration changes don't require code modifications

Agent: devops-engineer
Dependencies: 4

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {component}: What is being configured
- Specify which settings need to be configurable
- Consider security for sensitive settings (secrets management)

**Atomicity Score:** 85-95 (EXCELLENT)
- Single configuration concern
- 1-3 files
- Clear scope

---

## UI Component

### Template: Create UI Component

**Title Format:** `Create {Component Name} Component`

**Description:**
```
Build a reusable {component name} component that displays {information} and supports {interactions}. The component follows design system guidelines and accessibility standards.
```

**Acceptance Criteria:**
```
- Component displays {information} correctly
- Component supports required user interactions
- Component follows established design system and accessibility guidelines
```

**Usage Example:**
```
### Create Task Card Component

Build a reusable task card component that displays task information and supports view/edit interactions. The component follows design system guidelines and accessibility standards.

Acceptance Criteria:
- Component displays task information correctly
- Component supports required user interactions (view, edit)
- Component follows established design system and accessibility guidelines

Agent: frontend-developer
Dependencies: 5

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {component name}: Specific component being built
- {information}: What data the component displays
- {interactions}: User actions the component supports
- Add specific accessibility requirements if critical

**Atomicity Score:** 85-95 (EXCELLENT)
- Single component
- 1-2 files (component + styles)
- Focused responsibility

---

## Service Layer

### Template: Create Service Layer

**Title Format:** `Create {Service Name} Service Layer`

**Description:**
```
Implement service layer that handles {operations} for {domain area}. The service encapsulates business logic and provides a clean interface for other components.
```

**Acceptance Criteria:**
```
- Service layer provides methods for required {operations}
- Service handles errors gracefully and returns consistent responses
- Service follows established patterns and coding conventions
```

**Usage Example:**
```
### Create Task Management Service Layer

Implement service layer that handles CRUD operations for task management. The service encapsulates business logic and provides a clean interface for other components.

Acceptance Criteria:
- Service layer provides methods for required CRUD operations
- Service handles errors gracefully and returns consistent responses
- Service follows established patterns and coding conventions

Agent: backend-developer
Dependencies: none

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {service name}: Name of the service
- {operations}: What operations the service provides
- {domain area}: Business domain being serviced
- Consider splitting if service covers too many operations

**Atomicity Score:** 75-85 (GOOD)
- Moderate complexity
- 1-3 files
- May need splitting if too many operations

---

## Design

### Template: Design UI Feature

**Title Format:** `Design {Feature Name} Interface`

**Description:**
```
Design the user interface for {feature name} that allows users to {user goal}. The design should include all UI states, interactions, and visual specifications.
```

**Acceptance Criteria:**
```
- Design includes all necessary UI states (loading, success, error, empty)
- Design specifies all user interactions and feedback mechanisms
- Design follows established design system and is documented in design brief
```

**Usage Example:**
```
### Design Task Management Interface

Design the user interface for task management that allows users to view, create, and organize tasks. The design should include all UI states, interactions, and visual specifications.

Acceptance Criteria:
- Design includes all necessary UI states (loading, success, error, empty)
- Design specifies all user interactions and feedback mechanisms (create, edit, delete, organize)
- Design follows established design system and is documented in design brief

Agent: ui-ux-designer
Dependencies: none

**Design Context**:
- Update docs/design-brief.md to incorporate design decisions for this feature
- If design-brief.md doesn't exist, create it with the foundational design system
- Add a feature-specific section under the "## Features" heading
- Include component specifications, interaction patterns, and all UI states
- Ensure consistency with existing design system (colors, typography, spacing)

**Important**: This story describes WHAT needs to be achieved using generic, technology-agnostic language. ALL implementation details (technology choices, frameworks, libraries, tools, file formats, patterns, architecture) MUST be decided by the assigned development agent based on project context and best practices. DO NOT include ANY specific technology references in this story.
```

**Customization Points:**
- {feature name}: Feature being designed
- {user goal}: What users need to accomplish
- Specify critical UI states or interactions
- Add accessibility or responsive design requirements if needed

**Atomicity Score:** 80-90 (GOOD to EXCELLENT)
- Single feature design
- Typically 1 design document
- Clear deliverable

---

## Best Practices for Using Templates

### DO:
- Customize all placeholders to match your specific domain
- Adjust acceptance criteria to reflect actual requirements
- Verify atomicity score after customization
- Keep stories technology-agnostic
- Focus on observable behaviors and outcomes
- Add the technology-agnostic disclaimer at the end

### DON'T:
- Use templates without customization
- Add technology-specific details
- Combine multiple templates into one story
- Exceed 3-4 acceptance criteria
- Include implementation details in descriptions

### Validation Checklist:
- [ ] All placeholders replaced with domain-specific terms
- [ ] Acceptance criteria are testable and observable
- [ ] No technology-specific terms used
- [ ] Story is independently deployable
- [ ] Technology-agnostic disclaimer included
- [ ] Atomicity score >= 70 (run validation)

---

## Template Selection Guide

| When you need to... | Use this template |
|---------------------|-------------------|
| Add new entity to system | Create New Entity |
| Set up new component/module | Initialize New Component or Module |
| Show list of items | Display List of Entities |
| Show details of one item | Display Single Entity Details |
| Change existing data | Update Existing Entity |
| Remove data from system | Delete Entity |
| Let users sign in | User Login |
| Let users create account | User Registration |
| Let users sign out | User Logout |
| Let users reset password | Password Reset |
| Create backend endpoint | Create API Endpoint |
| Set up environment config | Configure Environment Settings |
| Build UI element | Create UI Component |
| Add business logic layer | Create Service Layer |
| Design user interface | Design UI Feature |

---

## Atomicity Validation Reference

All templates are designed to score >= 70 on atomicity validation. After customizing a template:

1. Check title complexity (no "and", multiple verbs, or scope keywords)
2. Count acceptance criteria (3-4 maximum)
3. Estimate file impact (1-5 files ideal)
4. Estimate time (1-3 days maximum)
5. Verify no technology references

If customization causes atomicity score to drop below 70, split the story or simplify acceptance criteria.

---

## Version History

- v1.0 (2025-10-19): Initial template library with 15 templates covering CRUD, authentication, API, configuration, UI, service, and design patterns
