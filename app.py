import streamlit as st
import math

# ==========================
# HÀM TÍNH TOÁN MARTINGALE
# ==========================
def compute_martingale(balance, base_bet, payout, chance, multiplier, house_edge):
    p = chance / 100
    q = 1 - p
    actual_payout = payout * (1 - house_edge / 100)

    # Tính số lần thua liên tiếp tối đa (L)
    if multiplier <= 1:
        L = math.floor(balance / base_bet)
    else:
        RHS = (balance * (multiplier - 1) / base_bet) + 1
        L = math.floor(math.log(RHS) / math.log(multiplier))

    # Xác suất phá sản
    bust_prob = q ** (L + 1)

    # Lợi nhuận mỗi lần thắng
    profit_per_win = base_bet * (actual_payout - 1)

    return L, bust_prob, profit_per_win, actual_payout

# ==========================
# GIAO DIỆN STREAMLIT
# ==========================
st.set_page_config(page_title="Dice / Limbo Martingale Calculator", layout="wide")

st.title("🎲 Máy tính xác suất Dice / Limbo - Martingale")

st.markdown("""
Công cụ tính xác suất phá sản và số lần thua liên tiếp tối đa khi chơi **Dice hoặc Limbo** với chiến lược **Martingale**.

⚠️ *Các con số chỉ mang tính chất mô phỏng. Bạn tự chịu rủi ro khi áp dụng chiến lược này.*
""")

# --- Nhập thông số ---
col1, col2 = st.columns(2)

with col1:
    balance = st.number_input("💰 Balance (Vốn)", value=0.00200000, format="%.8f")
    base_bet = st.number_input("🎯 Base Bet (Cược cơ bản)", value=0.00000001, format="%.8f")
    payout = st.number_input("💵 Payout (Thanh toán)", value=2.00, format="%.2f")

with col2:
    chance = st.number_input("🎲 Chance (%)", value=49.5, format="%.2f")
    multiplier = st.number_input("📈 Loss Multiplier (Tăng khi thua)", value=2.00, format="%.2f")
    house_edge = st.number_input("🏠 House Edge (%)", value=1.00, format="%.2f")

# --- Nút tính toán ---
if st.button("Tính toán"):
    L, bust_prob, profit_per_win, actual_payout = compute_martingale(
        balance, base_bet, payout, chance, multiplier, house_edge
    )

    st.subheader("📊 Kết quả tính toán")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Số lần thua tối đa (L)", f"{L}")
    with col_res2:
        st.metric("Xác suất phá sản (%)", f"{bust_prob*100:.6f}")
    with col_res3:
        st.metric("Lợi nhuận mỗi lần thắng", f"{profit_per_win:.8f}")

    st.write("---")
    st.markdown(f"""
    ### 📝 Phân tích chi tiết
    - Balance = **{balance:.8f}**, Base Bet = **{base_bet:.8f}**
    - Chance = **{chance:.2f}%**, Loss Multiplier = **{multiplier:.2f}**
    - House Edge = **{house_edge:.2f}%**
    - Bạn có thể chịu được **{L} lần thua liên tiếp** trước khi bị phá sản.
    - Xác suất thua liên tiếp **{L+1} lần** (phá sản) ≈ **{bust_prob*100:.6f}%**
    - Payout thực tế (sau house edge) = **{actual_payout:.6f}**
    - Lợi nhuận mỗi lần thắng = **{profit_per_win:.8f}**
    """)

    st.info("⚠️ Lưu ý: Sòng có thể giới hạn mức cược tối đa, điều này làm tăng rủi ro phá sản.")

st.markdown("""
---
### 📐 Công thức
1. **Vốn cần để chịu L lần thua liên tiếp:**
   `Required(L) = base_bet * (multiplier^L - 1) / (multiplier - 1)`

2. **Xác suất phá sản:**
   `P_bust = q^(L+1)` trong đó `q = 1 - chance/100`

3. **Lợi nhuận mỗi lần thắng:**
   `Profit = base_bet * (payout - 1)`
""")

st.caption("© 2025 Dice/Limbo Martingale Calculator — Open Source Tool")
