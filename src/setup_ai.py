"""
Quick setup script for AI Chatbot features.

This script helps you set up the AI-powered Resource Concierge.
"""

import os
import subprocess
import sys

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_openai_installed():
    """Check if openai package is installed."""
    try:
        import openai
        return True
    except ImportError:
        return False

def install_openai():
    """Install openai package."""
    print("Installing OpenAI package...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==1.3.0"])
        print("✅ OpenAI package installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install OpenAI package")
        return False

def get_api_key():
    """Prompt user for API key."""
    print("\n🔑 OpenAI API Key Setup")
    print("-" * 60)
    print("To use AI features, you need an OpenAI API key.")
    print("Get one at: https://platform.openai.com/api-keys")
    print("\nAlternatively, press Enter to use keyword-based fallback mode (no API key needed).")
    print("-" * 60)
    
    api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Set environment variable
        os.environ['OPENAI_API_KEY'] = api_key
        print("\n✅ API key set for this session!")
        
        # Offer to save permanently
        print("\n💾 Would you like to save this to a .env file?")
        print("   (This will allow the key to persist across sessions)")
        save = input("Save to .env? (y/n): ").strip().lower()
        
        if save == 'y':
            with open('.env', 'a') as f:
                f.write(f"\n# OpenAI API Configuration\n")
                f.write(f"OPENAI_API_KEY={api_key}\n")
                f.write(f"OPENAI_MODEL=gpt-3.5-turbo\n")
            print("✅ API key saved to .env file!")
        
        return True
    else:
        print("\n⚠️  No API key provided. AI chatbot will use keyword-based fallback mode.")
        print("   You can add an API key later by setting the OPENAI_API_KEY environment variable.")
        return False

def main():
    """Main setup function."""
    print_header("🤖 AI Chatbot Setup - Campus Resource Hub")
    
    # Check if openai is installed
    if not check_openai_installed():
        print("📦 OpenAI package not found.")
        install = input("Would you like to install it now? (y/n): ").strip().lower()
        
        if install == 'y':
            if not install_openai():
                print("\n❌ Setup failed. Please install manually:")
                print("   pip install openai")
                return
        else:
            print("\n⚠️  Skipping OpenAI installation.")
            print("   AI chatbot will use keyword-based fallback mode.")
            print("\n   To install later, run:")
            print("   pip install openai")
            return
    else:
        print("✅ OpenAI package is already installed!")
    
    # Get API key
    has_key = get_api_key()
    
    # Final instructions
    print_header("🎉 Setup Complete!")
    
    print("Next steps:\n")
    print("1. Start the application:")
    print("   python run.py")
    print("\n2. Open your browser to:")
    print("   http://localhost:5000")
    print("\n3. Click 'AI Assistant' in the navigation bar")
    print("\n4. Start chatting with the AI Resource Concierge!")
    
    if has_key:
        print("\n✨ AI Features Enabled:")
        print("   ✅ Natural language understanding")
        print("   ✅ Context-aware conversations")
        print("   ✅ Personalized recommendations")
    else:
        print("\n📝 Current Mode: Keyword-Based Fallback")
        print("   ✅ Fast and free")
        print("   ✅ Works without API key")
        print("   ⚠️  Less intelligent than OpenAI")
        print("\n   To enable AI features, set your API key:")
        print("   export OPENAI_API_KEY=sk-your-key-here")
    
    print("\n📖 For detailed instructions, see:")
    print("   AI_SETUP_GUIDE.md")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("Please check the error and try again.")

