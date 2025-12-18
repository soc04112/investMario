import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import LoginWelcomeModal from './LoginWelcomeModal';
import WelcomeModal from "./WelcomeModal"; 

export default function GoogleRedirect() {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [signshowModel, setSignShowModal] = useState(false)
  const [modalMessage, setModalMessage] = useState(""); 

  const handleModalConfirm = () => {
    setShowModal(false);
    setTimeout(() => {
      window.location.href = "/trade";
    }, 300); 
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (!code) return;

    const sendCodeToServer = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_POST_URL}/api/GoogleLogin`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: code }),
          credentials: "include",
        });

        const data = await res.json();

        if (data.message === "exists" || data.message === "new") {
          setModalMessage(`${data.userid}님 반가워요!`);
          setShowModal(true); 
        } 

      } catch (err) {
        console.error("Fetch error:", err);
        setModalMessage("로그인 실패: " + err);
        setShowModal(true);
      }
    };

    sendCodeToServer();
  }, [navigate]);

  return (
    <>
      {showModal && (
        <LoginWelcomeModal
          message={modalMessage}
          onConfirm={handleModalConfirm}
        />
      )}
      {signshowModel && (
        <WelcomeModal
          onConfirm={() => navigate("/trade")}
        />
      )}
    </>
  );
}
