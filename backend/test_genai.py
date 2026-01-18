
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
print(f"API Key present: {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test GenerationConfig access
        try:
            config = genai.types.GenerationConfig(
                temperature=0.7
            )
            print("genai.types.GenerationConfig works")
        except AttributeError:
            print("genai.types.GenerationConfig FAILED")
            try:
                config = genai.GenerationConfig(temperature=0.7)
                print("genai.GenerationConfig works")
            except Exception as e:
                print(f"genai.GenerationConfig also FAILED: {e}")

        # Test generation
        try:
            response = model.generate_content("Hello")
            print("Generation works")
        except Exception as e:
            print(f"Generation failed: {e}")

    except Exception as e:
        print(f"Bigger error: {e}")
