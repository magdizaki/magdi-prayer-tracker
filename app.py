import streamlit as st
import pandas as pd
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="تتبع صلوات القضاء والفوائت الذكي", layout="wide")

st.markdown('<link rel="manifest" href="./manifest.json">', unsafe_allow_html=True)

# --- 1. إدارة جلسة المستخدم (بيانات مستقلة لكل زائر) ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Magdi"

if 'years_missed' not in st.session_state:
    st.session_state.years_missed = 10

if 'target_years' not in st.session_state:
    st.session_state.target_years = 5  # الخطة الافتراضية لإنجاز الفوائت

if 'prayer_table' not in st.session_state:
    st.session_state.prayer_table = pd.DataFrame({
        'Prayer': ['Fagr', 'Duhr', 'Asr', 'Maghrib', 'Isha'],
        'Fin': [0, 0, 0, 0, 0],
        'Total': [10 * 365] * 5
    })

if 'tracker_table' not in st.session_state:
    st.session_state.tracker_table = pd.DataFrame(columns=['Date', 'Prayer'])

# --- 2. لوحة التحكم الجانبية (الإعدادات وتصميم الخطة) ---
with st.sidebar:
    st.header("⚙️ إعداداتك وخطتك الشخصية")
    
    # إدخال الاسم
    custom_name = st.text_input("اسمك الكريم:", value=st.session_state.user_name)
    if custom_name != st.session_state.user_name:
        st.session_state.user_name = custom_name
        st.rerun()
        
    # [الخطوة 1] إدخال سنوات الفوائت
    years_input = st.number_input("1. عدد سنوات الفوائت الكلية:", min_value=1, max_value=100, value=st.session_state.years_missed)
    if years_input != st.session_state.years_missed:
        st.session_state.years_missed = years_input
        st.session_state.prayer_table['Total'] = years_input * 365
        st.rerun()
        
    # [الخطوة 2] إدخال الخطة المستهدفة للإنجاز
    target_input = st.number_input("2. تريد إنجازها خلال كم سنة؟", min_value=1, max_value=100, value=st.session_state.target_years)
    if target_input != st.session_state.target_years:
        st.session_state.target_years = target_input
        st.rerun()
        
    st.markdown("---")
    st.subheader("🛠️ إدخال صلوات سابقة (إن وُجدت)")
    for index, row in st.session_state.prayer_table.iterrows():
        new_fin = st.number_input(f"ما تم قضاؤه سابقاً لـ {row['Prayer']}:", min_value=0, max_value=int(row['Total']), value=int(row['Fin']), key=f"edit_{row['Prayer']}")
        if new_fin != row['Fin']:
            st.session_state.prayer_table.at[index, 'Fin'] = new_fin
            st.rerun()

# --- 3. العمليات الحسابية والمعادلات الذكية ---
df = st.session_state.prayer_table.copy()
df['Left'] = df['Total'] - df['Fin']

sum_finished = df['Fin'].sum()
days_finished = int(sum_finished / 5)
today_str = str(datetime.date.today())
total_prayed_today = len(st.session_state.tracker_table[st.session_state.tracker_table['Date'] == today_str])
sum_needed = df['Left'].sum()

# حساب كم فرض مطلوب يومياً بناءً على خطة المستخدم
# المعادلة: (عدد سنوات الفوائت / عدد سنوات الخطة) -> للحصول على عدد الفروض يومياً
prayers_needed_per_day_each = round(st.session_state.years_missed / st.session_state.target_years, 1)
total_daily_target_all_prayers = prayers_needed_per_day_each * 5

# الحسابات الكودا (Coda) الأصلية المتواجدة بالصور
years_to_finish_5_daily = round((sum_needed / 5) / 365, 2) if sum_needed > 0 else 0
if sum_finished > 0:
    years_to_finish_by_current_page = round((sum_needed / sum_finished) * (sum_finished / (5 * 365)), 2)
    if years_to_finish_by_current_page == 0 and sum_needed > 0:
        years_to_finish_by_current_page = round((sum_needed / 5) / 365, 2)
else:
    years_to_finish_by_current_page = st.session_state.years_missed

# --- 4. عرض واجهة المستخدم الرئيسية ---
st.title(f"🧔 {st.session_state.user_name} Prayer Tracker")

# صندوق معلومات الخطة المستهدفة
st.info(f"💡 **خطتك الحالية:** قضاء فوائت **{st.session_state.years_missed} سنوات** خلال **{st.session_state.target_years} سنوات** وعليك قضاء **[{prayers_needed_per_day_each}] فرض يومياً** من كل صلاة لتلتزم بالخطة.")

# عرض الإحصائيات الستة الكبرى
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Sum of Finished:** {sum_finished}")
    st.markdown(f"**Days Finished:** {days_finished}")
with col2:
    st.markdown(f"**Total Prayed Today:** {total_prayed_today} / {int(total_daily_target_all_prayers)} فرض")
    st.markdown(f"**Sum of Needed:** {sum_needed:,}")
with col3:
    st.markdown(f"**Years to finish by 5 prayers a day:** {years_to_finish_5_daily} سنة")
    st.markdown(f"**Years to finish by current page:** {years_to_finish_by_current_page} سنة")

st.markdown("---")

# عرض جدول الصلوات الرئيسي
st.subheader(f"📋 جدول تتبع الصلوات")

cols_header = st.columns([2, 1, 1, 1, 1, 2, 1, 1])
cols_header[0].markdown("**Prayer**")
cols_header[1].markdown("**Done**")
cols_header[2].markdown("**Now (اليوم)**")
cols_header[3].markdown("**Target (الهدف اليومي)**")
cols_header[4].markdown("**Fin**")
cols_header[5].markdown("**Left**")
cols_header[6].markdown("**Total**")
cols_header[7].markdown("**Years**")

for index, row in df.iterrows():
    col_p, col_btn, col_now, col_target, col_fin, col_left, col_tot, col_yrs = st.columns([2, 1, 1, 1, 1, 2, 1, 1])
    
    col_p.write(f"**{row['Prayer']}**")
    
    # زر الإضافة التفاعلي الأخضر (✓ D)
    if col_btn.button(f"✓ D", key=f"btn_{row['Prayer']}"):
        st.session_state.prayer_table.at[index, 'Fin'] += 1
        new_track = pd.DataFrame({'Date': [today_str], 'Prayer': [row['Prayer']]})
        st.session_state.tracker_table = pd.concat([st.session_state.tracker_table, new_track], ignore_index=True)
        st.rerun()
        
    # حساب الصلوات المسجلة اليوم
    now_count = len(st.session_state.tracker_table[(st.session_state.tracker_table['Date'] == today_str) & (st.session_state.tracker_table['Prayer'] == row['Prayer'])])
    
    # تلوين خانة اليوم لتشجيع المستخدم إذا حقق هدفه اليومي
    if now_count >= prayers_needed_per_day_each:
        col_now.write(f"🟢 {now_count}")
    else:
        col_now.write(f"⚪ {now_count}")
        
    col_target.write(f"🎯 {prayers_needed_per_day_each}")
    col_fin.write(f"{row['Fin']}")
    col_left.write(f"{row['Left']:,}")
    col_tot.write(f"{row['Total']:,}")
    col_yrs.write(f"{st.session_state.years_missed}")

st.markdown("---")

# 5. سجل صلوات اليوم الشخصي
st.subheader("⏱️ سجل صلوات اليوم الشخصي")
if not st.session_state.tracker_table.empty:
    st.dataframe(st.session_state.tracker_table.iloc[::-1], use_container_width=True)
else:
    st.info("لم تقم بتسجيل أي فروض لليوم بعد.")
