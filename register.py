

from fastapi import FastAPI, HTTPException, Depends, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from pony.orm import Database, Required, Optional, PrimaryKey, db_session, select, sql_debug, commit
from pydantic import BaseModel, EmailStr
import uvicorn
from passlib.context import CryptContext
from typing import List, Optional as OptionalType
from datetime import datetime, timedelta
import logging
import traceback
import json

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable SQL debugging
sql_debug(True)

# Initialize FastAPI app
app = FastAPI(title="User Registration API")
router = APIRouter()

# Add CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database configuration
db = Database()
db.bind(provider='postgres',
        user='postgres',
        password='12345678',
        host='localhost',
        database='postgres')


# Create schema if not exists
@db_session
def ensure_schema_exists():
    try:
        db.execute("CREATE SCHEMA IF NOT EXISTS cmti")
        db.execute("SET search_path TO cmti, public")
        logger.info("Schema creation successful and search path set to cmti, public")
    except Exception as e:
        logger.error(f"Schema creation error: {e}")
        logger.error(traceback.format_exc())


ensure_schema_exists()


# First, manually create or update the table with all required columns
@db_session
def update_table_manually():
    try:
        # Create table if it doesn't exist
        db.execute("""
        CREATE TABLE IF NOT EXISTS cmti.registervalues (
            id SERIAL PRIMARY KEY,
            emailid VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            employee_status VARCHAR(255) NOT NULL
        )
        """)

        # Try to add the last_login column (will fail silently if already exists)
        try:
            db.execute("ALTER TABLE cmti.registervalues ADD COLUMN last_login TIMESTAMP NULL")
            logger.info("Added last_login column")
        except Exception as e:
            # Column might already exist
            logger.info(f"Note about last_login column: {e}")

        logger.info("Table structure updated successfully")
    except Exception as e:
        logger.error(f"Error updating table: {e}")
        logger.error(traceback.format_exc())


update_table_manually()


# Define entity without last_login first - for compatibility
class RegisterValuesBase(db.Entity):
    _table_ = 'registervalues'
    _schema_ = 'cmti'

    id = PrimaryKey(int, auto=True)
    emailid = Required(str, unique=True)
    name = Required(str)
    password = Required(str)
    employee_status = Required(str)


# Generate mapping with the base entity without checking tables
db.generate_mapping(create_tables=False, check_tables=False)


# Pydantic models
class UserRegister(BaseModel):
    emailid: EmailStr
    name: str
    password: str
    employee_status: str


class UserLogin(BaseModel):
    emailid: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    emailid: str
    name: str
    employee_status: str


class EmployeeResponse(BaseModel):
    id: int
    name: str
    emailid: str
    employee_status: str
    status: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info(f"Password verification: {result}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        logger.error(traceback.format_exc())
        return False


# Add a middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    # Log request body for debugging if it's POST/PUT
    if request.method in ["POST", "PUT"]:
        try:
            body = await request.body()
            if body:
                # Try to parse as JSON but don't log passwords
                try:
                    body_json = json.loads(body)
                    if isinstance(body_json, dict) and "password" in body_json:
                        masked_body = body_json.copy()
                        masked_body["password"] = "********"
                        logger.info(f"Request body: {masked_body}")
                    else:
                        logger.info(f"Request body: {body_json}")
                except:
                    # If not JSON, just log the length
                    logger.info(f"Request body length: {len(body)} bytes")
        except Exception as e:
            logger.error(f"Error logging request body: {e}")

    # Set search path for DB sessions
    @db_session
    def set_path():
        db.execute("SET search_path TO cmti, public")

    set_path()

    # Process the request and log the response
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request error: {e}")
        logger.error(traceback.format_exc())
        raise


@router.get("/health")
def health_check():
    """Simple health check endpoint to verify the API is running"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@router.get("/employees", response_model=List[EmployeeResponse])
@db_session
def get_employees():
    try:
        db.execute("SET search_path TO cmti, public")

        current_time = datetime.now()
        # Consider active if logged in within the last 24 hours
        active_threshold = current_time - timedelta(hours=24)

        logger.info(f"Fetching employees. Active threshold: {active_threshold}")

        # Use SQL directly to handle the last_login column
        results = db.execute("""
        SELECT id, name, emailid, employee_status, last_login 
        FROM cmti.registervalues
        """).fetchall()

        logger.info(f"Found {len(results)} employees in database")

        employee_list = []
        for row in results:
            # Extract values from row
            id, name, emailid, employee_status, last_login = row

            # Set status based on last_login (if it's not None and recent)
            if last_login and last_login >= active_threshold:
                status = "Active"
            else:
                status = "Inactive"

            logger.info(f"Employee {id} ({emailid}) - Last login: {last_login} - Status: {status}")

            employee_list.append({
                "id": id,
                "name": name,
                "emailid": emailid,
                "employee_status": employee_status,
                "status": status
            })

        return employee_list

    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch employees: {str(e)}"
        )


@router.post("/register", response_model=UserResponse)
@db_session
def register_user(user: UserRegister):
    try:
        # Set search path directly in this session
        db.execute("SET search_path TO cmti, public")

        logger.info(f"Current search_path: {db.execute('SHOW search_path').fetchone()[0]}")
        logger.info(f"Received registration request: {user.dict(exclude={'password'})}")

        # Check if user already exists
        existing_user = db.execute("""
        SELECT id FROM cmti.registervalues WHERE emailid = $email
        """, {'email': user.emailid}).fetchone()

        if existing_user:
            logger.warning(f"Registration attempt for existing email: {user.emailid}")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user with hashed password (direct SQL to avoid entity mapping issues)
        hashed_password = hash_password(user.password)
        logger.info(f"Password hashed successfully for {user.emailid}")

        current_time = datetime.now()
        logger.info(f"Setting initial last_login to {current_time}")

        result = db.execute("""
        INSERT INTO cmti.registervalues (emailid, name, password, employee_status, last_login)
        VALUES ($email, $name, $password, $employee_status, $last_login)
        RETURNING id
        """, {
            'email': user.emailid,
            'name': user.name,
            'password': hashed_password,
            'employee_status': user.employee_status,
            'last_login': current_time
        })

        new_id = result.fetchone()[0]

        # Commit explicitly to ensure changes are saved
        commit()
        logger.info(f"User registered successfully: {new_id}")

        return {
            "id": new_id,
            "emailid": user.emailid,
            "name": user.name,
            "employee_status": user.employee_status
        }
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        logger.error(traceback.format_exc())
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/login", response_model=UserResponse)
@db_session
def login_user(user: UserLogin):
    try:
        # Set search path directly in this session
        db.execute("SET search_path TO cmti, public")

        logger.info(f"Received login request for email: {user.emailid}")
        logger.info(f"Password provided: {user.password[:1]}{'*' * (len(user.password) - 1)}")

        # Get raw database info first for debugging
        raw_user_data = db.execute("""
        SELECT * FROM cmti.registervalues WHERE emailid = $email
        """, {'email': user.emailid}).fetchall()

        logger.info(f"Raw query returned {len(raw_user_data)} rows")

        if raw_user_data:
            for i, row in enumerate(raw_user_data):
                # Log all columns except full password hash
                safe_row = list(row)
                if len(safe_row) >= 4:  # Make sure password index exists
                    password_hash = safe_row[3]
                    safe_row[3] = f"{password_hash[:10]}..." if password_hash else "None"
                logger.info(f"Row {i}: {safe_row}")

        # Find user by email with all needed fields
        user_data = db.execute("""
        SELECT id, emailid, name, password, employee_status
        FROM cmti.registervalues 
        WHERE emailid = $email
        """, {'email': user.emailid}).fetchone()

        if not user_data:
            logger.warning(f"User not found: {user.emailid}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        logger.info(f"Found user ID: {user_data[0]}, email: {user_data[1]}")

        # Extract stored password and check if it's None or empty
        stored_password = user_data[3]
        if not stored_password:
            logger.error(f"Stored password is empty for user {user_data[1]}")
            raise HTTPException(status_code=500, detail="Invalid password hash in database")

        logger.info(f"Stored password hash: {stored_password[:10]}...")

        # Verify password
        password_verified = verify_password(user.password, stored_password)
        logger.info(f"Password verification result: {password_verified}")

        if not password_verified:
            logger.warning(f"Password verification failed for user: {user.emailid}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Update last_login time to current time
        current_time = datetime.now()
        logger.info(f"Updating last_login to {current_time} for {user.emailid}")

        try:
            db.execute("""
            UPDATE cmti.registervalues 
            SET last_login = $last_login 
            WHERE emailid = $email
            """, {'last_login': current_time, 'email': user.emailid})

            # Commit the transaction explicitly
            commit()
            logger.info(f"Last login updated and transaction committed")

            # Verify the update happened
            updated_login = db.execute("""
            SELECT last_login FROM cmti.registervalues WHERE emailid = $email
            """, {'email': user.emailid}).fetchone()

            logger.info(f"Updated last_login verification: {updated_login}")
        except Exception as e:
            logger.error(f"Error updating last_login: {e}")
            logger.error(traceback.format_exc())
            # Continue despite error, this shouldn't block login

        logger.info(f"User logged in successfully: {user_data[0]}")  # Index 0 is id

        # Return user data (excluding password)
        return {
            "id": user_data[0],
            "emailid": user_data[1],
            "name": user_data[2],
            "employee_status": user_data[4]
        }
    except HTTPException:
        # Re-raise HTTP exceptions without additional wrapping
        raise
    except Exception as e:
        logger.error(f"Unexpected error in login: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


# Debug endpoint to inspect a user
@router.get("/debug/user/{email}")
@db_session
def debug_user(email: str):
    try:
        db.execute("SET search_path TO cmti, public")

        # Only for development/debugging
        user_data = db.execute("""
        SELECT id, emailid, name, employee_status, last_login,
               LENGTH(password) as password_length,
               SUBSTRING(password, 1, 10) as password_prefix
        FROM cmti.registervalues 
        WHERE emailid = $email
        """, {'email': email}).fetchone()

        if not user_data:
            return {"status": "error", "message": "User not found"}

        return {
            "status": "success",
            "user_found": True,
            "id": user_data[0],
            "email": user_data[1],
            "name": user_data[2],
            "employee_status": user_data[3],
            "last_login": user_data[4],
            "password_info": {
                "length": user_data[5],
                "prefix": user_data[6]
            }
        }
    except Exception as e:
        logger.error(f"Debug user error: {e}")
        return {"status": "error", "message": str(e)}


# Add reset password functionality
@router.post("/reset-password")
@db_session
def reset_password(email: str, new_password: str):
    try:
        db.execute("SET search_path TO cmti, public")

        # Check if user exists
        user = db.execute("SELECT id FROM cmti.registervalues WHERE emailid = $email", {'email': email}).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Hash the new password
        hashed_password = hash_password(new_password)

        # Update the password
        db.execute("""
        UPDATE cmti.registervalues 
        SET password = $password 
        WHERE emailid = $email
        """, {'password': hashed_password, 'email': email})

        # Commit the transaction
        commit()

        return {"status": "success", "message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")


# Keep the old endpoint for backward compatibility, but mark it as deprecated
@router.post("/registerdetails", response_model=UserResponse, deprecated=True)
@db_session
def register_user_old(user: UserRegister):
    # Set search path directly in this session too
    db.execute("SET search_path TO cmti, public")
    return register_user(user)


app.include_router(router, prefix="/register", tags=["Register"])

if __name__ == "__main__":
    logger.info("Starting User Registration API server")
    uvicorn.run("register:app", host="172.18.100.33", port=30000, reload=True)