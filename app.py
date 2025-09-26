# app.py (updated) — Streamlit Dice/Limbo Martingale Calculator
import streamlit as st
import math

def compute_martingale(balance, base_bet, payout, chance, multiplier, house_edge):
    p = chance / 100
    q = 1 - p
    actual_payout = payout * (1 - house_edge / 100)

    # Tính L
    if multiplier <= 1:
        L = math.floor(balance / base_bet)
    else:
        RHS = (balance * (multiplier - 1) / base_bet) + 1
        # guard against negative/zero
        if RHS <= 1:
            L = 0
        else:
            L = math.floor(math.log(RHS) / math.log(multiplier))

    bust_prob = q ** (L + 1)
    profit_per_win = base_bet * (actual_payout - 1)
    return L, bust_prob, profit_per_win, actual_payout

st.set_page_config(page_title="Dice / Limbo Martingale Calculator", layout="wide")
st.title("🎲 Máy tính xác suất Dice / Limbo - Martingale (with sync)")

st.markdown("""
Công cụ tính xác suất phá sản & chuỗi thua tối đa với tùy chọn **đồng bộ Chance ↔ Payout**.
- Bật `Sync chance with payout` để khi thay đổi Payout hoặc House Edge, Chance sẽ được cập nhật tự động theo công thức implied chance.
""")

# layout
col1, col2 = st.columns(2)

with col1:
    balance = st.number_input("💰 Balance (Vốn)", value=0.00200000, format="%.8f")
    base_bet = st.number_input("🎯 Base Bet (Cược cơ bản)", value=0.00000001, format="%.8f")
    payout = st.number_input("💵 Payout (Thanh toán)", value=2.00, format="%.4f")

with col2:
    # sync checkbox stored in session_state
    if 'sync' not in st.session_state:
        st.session_state.sync = True
    sync = st.checkbox("🔗 Sync chance with payout (implied fair chance)", value=st.session_state.sync,
                       help="When on, changing Payout or House Edge updates Chance to the implied fair value (1/actual_payout).")
    st.session_state.sync = sync

    house_edge = st.number_input("🏠 House Edge (%)", value=1.00, format="%.2f")
    multiplier = st.number_input("📈 Loss Multiplier (Tăng khi thua)", value=2.00, format="%.2f")

    # Compute implied chance if sync is on
    actual_payout = payout * (1 - house_edge / 100)
    if sync:
        if actual_payout > 1e-12:
            implied_chance = 100.0 / actual_payout
            # clamp implied_chance to (0,100]
            implied_chance = max(min(implied_chance, 100.0), 0.0000001)
        else:
            implied_chance = 0.0000001
        # Show chance as number_input but keep in sync (disabled editing while sync on)
        chance = st.number_input("🎲 Chance (%)", value=implied_chance, format="%.6f", disabled=True)
        st.caption(f"Implied chance = 100 / (payout * (1 - house_edge/100)) = {implied_chance:.6f}%")
    else:
        # not synced: let user edit chance freely
        chance = st.number_input("🎲 Chance (%)", value=49.5, format="%.6f")

# Calculate when button pressed
if st.button("Tính toán"):
    L, bust_prob, profit_per_win, actual_payout = compute_martingale(
        balance, base_bet, payout, chance, multiplier, house_edge
    )

    st.subheader("📊 Kết quả tính toán")
    c1, c2, c3 = st.columns(3)
    c1.metric("Số lần thua tối đa (L)", f"{L}")
    c2.metric("Xác suất phá sản (%)", f"{bust_prob*100:.6f}")
    c3.metric("Lợi nhuận mỗi lần thắng", f"{profit_per_win:.8f}")

    st.write("---")
    st.markdown(f"""
    - Balance = **{balance:.8f}**, Base Bet = **{base_bet:.8f}**  
    - Chance = **{chance:.6f}%**, Payout = **{payout:.4f}**, House Edge = **{house_edge:.2f}%**  
    - Loss Multiplier = **{multiplier:.2f}**  
    - Payout sau house edge = **{actual_payout:.6f}**  
    - Bạn có thể chịu được **{L} lần thua liên tiếp** trước khi phá sản.  
    - Xác suất thua liên tiếp **{L+1} lần** (phá sản) ≈ **{bust_prob*100:.6f}%**
    """)

st.markdown("---")
st.caption("© 2025 Dice/Limbo Martingale Calculator — Updated")
