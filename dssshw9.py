from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_PATH = r"C:\Users\rmukh\PycharmProjects\dssshw9\tinyllama"

# Load the model and tokenizer from the local path
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token  
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

# Function to generate a response using TinyLlama
def generate_response(prompt: str) -> str:
    # Prepend context to guide the model
    formatted_prompt = (
        "You are a helpful assistant. Provide detailed and useful responses to user queries.\n\n"
        f"User: {prompt}\nAssistant:"
    )

    # Tokenize the input with padding
    inputs = tokenizer(formatted_prompt, return_tensors="pt", padding=True)

    
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    
    outputs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=500,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )
 
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    response = response.replace(formatted_prompt, "").strip()
    return response

async def send_message(update: Update, text: str) -> None:
    """Send a message to the user."""
    await update.message.reply_text(text)

async def receive_message(update: Update) -> str:
    """Receive and process a user's message."""
    user_message = update.message.text
    response = generate_response(user_message)  # Generate AI response
    return response

# Telegram bot command to handle /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(update, "Hello! Ask me anything!")

# Telegram bot handler for messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = await receive_message(update)
    await send_message(update, response)

def main():
    TELEGRAM_BOT_TOKEN = "7625144410:AAE1EUyZvL8fHYUzwfF9VftGBlka5TlIeCA"

    # Initialize the Telegram bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

if _name_ == "_main_":
    main()
