import re
import os
from datetime import datetime
from uuid import uuid4
from collections import defaultdict

from openai import OpenAI
from uagents import Agent, Protocol, Context
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

# --------------------------------------
# Original helpline database by state
# --------------------------------------
helplines_by_state = {
    "tamil nadu": {
        "Women Helpline": "1091",
        "Police Emergency": "100",
        "Tamil Nadu Legal Services": "044-2534-0345",
        "Childline": "1098",
        "Local NGO - PCVC": "+91-44-2615-4883"
    },
    "maharashtra": {
        "Women Helpline": "103",
        "Mumbai Police": "100",
        "Legal Aid Mumbai": "022-2262-2213",
        "Sneha NGO (Domestic Abuse)": "022-2431-2828"
    },
    "karnataka": {
        "Women Helpline": "1091",
        "Bangalore Police": "100",
        "Karnataka Legal Services": "080-2238-7979",
        "Vanitha Sahayavani NGO": "080-2294-3450"
    },
    "delhi": {
        "Women Helpline": "181",
        "Delhi Police": "100",
        "Delhi Legal Services": "011-2338-7376",
        "DCW Helpline": "011-2337-1762"
    }
}

# --------------------------------------
# National emergency helplines
# --------------------------------------
national_helplines = {
    "Emergency Services (Police, Fire, Ambulance)": "112",
    "Women Helpline (availability varies by state)": "181",
    "Child Helpline": "1098",
    "National Commission for Women Helpline": "14490",
    "Cybercrime Helpline (financial cyber fraud)": "1930"
}

# --------------------------------------
# Additional state and UT coverage
# --------------------------------------
additional_locations = [
    "andhra pradesh",
    "arunachal pradesh",
    "assam",
    "bihar",
    "chhattisgarh",
    "goa",
    "gujarat",
    "haryana",
    "himachal pradesh",
    "jharkhand",
    "kerala",
    "madhya pradesh",
    "manipur",
    "meghalaya",
    "mizoram",
    "nagaland",
    "odisha",
    "punjab",
    "rajasthan",
    "sikkim",
    "telangana",
    "tripura",
    "uttar pradesh",
    "uttarakhand",
    "west bengal",
    "andaman and nicobar islands",
    "chandigarh",
    "dadra and nagar haveli and daman and diu",
    "jammu and kashmir",
    "ladakh",
    "lakshadweep",
    "puducherry"
]

for location in additional_locations:
    if location not in helplines_by_state:
        helplines_by_state[location] = {
            "Emergency Services": "112",
            "Women Helpline (verify local availability)": "181",
            "Child Helpline": "1098"
        }

# --------------------------------------
# Conversation memory per sender
# --------------------------------------
conversation_history = defaultdict(list)
MAX_HISTORY_LENGTH = 10


def save_message(sender, role, content):
    """Save messages and keep the latest 10 entries."""
    conversation_history[sender].append({
        "role": role,
        "content": content
    })

    conversation_history[sender] = (
        conversation_history[sender][-MAX_HISTORY_LENGTH:]
    )


# --------------------------------------
# Detect user's state or union territory
# --------------------------------------
city_to_state = {
    "pune": "maharashtra",
    "mumbai": "maharashtra",
    "bangalore": "karnataka",
    "bengaluru": "karnataka",
    "chennai": "tamil nadu",
    "hyderabad": "telangana",
    "kolkata": "west bengal",
    "lucknow": "uttar pradesh",
    "jaipur": "rajasthan",
    "ahmedabad": "gujarat",
    "dehradun": "uttarakhand",
    "roorkee": "uttarakhand",
}

def detect_location(user_input):
    lower_input = user_input.lower()

    for city, state in city_to_state.items():
        if re.search(rf"\b{city}\b", lower_input):
            return state

    locations = sorted(helplines_by_state.keys(), key=len, reverse=True)
    for location in locations:
        if re.search(rf"\b{re.escape(location)}\b", lower_input):
            return location

    return None


# --------------------------------------
# National and state emergency response
# --------------------------------------
def get_emergency_response(location=None):
    response = (
        "🛡️ SHAKTI AI SAFETY SUPPORT\n\n"
        "Your safety comes first. If you are in immediate danger, "
        "move to a safer place if possible and contact emergency "
        "services or someone you trust.\n\n"
        "NATIONAL CONTACTS:\n"
    )

    for service, number in national_helplines.items():
        response += f"- {service}: {number}\n"

    if location and location in helplines_by_state:
        response += (
            f"\nADDITIONAL CONTACTS FOR {location.title()}:\n"
        )

        for service, number in helplines_by_state[location].items():
            response += f"- {service}: {number}\n"

    response += (
        "\nImportant: Verify local NGO and legal-office numbers "
        "before relying on them. Women Helpline 181 is not "
        "operational in every state.\n\n"
        "If calling is unsafe, consider a trusted person or another "
        "safe way of seeking help. Only take steps that are safe "
        "for your circumstances."
    )

    return response


# --------------------------------------
# Personal safety planning feature
# --------------------------------------
def get_safety_plan():
    return """
🛡️ PERSONAL SAFETY PLAN

Here are some options to consider if they are safe for you:

1. Identify a safer place you could go if necessary.
2. Choose a trusted person and agree on a check-in method.
3. Keep essential medicines and important documents accessible,
   if doing so would not increase your risk.
4. Memorize an emergency contact in case your phone is unavailable.
5. Consider whether someone can monitor your phone or messages.
6. If you need immediate assistance in India, call 112 if safe.

You do not have to follow every step. Choose what works for you.

Would you like help thinking through your particular situation?
"""


# --------------------------------------
# Emotional support and grounding
# --------------------------------------
def get_grounding_exercise():
    return """
💜 LET'S TAKE A MOMENT TOGETHER

If you are somewhere safe and comfortable:

1. Put both feet on the floor.
2. Breathe gently and slowly, without forcing your breath.
3. Notice five things you can see.
4. Notice four things you can feel.
5. Notice three things you can hear.
6. Remind yourself: "I can take this one step at a time."

Skip any step that feels uncomfortable.

You can tell me what is troubling you whenever you feel ready.
You do not have to share anything you are uncomfortable sharing.
"""


# --------------------------------------
# Legal awareness feature
# --------------------------------------
def get_legal_awareness_response():
    return """
⚖️ LEGAL AWARENESS AND SUPPORT

If you are experiencing harassment, abuse, threats, or violence,
you may have options for seeking support.

- Contact emergency services on 112 if you are in immediate danger.
- Ask your State or District Legal Services Authority about legal aid.
- Consider contacting a suitable police station or relevant authority.
- A One Stop Centre may be able to connect eligible women with
  legal support, counselling, medical assistance, and other services.
- Keep records of incidents only if doing so is safe.
- You do not need to share private documents or identifying details
  with this chatbot.

The available options depend on your location and circumstances.
This is general legal information, not a substitute for advice
from a qualified legal professional.

Would you like general information about reporting abuse,
accessing legal aid, or understanding your options?
"""


# --------------------------------------
# Feature keyword groups
# --------------------------------------
emergency_keywords = [
    "helpline",
    "need help",
    "emergency",
    "unsafe",
    "harassment",
    "abuse",
    "violence",
    "danger",
    "assault"
]

# These phrases can trigger emergency support even without
# the user mentioning a state.
urgent_keywords = [
    "in immediate danger",
    "i am in danger",
    "i'm in danger",
    "i feel unsafe",
    "i am unsafe",
    "i'm unsafe",
    "not safe",
    "domestic violence",
    "sexual assault",
    "someone is following me",
    "i am being followed",
    "someone is hurting me",
    "he is hitting me",
    "she is hitting me",
    "stalking",
    "rape",
    "threatened me",
    "threatening me",
    "forced me",
    "being attacked",
    "need emergency help"
]

safety_plan_keywords = [
    "make a safety plan",
    "personal safety plan",
    "how can i stay safe",
    "how do i stay safe",
    "safety planning"
]

emotional_support_keywords = [
    "grounding exercise",
    "help me calm down",
    "i feel overwhelmed",
    "i need emotional support",
    "i feel anxious",
    "i am feeling anxious",
    "i feel helpless"
]

legal_keywords = [
    "legal aid",
    "legal rights",
    "legal help",
    "legal awareness",
    "report abuse",
    "report harassment",
    "how do i file a complaint"
]


# --------------------------------------
# Create the agent
# --------------------------------------
AGENT_SEED = os.getenv("AGENT_SEED")

if not AGENT_SEED:
    raise RuntimeError(
        "AGENT_SEED is missing. Set it in your environment first."
    )

agent = Agent(
    name="shakti_ai",
    port=8001,
    seed=AGENT_SEED,
    mailbox=True,
    description=(
        "SHAKTI AI - Assisting women with "
        "safety, legal, and emotional needs"
    )
)

# --------------------------------------
# ASI model client
# --------------------------------------
# Set ASI_API_KEY in your environment before running this file.
# Do not hard-code or publish real API keys.
ASI_API_KEY = os.getenv("ASI_API_KEY")

if not ASI_API_KEY:
    raise RuntimeError(
        "ASI_API_KEY is missing. Set it in your environment first."
    )

client = OpenAI(
    base_url="https://api.asi1.ai/v1",
    api_key=ASI_API_KEY
)

# --------------------------------------
# Chat protocol
# --------------------------------------
protocol = Protocol(spec=chat_protocol_spec)


@protocol.on_message(ChatMessage)
async def handle_user_message(
    ctx: Context,
    sender: str,
    msg: ChatMessage
):
    # Acknowledge the received message.
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.utcnow(),
            acknowledged_msg_id=msg.msg_id
        )
    )

    # Extract text content from the message.
    user_input = ""

    for item in msg.content:
        if isinstance(item, TextContent):
            user_input += item.text

    user_input = user_input.strip()

    # Ignore empty messages.
    if not user_input:
        response = (
            "Hello, I am SHAKTI AI. I can help with safety, helplines, "
            "legal awareness and emotional support. How can I help you today?"
        )

        await ctx.send(
            sender,
            ChatMessage(
                timestamp=datetime.utcnow(),
                msg_id=uuid4(),
                content=[
                    TextContent(type="text", text=response)
                ]
            )
        )
        return

    # Store the user's message.
    save_message(sender, "user", user_input)

    lower_input = user_input.lower()

    # Detect the location.
    detected_location = detect_location(user_input)

    # Preserve the original state + emergency-keyword behavior.
    state_emergency = (
        detected_location is not None
        and any(
            keyword in lower_input
            for keyword in emergency_keywords
        )
    )

    # Also recognize urgent situations without a state name.
    urgent_emergency = any(
        keyword in lower_input
        for keyword in urgent_keywords
    )

    is_emergency = state_emergency or urgent_emergency

    # --------------------------------------
    # Route to one response only
    # --------------------------------------
    if is_emergency:
        response = get_emergency_response(detected_location)

    elif any(
        keyword in lower_input
        for keyword in safety_plan_keywords
    ):
        response = get_safety_plan()

    elif any(
        keyword in lower_input
        for keyword in emotional_support_keywords
    ):
        response = get_grounding_exercise()

    elif any(
        keyword in lower_input
        for keyword in legal_keywords
    ):
        response = get_legal_awareness_response()

    else:
        # --------------------------------------
        # Existing ASI-powered AI chatbot
        # --------------------------------------
        try:
            r = client.chat.completions.create(
                model="asi1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are SHAKTI AI, a smart, kind, and supportive AI assistant
built to help women with safety, legal awareness,
general health information, motivation, and emotional needs.

PERSONALITY:
- Be respectful, empathetic, calm, and non-judgmental.
- Use simple, clear, practical language.
- Never blame, shame, or pressure the user.
- Respect the user's choices and boundaries.

SAFETY:
- Prioritize immediate safety when a user describes danger,
  violence, stalking, abuse, or threats.
- Encourage emergency assistance when appropriate.
- Offer practical safety planning when requested.
- Do not encourage confrontation with an abuser or attacker.
- Do not claim that you have contacted the police, an NGO,
  or an emergency service unless a real integration confirms it.
- Remember that a person may be monitored through their device.
- Suggest only actions that are safe in the user's circumstances.

LEGAL AWARENESS:
- Provide general legal information, not guaranteed outcomes.
- Explain that laws and procedures depend on jurisdiction.
- Encourage qualified legal advice when necessary.
- Do not invent laws, legal contacts, or case outcomes.

HEALTH AND EMOTIONAL SUPPORT:
- Provide general health information responsibly.
- Recommend appropriate professional care when necessary.
- Never present yourself as a doctor, therapist, or lawyer.
- For a medical emergency, encourage prompt professional help.
- Offer grounding exercises and supportive conversation when useful.

PRIVACY:
- Do not request passwords, OTPs, PINs, or unnecessary
  identifying information.
- Remind users not to share sensitive information unnecessarily.
- Never promise absolute confidentiality or guaranteed privacy.

CONVERSATION:
- Use the provided conversation history for context.
- Do not claim to remember information that is not available.
- Ask only relevant follow-up questions.
- Never invent emergency contacts or claim to have called them.
"""
                    }
                ] + conversation_history[sender],
                max_tokens=2048,
            )

            response = (
                r.choices[0].message.content or
                "I'm sorry, I couldn't generate a response. "
                "Please try again."
            ).strip()

        except Exception:
            ctx.logger.exception("Error from ASI API")

            response = (
                "⚠️ I'm unable to process your request right now. "
                "Please try again shortly. If you are in immediate "
                "danger, contact local emergency services directly."
            )

    # Store the assistant response once, regardless of which
    # feature generated it.
    save_message(sender, "assistant", response)

    # --------------------------------------
    # Send the final response to the user
    # --------------------------------------
    await ctx.send(
        sender,
        ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=response)
            ]
        )
    )


# --------------------------------------
# Handle acknowledgements
# --------------------------------------
@protocol.on_message(ChatAcknowledgement)
async def ack_handler(
    ctx: Context,
    sender: str,
    msg: ChatAcknowledgement
):
    pass


# --------------------------------------
# Register protocol and run agent
# --------------------------------------
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()