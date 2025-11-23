import streamlit as st
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Payroll Samarata", page_icon="🍗")

st.title("🍗 Payroll Kedai Samarata")
st.caption("Aplikasi Hitung Gaji & Lembur Otomatis")

# --- KONSTANTA ---
GAJI_POKOK = 50000
RATE_LEMBUR_PER_JAM = 10000

# --- DATA INPUT ---
# Kita hapus st.form agar interaksi menjadi LANGSUNG (Real-time)
st.divider()

data_mingguan = {}
hari_kerja = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]

for hari in hari_kerja:
    st.subheader(f"📅 {hari}")
    
    # Layout kolom agar rapi
    col_status, col_berangkat, col_pulang = st.columns([1.5, 1, 1])
    
    with col_status:
        # Pilihan status
        status = st.radio(
            f"Status {hari}", 
            ["Normal (8 Jam)", "Lembur", "Libur"], 
            key=f"status_{hari}", 
            horizontal=True,
            label_visibility="collapsed" # Menyembunyikan label agar bersih
        )
    
    jam_berangkat = None
    jam_pulang = None
    
    # LOGIKA: Jika pencet LEMBUR, kolom jam LANGSUNG muncul
    if status == "Lembur":
        with col_berangkat:
            # step=60 artinya bisa diatur per 1 menit (60 detik)
            jam_berangkat = st.time_input(f"Berangkat {hari}", datetime.strptime("10:00", "%H:%M"), step=60)
        with col_pulang:
            jam_pulang = st.time_input(f"Pulang {hari}", datetime.strptime("21:30", "%H:%M"), step=60)

    data_mingguan[hari] = {
        "status": status,
        "berangkat": jam_berangkat,
        "pulang": jam_pulang
    }
    st.write("---") # Garis pemisah tipis antar hari

# --- TOMBOL PROSES ---
if st.button("💰 BUAT LAPORAN WA", type="primary", use_container_width=True):
    
    total_gaji_bersih = 0
    laporan_text = "*SLIP GAJI MINGGUAN KEDAI SAMARATA*\n"
    laporan_text += "Periode: Senin s.d. Sabtu\n\n"
    
    # Header Tabel Manual untuk WA
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
            
            # Hitung lembur (di atas 8 jam / 480 menit)
            menit_lembur = total_menit - 480
            
            if menit_lembur > 0:
                upah_lembur = (menit_lembur / 60) * RATE_LEMBUR_PER_JAM
                gaji_harian = GAJI_POKOK + upah_lembur
                
                # Format jam menit
                jam_l = int(menit_lembur // 60)
                menit_l = int(menit_lembur % 60)
                
                # Teks durasi lembur
                durasi_str = f"{jam_l}j {menit_l}m" if jam_l > 0 else f"{menit_l} menit"
                
                laporan_text += f"| *{hari}* | Lembur {durasi_str} | +Rp{int(upah_lembur):,} | Rp{int(gaji_harian):,} |\n"
                
            else:
                # Kasus kerja kurang dari 8 jam tapi pilih lembur
                gaji_harian = GAJI_POKOK
                laporan_text += f"| *{hari}* | Normal/Kurang | - | Rp{gaji_harian:,} |\n"

        total_gaji_bersih += gaji_harian

    # Footer Laporan
    laporan_text += f"\n*TOTAL DITERIMA: Rp{int(total_gaji_bersih):,}*"
    laporan_text += "\n\nTerima kasih atas kerja kerasnya! 🍗"
    
    # Format Rupiah (Ganti koma jadi titik)
    laporan_text = laporan_text.replace(",", ".") 
    
    # --- OUTPUT ---
    st.success("Laporan Berhasil Dibuat!")
    st.write("Klik ikon **Salin/Copy** di pojok kanan atas kotak abu-abu di bawah ini:")
    
    # Widget st.code ini OTOMATIS punya tombol copy & read-only
    st.code(laporan_text, language='markdown')