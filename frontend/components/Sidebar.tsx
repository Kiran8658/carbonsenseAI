import React from 'react';
import { BarChart3, TrendingUp, Home, Leaf, FileText, Cpu } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const Sidebar: React.FC = () => {
  const router = useRouter();

  const navItems = [
    { icon: Home,       label: 'Dashboard',  href: '/' },
    { icon: BarChart3,  label: 'Analytics',  href: '/analytics' },
    { icon: TrendingUp, label: 'Reports',    href: '/reports' },
  ];

  const isActive = (href: string) => router.pathname === href;

  return (
    <div className="w-64 h-screen fixed left-0 top-0 flex flex-col"
      style={{ background: "#040910", borderRight: "1px solid var(--border)" }}>

      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-5"
        style={{ borderBottom: "1px solid var(--border)" }}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: "linear-gradient(135deg,#22c55e,#4ade80)", boxShadow: "0 0 16px rgba(34,197,94,0.4)" }}>
          <Leaf size={16} color="#050b12" strokeWidth={2.5} />
        </div>
        <div>
          <h1 style={{ fontFamily: "Syne", fontSize: 16, fontWeight: 800, color: "var(--text-primary)", lineHeight: 1.1 }}>
            CarbonSense
          </h1>
          <p style={{ fontSize: 9, color: "var(--green-primary)", fontFamily: "DM Mono", letterSpacing: 1 }}>
            AI • v2.0
          </p>
        </div>
      </div>

      {/* ML Badge */}
      <div className="mx-4 mt-4 mb-2 px-3 py-2 rounded-lg text-center"
        style={{ background: "linear-gradient(135deg,rgba(34,197,94,0.08),rgba(74,222,128,0.04))", border: "1px solid rgba(34,197,94,0.15)" }}>
        <div className="flex items-center justify-center gap-2">
          <Cpu size={11} style={{ color: "#22c55e" }} />
          <span style={{ fontSize: 10, color: "#22c55e", fontFamily: "DM Mono", letterSpacing: 0.5 }}>
            ML PIPELINE ACTIVE
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <p style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "DM Mono", letterSpacing: 1, marginBottom: 8, paddingLeft: 12 }}>
          NAVIGATE
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          return (
            <Link key={item.href} href={item.href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-200 ${
                active ? '' : 'hover:bg-opacity-50'
              }`}
              style={{
                background: active ? "rgba(34,197,94,0.1)" : "transparent",
                border: active ? "1px solid rgba(34,197,94,0.2)" : "1px solid transparent",
                color: active ? "#22c55e" : "var(--text-muted)",
              }}
              onMouseEnter={e => {
                if (!active) {
                  (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.03)";
                  (e.currentTarget as HTMLElement).style.color = "var(--text-primary)";
                }
              }}
              onMouseLeave={e => {
                if (!active) {
                  (e.currentTarget as HTMLElement).style.background = "transparent";
                  (e.currentTarget as HTMLElement).style.color = "var(--text-muted)";
                }
              }}
            >
              <Icon size={17} />
              <span style={{ fontSize: 14, fontWeight: 500, fontFamily: "DM Sans" }}>{item.label}</span>
              {active && <div className="ml-auto w-1.5 h-1.5 rounded-full" style={{ background: "#22c55e", boxShadow: "0 0 8px #22c55e" }} />}
            </Link>
          );
        })}
      </nav>

      {/* Bottom: ESG Summary */}
      <div className="mx-3 mb-4 p-4 rounded-xl"
        style={{ background: "rgba(34,197,94,0.05)", border: "1px solid rgba(34,197,94,0.1)" }}>
        <div className="flex items-center gap-2 mb-2">
          <FileText size={12} style={{ color: "#22c55e" }} />
          <span style={{ fontSize: 11, color: "#22c55e", fontFamily: "Syne", fontWeight: 700 }}>ESG Ready</span>
        </div>
        <p style={{ fontSize: 11, color: "var(--text-muted)", lineHeight: 1.4 }}>
          Generate ESG reports from the Reports page
        </p>
      </div>
    </div>
  );
};

export default Sidebar;
