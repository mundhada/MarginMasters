import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Margin Masters", layout="wide", page_icon="💰")

# --- INITIALIZATION ---
if "current_quarter" not in st.session_state:
    st.session_state.current_quarter = 1
if "financials" not in st.session_state:
    st.session_state.financials = {
        "Revenue": 5_000_000,
        "Costs": int(5_000_000 * (1 - 0.18)),
        "Margin": 18.0,
        "Technical Debt": 0.0,
        "Team Morale": 4.0,
        "Client Satisfaction": 4.0,
        "Cash Flow": 500_000,
        "History": []
    }
if "outcome" not in st.session_state:
    st.session_state.outcome = ""
if "scenario" not in st.session_state:
    st.session_state.scenario = {}
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "total_score" not in st.session_state:
    st.session_state.total_score = 0

# --- ENHANCED SCENARIOS ---
SCENARIOS = [
    {
        "type": "Late Invoice Submission", 
        "desc": "Your billing team submitted invoices 2 weeks late to a major client. This delays payment and may require cost provisions for aged receivables.",
        "cost_impact": 50_000,
        "option_a": {
            "text": "Accept the cost provision and improve billing processes",
            "description": "Take the financial hit but invest in better systems",
            "effects": {"costs": 50_000, "morale": 0.1, "satisfaction": 0.1}
        },
        "option_b": {
            "text": "Push client for immediate payment despite late submission",
            "description": "Risk relationship but try to avoid provisions",
            "effects": {"costs": 25_000, "satisfaction": -0.3, "cash_flow": -30_000}
        },
        "learning": "Late invoicing affects cash flow and may require cost provisions. Better processes prevent future issues."
    },
    {
        "type": "Revenue Recognition vs Billing Gap", 
        "desc": "You've recognized $200K in revenue but haven't sent invoices yet. Aging analysis suggests provisions may be needed.",
        "cost_impact": 30_000,
        "option_a": {
            "text": "Rush invoice processing and accept provisions",
            "description": "Quick action but still take the cost hit",
            "effects": {"costs": 30_000, "cash_flow": 100_000}
        },
        "option_b": {
            "text": "Delay recognition until invoicing is complete",
            "description": "Conservative approach, adjust revenue timing",
            "effects": {"revenue": -200_000, "costs": 0}
        },
        "learning": "Revenue recognition timing should align with billing cycles to avoid provisions."
    },
    {
        "type": "Team Overtime Crunch", 
        "desc": "Critical project deadline approaching. Team needs 30% overtime for 3 weeks to deliver on time.",
        "cost_impact": 70_000,
        "option_a": {
            "text": "Approve overtime to meet deadline",
            "description": "Higher costs but maintain client relationships",
            "effects": {"costs": 70_000, "morale": -0.3, "satisfaction": 0.2}
        },
        "option_b": {
            "text": "Negotiate deadline extension",
            "description": "Protect costs and team, but risk client satisfaction",
            "effects": {"costs": 10_000, "satisfaction": -0.2, "morale": 0.1}
        },
        "learning": "Overtime increases costs significantly. Better project planning prevents crunches."
    },
    {
        "type": "Scope Creep Alert", 
        "desc": "Client requests additional features worth ~$80K in effort. Contract is ambiguous about whether this is included.",
        "cost_impact": 60_000,
        "option_a": {
            "text": "Absorb the work to maintain relationship",
            "description": "Take the cost hit for client satisfaction",
            "effects": {"costs": 60_000, "satisfaction": 0.4, "debt": 0.5}
        },
        "option_b": {
            "text": "Issue change order for additional work",
            "description": "Protect margins but negotiate with client",
            "effects": {"revenue": 80_000, "costs": 15_000, "satisfaction": -0.1}
        },
        "learning": "Clear contracts prevent scope creep. Change orders protect margins when scope expands."
    },
    {
        "type": "Technology Investment Opportunity", 
        "desc": "New development tools could improve team productivity by 15% but require upfront investment and training.",
        "cost_impact": 40_000,
        "option_a": {
            "text": "Invest in new tools and training",
            "description": "Short-term costs for long-term efficiency gains",
            "effects": {"costs": 40_000, "morale": 0.4, "debt": -0.2}
        },
        "option_b": {
            "text": "Continue with current tools",
            "description": "Preserve short-term margins",
            "effects": {"costs": 0, "morale": -0.1}
        },
        "learning": "Strategic investments can improve long-term productivity and margins."
    },
    {
        "type": "Quality vs Speed Dilemma", 
        "desc": "Critical bug found in production. Quick fix available but proper solution takes 2 weeks and significant resources.",
        "cost_impact": 55_000,
        "option_a": {
            "text": "Implement proper fix",
            "description": "Higher immediate cost but better long-term stability",
            "effects": {"costs": 55_000, "satisfaction": 0.2, "debt": -0.3}
        },
        "option_b": {
            "text": "Apply quick workaround",
            "description": "Lower immediate cost but increases technical debt",
            "effects": {"costs": 15_000, "debt": 1.0, "satisfaction": -0.1}
        },
        "learning": "Quality investments prevent future technical debt and support long-term margins."
    },
    {
        "type": "Client Payment Delay", 
        "desc": "Major client (20% of revenue) has cash flow issues and requests 60-day payment extension.",
        "cost_impact": 20_000,
        "option_a": {
            "text": "Grant extension with late fees",
            "description": "Maintain relationship but protect cash flow",
            "effects": {"cash_flow": -100_000, "costs": 20_000, "satisfaction": 0.2}
        },
        "option_b": {
            "text": "Demand immediate payment or halt work",
            "description": "Protect cash flow but risk losing major client",
            "effects": {"cash_flow": 50_000, "satisfaction": -0.5, "revenue": -200_000}
        },
        "learning": "Client payment terms directly impact cash flow and may require provisions."
    },
    {
        "type": "Aged Receivables Crisis", 
        "desc": "$150K in invoices are 80-90 days old. Accounting policies require significant cost provisions.",
        "cost_impact": 45_000,
        "option_a": {
            "text": "Accept provisions and improve collections",
            "description": "Take the hit and fix the process",
            "effects": {"costs": 45_000, "cash_flow": -50_000}
        },
        "option_b": {
            "text": "Aggressively pursue collections",
            "description": "Avoid provisions but risk client relationships",
            "effects": {"costs": 20_000, "satisfaction": -0.4, "cash_flow": 75_000}
        },
        "learning": "Aged receivables require cost provisions. Better collection processes prevent aging."
    },
    {
        "type": "Market Opportunity", 
        "desc": "Competitor failed, leaving market opening. Could capture additional revenue but need to scale team quickly.",
        "cost_impact": 80_000,
        "option_a": {
            "text": "Scale up to capture opportunity",
            "description": "Invest in growth for potential major revenue increase",
            "effects": {"costs": 80_000, "revenue": 300_000, "morale": 0.3}
        },
        "option_b": {
            "text": "Maintain current capacity",
            "description": "Avoid risk and maintain stable margins",
            "effects": {"costs": 0}
        },
        "learning": "Market opportunities require investment but can significantly increase revenue."
    },
    {
        "type": "Team Member Retention", 
        "desc": "Key senior developer received competing offer. Retention requires 25% salary increase plus bonus.",
        "cost_impact": 35_000,
        "option_a": {
            "text": "Match offer and retain talent",
            "description": "Higher costs but preserve expertise and morale",
            "effects": {"costs": 35_000, "morale": 0.3, "debt": -0.1}
        },
        "option_b": {
            "text": "Let them leave and hire replacement",
            "description": "Control costs but risk knowledge loss and delays",
            "effects": {"costs": 15_000, "morale": -0.4, "debt": 0.5}
        },
        "learning": "Key talent retention affects both immediate costs and long-term capability."
    }
]

def generate_scenario():
    scenario = random.choice(SCENARIOS)
    st.session_state.scenario = scenario

def calculate_score():
    """Calculate performance score based on multiple factors"""
    fin = st.session_state.financials
    base_score = fin["Margin"] * 10  # Base score from margin
    
    # Bonuses and penalties
    morale_bonus = (fin["Team Morale"] - 3.0) * 50
    satisfaction_bonus = (fin["Client Satisfaction"] - 3.0) * 50
    debt_penalty = fin["Technical Debt"] * -20
    cash_flow_bonus = min(fin["Cash Flow"] / 10_000, 50)  # Cap at 50
    
    total = base_score + morale_bonus + satisfaction_bonus + debt_penalty + cash_flow_bonus
    return max(0, total)

def apply_choice(choice):
    scenario = st.session_state.scenario
    fin = st.session_state.financials.copy()
    
    option = scenario[f"option_{choice.lower()}"]
    effects = option["effects"]
    
    # Apply effects
    fin["Revenue"] += effects.get("revenue", 0)
    fin["Costs"] += effects.get("costs", 0)
    fin["Team Morale"] = max(1.0, min(5.0, fin["Team Morale"] + effects.get("morale", 0)))
    fin["Client Satisfaction"] = max(1.0, min(5.0, fin["Client Satisfaction"] + effects.get("satisfaction", 0)))
    fin["Technical Debt"] = max(0.0, fin["Technical Debt"] + effects.get("debt", 0))
    fin["Cash Flow"] += effects.get("cash_flow", 0)
    
    # Update margin
    fin["Margin"] = round((fin["Revenue"] - fin["Costs"]) / fin["Revenue"] * 100, 2)
    
    # Store outcome and history
    outcome = f"**Choice Made:** {option['text']}\n\n**Result:** {option['description']}\n\n**Learning:** {scenario['learning']}"
    st.session_state.outcome = outcome
    
    fin["Scenario"] = scenario["type"]
    fin["Quarter"] = st.session_state.current_quarter
    fin["Score"] = calculate_score()
    
    st.session_state.financials = fin
    st.session_state.financials["History"].append(fin.copy())
    
    # Check for game over conditions
    if fin["Margin"] <= 0 or fin["Cash Flow"] <= -200_000:
        st.session_state.game_over = True

# --- MAIN UI ---
st.title("💰 Margin Masters: Strategic Business Simulation")
st.markdown("*Protect and improve your profit margins through strategic decision-making*")

if st.session_state.game_over:
    st.error("🚨 **Game Over!** Your margins or cash flow have reached critical levels.")
    if st.button("Restart Game"):
        # Reset all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
else:
    # Main game interface
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader(f"📅 Quarter {st.session_state.current_quarter} Challenge")
        
        if not st.session_state.scenario:
            generate_scenario()
        
        scenario = st.session_state.scenario
        
        # Scenario description
        st.info(f"**{scenario['type']}**\n\n{scenario['desc']}")
        
        # Choice buttons with clear descriptions
        st.markdown("### Your Options:")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"**Option A:** {scenario['option_a']['text']}")
            st.caption(scenario['option_a']['description'])
            if st.button("Choose Option A", type="primary", use_container_width=True):
                apply_choice("A")
                st.rerun()
        
        with col_b:
            st.markdown(f"**Option B:** {scenario['option_b']['text']}")
            st.caption(scenario['option_b']['description'])
            if st.button("Choose Option B", type="secondary", use_container_width=True):
                apply_choice("B")
                st.rerun()
    
    with col2:
        st.subheader("📊 Performance Dashboard")
        fin = st.session_state.financials
        
        # Key metrics with color coding
        margin_color = "normal" if fin['Margin'] >= 15 else "off" if fin['Margin'] >= 5 else "inverse"
        st.metric("Revenue", f"${fin['Revenue']:,}", delta=None)
        st.metric("Costs", f"${fin['Costs']:,}", delta=None)
        st.metric("Profit Margin", f"{fin['Margin']}%", delta=None, delta_color=margin_color)
        st.metric("Cash Flow", f"${fin['Cash Flow']:,}", delta=None)
        
        # Additional metrics
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Team Morale", f"{fin['Team Morale']:.1f}/5", delta=None)
            st.metric("Client Satisfaction", f"{fin['Client Satisfaction']:.1f}/5", delta=None)
        with col_m2:
            st.metric("Technical Debt", f"{fin['Technical Debt']:.1f}", delta=None)
            st.metric("Performance Score", f"{calculate_score():.0f}", delta=None)

# Outcome section
if st.session_state.outcome:
    st.subheader("📈 Quarter Results")
    st.markdown(st.session_state.outcome)

# Next quarter button
col_next1, col_next2, col_next3 = st.columns([1, 1, 1])
with col_next2:
    if st.button("➡️ Next Quarter", use_container_width=True, disabled=not st.session_state.outcome):
        st.session_state.current_quarter += 1
        st.session_state.outcome = ""
        st.session_state.scenario = {}
        st.rerun()

# History and Analytics
if st.session_state.financials["History"]:
    st.subheader("📊 Performance Analytics")
    
    history_df = pd.DataFrame(st.session_state.financials["History"])
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Financial Trends", "📋 Decision History", "🎯 Performance Summary"])
    
    with tab1:
        # Financial trend charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Revenue vs Costs Trend")
            chart_data = history_df.set_index("Quarter")[["Revenue", "Costs"]]
            st.line_chart(chart_data)
        
        with col_chart2:
            st.subheader("Profit Margin Trend (%)")
            margin_data = history_df.set_index("Quarter")["Margin"]
            st.line_chart(margin_data)
            st.caption("🎯 Target: 15% margin")
        
        # Team metrics
        st.subheader("Team & Client Metrics")
        team_data = history_df.set_index("Quarter")[["Team Morale", "Client Satisfaction"]]
        st.line_chart(team_data)
    
    with tab2:
        # Decision history table
        display_df = history_df[["Quarter", "Scenario", "Revenue", "Costs", "Margin", "Score"]].copy()
        display_df["Revenue"] = display_df["Revenue"].apply(lambda x: f"${x:,}")
        display_df["Costs"] = display_df["Costs"].apply(lambda x: f"${x:,}")
        display_df["Margin"] = display_df["Margin"].apply(lambda x: f"{x}%")
        display_df["Score"] = display_df["Score"].apply(lambda x: f"{x:.0f}")
        st.dataframe(display_df, use_container_width=True)
    
    with tab3:
        # Performance summary
        col_perf1, col_perf2, col_perf3 = st.columns(3)
        
        with col_perf1:
            avg_margin = history_df["Margin"].mean()
            margin_trend = "📈" if history_df["Margin"].iloc[-1] > history_df["Margin"].iloc[0] else "📉"
            st.metric("Average Margin", f"{avg_margin:.1f}%", delta=f"{margin_trend}")
        
        with col_perf2:
            total_revenue = history_df["Revenue"].sum()
            st.metric("Total Revenue", f"${total_revenue:,}")
        
        with col_perf3:
            avg_score = history_df["Score"].mean()
            st.metric("Average Score", f"{avg_score:.0f}")
        
        # Key insights
        st.markdown("### 💡 Key Insights")
        best_quarter = history_df.loc[history_df["Score"].idxmax()]
        worst_quarter = history_df.loc[history_df["Score"].idxmin()]
        
        st.success(f"**Best Quarter:** Q{best_quarter['Quarter']} - {best_quarter['Scenario']} (Score: {best_quarter['Score']:.0f})")
        st.error(f"**Challenging Quarter:** Q{worst_quarter['Quarter']} - {worst_quarter['Scenario']} (Score: {worst_quarter['Score']:.0f})")

# Help section
with st.expander("ℹ️ How to Play & Strategy Tips"):
    st.markdown("""
    **Objective:** Maintain and improve your profit margins while balancing multiple business factors.
    
    **Key Metrics:**
    - **Profit Margin:** Your primary goal - keep above 15% for good performance
    - **Cash Flow:** Must stay positive - negative cash flow can end the game
    - **Team Morale:** Affects productivity and technical debt
    - **Client Satisfaction:** Influences future revenue opportunities
    - **Technical Debt:** Accumulates costs over time if not managed
    
    **Strategy Tips:**
    - Balance short-term costs with long-term benefits
    - Invest in team and tools for sustainable margins
    - Manage cash flow carefully - late payments hurt
    - Address technical debt before it compounds
    - Strong client relationships enable better negotiations
    
    **Scoring:** Based on margin performance, team metrics, and financial stability.
    """)