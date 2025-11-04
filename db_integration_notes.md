## 1. Python/FastAPI Package Purposes
1. sqlalchemy: ORM for SQL databases—models, queries, migrations.

2. alembic: Migration/version control for DB schemas.

3. asyncpg: High-performance async PostgreSQL driver.

4. python-dotenv: Loads environment variables from .env files.

## 2. python specific new things that I didnt know earlier
1. Hyphen vs Underscore in import paths.
    - Hyphens (-) are not allowed in Python module names; use underscores (_) instead.
    - Example: `python-dotenv` is installed via pip, but imported as `import dotenv`.
2. Variables, functions and other fields are exported by default.
    - No need for explicit export statements like in some other languages.
3. Use of `__init__.py` files to mark directories as packages.
    - Allows for package-level initialization code.
    - allows . syntax imports within the package.
    - for allowing absolute imports from other packages, you have to mark the directory as the package mandatorily. like importing from app.core.config import settings in app.main.py will not work unless app is marked as a package with __init__.py file. and also core should be marked as a package too.
4. If you have to use a reserved keyword as a variable name, then appending an underscore (_) at the end is a common convention.
    - Example: `class_`, `def_`, etc.

## 3. Docker Common Doubts / Notes:

### How to run PostgreSQL in Docker locally
1. Docker Command to Run PostgreSQL
Run this command in your terminal (Docker must be installed and running):

```cmd
docker run --name postgres-db \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=mydatabase \
  -p 5432:5432 \
  -d postgres:16
```

--name postgres-db: Name your container.

-e POSTGRES_USER=...: Set the database username.

-e POSTGRES_PASSWORD=...: Set the password.

-e POSTGRES_DB=...: Pre-create this database.

-p 5432:5432: Expose port 5432 (Postgres default).

-d postgres:16: Use latest stable Postgres 16 in detached mode.

---

**NOTE:** Make sure the image name is at the end of the command. Otherwise, all other options will be ignored and not applied to the postgress container & may be it will throw error too.

---

2. Setup Your .env File for FastAPI
Create a .env file in your project root:

```text
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
SECRET_KEY=your-very-secret-key
```
DATABASE_URL uses the username, password, host, and db name you set in your Docker command.

3. Using the Environment Variable in FastAPI Config
Your config class should reference this .env:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
```

## 4. Common Docker Commands:
- List running containers:
  ```bash
  docker ps
  ```
- List all containers (including stopped):
  ```bash
  docker ps -a
  ```
- Stop a container:
  ```bash
  docker stop <container_id_or_name>
  ```
- Start a container:
  ```bash
  docker start <container_id_or_name>
  ```
- Remove a container:
  ```bash
  docker rm <container_id_or_name>
  ```  
- List all images : 
    ```bash
    docker images
    ``` 
- Remove an image:
    ```bash
    docker rmi <image_id_or_name>
    ```
- Build an image from Dockerfile:
    ```bash
    docker build -t <image_name> .
    ```
- Run a container from an image:
    ```bash
    docker run -d -p <host_port>:<container_port> --name <container_name> <image_name>
    ```
- View logs of a container:
    ```bash
    docker logs <container_id_or_name>
    ```
- Volume management:
    - Create a volume:
      ```bash
      docker volume create <volume_name>
      ```
    - List volumes:
      ```bash
      docker volume ls
      ```
    - Remove a volume:
      ```bash
      docker volume rm <volume_name>
      ```
    - Adding volume to postgres container:
      ```bash
      docker run --name postgres-db -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 -v pgdata:/var/lib/postgresql/data -d postgres:16
      ```
    

## 4. Database URLS
- Format: dialect+driver://username:password@host:port/database
- Example for PostgreSQL with asyncpg: postgresql+asyncpg://user:password@localhost:5432/mydatabase
- dialect: Database type (e.g., postgresql, mysql, sqlite).
- driver: Optional, specifies the DBAPI to use (e.g., asyncpg for PostgreSQL).

## 5. Alembic Common Commands

## 6. Database Connections and Session Management Theory

### 6.1 Core Concepts

**What is a Database Session?**
- A session is a workspace for your database operations—it tracks changes to objects and manages transactions.
- Think of it as a "shopping cart" for database changes: you add/modify items (objects), then commit (checkout) or rollback (discard).
- Sessions are NOT thread-safe—each thread/request should have its own session.

**What is a Database Connection?**
- A connection is the actual TCP/network link to the database server.
- Opening a new connection is expensive (network handshake, authentication, etc.).
- Sessions use connections to send SQL commands to the database.

**Connection Pooling**
- Instead of creating a new connection for every request, maintain a pool of reusable connections.
- When a session needs a connection, it borrows one from the pool; when done, it returns it.
- This dramatically improves performance by reducing connection overhead.
- SQLAlchemy handles pooling automatically via the `Engine`.

### 6.2 Session Lifecycle Pattern

**Session Per Request Pattern (Recommended for Web Apps)**
1. **Create** a new session when a request comes in
2. **Use** the session to query/modify data
3. **Commit** changes if everything succeeds
4. **Rollback** if an error occurs
5. **Close** the session to return the connection to the pool

**Why This Pattern?**
- **Thread Safety**: Each request gets its own session, avoiding race conditions
- **Transaction Boundaries**: Each request is a transaction—either all changes succeed or none do
- **Resource Management**: Sessions are closed automatically, preventing connection leaks

### 6.3 Key SQLAlchemy Components

**Engine**
- The starting point for SQLAlchemy—creates and manages the connection pool
- Created once at application startup
- Example:
  ```python
  from sqlalchemy.ext.asyncio import create_async_engine
  
  engine = create_async_engine(
      "postgresql+asyncpg://user:pass@localhost/db",
      echo=True,  # Log all SQL queries
      pool_size=5,  # Max 5 connections in pool
      max_overflow=10  # Allow 10 extra connections if pool is full
  )
  ```

**SessionMaker (Session Factory)**
- A factory for creating session instances—configured once, used many times
- Not a session itself, but produces sessions with consistent configuration
- Example:
  ```python
  from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
  
  # Create the factory
  AsyncSessionLocal = async_sessionmaker(
      bind = engine,
      class_ = AsyncSession,
      expire_on_commit = False  # Don't expire objects after commit
  )
  
  # Later, create sessions from the factory
  async with AsyncSessionLocal() as session:
      # Use the session here
      pass
  ```

**Session**
- The actual workspace for database operations
- Tracks object changes (insert, update, delete)
- Manages transactions (begin, commit, rollback)
- Should be created per request, not shared between requests

### 6.4 Context Managers for Session Lifecycle

**Why Use Context Managers?**
- Automatically handle session cleanup (close/rollback) even if errors occur
- Ensure connections are returned to the pool
- Python's `async with` statement handles `__aenter__` and `__aexit__` automatically

**Pattern:**
```python
async with async_session_maker() as session:
    # Session is open
    async with session.begin():
        # Transaction started automatically
        session.add(new_object)
        # If no exception: commit happens automatically
        # If exception: rollback happens automatically
    # Session closes automatically, connection returns to pool
```

### 6.5 Dependency Injection in FastAPI

**The Problem:**
- Every route handler needs a database session
- We want to ensure sessions are created per request and cleaned up properly
- Manually creating/closing sessions in each handler is error-prone

**The Solution: FastAPI Dependencies**
- Define a dependency function that yields a session
- FastAPI calls this function for each request
- The `yield` statement allows cleanup code to run after the request completes

**Benefits:**
- **DRY**: Write session management logic once
- **Automatic Cleanup**: Session is closed even if route raises an exception
- **Type Safety**: Type hints help IDEs and type checkers
- **Testability**: Easy to override dependencies in tests

## 7. Session Management Implementation in FastAPI

### 7.1 Basic Setup

**Step 1: Create the Engine (in `database.py`)**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL from config
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

# Create engine (connection pool)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True  # Verify connections before using
)

# Create session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for ORM models
Base = declarative_base()
```

**Step 2: Create Dependency Function**
```python
# Still in database.py
async def get_db() -> AsyncSession:
    """
    Dependency that provides a database session.
    Yields a session and ensures it's closed after use.
    """
    async with async_session_maker() as session:
        try:
            yield session  # Provide session to route handler
            await session.commit()  # Commit if no errors
        except Exception:
            await session.rollback()  # Rollback on error
            raise  # Re-raise the exception
        finally:
            await session.close()  # Always close session
```

### 7.2 Using the Session Dependency in Routes

**Example: Create Task Endpoint**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.task import Task

router = APIRouter()

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)  # Inject session
):
    """
    FastAPI calls get_db() automatically before this handler runs.
    The session is passed as the 'db' parameter.
    """
    # Create new task
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority
    )
    
    # Add to session
    db.add(new_task)
    
    # Commit happens in get_db after this function returns
    # No need to manually commit here
    
    return {"id": new_task.id, "title": new_task.title}
```

**Example: Query Tasks**
```python
@router.get("/tasks")
async def get_tasks(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Query tasks with pagination"""
    from sqlalchemy import select
    
    # Build query
    query = select(Task).offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return {"tasks": tasks, "count": len(tasks)}
```

### 7.3 Alternative: Manual Transaction Control

If you need explicit control over commits:

```python
@router.post("/tasks/batch")
async def create_tasks_batch(
    tasks_data: List[TaskCreate],
    db: AsyncSession = Depends(get_db)
):
    """Create multiple tasks in one transaction"""
    try:
        # Begin explicit transaction
        async with db.begin():
            for task_data in tasks_data:
                new_task = Task(**task_data.dict())
                db.add(new_task)
            
            # Commit happens automatically when exiting 'with' block
        
        return {"created": len(tasks_data)}
    
    except Exception as e:
        # Rollback happens automatically
        raise HTTPException(status_code=400, detail=str(e))
```

### 7.4 Complete Example with Error Handling

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.task import Task, TaskCreate

router = APIRouter()

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task with proper error handling"""
    # Query existing task
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    # Handle not found
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Add to session (marks as modified)
    db.add(task)
    
    # Commit happens in get_db dependency
    # If error occurs, rollback happens automatically
    
    return {"id": task.id, "updated": True}
```

### 7.5 Key Patterns Summary

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Depends(get_db)** | Standard CRUD operations | Most route handlers |
| **async with db.begin()** | Explicit transaction control | Batch operations, complex workflows |
| **db.add(obj)** | Stage changes | Create/update single objects |
| **db.add_all([obj1, obj2])** | Stage multiple changes | Batch inserts |
| **await db.commit()** | Explicitly commit | When not using get_db's auto-commit |
| **await db.rollback()** | Explicitly rollback | Custom error handling |
| **await db.refresh(obj)** | Reload from DB | Get updated fields after commit |

### 7.6 Common Pitfalls to Avoid

1. **Don't share sessions between requests**
   - ❌ Bad: `db = get_session()` at module level
   - ✅ Good: `db: AsyncSession = Depends(get_db)` in route parameters

2. **Don't forget to await async operations**
   - ❌ Bad: `result = db.execute(query)`
   - ✅ Good: `result = await db.execute(query)`

3. **Don't access lazy-loaded relationships outside session**
   - ❌ Bad: Return ORM object, then access `obj.relationship` outside handler
   - ✅ Good: Use `selectinload()` or access relationships before returning

4. **Don't commit inside loops for individual items**
   - ❌ Bad: `for item in items: db.add(item); await db.commit()`
   - ✅ Good: `db.add_all(items); await db.commit()` (bulk operation)