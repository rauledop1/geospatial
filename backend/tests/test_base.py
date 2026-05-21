import sys
import os

# Add backend directory to sys.path so we can import 'app'
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

def test_imports():
    print("Starting environment verification...")
    try:
        import fastapi
        print(f"✓ FastAPI imported successfully (version: {fastapi.__version__})")
        
        import pydantic
        print(f"✓ Pydantic imported successfully (version: {pydantic.__version__})")
        
        import yaml
        print("✓ PyYAML imported successfully")
        
        import pydantic_settings
        print("✓ pydantic-settings imported successfully")
        
        # Test loading config and ag.yaml parsing
        from app.config import settings, geoportal_config
        print(f"✓ app.config module loaded successfully.")
        print(f"✓ APP_NAME from environment: '{settings.APP_NAME}'")
        
        title = geoportal_config.get("geoportal", {}).get("title")
        print(f"✓ ag.yaml configurations read correctly. Title: '{title}'")
        
        print("\n[SUCCESS] Architectural foundation verified. Ready for GIS service implementation.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILURE] Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
