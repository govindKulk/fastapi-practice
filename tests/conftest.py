import pytest_asyncio
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import task_app as app
from app.core.database import Base
from app.api import deps
from app.models.database import User
from app.crud.user import user as crud_user
from app.models.user import UserCreate

# Test database URL - use SQLite in memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Event loop fixture for session scope
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Create test engine with proper configuration
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

@pytest_asyncio.fixture(scope="function")
async def db_setup() -> AsyncGenerator[None, None]:
    """Set up the database tables before each test and tear down after"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db(db_setup: None) -> AsyncGenerator[AsyncSession, None]:  # type: ignore[type-arg]
    """Create a fresh database session for each test"""
    # Create session factory for this test
    testing_session_local = async_sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    # Create a new session for the test
    async with testing_session_local() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database override"""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[deps.get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a test user for authentication tests"""
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
        full_name="Test User"
    )
    user = await crud_user.create(db, obj_in=user_in)
    await db.commit()
    await db.refresh(user)
    return user
