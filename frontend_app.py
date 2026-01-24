#!/usr/bin/env python3
"""
AI Employee Dashboard + Chat Interface
Hackathon-ready Streamlit frontend for FTE-H

Run: streamlit run frontend_app.py
Set: OPENAI_API_KEY environment variable for AI chat
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent))

from odoo_mcp_server import OdooMCPServer

# Page config
st.set_page_config(
    page_title="AI Employee - FTE-H",
    page_icon="🤖",
    layout="wide"
)

# Initialize Odoo server (auto-detect mode based on credentials)
@st.cache_resource
def get_odoo_server():
    # Use production mode if credentials are set, otherwise sandbox
    if os.getenv("ODOO_PASSWORD") and os.getenv("ODOO_URL"):
        return OdooMCPServer(mode="production")
    return OdooMCPServer(mode="sandbox")

@st.cache_resource
def get_openai_client():
    """Initialize OpenAI client if API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        except Exception as e:
            st.warning(f"OpenAI API error: {e}")
            return None
    return None

odoo = get_odoo_server()
openai_client = get_openai_client()


def get_odoo_context(odoo: OdooMCPServer) -> str:
    """Build context string from Odoo data for Claude."""
    invoices = odoo.invoices
    partners = odoo.partners

    total_revenue = sum(inv['amount_total'] for inv in invoices)
    pending = [inv for inv in invoices if inv['state'] == 'posted']
    paid = [inv for inv in invoices if inv['state'] == 'paid']

    context = f"""Current Odoo Financial Data:

SUMMARY:
- Total Invoices: {len(invoices)}
- Pending Invoices: {len(pending)} (${sum(i['amount_total'] for i in pending):,.2f})
- Paid Invoices: {len(paid)}
- Total Revenue: ${total_revenue:,.2f}

PENDING INVOICES:
"""
    for inv in pending:
        context += f"- {inv['name']}: {inv['partner_name']} - ${inv['amount_total']:,.2f} due {inv['due_date']}\n"

    context += "\nCUSTOMERS:\n"
    for p in partners:
        context += f"- {p['name']} ({p['email']})\n"

    return context


def generate_response_openai(prompt: str, odoo: OdooMCPServer, message_history: list) -> str:
    """Generate response using OpenAI API."""
    if not openai_client:
        return generate_response_fallback(prompt, odoo)

    try:
        # Build system prompt with Odoo context
        system_prompt = f"""You are an AI Employee assistant for a financial operations team.
You have access to the company's Odoo ERP data and help with invoices, customers, and financial queries.
Be concise and helpful. Use the data below to answer questions accurately.

{get_odoo_context(odoo)}

Answer questions about invoices, customers, payments, and financial status based on this data.
If asked about something not in the data, be honest that you don't have that information."""

        # Build messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]

        for msg in message_history[1:]:  # Skip initial assistant greeting
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({"role": "user", "content": prompt})

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap, good for hackathon
            max_tokens=500,
            messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"OpenAI API error: {str(e)}\n\nFalling back to basic response:\n\n{generate_response_fallback(prompt, odoo)}"


def generate_response_fallback(prompt: str, odoo: OdooMCPServer) -> str:
    """Fallback response when Claude API is not available."""
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in ["invoice", "invoices", "billing"]):
        pending = [inv for inv in odoo.invoices if inv['state'] == 'posted']
        if pending:
            response = f"You have **{len(pending)} pending invoices**:\n\n"
            for inv in pending[:3]:
                response += f"- {inv['name']}: ${inv['amount_total']:,.2f} due {inv['due_date']}\n"
            return response
        return "All invoices are paid!"

    elif any(word in prompt_lower for word in ["customer", "client", "partner"]):
        response = f"You have **{len(odoo.partners)} customers**:\n\n"
        for p in odoo.partners[:3]:
            response += f"- {p['name']} ({p['email']})\n"
        return response

    elif any(word in prompt_lower for word in ["revenue", "total", "money", "summary"]):
        total = sum(inv['amount_total'] for inv in odoo.invoices)
        paid = sum(inv['amount_total'] for inv in odoo.invoices if inv['state'] == 'paid')
        return f"**Financial Summary:**\n- Total Revenue: ${total:,.2f}\n- Collected: ${paid:,.2f}\n- Outstanding: ${total-paid:,.2f}"

    elif any(word in prompt_lower for word in ["overdue", "late", "unpaid"]):
        overdue = [inv for inv in odoo.invoices if inv.get('amount_residual', 0) > 0]
        if overdue:
            response = f"**{len(overdue)} invoices with outstanding balance:**\n\n"
            for inv in overdue:
                response += f"- {inv['name']}: ${inv['amount_residual']:,.2f} outstanding\n"
            return response
        return "No overdue invoices! All caught up."

    elif any(word in prompt_lower for word in ["help", "what can you do"]):
        return """I can help you with:
- **Invoices**: View pending, paid, or overdue invoices
- **Customers**: List customer information
- **Revenue**: Get financial summaries

Try asking: "Show me pending invoices" or "What's our total revenue?" """

    else:
        return "I can help with invoices, customers, and financial reports. Try asking about pending invoices or customer list!"


# Sidebar
with st.sidebar:
    st.title("AI Employee")
    st.caption("FTE-H Hackathon Demo")

    mode = st.radio("Mode", ["Dashboard", "Chat", "Both"], index=2)

    st.divider()

    # Status indicators
    st.caption("Status")
    st.success(f"Odoo: {odoo.mode} mode")

    if openai_client:
        st.success("OpenAI API: Connected")
    else:
        st.warning("OpenAI API: Not configured")
        st.caption("Set OPENAI_API_KEY env var")

# Main content
st.title("AI Employee Dashboard")

if mode in ["Dashboard", "Both"]:
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    invoices = odoo.invoices
    partners = odoo.partners

    total_revenue = sum(inv['amount_total'] for inv in invoices)
    pending = [inv for inv in invoices if inv['state'] == 'posted']
    paid = [inv for inv in invoices if inv['state'] == 'paid']

    col1.metric("Total Invoices", len(invoices))
    col2.metric("Pending", len(pending), f"${sum(i['amount_total'] for i in pending):,.0f}")
    col3.metric("Paid", len(paid))
    col4.metric("Revenue", f"${total_revenue:,.0f}")

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Invoices", "Customers", "Reports"])

    with tab1:
        st.subheader("Recent Invoices")

        invoice_data = []
        for inv in invoices:
            invoice_data.append({
                "Invoice": inv['name'],
                "Customer": inv['partner_name'],
                "Amount": f"${inv['amount_total']:,.2f}",
                "Due Date": inv['due_date'],
                "Status": inv['state'].upper(),
                "Balance": f"${inv['amount_residual']:,.2f}"
            })

        st.dataframe(invoice_data, use_container_width=True)

    with tab2:
        st.subheader("Customers")

        customer_data = []
        for p in partners:
            customer_data.append({
                "Name": p['name'],
                "Email": p['email'],
                "Phone": p['phone']
            })

        st.dataframe(customer_data, use_container_width=True)

    with tab3:
        st.subheader("Financial Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### By Status")
            status_data = {
                "Paid": len(paid),
                "Pending": len(pending),
            }
            st.bar_chart(status_data)

        with col2:
            st.markdown("### Quick Stats")
            st.info(f"**Average Invoice:** ${total_revenue/len(invoices):,.2f}")
            st.info(f"**Total Customers:** {len(partners)}")

if mode in ["Chat", "Both"]:
    st.divider()
    st.subheader("Chat with AI Employee")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI Employee. I can help you with invoices, customer info, and financial reports. What would you like to know?"}
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about invoices, customers, reports..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response (uses OpenAI if available, fallback otherwise)
        with st.spinner("Thinking..."):
            response = generate_response_openai(prompt, odoo, st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
