import streamlit as st
from datetime import datetime, time, timedelta

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Payroll Samarata", page_icon="🍗")

st.title("🍗 Payroll Kedai Samarata")
st.caption("Aplikasi sudah di-hack agar keyboard langsung Numeric Mode!")

# --- KONSTANTA ---
GAJI_POKOK = 50000
RATE_LEMBUR_PER_JAM = 10000

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
    
    # 2. Jika LEMBUR, Munculkan Input Jam
    if status == "Lembur":
        
        col_b, col_p = st.columns(2)
        
        # JAM BERANGKAT
        with col_b:
            jam_berangkat = st.time_input(
                f"Jam Berangkat {hari}", 
                datetime.strptime("10:00", "%H:%M").time(), 
                step=timedelta(minutes=1),
                key=f"jb_{hari}"
            )
        
        # JAM PULANG
        with col_p:
            jam_pulang = st.time_input(
                f"Jam Pulang {hari}", 
                datetime.strptime("21:30", "%H:%M").time(), 
                step=timedelta(minutes=1),
                key=f"jp_{hari}"
            )

    data_mingguan[hari] = {
        "status": status,
        "berangkat": jam_berangkat,
        "pulang": jam_pulang
    }
    st.write("---") 

# --- SUNTIKAN JAVASCRIPT UNTUK KEYBOARD NUMERIC ---
# Kita gunakan inputmode='tel' agar muncul keypad telepon/angka yang lebih besar di Android
js_code = """
<script>
    function setNumericKeyboard() {
        // Target semua input teks yang digunakan oleh st.time_input
        const timeInputs = document.querySelectorAll('input[type="text"]');
        
        timeInputs.forEach(input => {
            // Cek apakah input adalah bagian dari widget jam/tanggal Streamlit
            if (input.placeholder === "HH:MM" || input.placeholder === "HH:MM:SS") {
                 // Set inputmode ke 'tel' (paling efektif di Android untuk keypad angka)
                 input.setAttribute('inputmode', 'tel');
            }
        });
    }
    // Jalankan fungsi setelah Streamlit selesai memuat
    window.onload = setNumericKeyboard;
</script>
"""
# Baris ini menyuntikkan kode JavaScript ke halaman web
st.markdown(js_code, unsafe_allow_html=True)
# --- AKHIR SUNTIKAN ---


# --- TOMBOL PROSES (Perhitungan) ---
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
            
        elif data["status"] == "Lembur" and data["berangkat"] and data["pulang"]:
            # Perhitungan durasi (sama seperti sebelumnya)
            t1 = datetime.combine(datetime.today(), data["berangkat"])
            t2 = datetime.combine(datetime.today(), data["pulang"])
            durasi = t2 - t1
            total_menit = durasi.total_seconds() / 60
            if total_menit < 0: total_menit += 24 * 60
            
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
        
        else:
             gaji_harian = GAJI_POKOK
             laporan_text += f"| *{hari}* | Normal | - | Rp{gaji_harian:,} |\n"


        total_gaji_bersih += gaji_harian

    laporan_text += f"\n*TOTAL DITERIMA: Rp{int(total_gaji_bersih):,}*"
    laporan_text += "\n\nTerima kasih atas kerja kerasnya! 🍗"
    laporan_text = laporan_text.replace(",", ".") 
    
    st.success("Laporan Berhasil Dibuat!")
    st.code(laporan_text, language='markdown')
