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
import json
from pathlib import Path
from datetime import datetime, timedelta
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

# Define tools for OpenAI function calling
ODOO_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_invoices",
            "description": "Get list of invoices from Odoo. Can filter by status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": ["draft", "posted", "paid", "unpaid"],
                        "description": "Filter invoices by state"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of invoices to return",
                        "default": 10
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customers",
            "description": "Get list of customers/partners from Odoo",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_customer",
            "description": "Create a new customer/partner in Odoo",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Customer name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Customer email address"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Customer phone number"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_invoice",
            "description": "Create a new invoice for a customer. Will create customer if they don't exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Invoice amount in dollars"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the service/product"
                    },
                    "due_days": {
                        "type": "integer",
                        "description": "Number of days until payment is due",
                        "default": 30
                    }
                },
                "required": ["customer_name", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_summary",
            "description": "Get financial summary including total revenue, pending, and paid amounts",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# Initialize Odoo server
@st.cache_resource
def get_odoo_server():
    odoo_url = os.getenv("ODOO_URL", "")
    odoo_password = os.getenv("ODOO_PASSWORD", "")

    is_real_creds = (
        odoo_url and
        odoo_password and
        "yourcompany" not in odoo_url and
        "your-" not in odoo_password
    )

    server = OdooMCPServer(mode="production" if is_real_creds else "sandbox")

    if is_real_creds:
        auth_result = server.authenticate()
        if not auth_result.get('success'):
            st.error(f"Odoo authentication failed: {auth_result.get('message', 'Unknown error')}")

    return server


@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        except Exception as e:
            st.warning(f"OpenAI API error: {e}")
            return None
    return None


def get_invoices_data(odoo: OdooMCPServer, state: str = None, limit: int = 50) -> list:
    """Get invoices from Odoo."""
    result = odoo.get_invoices(state=state, limit=limit)
    if result.get('success'):
        invoices = result.get('invoices', [])
        normalized = []
        for inv in invoices:
            normalized.append({
                'id': inv.get('id'),
                'name': inv.get('name', 'N/A'),
                'partner_id': inv.get('partner_id', [0, 'Unknown'])[0] if isinstance(inv.get('partner_id'), list) else inv.get('partner_id'),
                'partner_name': inv.get('partner_id', [0, 'Unknown'])[1] if isinstance(inv.get('partner_id'), list) else inv.get('partner_name', 'Unknown'),
                'invoice_date': inv.get('invoice_date', 'N/A'),
                'due_date': inv.get('invoice_date_due', inv.get('due_date', 'N/A')),
                'amount_total': inv.get('amount_total', 0),
                'amount_residual': inv.get('amount_residual', 0),
                'state': inv.get('state', 'draft'),
                'payment_state': inv.get('payment_state', 'not_paid')
            })
        return normalized
    return []


def get_partners_data(odoo: OdooMCPServer) -> list:
    """Get partners/customers from Odoo."""
    result = odoo.get_partners()
    if result.get('success'):
        partners = result.get('partners', [])
        normalized = []
        for p in partners:
            normalized.append({
                'id': p.get('id'),
                'name': p.get('name', 'Unknown'),
                'email': p.get('email', 'N/A') or 'N/A',
                'phone': p.get('phone', 'N/A') or 'N/A'
            })
        return normalized
    return []


def execute_tool(odoo: OdooMCPServer, tool_name: str, arguments: dict) -> str:
    """Execute an Odoo tool and return the result as a string."""

    if tool_name == "get_invoices":
        invoices = get_invoices_data(odoo, state=arguments.get('state'), limit=arguments.get('limit', 10))
        if not invoices:
            return "No invoices found. Try creating one first!"
        result = f"Found {len(invoices)} invoice(s):\n"
        for inv in invoices[:10]:
            status = "PAID" if inv['payment_state'] == 'paid' else inv['state'].upper()
            result += f"- {inv['name']}: {inv['partner_name']} - ${inv['amount_total']:,.2f} ({status})\n"
        return result

    elif tool_name == "get_customers":
        partners = get_partners_data(odoo)
        if not partners:
            return "No customers found. Try creating one first with 'create a customer named XYZ'!"
        result = f"Found {len(partners)} customer(s):\n"
        for p in partners[:10]:
            result += f"- {p['name']} (ID: {p['id']}, Email: {p['email']})\n"
        return result

    elif tool_name == "create_customer":
        name = arguments.get('name')
        email = arguments.get('email')
        phone = arguments.get('phone')

        result = odoo.create_partner(name, email, phone)

        if result.get('success'):
            partner = result.get('partner', {})
            return f"✅ Customer created successfully!\n- Name: {name}\n- ID: {partner.get('id', result.get('partner_id'))}\n- Email: {partner.get('email', 'N/A')}"
        else:
            return f"❌ Failed to create customer: {result.get('error', 'Unknown error')}"

    elif tool_name == "create_invoice":
        customer_name = arguments.get('customer_name')
        amount = arguments.get('amount')
        description = arguments.get('description', 'Services')
        due_days = arguments.get('due_days', 30)

        # Find customer
        partners = get_partners_data(odoo)
        partner = next((p for p in partners if customer_name.lower() in p['name'].lower()), None)

        # Auto-create customer if not found
        if not partner:
            create_result = odoo.create_partner(customer_name)
            if create_result.get('success'):
                partner = create_result.get('partner', {})
                if not partner.get('id'):
                    partner['id'] = create_result.get('partner_id')
            else:
                return f"❌ Failed to create customer '{customer_name}': {create_result.get('error', 'Unknown error')}"

        # Create invoice
        lines = [{'product': description, 'quantity': 1, 'price': amount}]
        result = odoo.create_invoice(partner['id'], lines)

        if result.get('success'):
            inv = result.get('invoice', {})
            return f"✅ Invoice created successfully!\n- Invoice: {inv.get('name', result.get('invoice_id'))}\n- Customer: {customer_name}\n- Amount: ${amount:,.2f}\n- Due in: {due_days} days"
        else:
            return f"❌ Failed to create invoice: {result.get('error', 'Unknown error')}"

    elif tool_name == "get_financial_summary":
        invoices = get_invoices_data(odoo)
        if not invoices:
            return "No financial data available yet. Create some invoices first!"

        total_revenue = sum(inv['amount_total'] for inv in invoices)
        paid = sum(inv['amount_total'] for inv in invoices if inv['payment_state'] == 'paid')
        pending = sum(inv['amount_total'] for inv in invoices if inv['state'] == 'posted' and inv['payment_state'] != 'paid')
        outstanding = sum(inv['amount_residual'] for inv in invoices)

        return f"""📊 Financial Summary:
- Total Invoiced: ${total_revenue:,.2f}
- Collected (Paid): ${paid:,.2f}
- Pending Payment: ${pending:,.2f}
- Outstanding Balance: ${outstanding:,.2f}
- Number of Invoices: {len(invoices)}"""

    return f"Unknown tool: {tool_name}"


def generate_response_with_tools(prompt: str, odoo: OdooMCPServer, openai_client, message_history: list) -> str:
    """Generate response using OpenAI with function calling."""
    if not openai_client:
        return "OpenAI API not configured. Please set OPENAI_API_KEY."

    try:
        # Build messages
        system_prompt = """You are an AI Employee assistant for a financial operations team.
You can help with invoices, customers, and financial queries using the available tools.
When a user asks to create an invoice, use the create_invoice tool.
When they ask about customers, use get_customers.
When they ask about invoices or financial data, use the appropriate tool.
Be helpful and concise."""

        messages = [{"role": "system", "content": system_prompt}]

        for msg in message_history[1:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": prompt})

        # First call - may request tool use
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=messages,
            tools=ODOO_TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Check if tool calls were made
        if assistant_message.tool_calls:
            # Execute each tool call
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                result = execute_tool(odoo, tool_name, arguments)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": result
                })

            # Add assistant message and tool results
            messages.append(assistant_message)
            messages.extend(tool_results)

            # Get final response
            final_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=500,
                messages=messages
            )

            return final_response.choices[0].message.content

        # No tool calls, return direct response
        return assistant_message.content

    except Exception as e:
        return f"Error: {str(e)}"


odoo = get_odoo_server()
openai_client = get_openai_client()


# Sidebar
with st.sidebar:
    st.title("AI Employee")
    st.caption("FTE-H Hackathon Demo")

    mode = st.radio("Mode", ["Dashboard", "Chat", "Both"], index=2)

    st.divider()

    st.caption("Status")
    st.success(f"Odoo: {odoo.mode} mode")

    if openai_client:
        st.success("OpenAI API: Connected")
    else:
        st.warning("OpenAI API: Not configured")

    st.divider()
    st.caption("Chat can:")
    st.markdown("""
    - 👥 **Create customers**
    - ➕ **Create invoices**
    - 📄 View invoices
    - 📊 Financial summary
    """)

# Main content
st.title("AI Employee Dashboard")

if mode in ["Dashboard", "Both"]:
    invoices = get_invoices_data(odoo)
    partners = get_partners_data(odoo)

    if not invoices:
        st.warning("No invoices found. Create some invoices in Odoo or via chat!")

    col1, col2, col3, col4 = st.columns(4)

    total_revenue = sum(inv['amount_total'] for inv in invoices) if invoices else 0
    pending = [inv for inv in invoices if inv['state'] == 'posted']
    paid = [inv for inv in invoices if inv['payment_state'] == 'paid']

    col1.metric("Total Invoices", len(invoices))
    col2.metric("Pending", len(pending), f"${sum(i['amount_total'] for i in pending):,.0f}" if pending else "$0")
    col3.metric("Paid", len(paid))
    col4.metric("Revenue", f"${total_revenue:,.0f}")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["Invoices", "Customers", "Reports"])

    with tab1:
        st.subheader("Recent Invoices")
        if invoices:
            invoice_data = []
            for inv in invoices:
                invoice_data.append({
                    "Invoice": inv['name'],
                    "Customer": inv['partner_name'],
                    "Amount": f"${inv['amount_total']:,.2f}",
                    "Due Date": str(inv['due_date']),
                    "Status": inv['state'].upper(),
                    "Balance": f"${inv['amount_residual']:,.2f}"
                })
            st.dataframe(invoice_data, use_container_width=True)
        else:
            st.info("No invoices yet. Try asking the chat to create one!")

    with tab2:
        st.subheader("Customers")
        if partners:
            customer_data = []
            for p in partners:
                customer_data.append({
                    "Name": p['name'],
                    "Email": p['email'],
                    "Phone": p['phone']
                })
            st.dataframe(customer_data, use_container_width=True)
        else:
            st.info("No customers yet.")

    with tab3:
        st.subheader("Financial Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### By Status")
            if invoices:
                status_data = {"Paid": len(paid), "Pending": len(pending)}
                st.bar_chart(status_data)

        with col2:
            st.markdown("### Quick Stats")
            if invoices:
                st.info(f"**Average Invoice:** ${total_revenue/len(invoices):,.2f}")
            st.info(f"**Total Customers:** {len(partners)}")

if mode in ["Chat", "Both"]:
    st.divider()
    st.subheader("Chat with AI Employee")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": """Hello! I'm your AI Employee. I can help you with:

**Actions I can take:**
- Create a customer: "Create a customer named KFS with email kfs@test.com"
- Create an invoice: "Create an invoice for KFS for $50"
- View invoices: "Show me all invoices"
- View customers: "List all customers"
- Financial summary: "Give me a financial summary"

**Try:** "Create a customer named KFS" """}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about invoices, create invoices, get summaries..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Working..."):
            response = generate_response_with_tools(prompt, odoo, openai_client, st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

        # Rerun to update dashboard if invoice was created
        if "create" in prompt.lower() and "invoice" in prompt.lower():
            st.rerun()
