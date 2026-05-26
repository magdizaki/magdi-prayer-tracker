import streamlit as st
import pandas as pd
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="تتبع صلوات والقضاء", layout="wide")

# 1. تهيئة البيانات وتخزينها في ذاكرة الجلسة (Session State) حتى لا تضيع عند التحديث
if 'years_missed' not in st.session_state:
    st.session_state.years_missed = 10  # القيمة الافتراضية 10 سنوات كما في الصور

# حساب الإجمالي لكل فرض (عدد السنوات * 365 يوم)
total_per_prayer = st.session_state.years_missed * 365

# إنشاء جدول الصلوات الرئيسي إذا لم يكن موجوداً
if 'prayer_table' not in st.session_state:
    st.session_state.prayer_table = pd.DataFrame({
        'Prayer': ['Fagr', 'Duhr', 'Asr', 'Maghrib', 'Isha'],
        'Fin': [0, 0, 0, 0, 0], # الصلوات المنجزة
        'Total': [total_per_prayer] * 5
    })

# إنشاء جدول التتبع اليومي (Tracker) لتسجيل كل نقرة بزر
if 'tracker_table' not in st.session_state:
    st.session_state.tracker_table = pd.DataFrame(columns=['Date', 'Prayer'])

# --- واجهة المستخدم ---
st.title("🧔 Magdi Prayer - صلاة المغدي والقضاء")

# قسم إدخال عدد السنوات المطلوبة
with st.sidebar:
    st.header("⚙️ الإعدادات")
    years_input = st.number_input("عدد سنوات الفوائت:", min_value=1, max_value=100, value=st.session_state.years_missed)
    
    # إذا قام المستخدم بتغيير عدد السنوات، يتم تحديث الجدول
    if years_input != st.session_state.years_missed:
        st.session_state.years_missed = years_input
        total_per_prayer = years_input * 365
        st.session_state.prayer_table['Total'] = total_per_prayer
        # إعادة حساب المتبقي تلقائياً
        st.rerun()

# 2. الحسابات الإجمالية (المعادلات أعلى الصور)
df = st.session_state.prayer_table.copy()
df['Left'] = df['Total'] - df['Fin'] # المتبقي

sum_finished = df['Fin'].sum()
sum_needed = df['Left'].sum()
total_prayed_today = len(st.session_state.tracker_table[st.session_state.tracker_table['Date'] == str(datetime.date.today())])

# حساب السنين المتبقية بناءً على معدل 5 صلوات في اليوم
years_to_finish_5_daily = round((sum_needed / 5) / 365, 2) if sum_needed > 0 else 0

# عرض الإحصائيات العلوية
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("إجمالي المنجز (Sum of Finished)", f"{sum_finished} صلاة")
col_m2.metric("المتبقي الكلي (Sum of Needed)", f"{sum_needed} صلاة")
col_m3.metric("صلوات اليوم (Today)", f"{total_prayed_today}")
col_m4.metric("سنوات الانتهاء بمعدل 5 يومياً", f"{years_to_finish_5_daily} سنة")

st.markdown("---")

# 3. عرض جدول الصلوات مع أزرار الإضافة (مثل أزرار الداتا بيز في الصور)
st.subheader("📊 جدول الصلوات الرئيسي")

# عرض العناوين لتشبه الجدول
cols_header = st.columns([2, 2, 2, 2, 2])
cols_header[0].markdown("**الفرض (Prayer)**")
cols_header[1].markdown("**إضافة صلاة**")
cols_header[2].markdown("**المنجز (Fin)**")
cols_header[3].markdown("**المتبقي (Left)**")
cols_header[4].markdown("**الإجمالي المطلوب (Total)**")

# بناء صفوف الجدول ديناميكياً
for index, row in df.iterrows():
    col_p, col_btn, col_fin, col_left, col_tot = st.columns([2, 2, 2, 2, 2])
    
    col_p.write(f"**{row['Prayer']}**")
    
    # زر الإضافة المماثل لـ (RunActions / AddRow) في صورتك الأخيرة
    if col_btn.button(f"✓ D", key=f"btn_{row['Prayer']}"):
        # 1. زيادة المنجز بمقدار 1
        st.session_state.prayer_table.at[index, 'Fin'] += 1
        
        # 2. تسجيل العملية في جدول الـ Tracker بالتاريخ الحالي
        today_str = str(datetime.date.today())
        new_track = pd.DataFrame({'Date': [today_str], 'Prayer': [row['Prayer']]})
        st.session_state.tracker_table = pd.concat([st.session_state.tracker_table, new_track], ignore_index=True)
        
        # تحديث الصفحة لعرض الأرقام الجديدة
        st.rerun()
        
    col_fin.write(f"{row['Fin']}")
    col_left.write(f"{row['Left']}")
    col_tot.write(f"{row['Total']}")

st.markdown("---")

# 4. جدول التتبع اليومي (Prayer Magdi Tracker) كما في الصورة الثانية
st.subheader("📑 سجل التتبع اليومي (Prayer Magdi Tracker)")
if not st.session_state.tracker_table.empty:
    # عرض آخر 10 صلوات تم تسجيلها بترتيب أحدثها أولاً
    st.dataframe(st.session_state.tracker_table.iloc[::-1].head(10), use_container_width=True)
else:
    st.info("لم تقم بتسجيل أي صلوات اليوم بعد. اضغط على زر ✓ D بالأعلى لبدء التسجيل.")
