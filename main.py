# #
# # import asyncio
# # import uvicorn
# # import multiprocessing
# # import time
# # import sys
# # import os
# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel
# # import json
# #
# # # Add the current directory to Python path
# # current_dir = os.path.dirname(os.path.abspath(__file__))
# # sys.path.append(current_dir)
# #
# # # Create main FastAPI app
# # app = FastAPI(
# #     title="Combined API Services",
# #     description="API for processing lab test PDFs",
# #     version="1.0.0",
# #     docs_url="/docs",
# #     openapi_url="/openapi.json"
# # )
# #
# # # Add CORS middleware
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# #
# # # Import routers from each service
# # try:
# #     from mechanical import router as mechanical_router
# #     from aluminium import router as aluminium_router
# #     from steel import router as steel_router
# #     from foundry import router as foundry_router
# #     from radiology import router as radiology_router
# #     from rubber import router as rubber_router
# #     from chemical import router as chemical_router
# #
# #     # Include routers with prefixes
# #     app.include_router(mechanical_router, prefix="/mechanical", tags=["Mechanical"])
# #     app.include_router(aluminium_router, prefix="/aluminium", tags=["Aluminium"])
# #     app.include_router(steel_router, prefix="/steel", tags=["Steel"])
# #     app.include_router(foundry_router, prefix="/foundry", tags=["Foundry"])
# #     app.include_router(radiology_router, prefix="/radiology", tags=["Radiology"])
# #     app.include_router(rubber_router, prefix="/rubber", tags=["Rubber"])
# #     app.include_router(chemical_router, prefix="/chemical", tags=["Chemical"])
# #
# # except ImportError as e:
# #     print(f"Error importing routers: {e}")
# #
# # # Health check endpoint
# # @app.get("/health", tags=["Health"])
# # async def health_check():
# #     return {"status": "ok", "message": "API is running"}
# #
# # def run_mechanical():
# #     try:
# #         uvicorn.run("mechanical:app", host="localhost", port=7000, reload=False)
# #     except Exception as e:
# #         print(f"Mechanical Server error: {e}")
# #
# # def run_aluminium():
# #     try:
# #         uvicorn.run("aluminium:app", host="localhost", port=11000, reload=False)
# #     except Exception as e:
# #         print(f"Aluminium Server error: {e}")
# #
# # def run_steel():
# #     try:
# #         uvicorn.run("steel:app", host="localhost", port=8000, reload=False)
# #     except Exception as e:
# #         print(f"Steel Server error: {e}")
# #
# # def run_foundry():
# #     try:
# #         uvicorn.run("foundry:app", host="localhost", port=15000, reload=False)
# #     except Exception as e:
# #         print(f"Foundry Server error: {e}")
# #
# # def run_radiology():
# #     try:
# #         uvicorn.run("radiology:app", host="localhost", port=12000, reload=False)
# #     except Exception as e:
# #         print(f"Radiology Server error: {e}")
# #
# # def run_rubber():
# #     try:
# #         uvicorn.run("rubber:app", host="localhost", port=28000, reload=False)
# #     except Exception as e:
# #         print(f"Rubber Server error: {e}")
# #
# # def run_combined_api():
# #     try:
# #         uvicorn.run("main:app", host="localhost", port=19001, reload=False)  # Changed port to 19001
# #     except Exception as e:
# #         print(f"Combined API Server error: {e}")
# #
# # def run_multiprocess():
# #     # Create process objects
# #     mechanical_process = multiprocessing.Process(target=run_mechanical)
# #     aluminium_process = multiprocessing.Process(target=run_aluminium)
# #     steel_process = multiprocessing.Process(target=run_steel)
# #     foundry_process = multiprocessing.Process(target=run_foundry)
# #     radiology_process = multiprocessing.Process(target=run_radiology)
# #     rubber_process = multiprocessing.Process(target=run_rubber)
# #     combined_api_process = multiprocessing.Process(target=run_combined_api)
# #
# #     # List of all processes
# #     processes = [
# #         mechanical_process,
# #         aluminium_process,
# #         steel_process,
# #         foundry_process,
# #         radiology_process,
# #         rubber_process,
# #         combined_api_process
# #     ]
# #
# #     try:
# #         # Start all processes
# #         for process in processes:
# #             process.start()
# #             time.sleep(1)  # Add small delay between starting processes
# #
# #         # Keep the main process alive
# #         # while all(process.is_alive() for process in processes):
# #         while any(process.is_alive() for process in processes):
# #             time.sleep(1)
# #
# #     except KeyboardInterrupt:
# #         print("\nStopping servers...")
# #     except Exception as e:
# #         print(f"Error in main process: {e}")
# #     finally:
# #         # Terminate processes if they are still running
# #         for process in processes:
# #             if process.is_alive():
# #                 process.terminate()
# #                 process.join()
# #
# #         print("All servers stopped successfully")
# #
# # if __name__ == "__main__":
# #     import sys
# #
# #     if len(sys.argv) > 1 and sys.argv[1] == "--multiprocess":
# #         # Run in multiprocess mode
# #         run_multiprocess()
# #     else:
# #         # Run single combined API
# #         import uvicorn
# #         uvicorn.run("main:app", host="localhost", port=19001, reload=True)  # Changed port to 19001
# #
# # # if __name__ == "__main__":
# # #     # Always run in multiprocess mode without requiring command-line arguments
# # #     run_multiprocess()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# import asyncio
# import uvicorn
# import multiprocessing
# import time
# import sys
# import os
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import json
#
# # Add the current directory to Python path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)
#
# # Create main FastAPI app
# app = FastAPI(
#     title="Combined API Services",
#     description="API for processing lab test PDFs",
#     version="1.0.0",
#     docs_url="/docs",
#     openapi_url="/openapi.json"
# )
#
# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Import routers from each service
# try:
#     from mechanical import router as mechanical_router
#     from aluminium import router as aluminium_router
#     from steel import router as steel_router
#     from foundry import router as foundry_router
#     from radiology import router as radiology_router
#     from rubber import router as rubber_router
#     from chemical import router as chemical_router
#
#     # Include routers with prefixes
#     app.include_router(mechanical_router, prefix="/mechanical", tags=["Mechanical"])
#     app.include_router(aluminium_router, prefix="/aluminium", tags=["Aluminium"])
#     app.include_router(steel_router, prefix="/steel", tags=["Steel"])
#     app.include_router(foundry_router, prefix="/foundry", tags=["Foundry"])
#     app.include_router(radiology_router, prefix="/radiology", tags=["Radiology"])
#     app.include_router(rubber_router, prefix="/rubber", tags=["Rubber"])
#     app.include_router(chemical_router, prefix="/chemical", tags=["Chemical"])
#
# except ImportError as e:
#     print(f"Error importing routers: {e}")
#
# # Health check endpoint
# @app.get("/health", tags=["Health"])
# async def health_check():
#     return {"status": "ok", "message": "API is running"}
#
# def run_mechanical():
#     try:
#         uvicorn.run("mechanical:app", host="localhost", port=7000, reload=False)
#     except Exception as e:
#         print(f"Mechanical Server error: {e}")
#
# def run_aluminium():
#     try:
#         uvicorn.run("aluminium:app", host="localhost", port=11000, reload=False)
#     except Exception as e:
#         print(f"Aluminium Server error: {e}")
#
# def run_steel():
#     try:
#         uvicorn.run("steel:app", host="localhost", port=8000, reload=False)
#     except Exception as e:
#         print(f"Steel Server error: {e}")
#
# def run_foundry():
#     try:
#         uvicorn.run("foundry:app", host="localhost", port=15000, reload=False)
#     except Exception as e:
#         print(f"Foundry Server error: {e}")
#
# def run_radiology():
#     try:
#         uvicorn.run("radiology:app", host="localhost", port=12000, reload=False)
#     except Exception as e:
#         print(f"Radiology Server error: {e}")
#
# def run_rubber():
#     try:
#         uvicorn.run("rubber:app", host="localhost", port=28000, reload=False)
#     except Exception as e:
#         print(f"Rubber Server error: {e}")
#
# def run_chemical():
#     try:
#         uvicorn.run("chemical:app", host="localhost", port=10000, reload=False)
#     except Exception as e:
#         print(f"Chemical Server error: {e}")
#
# def run_combined_api():
#     try:
#         uvicorn.run("main:app", host="localhost", port=19001, reload=False)  # Changed port to 19001
#     except Exception as e:
#         print(f"Combined API Server error: {e}")
#
# def run_multiprocess():
#     # Create process objects
#     mechanical_process = multiprocessing.Process(target=run_mechanical)
#     aluminium_process = multiprocessing.Process(target=run_aluminium)
#     steel_process = multiprocessing.Process(target=run_steel)
#     foundry_process = multiprocessing.Process(target=run_foundry)
#     radiology_process = multiprocessing.Process(target=run_radiology)
#     rubber_process = multiprocessing.Process(target=run_rubber)
#     chemical_process = multiprocessing.Process(target=run_chemical)
#     combined_api_process = multiprocessing.Process(target=run_combined_api)
#
#     # List of all processes
#     processes = [
#         mechanical_process,
#         aluminium_process,
#         steel_process,
#         foundry_process,
#         radiology_process,
#         rubber_process,
#         chemical_process,
#         combined_api_process
#     ]
#
#     try:
#         # Start all processes
#         for process in processes:
#             process.start()
#             time.sleep(1)  # Add small delay between starting processes
#
#         # Keep the main process alive
#         # while all(process.is_alive() for process in processes):
#         while any(process.is_alive() for process in processes):
#             time.sleep(1)
#
#     except KeyboardInterrupt:
#         print("\nStopping servers...")
#     except Exception as e:
#         print(f"Error in main process: {e}")
#     finally:
#         # Terminate processes if they are still running
#         for process in processes:
#             if process.is_alive():
#                 process.terminate()
#                 process.join()
#
#         print("All servers stopped successfully")
#
# if __name__ == "__main__":
#     import sys
#
#     if len(sys.argv) > 1 and sys.argv[1] == "--multiprocess":
#         # Run in multiprocess mode
#         run_multiprocess()
#     else:
#         # Run single combined API
#         import uvicorn
#         uvicorn.run("main:app", host="localhost", port=19001, reload=True)























#
# import asyncio
# import uvicorn
# import multiprocessing
# import time
# import sys
# import os
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import json
#
# # Add the current directory to Python path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)
#
# # Create main FastAPI app
# app = FastAPI(
#     title="Combined API Services",
#     description="API for processing lab test PDFs",
#     version="1.0.0",
#     docs_url="/docs",
#     openapi_url="/openapi.json"
# )
#
# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Import routers from each service
# try:
#     from mechanical import router as mechanical_router
#     from aluminium import router as aluminium_router
#     from steel import router as steel_router
#     from foundry import router as foundry_router
#     from radiology import router as radiology_router
#     from rubber import router as rubber_router
#     from chemical import router as chemical_router
#
#     # Include routers with prefixes
#     app.include_router(mechanical_router, prefix="/mechanical", tags=["Mechanical"])
#     app.include_router(aluminium_router, prefix="/aluminium", tags=["Aluminium"])
#     app.include_router(steel_router, prefix="/steel", tags=["Steel"])
#     app.include_router(foundry_router, prefix="/foundry", tags=["Foundry"])
#     app.include_router(radiology_router, prefix="/radiology", tags=["Radiology"])
#     app.include_router(rubber_router, prefix="/rubber", tags=["Rubber"])
#     app.include_router(chemical_router, prefix="/chemical", tags=["Chemical"])
#
# except ImportError as e:
#     print(f"Error importing routers: {e}")
#
# # Health check endpoint
# @app.get("/health", tags=["Health"])
# async def health_check():
#     return {"status": "ok", "message": "API is running"}
#
# def run_mechanical():
#     try:
#         uvicorn.run("mechanical:app", host="localhost", port=7000, reload=False)
#     except Exception as e:
#         print(f"Mechanical Server error: {e}")
#
# def run_aluminium():
#     try:
#         uvicorn.run("aluminium:app", host="localhost", port=11000, reload=False)
#     except Exception as e:
#         print(f"Aluminium Server error: {e}")
#
# def run_steel():
#     try:
#         uvicorn.run("steel:app", host="localhost", port=8000, reload=False)
#     except Exception as e:
#         print(f"Steel Server error: {e}")
#
# def run_foundry():
#     try:
#         uvicorn.run("foundry:app", host="localhost", port=15000, reload=False)
#     except Exception as e:
#         print(f"Foundry Server error: {e}")
#
# def run_radiology():
#     try:
#         uvicorn.run("radiology:app", host="localhost", port=12000, reload=False)
#     except Exception as e:
#         print(f"Radiology Server error: {e}")
#
# def run_rubber():
#     try:
#         uvicorn.run("rubber:app", host="localhost", port=28000, reload=False)
#     except Exception as e:
#         print(f"Rubber Server error: {e}")
#
# def run_combined_api():
#     try:
#         uvicorn.run("main:app", host="localhost", port=19001, reload=False)  # Changed port to 19001
#     except Exception as e:
#         print(f"Combined API Server error: {e}")
#
# def run_multiprocess():
#     # Create process objects
#     mechanical_process = multiprocessing.Process(target=run_mechanical)
#     aluminium_process = multiprocessing.Process(target=run_aluminium)
#     steel_process = multiprocessing.Process(target=run_steel)
#     foundry_process = multiprocessing.Process(target=run_foundry)
#     radiology_process = multiprocessing.Process(target=run_radiology)
#     rubber_process = multiprocessing.Process(target=run_rubber)
#     combined_api_process = multiprocessing.Process(target=run_combined_api)
#
#     # List of all processes
#     processes = [
#         mechanical_process,
#         aluminium_process,
#         steel_process,
#         foundry_process,
#         radiology_process,
#         rubber_process,
#         combined_api_process
#     ]
#
#     try:
#         # Start all processes
#         for process in processes:
#             process.start()
#             time.sleep(1)  # Add small delay between starting processes
#
#         # Keep the main process alive
#         # while all(process.is_alive() for process in processes):
#         while any(process.is_alive() for process in processes):
#             time.sleep(1)
#
#     except KeyboardInterrupt:
#         print("\nStopping servers...")
#     except Exception as e:
#         print(f"Error in main process: {e}")
#     finally:
#         # Terminate processes if they are still running
#         for process in processes:
#             if process.is_alive():
#                 process.terminate()
#                 process.join()
#
#         print("All servers stopped successfully")
#
# if __name__ == "__main__":
#     import sys
#
#     if len(sys.argv) > 1 and sys.argv[1] == "--multiprocess":
#         # Run in multiprocess mode
#         run_multiprocess()
#     else:
#         # Run single combined API
#         import uvicorn
#         uvicorn.run("main:app", host="localhost", port=19001, reload=True)  # Changed port to 19001
#
# # if __name__ == "__main__":
# #     # Always run in multiprocess mode without requiring command-line arguments
# #     run_multiprocess()



























import asyncio
import logging

import uvicorn
import multiprocessing
import time
import sys
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Create main FastAPI app
app = FastAPI(
    title="Combined API Services",
    description="API for processing lab test PDFs",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers from each service
try:
    from mechanical import router as mechanical_router
    from aluminium import router as aluminium_router
    from steel import router as steel_router
    from foundry import router as foundry_router
    from radiology import router as radiology_router
    from rubber import router as rubber_router
    from chemical import router as chemical_router
    from register import router as register_router

    # Include routers with prefixes
    app.include_router(mechanical_router, prefix="/mechanical", tags=["Mechanical"])
    app.include_router(aluminium_router, prefix="/aluminium", tags=["Aluminium"])
    app.include_router(steel_router, prefix="/steel", tags=["Steel"])
    app.include_router(foundry_router, prefix="/foundry", tags=["Foundry"])
    app.include_router(radiology_router, prefix="/radiology", tags=["Radiology"])
    app.include_router(rubber_router, prefix="/rubber", tags=["Rubber"])
    app.include_router(chemical_router, prefix="/chemical", tags=["Chemical"])
    app.include_router(register_router, prefix="/register", tags=["Register"])



except ImportError as e:
    print(f"Error importing routers: {e}")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    logger.info("App")
    uvicorn.run("main:app", host="172.18.100.33", port=16000, reload=True)