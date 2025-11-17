import os
import requests
import streamlit as st

# ====== CẤU HÌNH API KEY ======
# Cách an toàn: đặt SCOPUS_API_KEY ở environment variable, ví dụ:
#   export SCOPUS_API_KEY="xxxxx" (Linux/Mac)
#   setx SCOPUS_API_KEY "xxxxx"   (Windows, mở terminal mới)
API_KEY = os.getenv("SCOPUS_API_KEY")

BASE_URL = "https://api.elsevier.com/content/search/scopus"


def check_scopus_by_title(title: str):
    query = f'TITLE("{title}")'
    params = {
        "query": query,
        "count": 10,
        "view": "STANDARD"
    }
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json"
    }
    r = requests.get(BASE_URL, params=params, headers=headers)
    r.raise_for_status()
    data = r.json()
    total = int(data["search-results"]["opensearch:totalResults"])

    results = []
    if total > 0:
        for entry in data["search-results"]["entry"]:
            results.append({
                "title": entry.get("dc:title"),
                "creator": entry.get("dc:creator"),
                "publicationName": entry.get("prism:publicationName"),
                "coverDate": entry.get("prism:coverDate"),
                "doi": entry.get("prism:doi"),
                "scopus_id": entry.get("dc:identifier"),
            })
    return total, results


def check_scopus_by_doi(doi: str):
    query = f'DOI("{doi}")'
    params = {
        "query": query,
        "count": 5,
        "view": "STANDARD"
    }
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json"
    }
    r = requests.get(BASE_URL, params=params, headers=headers)
    r.raise_for_status()
    data = r.json()
    total = int(data["search-results"]["opensearch:totalResults"])

    if total > 0:
        entry = data["search-results"]["entry"][0]
        info = {
            "title": entry.get("dc:title"),
            "creator": entry.get("dc:creator"),
            "publicationName": entry.get("prism:publicationName"),
            "coverDate": entry.get("prism:coverDate"),
            "doi": entry.get("prism:doi"),
            "scopus_id": entry.get("dc:identifier"),
        }
        return total, info
    else:
        return 0, None


# ====== GIAO DIỆN WEB VỚI STREAMLIT ======
def main():
    st.title("(APD) Kiểm tra bài báo có thuộc Scopus hay không?")
    st.write("Nhập **DOI** (khuyến nghị) hoặc **tiêu đề bài báo** để kiểm tra.")

    if not API_KEY:
        st.error("Chưa tìm thấy SCOPUS_API_KEY trong environment variable. Hãy cấu hình API key trước.")
        st.stop()

    option = st.radio(
        "Bạn muốn kiểm tra theo:",
        ("DOI", "Tiêu đề (Title)")
    )

    if option == "DOI":
        doi = st.text_input("Nhập DOI bài báo (ví dụ: 10.1016/j.future.2020.01.001)")
        if st.button("Kiểm tra DOI"):
            if not doi.strip():
                st.warning("Vui lòng nhập DOI.")
            else:
                try:
                    total, info = check_scopus_by_doi(doi.strip())
                    if total > 0:
                        st.success("Bài báo với DOI này **CÓ** trong Scopus.")
                        st.write("**Tiêu đề:**", info["title"])
                        st.write("**Tác giả chính:**", info["creator"])
                        st.write("**Tạp chí:**", info["publicationName"])
                        st.write("**Ngày xuất bản:**", info["coverDate"])
                        st.write("**DOI:**", info["doi"])
                        st.write("**Scopus ID:**", info["scopus_id"])
                    else:
                        st.error("Không tìm thấy bài báo với DOI này trong Scopus.")
                except Exception as e:
                    st.error(f"Lỗi khi gọi API: {e}")

    else:  # Title
        title = st.text_input("Nhập tiêu đề bài báo (hoặc gần đúng)")
        if st.button("Kiểm tra tiêu đề"):
            if not title.strip():
                st.warning("Vui lòng nhập tiêu đề.")
            else:
                try:
                    total, results = check_scopus_by_title(title.strip())
                    if total > 0:
                        st.success(f"Tìm thấy {total} kết quả trong Scopus (hiển thị tối đa 10).")
                        for i, art in enumerate(results, start=1):
                            st.markdown(f"### Kết quả {i}")
                            st.write("**Tiêu đề:**", art["title"])
                            st.write("**Tác giả chính:**", art["creator"])
                            st.write("**Tạp chí:**", art["publicationName"])
                            st.write("**Ngày xuất bản:**", art["coverDate"])
                            st.write("**DOI:**", art["doi"])
                            st.write("**Scopus ID:**", art["scopus_id"])
                            st.markdown("---")
                    else:
                        st.error("Không tìm thấy bài báo với tiêu đề đã nhập trong Scopus.")
                except Exception as e:
                    st.error(f"Lỗi khi gọi API: {e}")

        st.markdown("""
        <hr>
        <div style='text-align:center; color:gray; font-size:14px; margin-top:20px;'>
            © 2025 – Phòng Quản lý Khoa học và hợp tác - Học viện Chính sách và Phát triển (APD).
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
