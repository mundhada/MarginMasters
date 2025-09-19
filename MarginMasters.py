import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Margin Masters: Account My Account")

# --- INITIALIZE SESSION STATE ---
if 'quarter' not in st.session_state:
    st.session_state.quarter = 1
if 'revenue' not in st.session_state:
    st.session_state.revenue = 5_000_000  # 5M AUD per quarter
if 'margin' not in st.session_state:
    st.session_state.margin = 0.18  # starting operating margin
if 'costs' not in st.session_state:
    st.session_state.costs = st.session_state.revenue * (1 - st.session_state.margin)
if 'history' not in st.session_state:
    st.session_state.history = []  # store metrics per quarter
if 'scenario' not in st.session_state:
    st.session_state.scenario = None
if 'outcome' not in st.session_state:
    st.session_state.outcome = ""

# --- SCENARIOS ---
scenarios = [
    {
        "name": "Scope Creep",
        "description": "Client requests extra features beyond original scope, adding {extra_hours} hours of work at ${hourly_rate}/hour.",
        "params": {"extra_hours": (20, 80), "hourly_rate": (120, 180)},
        "choices": {
            "A": "Absorb the work",
            "B": "Request change order"
        }
    },
    {
        "name": "Resource Investment",
        "description": "Invest ${cost} in tools or training to improve team efficiency.",
        "params": {"cost": (5000, 15000)},
        "choices": {
            "A": "Approve investment",
            "B": "Defer to protect margin"
        }
    },
    {
        "name": "Timeline Pressure",
        "description": "Client wants delivery {weeks} weeks earlier, requiring {overtime_hours} hours overtime at 1.5x rate.",
        "params": {"weeks": (2, 6), "overtime_hours": (80, 200)},
        "choices": {
            "A": "Accept overtime",
            "B": "Negotiate timeline"
        }
    },
    {
        "name": "Quality Issue",
        "description": "Bugs found require {fix_hours} hours to fix properly, or {quick_hours} hours for quick workaround.",
        "params": {"fix_hours": (40, 100), "quick_hours": (10, 25)},
        "choices": {
            "A": "Proper fix",
            "B": "Quick fix"
        }
    },
    {
        "name": "Invoice Submitted Late",
        "description": "Invoices worth ${amount} were submitted late. Cash flow may be impacted.",
        "params": {"amount": (50_000, 200_000)},
        "choices": {
            "A": "Expedite submissions",
            "B": "Accept delays"
        }
    },
    {
        "name": "Invoice Paid Late",
        "description": "Outstanding invoices worth ${amount} delayed 80–90 days. Provision for doubtful debts needed.",
        "params": {"amount": (50_000, 200_000)},
        "choices": {
            "A": "Follow up aggressively",
            "B": "Wait for payment"
        }
    },
    {
        "name": "Revenue Recognized But Not Billed",
        "description": "Revenue of ${amount} recognized but not yet billed. Aging may require cost provision.",
        "params": {"amount": (50_000, 150_000)},
        "choices": {
            "A": "Ensure billing immediately",
            "B": "Defer billing"
        }
    },
    {
        "name": "Outstanding Invoices 80-90 days",
        "description": "Invoices worth ${amount} are 80–90 days outstanding. Risk of provisions for bad debt.",
        "params": {"amount": (50_000, 200_000)},
        "choices": {
            "A": "Implement stricter collection",
            "B": "Maintain current approach"
        }
    }
]

def generate_scenario():
    sc = random.choice(scenarios)
    params = {}
    for k, v in sc['params'].items():
        params[k] = random.randint(v[0], v[1])
    sc_text = sc['description'].format(**params)
    sc['generated_params'] = params
    sc['text'] = sc_text
    return sc

def apply_choice(scenario, choice):
    revenue = st.session_state.revenue
    costs = st.session_state.costs
    margin = st.session_state.margin
    explanation = ""
    
    if scenario['name'] == "Scope Creep":
        extra_cost = scenario['generated_params']['extra_hours'] * scenario['generated_params']['hourly_rate']
        if choice == "A":
            costs += extra_cost
            explanation = f"Absorbed extra work costing ${extra_cost:,}, increasing costs and lowering margin."
        else:
            # Assume 15% markup
            revenue += int(extra_cost * 1.15)
            costs += extra_cost
            explanation = f"Change order added ${int(extra_cost*1.15):,} revenue, costs increased by ${extra_cost:,}."
    
    elif scenario['name'] == "Resource Investment":
        invest = scenario['generated_params']['cost']
        if choice == "A":
            costs += invest
            explanation = f"Invested ${invest:,} in tools/training, increasing costs but may improve future efficiency."
        else:
            explanation = f"Deferred investment, margin protected but team efficiency may suffer."
    
    elif scenario['name'] == "Timeline Pressure":
        overtime_hours = scenario['generated_params']['overtime_hours']
        overtime_cost = int(overtime_hours * 150 * 1.5)
        if choice == "A":
            costs += overtime_cost
            explanation = f"Overtime costs ${overtime_cost:,} incurred, meeting deadline but margin drops."
        else:
            bonus = random.randint(5000, 15000)
            revenue += bonus
            explanation = f"Negotiated timeline; minor revenue bonus ${bonus:,}, avoided overtime costs."
    
    elif scenario['name'] == "Quality Issue":
        fix_hours = scenario['generated_params']['fix_hours']
        quick_hours = scenario['generated_params']['quick_hours']
        if choice == "A":
            costs += fix_hours * 120
            explanation = f"Proper fix costs ${fix_hours*120:,}, quality improved."
        else:
            costs += quick_hours * 120
            explanation = f"Quick fix costs ${quick_hours*120:,}, but may incur future debt."
    
    elif scenario['name'] in ["Invoice Submitted Late", "Invoice Paid Late", "Revenue Recognized But Not Billed", "Outstanding Invoices 80-90 days"]:
        amt = scenario['generated_params']['amount']
        # Revenue should not change if already recognized
        costs += int(amt * 0.05)  # provision 5% for bad debt / admin costs
        explanation = f"Provisioned 5% (${int(amt*0.05):,}) of invoice amount due to late submission/payment or aging."
    
    # Update session state
    st.session_state.revenue = revenue
    st.session_state.costs = costs
    st.session_state.margin = (revenue - costs)/revenue
    st.session_state.outcome = explanation
    
    # Record history
    st.session_state.history.append({
        "Quarter": st.session_state.quarter,
        "Scenario": scenario['name'],
        "Choice": choice,
        "Revenue": revenue,
        "Costs": costs,
        "Operating Margin": st.session_state.margin
    })

# --- UI ---
st.title("Margin Masters: Account My Account")

# Quarter navigation
st.write(f"### Quarter {st.session_state.quarter}")

if st.session_state.scenario is None:
    st.session_state.scenario = generate_scenario()

scenario = st.session_state.scenario
st.write(f"**Scenario:** {scenario['text']}")
col1, col2 = st.columns(2)
if col1.button(f"Choice A: {scenario['choices']['A']}"):
    apply_choice(scenario, "A")
    st.session_state.scenario = None
    st.session_state.quarter += 1
if col2.button(f"Choice B: {scenario['choices']['B']}"):
    apply_choice(scenario, "B")
    st.session_state.scenario = None
    st.session_state.quarter += 1

if st.session_state.outcome:
    st.success(f"Outcome & Explanation: {st.session_state.outcome}")

# Display chart
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df_hist['Quarter'], df_hist['Operating Margin']*100, marker='o', label='Operating Margin (%)')
    ax.set_ylim(0, 40)
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Operating Margin (%)")
    ax.set_title("Operating Margin Progression")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # Display metrics table with % formatting
    df_table = df_hist.copy()
    df_table['Operating Margin'] = df_table['Operating Margin'].apply(lambda x: f"{x*100:.1f}%")
    st.table(df_table[["Quarter", "Scenario", "Choice", "Revenue", "Costs", "Operating Margin"]])
