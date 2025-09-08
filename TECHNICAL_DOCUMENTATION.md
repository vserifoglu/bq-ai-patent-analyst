# BQ AI Patent Analyst - Technical Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Refactoring Journey](#refactoring-journey)
4. [Core Components](#core-components)
5. [Design Patterns](#design-patterns)
6. [Testing Strategy](#testing-strategy)
7. [Development Guidelines](#development-guidelines)
8. [Contributing Guide](#contributing-guide)

---

## 🎯 Project Overview

**BQ AI Patent Analyst** is an intelligent patent analysis system that transforms unstructured patent PDFs into a queryable knowledge graph using BigQuery AI and Streamlit. The project has undergone comprehensive refactoring to achieve high testability, maintainability, and loose coupling.

### Key Features
- **Semantic Search**: AI-powered search through patent components using vector embeddings
- **Data Visualization**: Strategic portfolio analysis with interactive charts
- **Real-time Analytics**: Component distribution analysis and outlier detection
- **Clean UI**: Progressive loading with separated business and presentation logic

### Technology Stack
- **Backend**: Python, BigQuery ML, Google Cloud Platform
- **Frontend**: Streamlit
- **Data Processing**: Pandas, Plotly
- **Architecture**: Clean Architecture with Dependency Injection

---

## 🏗️ Architecture Overview

The application follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│                 UI Layer                        │
│  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Streamlit       │  │ Pure UI Components  │  │
│  │ Controllers     │  │ (Dashboard, Tabs)   │  │
│  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              Application Layer                  │
│  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Dashboard       │  │  App Controller     │  │
│  │ Engine          │  │  (Business Logic)   │  │
│  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│               Service Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │ Semantic    │ │Visualization│ │   State  │  │
│  │ Search      │ │  Service    │ │ Manager  │  │
│  │ Service     │ │             │ │          │  │
│  └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│             Infrastructure Layer                │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │  BigQuery   │ │   Config    │ │ External │  │
│  │  Client     │ │  Management │ │   APIs   │  │
│  └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Refactoring Journey

### Problems We Solved

#### 🚨 Critical Issues (Before Refactoring)
1. **Framework Lock-in**: Business logic tightly coupled to Streamlit
2. **Global Dependencies**: `sys.path.append()`, `os.getenv()` throughout codebase  
3. **Untestable Code**: No way to test business logic without full UI environment
4. **Mixed Responsibilities**: UI rendering and business logic in same methods
5. **State Management**: Direct framework dependency making testing impossible

#### ✅ Solutions Implemented

**1. State Management Abstraction**
- Created `StateInterface` for framework independence
- Implemented `StateManager` (pure) and `StreamlitStateAdapter`
- Eliminated direct `st.session_state` access from business logic

**2. Business Logic Extraction**
- Separated pure business methods (`_get_*_data`) from UI rendering (`_render_*_ui`)
- Created testable data structures and return types
- Removed all `st.*` calls from business logic

**3. Dependency Injection**
- Added `AppConfig` for configuration management
- Constructor injection for all external dependencies
- Eliminated global state access patterns

**4. Clean Architecture Layers**
- **UI Components**: Pure rendering logic
- **Application Services**: Business orchestration
- **Domain Services**: Core business logic
- **Infrastructure**: External integrations

**5. Recent Refactors (Batches 1–4)**
- Core/UI decoupling: no Streamlit calls in `core/`; UI handles rendering via `DashboardUI` and `DataVisualizationTabUI` helpers
- GCP auth cache decoupled from Streamlit: `utils/gcp_auth.get_bigquery_client(use_cache=True)` and `reset_bigquery_client_cache()`
- AppController DI: accepts `bigquery_client_provider`; connection utilities accept optional client
- State managers clarified: `StreamlitStateManager` (prod), `PureStateManager` (tests); `StateManager` alias retained for compatibility

---

## 🔧 Core Components

### 1. Application Entry Point

**File**: `main.py`
```python
def main():
    controller = AppController()  # Business logic coordinator
    state_manager = StreamlitStateManager()  # Explicit Streamlit adapter
    engine = DashboardEngine(controller, state_manager)  # UI orchestrator
```

**Responsibilities**:
- Initialize core components with proper dependency injection
- Configure Streamlit layout and tabs
- Delegate control to DashboardEngine

### 2. Dashboard Engine

**File**: `core/dashboard.py`
**Class**: `DashboardEngine`

**Architecture Pattern**: **Coordinator + Template Method**

```python
class DashboardEngine:
    def run(self):
        if self.state.is_search_triggered():
            data = self._get_search_mode_data(query)      # Pure business logic
            self._render_search_mode_ui(query, data)      # Delegates to UI layer
        else:
            data = self._get_overview_mode_data()         # Pure business logic  
            self._render_overview_mode_ui(data)           # Delegates to UI layer
```

**Key Methods**:
- **Business Logic** (Testable):
  - `_get_overview_mode_data()` → Returns `dict`
  - `_get_search_mode_data(query)` → Returns `dict`
  - `_get_visualization_data()` → Returns `dict`
    - `_get_search_results(query)` → Returns `dict`

- **UI Rendering** (Framework-specific):
  - `_render_overview_mode_ui(data)`
  - `_render_search_mode_ui(query, data)`
  - `_render_data_tab_ui(data)`
    - Handled via `DashboardUI` methods in `components/ui/`

**Testing Strategy**:
```python
# Test business logic without UI
mock_controller = Mock()
mock_state = Mock()
engine = DashboardEngine(mock_controller, mock_state)

data = engine._get_search_mode_data("test query")
assert data['query'] == "test query"
assert 'success' in data
```

### 3. Application Controller

**File**: `core/app_controller.py`
**Class**: `AppController`

**Architecture Pattern**: **Service Coordinator + Factory**

```python
@dataclass
class AppConfig:
    project_id: str
    dataset_id: str = "patent_analysis"
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        # Safe environment loading

class AppController:
    def __init__(self, config: Optional[AppConfig] = None, ...):
        self.config = config or AppConfig.from_environment()
```

**Responsibilities**:
- Coordinate between semantic search and visualization services
- Handle BigQuery connection management
- Format data for UI consumption
- Manage service lifecycle with lazy initialization

**Key Methods**:
- `search_patents(request: SearchRequest) → SearchResponse`
- `get_connection_status() → ConnectionStatus`
- `get_formatted_portfolio_chart_data() → tuple[bool, str, dict]`

### 4. State Management System

**Architecture Pattern**: **Strategy + Adapter**

**Interface**: `core/interfaces/state_interface.py`
```python
class StateInterface(ABC):
    @abstractmethod
    def is_search_triggered(self) -> bool: ...
    @abstractmethod
    def trigger_search(self, query: str) -> None: ...
```

**Implementations**:
1. **Pure State Manager**: `core/state/state_manager.py`
   - Framework-independent
   - 100% testable
   - In-memory state management

2. **Streamlit Adapter**: `core/state/streamlit_state_adapter.py`
   - Streamlit-specific implementation
   - Handles `st.session_state` and `st.rerun()`
   - Production implementation

**Usage Pattern**:
```python
# Production (Streamlit)
from core.state_manager import StreamlitStateManager
state = StreamlitStateManager()

# Testing (Pure)
from core.state.state_manager import PureStateManager, AppState
state = PureStateManager(initial_state=AppState(search_triggered=True))
```

### 5. Service Layer

#### Semantic Search Service
**File**: `services/semantic_search.py`
**Pattern**: **Service + Configuration Object**

```python
@dataclass
class SearchConfig:
    project_id: str
    dataset_id: str = "patent_analysis"

class SemanticSearchService:
    def __init__(self, config: SearchConfig, bigquery_client: Optional[Client] = None):
        # Dependency injection for testability
```

**Key Features**:
- BigQuery ML integration for technical classification
- Vector search with configurable parameters
- SQL query builders extracted for testing
- Comprehensive error handling

#### Visualization Service
**File**: `services/visualization_service.py`
**Pattern**: **Service + Protocol-based DI**

```python
class BigQueryClient(Protocol):
    def query(self, sql: str) -> 'QueryResult': ...

@dataclass
class VisualizationResult:
    success: bool
    message: str
    data: Optional[pd.DataFrame] = None
```

**Responsibilities**:
- Portfolio analysis (bubble charts)
- Component distribution (histograms)  
- Outlier detection
- Chart data formatting with Plotly

### 6. UI Components

**Location**: `components/ui/`
**Pattern**: **Pure UI Components**

All UI components follow the principle of **accepting data, returning actions**:

```python
class SemanticSearchTabUI:
    def render_search_box(self, current_query: str = "") -> dict:
        # Renders UI, returns user actions
        return {
            'query': search_input,
            'search_clicked': search_clicked
        }
```

**Key Components**:
- `DashboardUI`: Tab coordination
- `SemanticSearchTabUI`: Search interface
- `DataVisualizationTabUI`: Charts and analytics

---

## 🎨 Design Patterns Used

### 1. **Dependency Injection**
```python
# Constructor injection for testability
class AppController:
    def __init__(self, config: AppConfig, bigquery_client=None, bigquery_client_provider=None): ...

# Interface segregation
class StateInterface(ABC): ...
```

### 2. **Strategy Pattern**
```python
# Different state management strategies
state_manager: StateInterface = StreamlitStateManager()  # Production
state_manager: StateInterface = PureStateManager()       # Testing
```

### 3. **Template Method**
```python
def run(self):
    data = self._get_data()    # Varies by mode
    self._render_ui(data)      # Consistent pattern
```

### 4. **Factory Method**
```python
@classmethod
def from_environment(cls) -> 'AppConfig':
    # Safe factory for configuration
```

### 5. **Protocol-based DI** 
```python
class BigQueryClient(Protocol):
    def query(self, sql: str) -> 'QueryResult': ...
# Enables easy mocking without inheritance
```

### 6. **Result Object Pattern**
```python
@dataclass
class VisualizationResult:
    success: bool
    message: str  
    data: Optional[pd.DataFrame] = None
# Consistent error handling across services
```

---

## 🧪 Testing Strategy

### Testing Architecture

The refactored codebase supports **comprehensive testing** at multiple levels:

#### 1. **Unit Testing** (Business Logic)
```python
def test_search_mode_data():
    # Pure business logic testing
    mock_controller = Mock()
    mock_state = Mock()
    engine = DashboardEngine(mock_controller, mock_state)
    
    data = engine._get_search_mode_data("test query")
    
    assert data['query'] == "test query"
    assert 'success' in data
    assert 'display_df' in data
```

#### 2. **Service Testing** (with Mocks)
```python
def test_semantic_search_service():
    config = SearchConfig(project_id="test-project")
    mock_client = Mock()
    service = SemanticSearchService(config, mock_client)
    
    result = service.run_semantic_search("wireless components")
    
    assert result['success'] in [True, False]
    mock_client.query.assert_called()
```

#### 3. **Integration Testing** (Components)
```python
def test_app_controller_integration():
    config = AppConfig(project_id="test-project")
    controller = AppController(config)
    
    status = controller.get_connection_status()
    
    assert hasattr(status, 'gcp_connected')
    assert hasattr(status, 'env_valid')
```

#### 4. **UI Component Testing**
```python
def test_search_ui_component():
    ui = SemanticSearchTabUI()
    
    # Mock Streamlit functions
    with patch('streamlit.text_input'), patch('streamlit.button'):
        result = ui.render_search_box("test query")
        
        assert 'query' in result
        assert 'search_clicked' in result
```

### Test Data Management

**Configuration for Testing**:
```python
# Easy test configuration
test_config = AppConfig(
    project_id="test-project-123",
    dataset_id="test_dataset"
)

# In-memory state for testing
from core.state.state_manager import PureStateManager, AppState
test_state = PureStateManager(
    initial_state=AppState(search_triggered=True, search_query="test query")
)
```

### Mock Strategies

**BigQuery Client Mocking**:
```python
mock_client = Mock()
mock_client.query.return_value.to_dataframe.return_value = test_df
service = VisualizationService(mock_client)
```

**State Mocking**:
```python
mock_state = Mock(spec=StateInterface)
mock_state.is_search_triggered.return_value = True
mock_state.get_search_query.return_value = "test"
```

---

## 👨‍💻 Development Guidelines

### Code Organization Principles

#### 1. **Layer Separation**
```
✅ UI components only handle rendering
✅ Business logic in services and controllers  
✅ Infrastructure isolated in utils and config
❌ No business logic in UI components
❌ No UI framework calls in business logic
```

#### 2. **Dependency Direction**
```
UI Layer → Application Layer → Service Layer → Infrastructure
✅ Higher layers depend on lower layers
✅ Use interfaces for inversion of control
❌ No circular dependencies
❌ No infrastructure details in business logic
```

#### 3. **Method Naming Conventions**
```python
# Business logic (testable)
def _get_search_data(self, query: str) -> dict: ...

# UI rendering (framework-specific)  
def _render_search_ui(self, data: dict) -> None: ...

# Public coordination
def run(self) -> None: ...
```

#### 4. **Data Flow Patterns**
```python
# CORRECT: Data flows down, actions flow up
data = self._get_business_data()           # Business logic
actions = self._render_ui(data)            # UI rendering
self._handle_actions(actions)              # Business logic

# INCORRECT: Mixed responsibilities
def handle_search():
    st.header("Search")                    # UI mixed with
    results = query_database()             # business logic
```

### Configuration Management

#### Environment Configuration
```python
# Production
controller = AppController()  # Loads from environment

# Testing  
config = AppConfig(project_id="test")
controller = AppController(config)

# Custom configuration
config = AppConfig(
    project_id="custom-project",
    dataset_id="custom_dataset"
)
```

#### Service Configuration
```python
# Semantic search configuration
search_config = SearchConfig(
    project_id=app_config.project_id,
    dataset_id=app_config.dataset_id,
    embedding_model="custom_model"
)
```

### Error Handling Patterns

#### Service Layer
```python
@dataclass
class ServiceResult:
    success: bool
    message: str
    data: Optional[Any] = None
    error_type: Optional[str] = None

def get_data(self) -> ServiceResult:
    try:
        data = self._fetch_data()
        return ServiceResult(success=True, message="Success", data=data)
    except Exception as e:
        return ServiceResult(success=False, message=str(e), error_type="fetch_error")
```

#### UI Layer
```python
def _render_results_ui(self, result: ServiceResult):
    if result.success:
        st.success(result.message)
        if result.data:
            st.dataframe(result.data)
    else:
        st.error(f"❌ {result.message}")
```

---

## 🤝 Contributing Guide

### Setting Up Development Environment

#### 1. **Clone and Setup**
```bash
git clone <repository-url>
cd bq-ai-patent-analyst
cd app
```

#### 2. **Environment Configuration**
```bash
# Create .env file
GOOGLE_CLOUD_PROJECT_ID=your-project-id
# Add other required environment variables
```

#### 3. **Dependencies**
```bash
pip install streamlit pandas google-cloud-bigquery plotly
# Or use requirements.txt if available
```

### Development Workflow

#### 1. **Understanding the Codebase**
1. Start with `main.py` to understand entry point
2. Read `core/dashboard.py` to understand orchestration
3. Explore `core/app_controller.py` for business logic
4. Check service layer for domain logic
5. Review UI components for presentation layer

#### 2. **Making Changes**

**Adding New Business Logic**:
```python
# 1. Add pure business method to DashboardEngine
def _get_new_feature_data(self, params) -> dict:
    # Pure business logic - easily testable
    return {'result': data}

# 2. Add corresponding UI method  
def _render_new_feature_ui(self, data: dict):
    # Streamlit-specific rendering
    st.write(data['result'])

# 3. Wire in coordinator method
def run_new_feature(self):
    data = self._get_new_feature_data(params)
    self._render_new_feature_ui(data)
```

**Adding New Services**:
```python
# 1. Follow existing service patterns
@dataclass 
class NewServiceConfig:
    setting1: str
    setting2: int = 10

class NewService:
    def __init__(self, config: NewServiceConfig, client=None):
        self.config = config
        self.client = client
    
    def process_data(self) -> ServiceResult:
        # Implementation with proper error handling
```

**Adding UI Components**:
```python
# 1. Create in components/ui/
class NewComponentUI:
    def render_component(self, data: dict) -> dict:
        # Pure UI logic
        # Return user actions as dict
        return {'action': 'value'}
```

#### 3. **Testing New Features**

**Write Tests First** (TDD approach):
```python
def test_new_feature_business_logic():
    # Test the _get_*_data method
    mock_controller = Mock()
    engine = DashboardEngine(mock_controller, Mock())
    
    result = engine._get_new_feature_data(test_params)
    
    assert result['expected_field'] == expected_value

def test_new_service():
    config = NewServiceConfig(setting1="test")
    service = NewService(config, mock_client)
    
    result = service.process_data()
    
    assert result.success is True
```

#### 4. **Code Review Checklist**

**Architecture Compliance**:
- [ ] Business logic separated from UI rendering
- [ ] Dependencies injected through constructors
- [ ] No global state access in business logic
- [ ] Proper error handling with Result objects
- [ ] Interface-based programming where appropriate

**Testing Requirements**:
- [ ] Business logic methods are pure functions
- [ ] Services can be tested with mocked dependencies
- [ ] Configuration can be injected for testing
- [ ] No framework dependencies in testable code

**Code Quality**:
- [ ] Clear method naming (`_get_*` vs `_render_*`)
- [ ] Proper typing and documentation
- [ ] Consistent error handling patterns
- [ ] No code duplication

### Common Patterns to Follow

#### 1. **Service Integration**
```python
# In AppController
def _get_new_service(self):
    if not self._new_service:
        config = NewServiceConfig(self.config.project_id)
        self._new_service = NewService(config, self._get_client())
    return self._new_service
```

#### 2. **State Management**
```python
# For new state needs, extend StateInterface
class StateInterface(ABC):
    @abstractmethod
    def get_new_state(self) -> str: ...
    
    @abstractmethod  
    def set_new_state(self, value: str) -> None: ...
```

#### 3. **UI Data Flow**
```python
# Always follow: Data → UI → Actions → Business Logic
def run_feature(self):
    data = self._get_feature_data()           # Business
    actions = self._render_feature_ui(data)   # UI  
    if actions.get('submit'):
        self._handle_feature_submit(actions)  # Business
```

### Performance Considerations

#### 1. **Lazy Loading**
```python
# Services are created only when needed
def _get_service(self):
    if not self._service:
        self._service = create_service()
    return self._service
```

#### 2. **Progressive UI Loading**
```python
# Load expensive operations progressively
sections = self.ui.create_placeholders()
self._load_section_async(sections['section1'])
self._load_section_async(sections['section2'])
```

#### 3. **Caching Strategies**
```python
# Cache expensive computations
@st.cache_data
def get_expensive_data():
    return expensive_computation()
```

### Debugging Guidelines

#### 1. **Business Logic Debugging**
```python
# Test business methods in isolation
engine = DashboardEngine(mock_controller, mock_state)
data = engine._get_search_mode_data("debug query")
print(f"Business logic result: {data}")
```

#### 2. **Service Debugging**  
```python
# Test services with real/mock clients
config = AppConfig(project_id="debug-project")
service = SemanticSearchService(config, real_client)
result = service.run_semantic_search("debug")
```

#### 3. **State Debugging**
```python
# Use pure state manager for debugging
state = StateManager()
state.trigger_search("debug query") 
print(f"State: {state.state}")
```

---

## 📚 Additional Resources

### Key Files to Understand
1. `main.py` - Application entry point
2. `core/dashboard.py` - Main orchestration engine
3. `core/app_controller.py` - Business logic coordinator
4. `core/interfaces/state_interface.py` - State management contract
5. `services/semantic_search.py` - Search functionality
6. `services/visualization_service.py` - Data visualization

### Architecture Decision Records
- **State Management**: Chose interface-based approach for framework independence
- **Business Logic Separation**: Template method pattern for testability
- **Dependency Injection**: Constructor injection for loose coupling
- **Error Handling**: Result object pattern for consistent error propagation

### Future Enhancement Areas
1. **API Layer**: Add REST API for programmatic access
2. **Caching Layer**: Implement Redis for query result caching  
3. **Authentication**: Add user authentication and authorization
4. **Batch Processing**: Support for batch patent analysis
5. **Export Features**: PDF reports and data export functionality

---

*This documentation is maintained alongside the codebase. When making architectural changes, please update this document accordingly.*
