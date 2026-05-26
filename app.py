import streamlit as st
import pandas as pd
import datetime

# إعدادات الصفحة لتكون متجاوبة ومريحة
st.set_page_config(page_title="تتبع صلوات القضاء والفوائت", layout="wide")

# --- 1. إدارة جلسة المستخدم (لتكون البيانات مستقلة وخاصة بكل زائر) ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Magdi"

if 'years_missed' not in st.session_state:
    st.session_state.years_missed = 10

# إنشاء جدول الصلوات الافتراضي للمستخدم الجديد (يبدأ من الصفر ليكون مناسباً للجميع)
if 'prayer_table' not in st.session_state:
    st.session_state.prayer_table = pd.DataFrame({
        'Prayer': ['Fagr', 'Duhr', 'Asr', 'Maghrib', 'Isha'],
        'Fin': [0, 0, 0, 0, 0],  # يبدأ من الصفر ويستطيع المستخدم تعديله من الإعدادات
        'Total': [10 * 365] * 5
    })

if 'tracker_table' not in st.session_state:
    st.session_state.tracker_table = pd.DataFrame(columns=['Date', 'Prayer'])

# --- 2. لوحة التحكم الجانبية (الإعدادات والتصحيح لكل مستخدم) ---
with st.sidebar:
    st.header("⚙️ إعداداتك الخاصة")
    st.write("قم بتخصيص التطبيق ليناسب حساباتك الشخصية:")
    
    # إدخال الاسم الشخصي
    custom_name = st.text_input("اسمك الكريم (يظهر في العنوان):", value=st.session_state.user_name)
    if custom_name != st.session_state.user_name:
        st.session_state.user_name = custom_name
        st.rerun()
        
    # إدخال عدد سنوات التفريط
    years_input = st.number_input("عدد سنوات الفوائت الإجمالية:", min_value=1, max_value=100, value=st.session_state.years_missed)
    if years_input != st.session_state.years_missed:
        st.session_state.years_missed = years_input
        st.session_state.prayer_table['Total'] = years_input * 365
        st.rerun()
        
    st.markdown("---")
    st.subheader("🛠️ لوحة التصحيح وإدخال البيانات")
    st.write("إذا كنت قد قضيت صلوات سابقاً قبل استخدام التطبيق، أدخلها هنا ليتم خصمها تلقائياً:")
    
    # مكنّا المستخدم من تعديل المنجز السابق يدويًا لكل فرض
    for index, row in st.session_state.prayer_table.iterrows():
        new_fin = st.number_input(f"ما تم قضاؤه سابقاً لـ {row['Prayer']}:", min_value=0, max_value=int(row['Total']), value=int(row['Fin']), key=f"edit_{row['Prayer']}")
        if new_fin != row['Fin']:
            st.session_state.prayer_table.at[index, 'Fin'] = new_fin
            st.rerun()

# --- 3. العمليات الحسابية والمعادلات ---
df = st.session_state.prayer_table.copy()
df['Left'] = df['Total'] - df['Fin']  # المتبقي تلقائياً لكل فرض

sum_finished = df['Fin'].sum()
days_finished = int(sum_finished / 5)
today_str = str(datetime.date.today())
total_prayed_today = len(st.session_state.tracker_table[st.session_state.tracker_table['Date'] == today_str])
sum_needed = df['Left'].sum()

# حساب السنوات المتبقية بمعدل 5 صلوات في اليوم
years_to_finish_5_daily = round((sum_needed / 5) / 365, 2) if sum_needed > 0 else 0

# حساب السنوات بناءً على الصفحة الحالية (معدل إنجازك الفعلي مقارنة بما فاتك)
if sum_finished > 0:
    years_to_finish_by_current_page = round((sum_needed / sum_finished) * (sum_finished / (5 * 365)), 2)
    # حماية القيمة من الهبوط غير المنطقي
    if years_to_finish_by_current_page == 0 and sum_needed > 0:
        years_to_finish_by_current_page = round((sum_needed / 5) / 365, 2)
else:
    years_to_finish_by_current_page = st.session_state.years_missed

# --- 4. عرض واجهة المستخدم الرئيسية ---
st.title(f"🧔 {st.session_state.user_name} Prayer")

# عرض الإحصائيات الستة الكبرى المطلوبة
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Sum of Finished (إجمالي المنجز):** {sum_finished}")
    st.markdown(f"**Days Finished (الأيام المنتهية):** {days_finished}")
with col2:
    st.markdown(f"**Total Prayed Today (صليت اليوم):** {total_prayed_today}")
    st.markdown(f"**Sum of Needed (إجمالي المتبقي):** {sum_needed:,}")
with col3:
    st.markdown(f"**Years to finish by 5 prayers a day:** {years_to_finish_5_daily} سنة")
    st.markdown(f"**Years to finish by current page:** {years_to_finish_by_current_page} سنة")

st.markdown("---")

# عرض جدول الصلوات الرئيسي (Magdi Prayer Table)
st.subheader(f"📋 {st.session_state.user_name} Prayer Table")

cols_header = st.columns([2, 1, 1, 1, 2, 1, 1])
cols_header[0].markdown("**Prayer (الفرض)**")
cols_header[1].markdown("**Done (اضغط عند الصلاة)**")
cols_header[2].markdown("**Now (اليوم)**")
cols_header[3].markdown("**Fin (المنجز)**")
cols_header[4].markdown("**Left (المتبقي)**")
cols_header[5].markdown("**Total (المطلوب)**")
cols_header[6].markdown("**Years (السنين)**")

for index, row in df.iterrows():
    col_p, col_btn, col_now, col_fin, col_left, col_tot, col_yrs = st.columns([2, 1, 1, 1, 2, 1, 1])
    
    col_p.write(f"**{row['Prayer']}**")
    
    # زر الإضافة التفاعلي الأخضر (✓ D) لتسجيل فرض تم صلاته الآن
    if col_btn.button(f"✓ D", key=f"btn_{row['Prayer']}"):
        st.session_state.prayer_table.at[index, 'Fin'] += 1
        new_track = pd.DataFrame({'Date': [today_str], 'Prayer': [row['Prayer']]})
        st.session_state.tracker_table = pd.concat([st.session_state.tracker_table, new_track], ignore_index=True)
        st.rerun()
        
    # حساب الصلوات المسجلة اليوم الفعلي
    now_count = len(st.session_state.tracker_table[(st.session_state.tracker_table['Date'] == today_str) & (st.session_state.tracker_table['Prayer'] == row['Prayer'])])
    
    col_now.write(f"{now_count}")
    col_fin.write(f"{row['Fin']}")
    col_left.write(f"{row['Left']:,}")
    col_tot.write(f"{row['Total']:,}")
    col_yrs.write(f"{st.session_state.years_missed}")

st.markdown("---")

# 5. جدول التتبع السفلي الخاص بالمستخدم الحالي
st.subheader("⏱️ سجل صلوات اليوم الشخصي (Prayer Tracker)")
if not st.session_state.tracker_table.empty:
    st.dataframe(st.session_state.tracker_table.iloc[::-1], use_container_width=True)
else:
    st.info("لم تقم بتسجيل أي فروض لليوم بعد. اضغط على زر ✓ D بالجدول عند قضاء أي صلاة.")
