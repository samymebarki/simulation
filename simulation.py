import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd

# Set page configuration for wide layout
st.set_page_config(layout="wide")

# Title
st.title("SAM's Simulation Dashboard")

# Add strategy explanation
st.header("Trading Strategy Logic")
st.markdown("""
### Strategy Overview
- **Initial Risk**: We start with an initial risk of 1% per trade for all accounts.
- **Account Switching**: If an account experiences 2 consecutive losses or reaches its profit target, we switch to the next account.
- **Risk Management**: 
  - The risk per trade is dynamically adjusted based on the account's performance to optimize capital preservation and maximize potential returns. 
  - **Risk Levels**:
    - **1% Risk**: This is the default risk level at the beginning of trading. It ensures that losses are limited and the account can withstand adverse conditions without significant drawdown.
    - **Increasing Risk**: 
      - If the account's cumulative profit exceeds 3% of the initial balance, the risk per trade is increased to 1.5%. This adjustment allows for potentially higher profits while still managing risk within acceptable limits.
      - If the profit increases further to exceed 6%, the risk level can be increased to 2%, maximizing the profit potential as the account gains strength.
    - **Decreasing Risk**: 
      - Conversely, if the account suffers a drawdown of more than 3% from the initial balance, the risk is reduced to 0.5%. This conservative approach helps protect the remaining capital during unfavorable trading periods.
  - The goal of this adaptive risk management strategy is to balance the pursuit of profits with the protection of capital, adjusting to the market conditions and the account's performance.
""")

# Add a table summarizing the risk management logic
st.header("Risk Management Logic Table")
risk_management_data = {
    "Account Performance": [
        "Initial Risk (0% - 3% Profit)",
        "3% - 6% Profit",
        "6% + Profit",
        "3% + Drawdown"
    ],
    "Risk Level Per Trade": [
        "1% (Default Risk)",
        "1.5% (Increased Risk)",
        "2% (Max Risk)",
        "0.5% (Reduced Risk)"
    ],
    "Description": [
        "Standard risk level applied to all accounts to maintain capital preservation.",
        "Increased risk to enhance profit potential as the account performs well.",
        "Maximum risk to maximize profits when the account shows strong performance.",
        "Decreased risk level to protect capital when the account experiences a significant drawdown."
    ]
}

# Create a DataFrame for the risk management data
risk_management_df = pd.DataFrame(risk_management_data)

# Display the risk management logic table with a custom style
st.table(risk_management_df.style.set_table_attributes('style="width: 100%; background-color: #f9f9f9;"').set_properties(**{
    'color': 'black', 
    'font-size': '14px', 
    'border': '1px solid #e0e0e0'
}))

# Input fields for user-defined parameters with custom style
st.sidebar.header("User Parameters")
initial_balance = st.sidebar.number_input("Initial Balance ($)", value=25000, min_value=1000, step=100)
max_drawdown_limit = st.sidebar.slider("Max Drawdown Limit (%)", 0.0, 1.0, 0.08, 0.01) / 100
win_rate = st.sidebar.slider("Win Rate (%)", 0, 100, 50) / 100
risk_reward_ratio = st.sidebar.number_input("Risk-Reward Ratio (R:R)", value=2.0, min_value=1.0)
accounts = st.sidebar.number_input("Number of Accounts", value=5, min_value=1, max_value=10)
profit_target = st.sidebar.slider("Profit Target (%)", 0.0, 100.0, 12.0, 1.0) / 100  # Convert percentage to decimal

# Function to simulate trading
def simulate_trading():
    global total_trades
    account_balances = [initial_balance] * accounts
    total_trades = 0  # Initialize total trades counter

    # Store trade results
    trade_results = []

    # Initialize lists for plotting
    balance_history = [[] for _ in range(accounts)]
    cumulative_profit_history = [[] for _ in range(accounts)]  # Track cumulative profit for each trade
    lowest_balances = [initial_balance] * accounts  # Track lowest balances

    # Initialize max consecutive win/loss counters
    max_consecutive_wins = [0] * accounts
    max_consecutive_losses = [0] * accounts

    all_accounts_above_target = False
    current_account_index = 0  # Start with the first account

    # Initialize trade numbers for each account
    trade_numbers = [1] * accounts

    while not all_accounts_above_target:
        current_balance = account_balances[current_account_index]

        # Skip trading for this account if the profit target is met
        if (current_balance - initial_balance) / initial_balance >= profit_target:
            # Switch to the next account if the current one is done
            current_account_index = (current_account_index + 1) % accounts
            continue  

        highest_balance = current_balance  # Track the highest balance for drawdown calculations
        
        # Initialize current streak counters for this account
        current_consecutive_wins = 0
        current_consecutive_losses = 0
        
        # Set initial risk
        risk_level = 0.01  # Initial risk of 1%

        # Begin trading for the current account
        while True:
            # Simulate win/loss
            is_win = random.random() < win_rate  
            if is_win:  # Win
                win_loss = 'Win'
                new_balance = current_balance + (current_balance * risk_level * risk_reward_ratio)
                current_consecutive_wins += 1 
                max_consecutive_wins[current_account_index] = max(max_consecutive_wins[current_account_index], current_consecutive_wins)  # Increment current wins
                current_consecutive_losses = 0  # Reset losses
            else:  # Loss
                win_loss = 'Loss'
                new_balance = current_balance - (current_balance * risk_level)
                current_consecutive_losses += 1  # Increment current losses
                max_consecutive_losses[current_account_index] = max(max_consecutive_losses[current_account_index], current_consecutive_losses)
                current_consecutive_wins = 0  # Reset wins
                
            # Update account balance
            account_balances[current_account_index] = new_balance
            current_balance = new_balance
            balance_history[current_account_index].append(new_balance)

            # Calculate cumulative profit
            cumulative_profit = (current_balance - initial_balance) / initial_balance * 100
            cumulative_profit_history[current_account_index].append(cumulative_profit)

            lowest_balances[current_account_index] = min(lowest_balances[current_account_index], current_balance)

            # Log trade result with detailed information
            trade_results.append({
                'account': current_account_index + 1,
                'trade_number': trade_numbers[current_account_index],  # Use separate trade number
                'new_balance': new_balance,
                'is_win': win_loss,
                'risk_level': f"{risk_level * 100:.2f}%",
                'cumulative_profit': f"{cumulative_profit:.2f}%",
            })
            total_trades += 1  # Increment total trades counter

            # Increment the trade number for the current account after logging
            trade_numbers[current_account_index] += 1  

            # Update the highest balance for drawdown calculation
            highest_balance = max(highest_balance, new_balance)

            # Check if two consecutive losses occurred
            if current_consecutive_losses == 2:
                # Log the condition and switch to the next account
                current_account_index = (current_account_index + 1) % accounts  # Switch to the next account
                trade_numbers[current_account_index] = 1  # Reset trade number for the new account
                current_consecutive_losses = 0  # Reset losses for the new account
                break  # Exit inner while loop to start trading on the next account

            
            if win_loss == 'Loss':
                # If there is a loss and risk was at 2% or 1.5%, revert to 1% risk
                if risk_level in [0.02, 0.015]:
                        risk_level = 0.01  # Revert to 1%
            # Manage risk level based on account performance
            if (current_balance - initial_balance) / initial_balance >= 0.06:
                risk_level = 0.02  # Increase to 2% risk
            elif (current_balance - initial_balance) / initial_balance >= 0.03:
                risk_level = 0.015  # Increase to 1.5% risk
            elif (initial_balance - current_balance) / initial_balance >= 0.03:
                risk_level = 0.005  # Decrease to 0.5% risk


            # Manage risk level based on account performance
            if (initial_balance - current_balance) >= (initial_balance * max_drawdown_limit):
                break  # Stop trading if max drawdown limit is reached
            
            # Check if the account has met the profit target after the trade
            if (current_balance - initial_balance) / initial_balance >= profit_target:
                break

        # Check if all accounts have met the profit target
        all_accounts_above_target = all(
            (balance - initial_balance) / initial_balance >= profit_target
            for balance in account_balances
        )

    return account_balances, trade_results, total_trades, max_consecutive_wins, max_consecutive_losses, cumulative_profit_history, lowest_balances

# Button to run simulation
if st.sidebar.button("Run Simulation"):
    # Execute simulation function
    account_balances, trade_results, total_trades, max_consecutive_wins, max_consecutive_losses, cumulative_profit_history, lowest_balances = simulate_trading()

    # Display performance metrics
    st.header("Simulation Performance Metrics")
    profit_percentages = [(balance - initial_balance) / initial_balance * 100 for balance in account_balances]
    formatted_profit_percentages = [f"{percentage:.2f}%" for percentage in profit_percentages]
    max_drawdowns = [((lowest_balances[i] - initial_balance) / initial_balance) * 100 for i in range(accounts)]
    formatted_max_drawdowns = [f"{draw:.2f}%" for draw in max_drawdowns]

    performance_data = pd.DataFrame({
        'Account': [f'Account {i + 1}' for i in range(accounts)],
        'Final Balance': account_balances,
        'Profit Percentage (%)': formatted_profit_percentages,
        'Max Drawdown (%)': formatted_max_drawdowns,
            'Max Consecutive Wins': max_consecutive_wins,
            'Max Consecutive Losses': max_consecutive_losses
    })

    st.table(performance_data.style.set_table_attributes('style="width: 100%; background-color: #f9f9f9;"').set_properties(**{
        'color': 'black', 
        'font-size': '14px', 
        'border': '1px solid #e0e0e0'
    }))

    # Display trade history
    st.header("Trade History")
    trade_history_df = pd.DataFrame(trade_results)
    st.table(trade_history_df.style.set_table_attributes('style="width: 100%; background-color: #f9f9f9;"').set_properties(**{
        'color': 'black', 
        'font-size': '14px', 
        'border': '1px solid #e0e0e0'
    }))

    # Plotting Cumulative Profit Over Trades
    st.header("Cumulative Profit Timeline")
    trade_indices = list(range(1, total_trades + 1))

    # Create a full timeline for all trades
    cumulative_profit_plot = []
    for i in range(accounts):
        # Extend the cumulative profit history with None for missing trades
        account_cumulative_profit = cumulative_profit_history[i] + [None] * (total_trades - len(cumulative_profit_history[i]))
        cumulative_profit_plot.append(account_cumulative_profit)

    # Plotting the cumulative profit for each account
    fig3, ax3 = plt.subplots(figsize=(10, 5))  # Specify figure size for better clarity
    for i in range(accounts):
        ax3.plot(cumulative_profit_plot[i], label=f'Account {i + 1}', marker='o')

    ax3.axhline(0, color='black', linestyle='--', label='Break-Even Line')
    ax3.axhline(profit_target * 100, color='red', linestyle='--', label='Profit Target (%)')
    ax3.set_title('Cumulative Profit Over Trades', fontsize=16)
    ax3.set_xlabel('Trade Number', fontsize=14)
    ax3.set_ylabel('Cumulative Profit (%)', fontsize=14)
    ax3.grid()
    ax3.legend()
    st.pyplot(fig3)

    st.write(f"Total Number of Trades Across All Accounts: {total_trades}")
