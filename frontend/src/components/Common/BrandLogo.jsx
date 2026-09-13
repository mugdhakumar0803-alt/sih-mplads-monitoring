function BrandLogo({ compact = false, dark = false, className = "" }) {
  const textColor = dark ? "text-white" : "text-navy";
  const subtitleColor = dark ? "text-slate-200" : "text-gray-500";
  const accentColor = dark ? "#F8FAFC" : "#0B1F3A";
  const lowOpacity = dark ? "rgba(255,255,255,0.9)" : "rgba(11,31,58,0.9)";

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <svg
        viewBox="0 0 120 84"
        className={compact ? "h-10 w-12" : "h-16 w-20"}
        aria-label="PANCHSETU logo"
        role="img"
      >
        <defs>
          <linearGradient id="panchsetu-wave" x1="0" x2="1">
            <stop offset="0%" stopColor="#F59E0B" />
            <stop offset="33%" stopColor="#F8FAFC" />
            <stop offset="66%" stopColor="#F8FAFC" />
            <stop offset="100%" stopColor="#22C55E" />
          </linearGradient>
        </defs>

        <path
          d="M10 56C24 48 34 48 42 54C48 58 52 60 60 60C69 60 75 56 82 52C90 46 97 46 110 55"
          fill="none"
          stroke="url(#panchsetu-wave)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        <g fill={accentColor}>
          <g transform="translate(12 8)">
            <circle cx="8" cy="9" r="4.5" fill={lowOpacity} />
            <path d="M4 20h8l2 18H2l2-18Z" fill={lowOpacity} />
          </g>
          <g transform="translate(26 4)">
            <circle cx="8" cy="9" r="4.8" fill={lowOpacity} />
            <path d="M3 22h10l2.5 17H.5L3 22Z" fill={lowOpacity} />
          </g>
          <g transform="translate(42 0)">
            <circle cx="9" cy="10" r="5.4" fill={lowOpacity} />
            <path d="M2 24h14l3.8 20H-1.8L2 24Z" fill={lowOpacity} />
          </g>
          <g transform="translate(60 4)">
            <circle cx="8" cy="9" r="4.8" fill={lowOpacity} />
            <path d="M3 22h10l2.5 17H.5L3 22Z" fill={lowOpacity} />
          </g>
          <g transform="translate(78 8)">
            <circle cx="8" cy="9" r="4.5" fill={lowOpacity} />
            <path d="M4 20h8l2 18H2l2-18Z" fill={lowOpacity} />
          </g>
        </g>
      </svg>

      <div
        className={[
          textColor,
          "font-black tracking-[0.14em] uppercase leading-none",
          compact ? "text-base" : "text-[2.15rem]",
        ].join(" ")}
      >
        PANCHSETU
      </div>

      {!compact && (
        <p className={`mt-1 text-sm ${subtitleColor}`}>
          MPLADS Monitoring & Accountability Portal
        </p>
      )}
    </div>
  );
}

export default BrandLogo;
