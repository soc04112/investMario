export async function User_Information() {
    try {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        const res = await fetch(`${import.meta.env.VITE_POST_URL}/api/get_user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                timezone: timezone
            })
        });
        
        const data = await res.json();
        console.log(data)

        return data;

    } catch (err) {
        console.error("데이터 가져오기 실패:", err);
        return null;
    }
}

export async function User_Infor_Modify(send_data) {
    try {
        const res = await fetch(`${import.meta.env.VITE_POST_URL}/api/userinfo_modify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                data : send_data
            })
        });

        const data = await res.json();
        
        if (data.data == "Update success") {
            alert("Update Complete");
            window.scrollTo(0, 0);
            window.location.reload(); 
        }

    } catch (err) {
        console.error("데이터 저장 실패:", err);
    }
}
