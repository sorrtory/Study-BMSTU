// components/GitHubBadge.tsx
import { FaGithub } from "react-icons/fa";

export default function GitHubBadge() {
  return (
    <a
      href="https://github.com/sorrtory-vercel/stable-fluids-webgpu"
      target="_blank"
      rel="noopener noreferrer"
      style={{
        position: "fixed",
        top: 16,
        left: 16,
        zIndex: 1000,
        background: "#000",
        color: "#fff",
        padding: "8px 12px",
        borderRadius: "999px",
        display: "flex",
        alignItems: "center",
        gap: "8px",
        textDecoration: "none",
      }}
    >
      <FaGithub size={18} />
      <span>GitHub</span>
    </a>
  );
}
