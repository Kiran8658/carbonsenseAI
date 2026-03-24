import { Leaf, Activity, FileText } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/router";

export default function Navbar() {
  const router = useRouter();
  const isReportsPage = router.pathname === "/reports";

  return (
    <nav
      style={{
        background: "rgba(10,15,26,0.85)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--border)",
        position: "sticky",
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        style={{
          maxWidth: 1280,
          margin: "0 auto",
          padding: "0 24px",
          height: 64,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        {/* Logo */}
        <Link href="/">
          <div style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }}>
            <div
              style={{
                width: 36,
                height: 36,
                background: "var(--green-glow)",
                border: "1px solid var(--green-primary)",
                borderRadius: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Leaf size={18} color="var(--green-primary)" />
            </div>
            <div>
              <span
                style={{
                  fontFamily: "Syne, sans-serif",
                  fontWeight: 800,
                  fontSize: 18,
                  color: "var(--text-primary)",
                  letterSpacing: "-0.02em",
                }}
              >
                Carbon<span style={{ color: "var(--green-primary)" }}>Sense</span>
              </span>
              <span
                style={{
                  marginLeft: 8,
                  background: "var(--green-glow)",
                  border: "1px solid var(--green-dim)",
                  color: "var(--green-primary)",
                  fontSize: 10,
                  fontWeight: 700,
                  fontFamily: "Syne, sans-serif",
                  letterSpacing: "0.1em",
                  padding: "2px 7px",
                  borderRadius: 20,
                  textTransform: "uppercase",
                }}
              >
                AI
              </span>
            </div>
          </div>
        </Link>

        {/* Right */}
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              color: "var(--text-muted)",
              fontSize: 13,
              fontFamily: "DM Mono, monospace",
            }}
          >
            <Activity size={14} color="var(--green-primary)" />
            <span>Live</span>
          </div>

          <Link href="/reports">
            <button
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                background: isReportsPage ? "var(--green-primary)" : "transparent",
                border: isReportsPage ? "none" : "1px solid var(--green-dim)",
                color: isReportsPage ? "white" : "var(--green-primary)",
                padding: "6px 14px",
                borderRadius: 8,
                fontSize: 12,
                fontWeight: 600,
                fontFamily: "Syne, sans-serif",
                cursor: "pointer",
                transition: "all 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (!isReportsPage) {
                  e.currentTarget.style.background = "var(--green-glow)";
                }
              }}
              onMouseLeave={(e) => {
                if (!isReportsPage) {
                  e.currentTarget.style.background = "transparent";
                }
              }}
            >
              <FileText size={14} />
              Reports
            </button>
          </Link>

          <div
            style={{
              background: "var(--green-glow)",
              border: "1px solid var(--green-dim)",
              borderRadius: 8,
              padding: "6px 14px",
              color: "var(--green-primary)",
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "Syne, sans-serif",
            }}
          >
            MSME Dashboard
          </div>
        </div>
      </div>
    </nav>
  );
}
