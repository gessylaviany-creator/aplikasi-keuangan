import streamlit as st
import pandas as pd
import datetime
import random
import smtplib
from email.mime.text import MIMEText

# 1. KONFIGURASI APLIKASI
st.set_page_config(page_title="Aplikasi Keuangan Gessyla & Lutfi", layout="wide", page_icon="💰")

# Inisialisasi State Database
if "users" not in st.session_state:
    st.session_state.users = {
        "admin@gmail.com": {"name": "Admin", "password": "admin", "role": "Admin", "verified": True},
        "gessyla@gmail.com": {"name": "Gessyla", "password": "123", "role": "User", "verified": True},
        "lutfi@gmail.com": {"name": "Lutfi", "password": "123", "role": "User", "verified": True}
    }

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "otp_store" not in st.session_state:
    st.session_state.otp_store = {}

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# Key unik untuk reset input form
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

# 2. OTENTIKASI (LOGIN & REGISTER)
if st.session_state.logged_in_user is None:
    st.title("🔐 Tracking Keuangan - Login")
    
    menu = st.sidebar.selectbox("Pilih Menu", ["Login", "Register Akun Baru"])
    
    if menu == "Register Akun Baru":
        st.subheader("Pendaftaran Akun Baru (Gmail)")
        reg_name = st.selectbox("Daftar Sebagai Profil", ["Gessyla", "Lutfi", "Admin"])
        reg_email = st.text_input("Alamat Gmail")
        reg_pass = st.text_input("Kata Sandi", type="password")
        
        if st.button("Kirim Kode OTP Verifikasi Email"):
            if "@gmail.com" not in reg_email:
                st.error("Wajib menggunakan alamat @gmail.com")
            elif reg_email in st.session_state.users:
                st.error("Email sudah terdaftar!")
            else:
                otp = str(random.randint(100000, 999999))
                
                # Konfigurasi Gmail Pengirim
                sender_email = gessylaviany@gmail.com  # Ganti dengan Gmail kamu
                sender_password = "kxkr kjwp ebkv plgg" # 16 digit App Password Google
                
                # Format Pesan Email
                msg = MIMEText(f"Kode OTP verifikasi akun Anda adalah: {otp}")
                msg['Subject'] = 'Kode OTP Verifikasi - Aplikasi Keuangan'
                msg['From'] = sender_email
                msg['To'] = reg_email
                
                try:
                    # Kirim via SMTP Gmail
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, reg_email, msg.as_string())
                    
                    st.session_state.otp_store[reg_email] = {
                        "otp": otp, "name": reg_name, "pass": reg_pass
                    }
                    st.success(f"Kode OTP berhasil dikirim ke {reg_email}! Cek kotak masuk/spam email kamu.")
                except Exception as e:
                    st.error(f"Gagal mengirim email: {e}")

        st.divider()
        st.subheader("Verifikasi OTP Email")
        verify_email = st.text_input("Masukkan Gmail yang Didaftarkan")
        input_otp = st.text_input("Masukkan 6 Digit Kode OTP")
        
        if st.button("Aktivasi Akun"):
            if verify_email in st.session_state.otp_store:
                correct_otp = st.session_state.otp_store[verify_email]["otp"]
                if input_otp == correct_otp:
                    user_data = st.session_state.otp_store[verify_email]
                    st.session_state.users[verify_email] = {
                        "name": user_data["name"],
                        "password": user_data["pass"],
                        "role": "Admin" if user_data["name"] == "Admin" else "User",
                        "verified": True
                    }
                    del st.session_state.otp_store[verify_email]
                    st.success("Akun berhasil diverifikasi! Silakan login.")
                else:
                    st.error("Kode OTP salah!")
            else:
                st.error("Email tidak ditemukan.")

    elif menu == "Login":
        st.subheader("Masuk ke Akun")
        login_email = st.text_input("Gmail")
        login_pass = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login_email in st.session_state.users:
                user = st.session_state.users[login_email]
                if user["password"] == login_pass and user["verified"]:
                    st.session_state.logged_in_user = {
                        "email": login_email,
                        "name": user["name"],
                        "role": user["role"]
                    }
                    st.rerun()
                else:
                    st.error("Password salah atau akun belum terverifikasi!")
            else:
                st.error("Email belum terdaftar!")

# 3. DASHBOARD UTAMA
else:
    current_user = st.session_state.logged_in_user
    st.sidebar.write(f"👤 Login sebagai: **{current_user['name']}** ({current_user['role']})")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None
        st.rerun()

    st.title("📊 Dashboard Catatan Keuangan")

    active_tab = st.radio(
        "Pilih Modul Transaksi:",
        ["Catatan Keuangan Pribadi", "🤝 Tabungan Bersama"],
        horizontal=True
    )

    st.divider()

    expense_categories = ["Makanan & Minuman", "Belanja", "Transportasi", "Tagihan & Pulsa", "Hiburan", "Kesehatan", "Lainnya"]
    income_categories = ["Gaji", "Bonus", "Hasil Usaha", "Hadiah", "Investasi", "Lainnya"]

    st.subheader(f"➕ Tambah Transaksi ({active_tab})")

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tx_type = st.selectbox("Jenis Transaksi", ["Pengeluaran", "Pemasukan"], key=f"type_{st.session_state.form_key}")
    with col2:
        categories = expense_categories if tx_type == "Pengeluaran" else income_categories
        tx_category = st.selectbox("Kategori", categories, key=f"cat_{st.session_state.form_key}")
    with col3:
        tx_amount = st.number_input("Jumlah (Rp)", min_value=0, step=5000, key=f"amount_{st.session_state.form_key}")
    with col4:
        tx_date = st.date_input("Tanggal", datetime.date.today(), key=f"date_{st.session_state.form_key}")

    tx_desc = st.text_input("Keterangan / Catatan", key=f"desc_{st.session_state.form_key}")

    if st.button("Simpan Transaksi"):
        if tx_amount > 0:
            target_account = "TABUNGAN_BERSAMA" if active_tab == "🤝 Tabungan Bersama" else current_user["name"]
            
            st.session_state.transactions.append({
                "User": current_user["name"],
                "Account": target_account,
                "Type": tx_type,
                "Category": tx_category,
                "Amount": tx_amount,
                "Date": str(tx_date),
                "Description": tx_desc
            })
            # Mengubah form_key untuk mereset seluruh form secara aman
            st.session_state.form_key += 1
            st.success("Transaksi berhasil disimpan!")
            st.rerun()
        else:
            st.warning("Jumlah transaksi harus lebih dari 0!")

    st.divider()

    target_account_filter = "TABUNGAN_BERSAMA" if active_tab == "🤝 Tabungan Bersama" else current_user["name"]
    
    df_all = pd.DataFrame(st.session_state.transactions)
    
    if not df_all.empty:
        df_filtered = df_all[df_all["Account"] == target_account_filter]
    else:
        df_filtered = pd.DataFrame()

    st.subheader(f"📈 Ringkasan & Laporan ({active_tab})")

    if not df_filtered.empty:
        total_pemasukan = df_filtered[df_filtered["Type"] == "Pemasukan"]["Amount"].sum()
        total_pengeluaran = df_filtered[df_filtered["Type"] == "Pengeluaran"]["Amount"].sum()
        saldo_akhir = total_pemasukan - total_pengeluaran

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.0f}")
        m2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}")
        m3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.0f}")

        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("**Grafik Pengeluaran per Kategori**")
            df_exp = df_filtered[df_filtered["Type"] == "Pengeluaran"]
            if not df_exp.empty:
                chart_data = df_exp.groupby("Category")["Amount"].sum()
                st.bar_chart(chart_data)
            else:
                st.info("Belum ada data pengeluaran.")

        with col_chart2:
            st.markdown("**Tabel Riwayat Transaksi**")
            st.dataframe(df_filtered[["Date", "User", "Type", "Category", "Amount", "Description"]], use_container_width=True)

        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Laporan (CSV)",
            data=csv_data,
            file_name=f"Laporan_Keuangan_{target_account_filter}_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("Belum ada transaksi yang dicatat pada modul ini.")
