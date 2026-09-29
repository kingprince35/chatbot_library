"""Terminal chatbot.
One-shot:    chatrelay "What is Python?"
Interactive: chatrelay   (commands: /groq /gemini /auto /reset /quit)
"""
import sys

from . import Chatbot, LLMError, build_providers


def main():
    try:
        from dotenv import find_dotenv, load_dotenv
        load_dotenv(find_dotenv(usecwd=True))
    except ImportError:
        pass  # python-dotenv is optional; env vars still work

    bot = Chatbot(build_providers())

    args = sys.argv[1:]
    if args:
        question = " ".join(args)
        try:
            r = bot.ask(question)
            print(r["reply"])
        except (LLMError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

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
