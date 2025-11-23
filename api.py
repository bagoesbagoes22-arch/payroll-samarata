import streamlit as st
from datetime import datetime, time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Payroll Samarata", page_icon="🍗")

st.title("🍗 Payroll Kedai Samarata")
st.caption("Sistem Gaji & Lembur Otomatis")

# --- KONSTANTA ---
GAJI_POKOK = 50000
RATE_LEMBUR_PER_JAM = 10000

# --- LIST JAM & MENIT (Untuk Dropdown) ---
# Kita buat list angka string "00" sampai "23" dan "00" sampai "59"
list_jam = [f"{i:02d}" for i in range(24)]   # ["00", "01", ... "23"]
list_menit = [f"{i:02d}" for i in range(60)] # ["00", "01", ... "59"]

# --- INPUT DATA ---
st.divider()

data_mingguan = {}
hari_kerja = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]

for hari in hari_kerja:
    st.subheader(f"📅 {hari}")
    
    # 1. Pilih Status dulu
    status = st.radio(
        f"Status {hari}", 
        ["Normal (8 Jam)", "Lembur", "Libur"], 
        key=f"status_{hari}", 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    jam_berangkat = None
    jam_pulang = None
    
    # 2. Jika LEMBUR, Munculkan Roda Gulir (Dropdown)
    if status == "Lembur":
        st.write("🔻 **Jam Berangkat:**")
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            # Default jam 10 pagi (index 10)
            b_jam = st.selectbox(f"Jam (Masuk) {hari}", list_jam, index=10, key=f"bj_{hari}")
        with col_b2:
            # Default menit 00 (index 0)
            b_menit = st.selectbox(f"Menit (Masuk) {hari}", list_menit, index=0, key=f"bm_{hari}")
            
        st.write("🔻 **Jam Pulang:**")
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            # Default jam 21 malam (index 21)
            p_jam = st.selectbox(f"Jam (Pulang) {hari}", list_jam, index=21, key=f"pj_{hari}")
        with col_p2:
            # Default menit 30 (index 30)
            p_menit = st.selectbox(f"Menit (Pulang) {hari}", list_menit, index=30, key=f"pm_{hari}")

        # Gabungkan Jam & Menit menjadi format Waktu agar bisa dihitung
        jam_berangkat = time(int(b_jam), int(b_menit))
        jam_pulang = time(int(p_jam), int(p_menit))

    data_mingguan[hari] = {
        "status": status,
        "berangkat": jam_berangkat,
        "pulang": jam_pulang
    }
    st.write("---") 

# --- TOMBOL PROSES ---
if st.button("💰 BUAT LAPORAN WA", type="primary", use_container_width=True):
    
    total_gaji_bersih = 0
    laporan_text = "*SLIP GAJI MINGGUAN KEDAI SAMARATA*\n"
    laporan_text += "Periode: Senin s.d. Sabtu\n\n"
    laporan_text += "| Hari | Keterangan | Lembur | Total |\n"
    laporan_text += "| :--- | :--- | :--- | :--- |\n"
    
    for hari, data in data_mingguan.items():
        gaji_harian = 0
        
        if data["status"] == "Libur":
            laporan_text += f"| *{hari}* | LIBUR | - | Rp0 |\n"
            continue
            
        elif data["status"] == "Normal (8 Jam)":
            gaji_harian = GAJI_POKOK
            laporan_text += f"| *{hari}* | Normal | - | Rp{gaji_harian:,} |\n"
            
        elif data["status"] == "Lembur":
            # Hitung selisih waktu
            t1 = datetime.combine(datetime.today(), data["berangkat"])
            t2 = datetime.combine(datetime.today(), data["pulang"])
            
            durasi = t2 - t1
            total_menit = durasi.total_seconds() / 60
            
            # Jika pulang lewat tengah malam (misal masuk 18:00 pulang 02:00)
            if total_menit < 0:
                total_menit += 24 * 60
            
            # Hitung lembur (di atas 8 jam / 480 menit)
            menit_lembur = total_menit - 480
            
            if menit_lembur > 0:
                upah_lembur = (menit_lembur / 60) * RATE_LEMBUR_PER_JAM
                gaji_harian = GAJI_POKOK + upah_lembur
                
                jam_l = int(menit_lembur // 60)
                menit_l = int(menit_lembur % 60)
                durasi_str = f"{jam_l}j {menit_l}m" if jam_l > 0 else f"{menit_l} menit"
                
                laporan_text += f"| *{hari}* | Lembur {durasi_str} | +Rp{int(upah_lembur):,} | Rp{int(gaji_harian):,} |\n"
            else:
                gaji_harian = GAJI_POKOK
                laporan_text += f"| *{hari}* | Normal/Kurang | - | Rp{gaji_harian:,} |\n"

        total_gaji_bersih += gaji_harian

    laporan_text += f"\n*TOTAL DITERIMA: Rp{int(total_gaji_bersih):,}*"
    laporan_text += "\n\nTerima kasih atas kerja kerasnya! 🍗"
    laporan_text = laporan_text.replace(",", ".") 
    
    st.success("Laporan Berhasil Dibuat!")
    st.code(laporan_text, language='markdown')
