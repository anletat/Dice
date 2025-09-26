import streamlit as st
import math
import pandas as pd
import io

# =========================
# Helper functions
# =========================
def fmt(value, dec=8):
    if value is None or math.isnan(value) or math.isinf(value):
        return "—"
    s = f"{value:.{dec}f}"
    s = s.rstrip("0").rstrip(".")
    return s

def fmt_prob(prob):
    if prob <= 0:
        return "0.00%"
    if prob >= 1:
        return "100.00%"
    return f"{prob*100:.8f}".rstrip("0").rstrip(".") + "%"

def human_odds(prob):
    if prob <= 0:
        return "—"
    val = 1 / prob
    if val >= 1e6:
        return f"1:{val/1e6:.3f}M"
    if val >= 1e3:
        return f"1:{val/1e3:.3f}K"
    return "1:" + fmt(val, 4)

def implied_chance(payout, house_edge):
    actual_payout = payout * (1 - house_edge / 100)
    if actual_payout <= 1e-12:
        return 0.0
    chance = 100.0 / actual_payout
    return max(min(chance, 100.0), 0.0)

def compute_L(balance, base_bet, multiplier):
    if base_bet <= 0:
        return 0
    if multiplier <= 1 + 1e-12:
        return math.floor(balance / base_bet)
    rhs = (balance * (multiplier - 1) / base_bet) + 1
    if rhs <= 1:
        return 0
    return max(0, math.floor(math.log(rhs) / math.log(multiplier)))

# =========================
# Streamlit app
# =========================
st.set_page_config(page_title="Dice / Limbo Martingale Calculator", layout="wide")
st.title("🎲 Dice / Limbo Martingale Calculator (Antebot-like)")

st.markdown("""
Công cụ tính toán chiến lược **Martingale** cho game Dice hoặc Limbo:
- Tính số lần thua liên tiếp tối đa (L).
- Hiển thị bảng chi tiết từng mức cược, tổng cược, lợi nhuận, xác suất.
- Xuất dữ liệu ra CSV.

⚠️ **Lưu ý:** Các con số chỉ mang tính tham khảo, bạn tự chịu trách nhiệm với vốn của mình.
""")

# === Input Layout ===
col1, col2 = st.columns(2)

with col1:
    balance = st.number_input("💰 Balance (Vốn)", value=0.00200000, format="%.8f")
    base_bet = st.number_input("🎯 Base Bet (Cược cơ bản)", value=0.00000001, format="%.8f")
    payout = st.number_input("💵 Payout (Thanh toán)", value=2.00, format="%.4f")
    house_edge = st.number_input("🏠 House Edge (%)", value=1.00, format="%.2f")
    sync = st.checkbox("🔗 Sync Chance with Payout (implied fair chance)", value=True,
                       help="Khi bật, Chance sẽ tự tính từ Payout và House Edge theo công thức implied fair chance.")

with col2:
    if sync:
        implied = implied_chance(payout, house_edge)
        chance = implied
        st.number_input("🎲 Chance (%)", value=chance, format="%.6f", disabled=True)
        st.caption(f"Implied chance = 100 / (payout × (1 - house_edge/100)) = {chance:.6f}%")
    else:
        chance = st.number_input("🎲 Chance (%)", value=49.5, format="%.6f")

    mult_type = st.selectbox("Đơn vị multiplier", ["%", "factor"], index=0)
    if mult_type == "%":
        mult_percent = st.number_input("📈 Increase on Loss (%)", value=100.0, format="%.2f")
        multiplier = 1 + mult_percent / 100
    else:
        multiplier = st.number_input("📈 Increase on Loss (factor)", value=2.00, format="%.2f")

    max_rows = st.number_input("Số dòng hiển thị (Max Rows)", value=30, step=1, min_value=1)

# === Calculation ===
p = chance / 100
q = 1 - p
L = compute_L(balance, base_bet, multiplier)
bust_prob = q ** (L + 1)

st.markdown("---")
st.subheader("📊 Kết quả")
st.write(f"""
Với **Balance** = {fmt(balance,8)}, **Base Bet** = {fmt(base_bet,8)}, **Chance** = {fmt(chance,6)}%, 
**Multiplier** = {fmt(multiplier,4)}:
- Bạn có thể chịu được **{L} lần thua liên tiếp** trước khi phá sản.
- Xác suất thua liên tiếp **{L+1} lần** (phá sản) ≈ **{bust_prob*100:.8f}%**
""")

# === Build Table ===
total_bet = 0.0
rows = []
for i in range(1, int(max_rows) + 1):
    bet = base_bet * (multiplier ** (i - 1))
    total_bet += bet
    profit = bet * (payout - 1)
    net_profit = profit - (total_bet - bet)
    prob = q ** i
    rows.append({
        "Loss": i,
        "Bet Amount": fmt(bet, 8),
        "Total Bet": fmt(total_bet, 8),
        "Profit": fmt(profit, 8),
        "Net Profit": fmt(net_profit, 8),
        "Probability": fmt_prob(prob),
        "Odds": human_odds(prob)
    })

df = pd.DataFrame(rows)

st.dataframe(df, use_container_width=True)

# === Export CSV ===
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)

st.download_button(
    label="📥 Export CSV",
    data=csv_buffer.getvalue(),
    file_name="martingale_calculator.csv",
    mime="text/csv",
)

st.markdown("---")
st.caption("© 2025 Dice/Limbo Martingale Calculator — Streamlit version")
