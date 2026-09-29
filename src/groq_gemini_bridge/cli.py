"""Terminal chatbot. Run: groq-gemini-chat   Commands: /groq /gemini /auto /reset /quit"""
from . import Chatbot, LLMError, build_providers


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv is optional; env vars still work

    bot = Chatbot(build_providers())
    preferred = None
    print(f"Keys loaded: {list(bot.providers)}  (commands: /groq /gemini /auto /reset /quit)")
    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text == "/quit":
            break
        if text == "/reset":
            bot.reset(); print("History cleared."); continue
        if text in ("/groq", "/gemini"):
            preferred = text[1:]; print(f"Using {preferred} first"); continue
        if text == "/auto":
            preferred = None; print("Auto mode"); continue
        try:
            r = bot.ask(text, preferred)
            print(f"Bot [{r['provider']}]: {r['reply']}")
        except (LLMError, ValueError) as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
