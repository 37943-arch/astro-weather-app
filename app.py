import requests
from datetime import datetime
import streamlit as st

# ตั้งค่าหน้าตาเว็บเบื้องต้น
st.set_page_config(page_title="AstroDash - ทั้งหมดเพื่อนักถ่ายภาพดาว", page_icon="🌌", layout="wide")

OPENWEATHER_API_KEY = "65cc3da47f993885606cea0b0fea7806"
WEATHERAPI_KEY = "6bc2e846b436449d9a465303262002"

# --- ฟังก์ชันดึงข้อมูลพยากรณ์อากาศ ---
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

def get_moon_phase(lat, lon, date):
    url = f"http://api.weatherapi.com/v1/astronomy.json?key={WEATHERAPI_KEY}&q={lat},{lon}&dt={date}"
    response = requests.get(url)
    return response.json()

# --- แถบเมนูด้านซ้าย (Sidebar) ---
st.sidebar.title("🪐 AstroDash Menu")
page = st.sidebar.radio("เลือกฟีเจอร์ที่ต้องการใช้งาน:", [
    "🌤️ พยากรณ์อากาศ & Astro Score", 
    "📷 คำนวณความเร็วชัตเตอร์ (500 Rule)", 
    "🎯 วัตถุท้องฟ้าเด่น & สมุดบันทึก"
])

st.sidebar.divider()
st.sidebar.caption("พัฒนาขึ้นเพื่อนักถ่ายภาพดาราศาสตร์ไทย 🇹🇭")

# ==========================================
# หน้าที่ 1: พยากรณ์อากาศ & Astro Score (เวอร์ชันมีแผนที่ + จุดแนะนำยอดนิยม)
# ==========================================ฆ
if page == "🌤️ พยากรณ์อากาศ & Astro Score":
    import folium
    from streamlit_folium import st_folium

    st.title("🌌 Astro Weather & Score Calculator")
    st.write("คลิกเลือกจุดแนะนำ หรือจิ้มเลือกจุดบนแผนที่เองเพื่อคำนวณสภาพอากาศ")
    st.divider()

    # 1. นิยามจุดถ่ายรูปดาวยอดนิยมในไทย (ชื่อ: [lat, lon, ซูม])
    hotspots = {
        "📍 กรุงเทพฯ (เริ่มต้น)": [13.7563, 100.5018, 6],
        "🏔️ ยอดดอยอินทนนท์ (เชียงใหม่)": [18.5882, 98.4871, 12],
        "⛰️ ผาแต้ม (อุบลราชธานี)": [15.3986, 105.5083, 12],
        "🏕️ อุทยานแห่งชาติแก่งกระจาน (เพชรบุรี)": [12.8711, 99.3621, 11],
        "🐄 เขายายเที่ยง (นครราชสีมา)": [14.8317, 101.5544, 12]
    }

    # สร้างปุ่มทางลัดด้านบนแผนที่
    st.write("✨ **ทางลัด: เลือกจุดถ่ายดาวยอดนิยมในไทย**")
    selected_hotspot = st.selectbox("เลือกสถานที่แนะนำ:", list(hotspots.keys()))

    # ดึงค่าพิกัดเริ่มต้นจากสถานที่ที่เลือกในข้อแกะ (ถ้ากดเลือกพิกัดจะเปลี่ยนทันที)
    default_lat = hotspots[selected_hotspot][0]
    default_lon = hotspots[selected_hotspot][1]
    default_zoom = hotspots[selected_hotspot][2]

    # 2. สร้างแผนที่และปักหมุดสีแดงไว้ตรงจุดแนะนำ
    m = folium.Map(location=[default_lat, default_lon], zoom_start=default_zoom)
    
    # ใส่หมุดบอกตำแหน่งสถานที่แนะนำให้เห็นเด่นชัด
    folium.Marker(
        [default_lat, default_lon], 
        popup=selected_hotspot, 
        tooltip="จุดที่เลือก",
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)
    
    m.add_child(folium.LatLngPopup())

    # แสดงผลแผนที่
    st.subheader("🗺️ แผนที่พิกัดถ่ายภาพ")
    map_output = st_folium(m, width=800, height=400, key=f"map_{selected_hotspot}")

    # 3. ตรวจสอบว่าผู้ใช้จิ้มจุดอื่นบนแผนที่เพื่อเปลี่ยนใจไหม
    lat_value = default_lat
    lon_value = default_lon

    if map_output and map_output.get("last_clicked"):
        lat_value = map_output["last_clicked"]["lat"]
        lon_value = map_output["last_clicked"]["lng"]

    # กล่องแสดงตัวเลขพิกัดสุดท้ายที่จะนำไปคำนวณ
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude (ละติจูด):", value=lat_value, format="%.4f")
    with col2:
        lon = st.number_input("Longitude (ลองจิจูด):", value=lon_value, format="%.4f")

    # ส่วนประมวลผลวันเวลา
    date_input_obj = st.date_input("เลือกวันที่ต้องการออกทริป:", datetime.today())
    date_input = date_input_obj.strftime("%Y-%m-%d")

    # ปุ่มคำนวณ (ใช้สูตรคิดคะแนนและดึง API จากโครงเดิมของคุณทั้งหมด)
    if st.button("🔮 คำนวณคะแนนสภาพดาวจากจุดนี้", type="primary"):
        with st.spinner('กำลังดึงข้อมูลสภาพอากาศ...'):
            try:
                weather_data = get_weather(lat, lon)
                moon_data = get_moon_phase(lat, lon, date_input)
                
                score = 0
                forecast_list = weather_data.get("list", [])
                selected_forecast = None

                for item in forecast_list:
                    if date_input in item["dt_txt"] and "21:00:00" in item["dt_txt"]:
                        selected_forecast = item
                        break

                if not selected_forecast:
                    st.error("❌ ไม่พบข้อมูลสภาพอากาศพยากรณ์สำหรับช่วงเวลา 21:00 น. ของวันที่ระบุ")
                else:
                    cloud = selected_forecast["clouds"]["all"]
                    humidity = selected_forecast["main"]["humidity"]
                    wind = selected_forecast["wind"]["speed"] * 3.6
                    visibility = selected_forecast.get("visibility", 0) / 1000
                    moon_illumination = int(moon_data["astronomy"]["astro"]["moon_illumination"])

                    st.subheader("📊 ข้อมูลสภาพอากาศคืนนี้ (เวลา 21:00 น.)")
                    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
                    m_col1.metric("☁️ เมฆ", f"{cloud}%")
                    m_col2.metric("💧 ความชื้น", f"{humidity}%")
                    m_col3.metric("💨 ลม", f"{wind:.1f} km/h")
                    m_col4.metric("👁️ การมองเห็น", f"{visibility} km")
                    m_col5.metric("🌙 แสงจันทร์", f"{moon_illumination}%")

                    if cloud < 20: score += 30
                    if humidity < 60: score += 20
                    if wind < 15: score += 15
                    if moon_illumination < 30: score += 25
                    if visibility > 8: score += 10

                    st.divider()
                    st.markdown(f"### 🌌 Astro Score ของจุดนี้: **{score}/100**")
                    
                    if score > 70:
                        st.success("⭐ ท้องฟ้าดีเยี่ยม! จุดนี้เหมาะสำหรับตั้งกล้องล่าทางช้างเผือกมาก")
                    elif score > 40:
                        st.warning("🌙 สภาพอากาศพอใช้ได้ แต่อาจมีเมฆหรือน้ำค้างกวนใจ")
                    else:
                        st.error("☁️ ท้องฟ้าปิดหรืออุปสรรคเยอะเกินไป เลี่ยงจุดนี้หรือเปลี่ยนวันดีกว่า")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

# ==========================================
# หน้าที่ 2: คำนวณความเร็วชัตเตอร์ (500 Rule)
# ==========================================
elif page == "📷 คำนวณความเร็วชัตเตอร์ (500 Rule)":
    st.title("📷 Shutter Speed Calculator for Astrophotography")
    st.write("คำนวณระยะเวลาเปิดหน้ากล้องที่นานที่สุด เพื่อไม่ให้ดาวยืดเป็นเส้น (Star Trails)")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        focal_length = st.number_input("ระยะเลนส์ ทางยาวโฟกัส (mm):", value=24, min_value=1)
    with c2:
        sensor_type = st.selectbox("ประเภทเซนเซอร์ของกล้อง (Sensor Size):", [
            "Full-frame (คูณ 1.0)",
            "APS-C Canon (คูณ 1.6)",
            "APS-C Nikon/Sony/Fuji (คูณ 1.5)",
            "Micro Four Thirds (คูณ 2.0)"
        ])

    # กำหนดค่าตัวคูณเซนเซอร์
    crop_factor = 1.0
    if "Canon" in sensor_type: crop_factor = 1.6
    elif "Nikon" in sensor_type: crop_factor = 1.5
    elif "Micro" in sensor_type: crop_factor = 2.0

    # คำนวณสูตร 500 Rule
    effective_focal_length = focal_length * crop_factor
    shutter_500 = 500 / effective_focal_length

    st.subheader("💡 ผลการคำนวณที่แนะนำ")
    st.info(f"ทางยาวโฟกัสเทียบเท่า Full-frame คือ: **{effective_focal_length:.1f} mm**")
    
    st.metric(label="⏱️ ชัตเตอร์นานที่สุดที่ยอมรับได้ (สูตร 500 Rule)", value=f"{shutter_500:.2f} วินาที")
    
    st.warning("⚠️ **ข้อแนะนำเพิ่มเติม:** สำหรับกล้องยุคใหม่ที่มีความละเอียดพิกเซลสูง แนะนำให้ลดเวลาลงจากผลลัพธ์นี้อีกประมาณ 15-20% (หรือใช้สูตร NPF) เพื่อให้จุดดาวคมชัดที่สุดเมื่อซูมดูภาพครับ")

# ==========================================
# หน้าที่ 3: วัตถุท้องฟ้าเด่น & สมุดบันทึก
# ==========================================
elif page == "🎯 วัตถุท้องฟ้าเด่น & สมุดบันทึก":
    st.title("🎯 Target Planner & Astro Diary")
    st.write("แนะนำวัตถุที่น่าสนใจและพื้นที่บันทึกประวัติตำแหน่งถ่ายภาพดาวของคุณ")
    st.divider()

    # ส่วนแนะนำเทรนด์วัตถุท้องฟ้าตามช่วงเวลา
    st.subheader("🔭 วัตถุท้องฟ้ายอดนิยมประจำฤดูกาล")
    targets = {
        "ใจกลางทางช้างเผือก (Milky Way Core)": "ช่วงที่สังเกตได้ดีที่สุดในไทยคือ เดือนมีนาคม - ตุลาคม (จะขึ้นเร็วในหน้าฝนและหน้าหนาวช่วงหัวค่ำ)",
        "กาแล็กซีแอนโดรเมดา (Andromeda Galaxy - M31)": "ช่วงปลายฝนต้นหนาว (ตุลาคม - มกราคม) จะลอยสูงกลางฟ้า ถ่ายง่ายมาก",
        "เนบิวลาโอไรออน (Orion Nebula - M42)": "ช่วงฤดูหนาว (ธันวาคม - มีนาคม) มองเห็นชัดเจนด้วยตาเปล่าบริเวณกลุ่มดาวนายพราน",
        "กระจุกดาวลูกไก่ (Pleiades - M45)": "ขึ้นเคียงคู่กับเนบิวลาโอไรออนในช่วงฤดูหนาว เหมาะสำหรับเลนส์ระยะเทเลโพโต้"
    }
    
    for target, desc in targets.items():
        with st.expander(f"✨ {target}"):
            st.write(desc)

    st.divider()

    # ส่วนสมุดบันทึกประวัติ (Astro Logbook)
    st.subheader("📝 สมุดบันทึกทริปถ่ายดาวส่วนตัว")
    st.write("พิมพ์บันทึกรายละเอียดทริปของคุณ แล้วกดปุ่มบันทึกเพื่อเก็บไว้ดูภายหลังได้")

    log_location = st.text_input("สถานที่ถ่ายภาพ:", placeholder="เช่น ดอยอินทนนท์, เขายายเที่ยง")
    log_notes = st.text_area("บันทึกความทรงจำ / อุปกรณ์ที่ใช้ / ปัญหาที่พบ:", placeholder="เช่น ฟ้าใสมาก เมฆน้อย ลมแรงจนขาตั้งสั่น ใช้เลนส์ 14mm f/2.8...")
    
    if st.button("💾 บันทึกไดอารี่"):
        if log_location and log_notes:
            st.success(f"บันทึกข้อมูลทริป '{log_location}' เรียบร้อยแล้วเมื่อ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            # จำลองการโชว์สิ่งที่เรากดบันทึก
            st.write("---")
            st.markdown(f"**📌 ประวัติที่บันทึกไว้ล่าสุด:**")
            st.caption(f"สถานที่: {log_location} | บันทึก: {log_notes}")
        else:
            st.error("กรุณากรอกข้อมูลสถานที่และรายละเอียดก่อนกดบันทึกนะครับ")