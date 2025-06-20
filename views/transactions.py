#!/usr/bin/env python3
"""
Transactions View - Job to be done: Track all position entries, exits, and yield claims
"""

from datetime import datetime, timedelta
import statistics

class TransactionsView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display transactions view with actual transaction data"""
        print("\n" + "="*120)
        print("💰 TRANSACTIONS")
        print("="*120)
        
        # Extract and display transactions
        transactions = self._extract_transactions()
        
        if not transactions:
            print("📊 No transaction data available.")
            print("\n💡 Transactions are extracted from your position entry/exit dates and yield claims.")
            return
        
        # Summary stats
        self._display_transaction_summary(transactions)
        
        # Transaction table
        self._display_transaction_table(transactions)
        
        # Cash flow analysis
        self._display_cash_flow_analysis(transactions)
    
    def _extract_transactions(self):
        """Extract transaction data from all positions"""
        transactions = []
        
        # Get all positions (active + closed)
        all_positions = (self.data_manager.get_all_active_positions() + 
                        self.data_manager.get_positions_by_strategy('closed'))
        
        for position in all_positions:
            position_name = position['token_pair'] or position['position_details'][:20]
            platform = position['platform']
            
            # Entry transaction (deposit)
            if position['entry_date'] and position['entry_value']:
                transactions.append({
                    'date': self._parse_date(position['entry_date']),
                    'type': 'DEPOSIT',
                    'position': position_name,
                    'platform': platform,
                    'strategy': position['strategy'],
                    'amount_usd': position['entry_value'],
                    'description': f"Initial deposit to {position_name}",
                    'position_id': position['id']
                })
            
            # Yield claims
            if position['claimed_yield_value'] and position['claimed_yield_value'] > 0:
                # Use entry date + estimated claim period (could be enhanced with actual claim dates)
                claim_date = self._estimate_claim_date(position['entry_date'], position.get('days_active'))
                transactions.append({
                    'date': claim_date,
                    'type': 'YIELD',
                    'position': position_name,
                    'platform': platform,
                    'strategy': position['strategy'],
                    'amount_usd': position['claimed_yield_value'],
                    'description': f"Yield claim from {position_name}",
                    'position_id': position['id']
                })
            
            # Transaction fees (negative transaction)
            if position['transaction_fees'] and position['entry_value']:
                fee_amount = position['entry_value'] * (position['transaction_fees'] / 100)
                transactions.append({
                    'date': self._parse_date(position['entry_date']),
                    'type': 'FEE',
                    'position': position_name,
                    'platform': platform,
                    'strategy': position['strategy'],
                    'amount_usd': -fee_amount,
                    'description': f"Transaction fees for {position_name}",
                    'position_id': position['id']
                })
            
            # Exit transaction (withdrawal)
            if position['exit_date'] and position['exit_value']:
                transactions.append({
                    'date': self._parse_date(position['exit_date']),
                    'type': 'WITHDRAWAL',
                    'position': position_name,
                    'platform': platform,
                    'strategy': position['strategy'],
                    'amount_usd': position['exit_value'],
                    'description': f"Exit from {position_name}",
                    'position_id': position['id']
                })
        
        # Sort by date (most recent first)
        return sorted(transactions, key=lambda x: x['date'], reverse=True)
    
    def _parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str or date_str == '':
            return datetime.now()
        
        try:
            # Try common date formats
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m/%d', '%Y-%m-%d %H:%M:%S']:
                try:
                    parsed = datetime.strptime(str(date_str), fmt)
                    # If no year provided, assume current year
                    if fmt == '%m/%d':
                        parsed = parsed.replace(year=datetime.now().year)
                    return parsed
                except ValueError:
                    continue
            
            # If parsing fails, return current date
            return datetime.now()
        except:
            return datetime.now()
    
    def _estimate_claim_date(self, entry_date, days_active):
        """Estimate yield claim date based on entry date and days active"""
        if not entry_date or not days_active:
            return self._parse_date(entry_date)
        
        entry_dt = self._parse_date(entry_date)
        # Estimate claim happened midway through position duration
        claim_dt = entry_dt + timedelta(days=days_active * 0.7)
        return claim_dt
    
    def _display_transaction_summary(self, transactions):
        """Display transaction summary statistics"""
        if not transactions:
            return
        
        # Calculate summary stats
        total_deposits = sum([t['amount_usd'] for t in transactions if t['type'] == 'DEPOSIT'])
        total_withdrawals = sum([t['amount_usd'] for t in transactions if t['type'] == 'WITHDRAWAL'])
        total_yields = sum([t['amount_usd'] for t in transactions if t['type'] == 'YIELD'])
        total_fees = sum([abs(t['amount_usd']) for t in transactions if t['type'] == 'FEE'])
        
        net_invested = total_deposits - total_withdrawals
        
        print(f"📊 TRANSACTION SUMMARY")
        print("-" * 60)
        print(f"💰 Total Deposits:    ${total_deposits:,.2f}")
        print(f"💸 Total Withdrawals: ${total_withdrawals:,.2f}")
        print(f"🏦 Net Invested:      ${net_invested:,.2f}")
        print(f"💎 Total Yields:      ${total_yields:,.2f}")
        print(f"💳 Total Fees:        ${total_fees:,.2f}")
        print(f"📈 Net Yield Return:  {(total_yields / total_deposits * 100) if total_deposits > 0 else 0:.2f}%")
        
        # Strategy breakdown
        long_txns = [t for t in transactions if t['strategy'] == 'long']
        neutral_txns = [t for t in transactions if t['strategy'] == 'neutral']
        
        print(f"\n📋 STRATEGY BREAKDOWN")
        print("-" * 60)
        print(f"📈 Long Strategy:     {len(long_txns)} transactions")
        print(f"⚖️  Neutral Strategy:  {len(neutral_txns)} transactions")
    
    def _display_transaction_table(self, transactions):
        """Display detailed transaction table"""
        print(f"\n📋 TRANSACTION HISTORY")
        print("-" * 120)
        print(f"{'Date':<12} {'Type':<12} {'Position':<20} {'Platform':<12} {'Strategy':<8} {'Amount':<12} {'Description':<30}")
        print("-" * 120)
        
        # Show most recent 20 transactions
        recent_transactions = transactions[:20]
        
        for txn in recent_transactions:
            date_str = txn['date'].strftime('%m/%d/%Y')
            
            # Format amount with color coding
            amount = txn['amount_usd']
            if txn['type'] == 'DEPOSIT':
                amount_str = f"+${amount:,.0f}"
                type_icon = "💰 DEPOSIT"
            elif txn['type'] == 'WITHDRAWAL':
                amount_str = f"+${amount:,.0f}"
                type_icon = "💸 WITHDRAW"
            elif txn['type'] == 'YIELD':
                amount_str = f"+${amount:,.0f}"
                type_icon = "💎 YIELD"
            elif txn['type'] == 'FEE':
                amount_str = f"-${abs(amount):,.0f}"
                type_icon = "💳 FEE"
            else:
                amount_str = f"${amount:,.0f}"
                type_icon = txn['type']
            
            strategy_icon = "📈 LONG" if txn['strategy'] == 'long' else "⚖️  NEUT"
            
            print(f"{date_str:<12} {type_icon:<12} {txn['position'][:18]:<20} "
                  f"{txn['platform'][:10]:<12} {strategy_icon:<8} {amount_str:<12} "
                  f"{txn['description'][:28]:<30}")
        
        if len(transactions) > 20:
            print(f"\n... and {len(transactions) - 20} more transactions")
    
    def _display_cash_flow_analysis(self, transactions):
        """Display cash flow analysis by time periods"""
        print(f"\n📈 CASH FLOW ANALYSIS")
        print("-" * 80)
        
        if not transactions:
            return
        
        # Group transactions by month
        monthly_flows = {}
        for txn in transactions:
            month_key = txn['date'].strftime('%Y-%m')
            
            if month_key not in monthly_flows:
                monthly_flows[month_key] = {
                    'deposits': 0,
                    'withdrawals': 0,
                    'yields': 0,
                    'fees': 0,
                    'net_flow': 0
                }
            
            if txn['type'] == 'DEPOSIT':
                monthly_flows[month_key]['deposits'] += txn['amount_usd']
                monthly_flows[month_key]['net_flow'] += txn['amount_usd']
            elif txn['type'] == 'WITHDRAWAL':
                monthly_flows[month_key]['withdrawals'] += txn['amount_usd']
                monthly_flows[month_key]['net_flow'] += txn['amount_usd']
            elif txn['type'] == 'YIELD':
                monthly_flows[month_key]['yields'] += txn['amount_usd']
                monthly_flows[month_key]['net_flow'] += txn['amount_usd']
            elif txn['type'] == 'FEE':
                monthly_flows[month_key]['fees'] += abs(txn['amount_usd'])
                monthly_flows[month_key]['net_flow'] -= abs(txn['amount_usd'])
        
        # Display monthly breakdown
        print(f"{'Month':<10} {'Deposits':<12} {'Withdrawals':<12} {'Yields':<10} {'Fees':<10} {'Net Flow':<12}")
        print("-" * 80)
        
        # Sort by month (most recent first)
        sorted_months = sorted(monthly_flows.keys(), reverse=True)[:6]  # Last 6 months
        
        for month in sorted_months:
            flows = monthly_flows[month]
            net_flow = flows['net_flow']
            net_flow_str = f"+${net_flow:,.0f}" if net_flow >= 0 else f"-${abs(net_flow):,.0f}"
            
            print(f"{month:<10} ${flows['deposits']:>10,.0f} ${flows['withdrawals']:>11,.0f} "
                  f"${flows['yields']:>8,.0f} ${flows['fees']:>8,.0f} {net_flow_str:>11}")
        
        # Platform breakdown
        print(f"\n🏢 CASH FLOW BY PLATFORM")
        print("-" * 60)
        
        platform_flows = {}
        for txn in transactions:
            platform = txn['platform']
            if platform not in platform_flows:
                platform_flows[platform] = {'total_flow': 0, 'yields': 0, 'count': 0}
            
            platform_flows[platform]['total_flow'] += txn['amount_usd']
            platform_flows[platform]['count'] += 1
            
            if txn['type'] == 'YIELD':
                platform_flows[platform]['yields'] += txn['amount_usd']
        
        # Sort platforms by total flow
        sorted_platforms = sorted(platform_flows.items(), 
                                key=lambda x: x[1]['total_flow'], reverse=True)
        
        print(f"{'Platform':<15} {'Total Flow':<12} {'Yields':<10} {'Transactions':<12}")
        print("-" * 60)
        
        for platform, flows in sorted_platforms:
            total_str = f"${flows['total_flow']:,.0f}"
            yields_str = f"${flows['yields']:,.0f}"
            
            print(f"{platform[:13]:<15} {total_str:>11} {yields_str:>9} {flows['count']:>11}")
        
        print("\n💡 Cash flow analysis helps identify your most productive platforms and strategies.")